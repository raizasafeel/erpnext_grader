from __future__ import annotations

import json

import frappe
import requests
from frappe import _
from frappe.utils import add_days, get_datetime, now_datetime
from frappe.utils.password import (
	get_decrypted_password,
	remove_encrypted_password,
	set_encrypted_password,
)


def _get_course() -> str | None:
	return frappe.db.get_single_value("ERPNext Assignment Portal Settings", "course")


def _require_enrolled(user: str | None = None) -> str:
	if user is None:
		user = frappe.session.user
		if user == "Guest":
			frappe.throw(_("Please log in."), frappe.AuthenticationError)
	course = _get_course()
	if not course or not frappe.db.exists(
		"LMS Enrollment", {"member": user, "course": course}
	):
		frappe.throw(
			_("{0} is not enrolled in this course.").format(user),
			frappe.PermissionError,
		)
	if frappe.db.exists("LMS Certificate", {"member": user, "course": course}):
		frappe.throw(
			_("{0} has already completed this course.").format(user),
			frappe.PermissionError,
		)
	return user


def _existing_site(user: str) -> dict | None:
	return frappe.db.get_value(
		"ERPNext Assignment Student Site",
		{"student": user},
		["name", "site"],
		as_dict=True,
	)


def _existing_token(name: str) -> str | None:
	return get_decrypted_password(
		"ERPNext Assignment Student Site", name, "token_bearer", raise_exception=False
	)


def _valid_token(name: str) -> str | None:
	"""Return the bearer token if it exists and not expired"""
	token = _existing_token(name)
	if not token:
		return None
	expiry = frappe.db.get_value("ERPNext Assignment Student Site", name, "token_expiry")
	if not expiry or get_datetime(expiry) <= now_datetime():
		return None
	return token


@frappe.whitelist()
def get_current_user_info() -> dict:
	user = frappe.session.user
	if user == "Guest":
		return {"user": None, "full_name": None, "course": None, "site": None}

	course = _get_course()
	site = frappe.db.get_value(
		"ERPNext Assignment Student Site",
		{"student": user},
		["name", "site", "last_checked"],
		as_dict=True,
	)
	# if site exists but has no URL or an invalid/expired token, disconnect
	if site and (not site.get("site") or not _valid_token(site["name"])):
		site = None
	return {
		"user": user,
		"full_name": frappe.db.get_value("User", user, "full_name"),
		"course": course,
		"site": site,
	}


@frappe.whitelist()
def get_assignments() -> list[dict]:
	return frappe.get_all(
		"ERPNext Assignment",
		filters={"published": 1},
		fields=["name", "day", "total_checks", "assignment_details"],
		order_by="day asc",
	)


@frappe.whitelist()
def get_my_submissions() -> list[dict]:
	user = _require_enrolled()
	rows = frappe.get_all(
		"ERPNext Assignment Submission",
		filters={"student": user},
		fields=[
			"name",
			"day",
			"submission_time",
			"status",
			"passed_checks",
			"total_checks",
			"percent",
			"results",
		],
		order_by="submission_time desc",
	)
	for r in rows:
		try:
			r["results"] = json.loads(r.get("results") or "[]")
		except (TypeError, ValueError):
			r["results"] = []
	return rows


@frappe.whitelist(allow_guest=True)
def issue_token(email: str) -> dict:
	"""demo site makes this call on app installation; we issue a 30 day token if student enrolled in course"""
	email = (email or "").strip()
	if not email:
		frappe.throw(_("Email is required."))
	_require_enrolled(email)

	token = frappe.generate_hash(length=48)
	expiry = add_days(now_datetime(), 30)

	existing = _existing_site(email)
	if existing:
		name = existing["name"]
		frappe.db.set_value(
			"ERPNext Assignment Student Site", name, "token_expiry", expiry
		)
	else:
		name = (
			frappe.get_doc(
				{
					"doctype": "ERPNext Assignment Student Site",
					"student": email,
					"token_expiry": expiry,
				}
			)
			.insert(ignore_permissions=True)
			.name
		)
	set_encrypted_password(
		"ERPNext Assignment Student Site", name, token, "token_bearer"
	)
	return {"token": token, "expires_at": str(expiry)}


@frappe.whitelist()
def register_site(site: str) -> dict:
	"""frontend call when student registers their demo site url"""
	user = _require_enrolled()
	site = (site or "").strip().rstrip("/")
	if not site:
		frappe.throw(_("Site URL is required."))

	existing = _existing_site(user)
	if not existing:
		frappe.throw(_("Install the grader support app on your demo first."))

	frappe.db.set_value(
		"ERPNext Assignment Student Site",
		existing["name"],
		{"site": site, "last_checked": now_datetime()},
	)
	return {"name": existing["name"], "site": site}


@frappe.whitelist()
def disconnect_site() -> dict:
	user = _require_enrolled()
	row = _existing_site(user)
	if not row:
		return {"ok": True}

	frappe.db.set_value(
		"ERPNext Assignment Student Site",
		row["name"],
		{"site": None, "token_expiry": None, "last_checked": now_datetime()},
	)
	remove_encrypted_password(
		"ERPNext Assignment Student Site", row["name"], "token_bearer"
	)
	return {"ok": True}


@frappe.whitelist()
def grade_day(day: str) -> dict:
	"""grading of a particular day; queues them up"""
	user = _require_enrolled()

	already_passed = frappe.db.exists(
		"ERPNext Assignment Submission",
		{"student": user, "day": day, "status": "Passed"},
	)
	if already_passed:
		frappe.throw(_("You've already passed this day. It can't be regraded."))

	site_row = _existing_site(user)
	if not site_row:
		frappe.throw(_("Install the grader support app on your demo first."))
	if not site_row.get("site"):
		frappe.throw(_("Save your site URL first."))
	if not _valid_token(site_row["name"]):
		frappe.throw(_("No valid token. Reinstall the grader support app to refresh."))

	if not frappe.db.get_value("ERPNext Assignment", day, "published"):
		frappe.throw(_("This assignment is not published."))

	frappe.enqueue(
		"erpnext_grader.erpnext_grader.api._run_grade",
		queue="short",
		job_name=f"grade-{user}-{day}",
		user=user,
		day=day,
		site_name=site_row["name"],
		site_url=site_row["site"],
	)
	return {"queued": True}


def _run_grade(user: str, day: str, site_name: str, site_url: str) -> None:
	try:
		token = _valid_token(site_name)
		if not token:
			_write_failed_submission(
				user, day, site_name, "No valid token. Reinstall the grader support app."
			)
			return

		checks_raw = frappe.db.get_value("ERPNext Assignment", day, "checks") or "{}"
		checks = json.loads(checks_raw)

		url = f"{site_url.rstrip('/')}/api/method/erpnext_grader_support.erpnext_grader_support.api.run_checks_api"
		try:
			resp = requests.post(
				url,
				headers={"X-Grader-Token": token},
				json={"checks": checks},
				timeout=15,
			)
		except requests.ConnectionError:
			_write_failed_submission(user, day, site_name, f"Could not reach {site_url}.")
			return
		except requests.Timeout:
			_write_failed_submission(user, day, site_name, f"Request to {site_url} timed out.")
			return

		if resp.status_code >= 400:
			_write_failed_submission(
				user, day, site_name, f"Demo returned {resp.status_code}: {resp.text[:300]}"
			)
			return

		try:
			result = resp.json().get("message") or {}
		except ValueError:
			_write_failed_submission(user, day, site_name, "Invalid response from demo.")
			return
	except Exception as e:
		_write_failed_submission(user, day, site_name, str(e) or e.__class__.__name__)
		return

	results = result.get("results") or []
	total = int(result.get("total") or 0)
	passed = int(result.get("passed") or 0)
	status = "Passed" if total and passed == total else "Failed"
	percent = round(passed / total * 100, 1) if total else 0

	frappe.get_doc(
		{
			"doctype": "ERPNext Assignment Submission",
			"site": site_name,
			"day": day,
			"total_checks": total,
			"passed_checks": passed,
			"percent": percent,
			"status": status,
			"results": json.dumps(results),
		}
	).insert(ignore_permissions=True)
	frappe.db.set_value(
		"ERPNext Assignment Student Site", site_name, "last_checked", now_datetime()
	)
	frappe.db.commit()


def _write_failed_submission(user: str, day: str, site_name: str, error: str) -> None:
	error_row = [
		{
			"label": "Grading error",
			"passed": False,
			"expected": "Grading completes successfully",
			"actual": error,
		}
	]
	frappe.get_doc(
		{
			"doctype": "ERPNext Assignment Submission",
			"site": site_name,
			"day": day,
			"total_checks": 0,
			"passed_checks": 0,
			"percent": 0,
			"status": "Failed",
			"results": json.dumps(error_row),
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()

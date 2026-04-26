# Copyright (c) 2026, Raiza and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document



class ERPNextAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assignment_details: DF.MarkdownEditor | None
		checks: DF.JSON | None
		day: DF.Int
		published: DF.Check
		total_checks: DF.Int
	# end: auto-generated types

	def autoname(self) -> None:
		self.name = f"day {self.day}"

	def validate(self) -> None:
		self.total_checks = _count_checks(self.checks)

		if not self.published:
			return

		# todo: use mandatory json for this
		if self.total_checks <= 0:
			frappe.throw(_("Published assignments must have at least one grading check."))

		if not self.assignment_details:
			frappe.throw(_("Published assignments must have assignment details."))


def _count_checks(checks_json: str | None) -> int:
	if not checks_json:
		return 0
	try:
		data = json.loads(checks_json)
	except (TypeError, ValueError):
		return 0
	if isinstance(data, dict):
		return sum(
			len(entry.get("checks", []))
			for entries in data.values()
			for entry in entries
		)
	if isinstance(data, list):
		return len(data)
	return 0

# Copyright (c) 2026, Raiza and contributors
import frappe
from frappe.tests.utils import FrappeTestCase


class TestERPNextAssignment(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _make(self, section, checks=None, **kw):
		doc = frappe.get_doc(
			{
				"doctype": "ERPNext Assignment",
				"section": section,
				"checks": frappe.as_json(checks or {}),
				**kw,
			}
		).insert(ignore_permissions=True)
		return doc

	def test_autoname_slugs_section(self):
		doc = self._make("Company Setup")
		self.assertEqual(doc.name, "company-setup")

	def test_autoname_suffixes_on_collision(self):
		a = self._make("Company Setup")
		b = self._make("Company Setup")
		self.assertEqual(a.name, "company-setup")
		self.assertEqual(b.name, "company-setup-2")

	def test_total_checks_counted(self):
		checks = {"Company": [{"title": "Co", "doctype": "Company", "name": "X",
			"checks": [{"heading": "a", "check_type": "match"},
			           {"heading": "b", "check_type": "match"}]}]}
		doc = self._make("Company", checks=checks)
		self.assertEqual(doc.total_checks, 2)

	def test_published_requires_checks(self):
		with self.assertRaises(frappe.ValidationError):
			self._make("Empty", published=1, assignment_details="hi")

import frappe
from frappe.tests.utils import FrappeTestCase
from erpnext_grader.erpnext_grader import api


class TestGraderAPI(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_assignments_returns_section_fields(self):
		frappe.get_doc({"doctype": "ERPNext Assignment", "section": "ZZ Customers",
			"section_order": 2, "blurb": "Two customers", "published": 1,
			"assignment_details": "do it",
			"checks": frappe.as_json({"ZZ Customers": [{"title": "C", "doctype": "Customer",
				"name": "X", "checks": [{"heading": "a", "check_type": "match"}]}]})}).insert(ignore_permissions=True)
		rows = api.get_assignments()
		self.assertTrue(any(r["section"] == "ZZ Customers" and r["section_order"] == 2 for r in rows))
		self.assertIn("blurb", rows[0])
		self.assertNotIn("day", rows[0])

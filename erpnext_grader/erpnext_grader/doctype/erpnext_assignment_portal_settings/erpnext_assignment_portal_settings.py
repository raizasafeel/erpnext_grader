# Copyright (c) 2026, Raiza and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ERPNextAssignmentPortalSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		course: DF.Link
	# end: auto-generated types

	pass

# Copyright (c) 2026, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ModeofPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		currency: DF.Link
		enabled: DF.Check
		type: DF.Literal["Bank", "Cash", "Check"]
	# end: auto-generated types

	pass

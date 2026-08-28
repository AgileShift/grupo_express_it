# Copyright (c) 2026, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PaymentEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.grupo_express_invoice_tool.doctype.payment_entry_line.payment_entry_line import PaymentEntryLine

		amended_from: DF.Link | None
		amount: DF.Currency
		currency: DF.Link
		customer: DF.Link
		entries: DF.Table[PaymentEntryLine]
		mode_of_payment: DF.Link
		posting_date: DF.Date
	# end: auto-generated types

	pass

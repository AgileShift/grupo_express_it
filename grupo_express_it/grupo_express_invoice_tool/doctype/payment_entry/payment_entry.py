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
		exchange_rate: DF.Float
		mode_of_payment: DF.Link
		posting_date: DF.Date
		total_allocated_amount: DF.Currency
		unallocated_amount: DF.Currency
	# end: auto-generated types

	pass

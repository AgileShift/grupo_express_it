from frappe.model.document import Document


class PaymentEntryLine(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allocated_amount: DF.Currency
		currency: DF.Link
		outstanding_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_doctype: DF.Literal["Sales Invoice"]
		reference_name: DF.Link
		total_amount: DF.Currency
	# end: auto-generated types

	pass

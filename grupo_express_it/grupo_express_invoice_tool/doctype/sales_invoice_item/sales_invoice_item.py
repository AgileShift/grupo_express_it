from frappe.model.document import Document


class SalesInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		exp: DF.Data | None
		extra_costs: DF.Check
		invoice_no: DF.Data | None
		invoiced_amount: DF.Currency
		item: DF.Link
		item_type: DF.Data | None
		margin_rate_or_amount: DF.Float
		margin_type: DF.Data | None
		packages: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		policy_number: DF.Data | None
		qty: DF.Float
		uom: DF.Data | None
		valuation_rate: DF.Currency
		vendor: DF.Data | None
	# end: auto-generated types

	pass

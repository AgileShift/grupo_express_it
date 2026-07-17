from frappe.model.document import Document


class PricingRule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		extra_costs: DF.Check
		item: DF.Link
		margin_rate_or_amount: DF.Float
		margin_type: DF.Literal["", "Sobre Factura", "Cantidad Fija", "Valoracion"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		uom: DF.Literal["Bultos", "Unidades", "Libra", "Kilos", "Docenas", "Piezas", "M2", "M3"]
		valuation_rate: DF.Currency
	# end: auto-generated types

	pass

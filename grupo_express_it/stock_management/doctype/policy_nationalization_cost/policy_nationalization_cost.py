from frappe.model.document import Document


class PolicyNationalizationCost(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount_nio: DF.Currency
		amount_usd: DF.Currency
		description: DF.Data | None
		exchange_rate: DF.Currency
		iva: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		posting_date: DF.Date | None
		provider: DF.Data | None
		reference: DF.Data | None
		type: DF.Literal["", "Impuestos Aduaneros", "Nacionalizacion"]
	# end: auto-generated types

	pass

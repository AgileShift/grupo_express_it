from frappe.model.document import Document


class PolicyCIFCost(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount_nio: DF.Currency
		amount_usd: DF.Currency
		description: DF.Data | None
		exchange_rate: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		posting_date: DF.Date | None
		provider: DF.Data | None
		type: DF.Literal["", "Flete", "Seguro"]
	# end: auto-generated types

	pass

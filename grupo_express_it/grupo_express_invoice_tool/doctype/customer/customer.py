from frappe.model.document import Document


class Customer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.grupo_express_invoice_tool.doctype.pricing_rule.pricing_rule import PricingRule

		aliases: DF.SmallText | None
		code: DF.Data | None
		email: DF.Data | None
		full_name: DF.Data
		mobile_no: DF.Data | None
		pricing_rules: DF.Table[PricingRule]
		ruc: DF.Data | None
	# end: auto-generated types

	pass

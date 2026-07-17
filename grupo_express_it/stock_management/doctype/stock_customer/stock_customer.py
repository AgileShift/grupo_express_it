from frappe.model.document import Document


class StockCustomer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		customer_name: DF.Data
		mobile_no: DF.Phone | None
		ruc: DF.Data | None
	# end: auto-generated types

	pass

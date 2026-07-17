from frappe.model.document import Document


class Item(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		item_name: DF.Data
		type: DF.Literal["", "Regular", "Contenedor", "Complemento"]
	# end: auto-generated types

	pass

from frappe.model.document import Document


class StockSalesInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		item: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		policy: DF.Link
		policy_item: DF.Link
		price: DF.Currency
		qty: DF.Float
		total: DF.Currency
		unit_price: DF.Currency
		uom: DF.Literal["", "Unidad", "Docenas", "Millar", "Gruesas", "Galones", "Yardas", "Metros", "Rollo", "Set", "Kit", "Cajas", "Paquetes", "Pieza", "Pares", "KG", "Libras", "Bolsas", "Juego", "Jarra"]
	# end: auto-generated types

	pass

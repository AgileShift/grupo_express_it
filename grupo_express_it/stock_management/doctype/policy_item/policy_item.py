from frappe.model.document import Document


class PolicyItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		cif_total_nio: DF.Currency
		cif_total_usd: DF.Currency
		customs_taxes: DF.Currency
		fob_total_price: DF.Currency
		fob_unit_price: DF.Currency
		freight_cost: DF.Currency
		insurance_cost: DF.Currency
		item: DF.Data
		nationalization_total: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		stock_value: DF.Currency
		total_price: DF.Currency
		unit_price: DF.Currency
		uom: DF.Literal["", "Unidad", "Docenas", "Millar", "Gruesas", "Galones", "Yardas", "Metros", "Rollo", "Set", "Kit", "Cajas", "Paquetes", "Pieza", "Pares", "KG", "Libras", "Bolsas", "Juego", "Jarra"]
	# end: auto-generated types

	pass

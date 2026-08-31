from typing import Tuple, List, Dict

import frappe
from frappe.model.document import Document


class StockSalesInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.stock_management.doctype.stock_sales_invoice_item.stock_sales_invoice_item import StockSalesInvoiceItem

		amended_from: DF.Link | None
		company: DF.Literal["", "Grupo SyM, S.A.", "Grupo Express, S.A.", "Importadora Internacional, S.A.", "Grupo de Importaciones Express, S.A."]
		currency_exchange: DF.Currency
		customer: DF.Link
		invoice_no: DF.Data
		items: DF.Table[StockSalesInvoiceItem]
		posting_date: DF.Date
		profit_margin: DF.Float
		subtotal: DF.Currency
		taxes: DF.Currency
		total: DF.Currency
	# end: auto-generated types

	def before_validate(self):
		# These are here for a final check before saving
		self.subtotal = sum(item.total for item in self.items)
		self.taxes = self.subtotal * 0.15
		self.total = self.subtotal + self.taxes

	def validate(self):
		pass  # TODO: item.qty > item.actual_qty. Trying to bill more stock than available

	def on_submit(self):
		""" Right on Spot to update Related Docs and last validation. After this point the doc is no longer editable """
		# TODO: optimize: frappe.db.set_value to make a single update for both fields, or even build a SQL for a single post
		policies, policy_item_map = self.update_actual_qty(for_update=False)  # ReFetch

		for item in self.items:  # Updates the Policy Item Fields
			policy_item_actual_qty = policy_item_map[item.policy_item] - float(item.qty)

			if policy_item_actual_qty < 0:  # Extra Validation for available stock
				frappe.throw(f"<b>Producto</b> en la fila <b>#{item.idx}</b>: Esta fuera de inventario.")

			policy_item_stock_value = policy_item_actual_qty * item.unit_price  # item.unit_price is Policy Item.unit_price

			frappe.db.set_value('Policy Item', item.policy_item, 'actual_qty', policy_item_actual_qty, update_modified=False)
			frappe.db.set_value('Policy Item', item.policy_item, 'stock_value', policy_item_stock_value, update_modified=False)

		for policy_name in policies:  # Updates the Policy Fields
			total_qty, total_billed_qty = 0.00, 0.00
			policy_items = frappe.get_all('Policy Item', filters={'parent': policy_name}, fields=['qty', 'actual_qty'])

			for policy_item in policy_items:
				total_qty += policy_item.qty
				total_billed_qty += policy_item.qty - policy_item.actual_qty

			# Policy Fields calculation
			per_billed = (float(total_billed_qty) / total_qty) * 100 if total_qty else 0
			status = 'Fully Billed' if per_billed >= 100 else 'Partly Billed' if per_billed > 0 else 'Not Billed'  # > 0 ?

			frappe.db.set_value('Policy', policy_name, 'status', status, update_modified=False)
			frappe.db.set_value('Policy', policy_name, 'per_billed', per_billed, update_modified=False)

	def on_cancel(self):
		raise NotImplementedError('Por ahora no esta permitida la cancelacion.')

	# CUSTOM METHOD
	@frappe.whitelist(allow_guest=False)
	def update_actual_qty(self, for_update: bool) -> Tuple[List[str], Dict[str, float]]:
		""" Update the actual_qty field in the items table from the Policy Item """
		policy_items = frappe.get_all(
			'Policy Item', fields=['name', 'actual_qty'],
			filters={'name': ['in', [item.policy_item for item in self.items]]}  # Build List of Policy Items from Items
		)

		policies = set()  # Build List of Unique Policy -> Sales Invoice item.policy == Policy Item.parent == Policy.name
		policy_item_map = {item['name']: item['actual_qty'] for item in policy_items}  # Build Map of Policy Items from query

		for si_item in self.items:
			policies.add(si_item.policy)  # si_item.policy is a Link to Policy, which is the parent of si_item.policy_item
			si_item.actual_qty = policy_item_map[si_item.policy_item]  # Updates Sales Invoice Item.actual_qty from Policy Item

		if for_update:  # TODO: Build SQL for update only if items.actual_qty != policy_item.actual_qty
			self.update_child_table('items')  # This actually updates the table

		return list(policies), policy_item_map  # This return can help us reduce loops


@frappe.whitelist(methods=['GET'], allow_guest=False)
@frappe.validate_and_sanitize_search_inputs
def get_policy_items(doctype, txt, searchfield, start, page_len, filters, as_dict):
	"""Returns items to be used for calculating taxes and charges"""
	policy = frappe.qb.DocType('Policy')
	policy_item = frappe.qb.DocType(doctype)  # We can use the hardcoded doctype string

	sql_query = (
		frappe.qb.from_(policy_item)
		.inner_join(policy).on(policy.name == policy_item.parent)
		.select('name', policy.name.as_('policy'), policy.posting_date.as_('date'), 'item', 'actual_qty', 'uom', 'unit_price', 'stock_value')
		.where((policy.company == filters['company']) & (policy.docstatus == 1) & (policy_item.actual_qty > 0))  # TODO: policy.status != Fully Billed
		.orderby(policy.posting_date, policy_item.qty)
		.limit(page_len).offset(start)
	)

	# TODO: This can be simplified? maybe a Dict. Something like a mapping
	if txt:
		sql_query = sql_query.where(policy_item.item.like(f"%{txt}%"))
	if policy_field := filters.get('policy'):
		sql_query = sql_query.where(policy.name == policy_field)
	if policy_date_field := filters.get('policy_date'):
		sql_query = sql_query.where(policy.posting_date.between(*policy_date_field))
	if uom_field := filters.get('uom'):
		sql_query = sql_query.where(policy_item.uom == uom_field)
	if actual_qty_field := filters.get('actual_qty'):
		sql_query = sql_query.where(policy_item.actual_qty >= actual_qty_field)  # TODO: check if this is correct or necessary
	if unit_price_field := filters.get('unit_price'):
		sql_query = sql_query.where(policy_item.unit_price <= unit_price_field)
	if stock_value_field := filters.get('stock_value'):
		sql_query = sql_query.where(policy_item.stock_value <= stock_value_field)
	if stock_value_field := filters.get('stock_value_min'):
		sql_query = sql_query.where(policy_item.stock_value >= stock_value_field)

	results = sql_query.run(as_dict=as_dict)

	for result in results:  # TODO: We can optimize this by formatting directly from SQL
		result['actual_qty'] = frappe.utils.fmt_money(result['actual_qty'], precision=2)
		result['unit_price'] = frappe.utils.fmt_money(result['unit_price'], precision=2, currency='NIO')
		result['stock_value'] = frappe.utils.fmt_money(result['stock_value'], precision=2, currency='NIO')

	return results

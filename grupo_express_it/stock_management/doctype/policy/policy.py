import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Policy(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.stock_management.doctype.policy_cif_cost.policy_cif_cost import PolicyCIFCost
		from grupo_express_it.stock_management.doctype.policy_item.policy_item import PolicyItem
		from grupo_express_it.stock_management.doctype.policy_nationalization_cost.policy_nationalization_cost import PolicyNationalizationCost

		amended_from: DF.Link | None
		cif_costs: DF.Table[PolicyCIFCost]
		company: DF.Literal["", "Grupo SyM, S.A.", "Grupo Express, S.A.", "Importadora Internacional, S.A.", "Grupo de Importaciones Express, S.A."]
		currency: DF.Link
		exchange_rate: DF.Float
		grand_total_nationalization: DF.Currency
		invoice: DF.Data
		items: DF.Table[PolicyItem]
		nationalization_costs: DF.Table[PolicyNationalizationCost]
		per_billed: DF.Percent
		policy: DF.Data
		posting_date: DF.Date
		provider: DF.Data
		status: DF.Literal["Draft", "Not Billed", "Partly Billed", "Fully Billed", "Cancelled"]
		total_cif: DF.Currency
		total_cost: DF.Currency
		total_customs_taxes: DF.Currency
		total_fob: DF.Currency
		total_freight: DF.Currency
		total_insurance: DF.Currency
		total_nationalization_costs: DF.Currency
		total_qty: DF.Float
	# end: auto-generated types

	def autoname(self):
		""" Set name as Policy Name. We assume that policy comes sanitized from the form: L - ##### """
		self.name = f'{self.policy} - {frappe.utils.getdate(self.posting_date).year}'

	def before_validate(self):
		self._merge_imported_nationalization_costs()

		# Sanitize fields
		self.exchange_rate = flt(self.exchange_rate)
		if self.exchange_rate <= 0:
			frappe.throw(_("Exchange Rate must be greater than zero."))

		if not self.items:
			frappe.throw(_("Policy must contain at least one item."))

		for item in self.items:
			item.qty = flt(item.qty)
			item.fob_unit_price = flt(item.fob_unit_price)

			if item.qty <= 0:
				frappe.throw(_("Row {0}: Quantity must be greater than zero.").format(item.idx))
			if item.fob_unit_price <= 0:
				frappe.throw(_("Row {0}: FOB Unit Price must be greater than zero.").format(item.idx))

		self._calculate()

	def before_submit(self):
		""" At this point the document is no longer editable. """
		required_totals = (
			(self.total_cif, _("CIF Costs: Total must be greater than zero.")),
			(self.total_freight, _("CIF Costs: Freight must be greater than zero.")),
			(self.total_insurance, _("CIF Costs: Insurance must be greater than zero.")),
			(self.grand_total_nationalization, _("Nationalization Costs: Total must be greater than zero.")),
			(self.total_customs_taxes, _("Nationalization Costs: Customs Taxes must be greater than zero.")),
			(self.total_nationalization_costs, _("Nationalization Costs: Expenses must be greater than zero.")),
		)

		for value, message in required_totals:
			if flt(value) <= 0:
				frappe.throw(message)

		self.per_billed = 0
		self.status = 'Not Billed'

		for item in self.items:
			item.actual_qty = item.qty           # At this exact moment all items are in stock
			item.stock_value = item.total_price

	def on_cancel(self):
		frappe.throw(_("Policy cancellation is not allowed."))

	@frappe.whitelist(allow_guest=False)
	def recalculate(self):
		self.before_validate()

	def _calculate(self):
		"""
		First Calculate the cost dependencies: CIF and Nationalization.
		Then Calculate Item FOB Total and finally apply Policy Logic
		"""

		# CIF Costs #

		total_cif, total_freight, total_insurance = 0.00, 0.00, 0.00
		for cif in self.cif_costs:
			cif.amount_usd = flt(cif.amount_usd)  # Sanitize (doc.is_new() and user paste on Items)
			cif.exchange_rate = self.exchange_rate  # Update value in CIF rows from Parent(Default)

			cif.amount_nio = cif.amount_usd * cif.exchange_rate  # re-calculate Amount NIO(readonly). Has no effect on Totals

			total_cif += cif.amount_usd
			if cif.type == 'Freight':
				total_freight += cif.amount_usd
			elif cif.type == 'Insurance':
				total_insurance += cif.amount_usd

		if total_cif != (total_freight + total_insurance):
			frappe.throw(_("CIF Costs must equal Freight plus Insurance."))

		# USD Values
		self.total_cif = total_cif
		self.total_freight = total_freight
		self.total_insurance = total_insurance

		# Nationalization Costs #

		grand_total_nationalization, total_customs_taxes, total_nationalization_costs = 0.00, 0.00, 0.00
		for nationalization in self.nationalization_costs:
			if nationalization.amount_usd and nationalization.exchange_rate:
				nationalization.amount_nio = nationalization.amount_usd * nationalization.exchange_rate  # Calculate Amount NIO
			elif nationalization.amount_nio:
				nationalization.amount_usd, nationalization.exchange_rate = 0.00, 0.00
			else:
				nationalization.amount_nio = 0.00

			grand_total_nationalization += nationalization.amount_nio
			if nationalization.type == 'Customs Taxes':
				total_customs_taxes += nationalization.amount_nio
			elif nationalization.type == 'Nationalization':
				total_nationalization_costs += nationalization.amount_nio

		# NIO Values
		self.grand_total_nationalization = flt(grand_total_nationalization, 2)
		self.total_customs_taxes = flt(total_customs_taxes, 2)
		self.total_nationalization_costs = flt(total_nationalization_costs, 2)

		# Items #

		# Pre-calculate Total FOB, and Unit FOB, this is used to determine the factors
		total_qty, total_fob = 0.00, 0.00
		for item in self.items:
			item.fob_total_price = item.qty * item.fob_unit_price  # Calculate Item Row Total FOB Price

			total_qty += item.qty
			total_fob += item.fob_total_price

		self.total_qty = total_qty  # Calculate Total QTY
		self.total_fob = total_fob  # Calculate Total FOB in NIO

		# Apply ITEM Calculation Logic #

		# Pre-calculate factors to be used in row calculations. If any of the divisors is zero, the factor is zero
		freight_factor = self.total_freight / self.total_fob
		insurance_factor = self.total_insurance / self.total_fob
		customs_taxes_factor = self.total_customs_taxes / (self.total_fob + self.total_cif)
		nationalization_factor = self.total_nationalization_costs / (self.total_fob + self.total_cif)

		total_cost = 0.00
		for item in self.items:
			item.freight_cost = freight_factor * item.fob_total_price      # Calculate Freight
			item.insurance_cost = insurance_factor * item.fob_total_price  # Calculate Insurance

			item.cif_total_usd = item.fob_total_price + item.freight_cost + item.insurance_cost  # Calculate CIF
			item.cif_total_nio = item.cif_total_usd * self.exchange_rate                         # Calculate CIF in NIO

			item.customs_taxes = customs_taxes_factor * item.cif_total_usd            # Calculate Customs Taxes
			item.nationalization_total = nationalization_factor * item.cif_total_usd  # Calculate Nationalization

			item.total_price = item.cif_total_nio + item.customs_taxes + item.nationalization_total  # Calculate Total Price
			item.unit_price = item.total_price / item.qty                                            # Calculate Unit Price

			total_cost += item.total_price

		self.total_cost = total_cost  # Calculate Total Cost

		return self

	def _merge_imported_nationalization_costs(self):
		if not frappe.flags.in_import or self.is_new():
			return

		previous_doc = self.get_doc_before_save()
		if not previous_doc:
			return

		previous_rows = {row.name: row for row in previous_doc.nationalization_costs}
		imported_rows, new_rows = {}, []

		for row in self.nationalization_costs:
			if row.is_new():
				new_rows.append(row.as_dict())
				continue

			if row.name not in previous_rows:
				frappe.throw(
					_("Nationalization Cost row {0} does not belong to Policy {1}.").format(
						frappe.bold(row.name),
						frappe.bold(self.name),
					)
				)

			imported_rows[row.name] = row.as_dict()

		merged_rows = [
			imported_rows.get(row.name, row.as_dict()) for row in previous_doc.nationalization_costs
		]
		merged_rows.extend(new_rows)
		self.set("nationalization_costs", merged_rows)

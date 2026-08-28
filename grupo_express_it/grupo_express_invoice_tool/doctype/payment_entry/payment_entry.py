import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PaymentEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.grupo_express_invoice_tool.doctype.payment_entry_line.payment_entry_line import PaymentEntryLine

		amended_from: DF.Link | None
		currency: DF.Link
		customer: DF.Link
		entries: DF.Table[PaymentEntryLine]
		exchange_rate: DF.Float
		mode_of_payment: DF.Link
		paid_amount: DF.Currency
		posting_date: DF.Date
		received_amount: DF.Currency
		total_allocated_amount: DF.Currency
		unallocated_amount: DF.Currency
	# end: auto-generated types

	def before_validate(self):
		self._set_paid_amount()
		invoices = self._get_referenced_invoices()
		self._set_reference_details(invoices)
		self._set_totals()

	def validate(self):
		self._validate_received_amount()
		self._validate_allocations()

	@frappe.whitelist(allow_guest=False)
	def allocate_received_amount_to_references(self) -> None:
		self._set_paid_amount()
		invoices = self._get_referenced_invoices()
		self._set_reference_details(invoices)
		self._allocate_paid_amount()
		self._set_totals()

	@frappe.whitelist(allow_guest=False)
	def calculate_payment_totals(self) -> None:
		self._set_paid_amount()
		self._set_totals()
		self._validate_allocation_total()

	def _set_paid_amount(self) -> None:
		received_amount = flt(self.received_amount, 2)

		if self.currency == "USD":
			self.exchange_rate = 1
			self.paid_amount = received_amount
			return

		self.exchange_rate = flt(self.exchange_rate, 6) or 36.624300

		if self.exchange_rate <= 0:
			frappe.throw(_("Exchange Rate must be greater than zero."))

		self.paid_amount = flt(received_amount / self.exchange_rate, 2)

	def _get_referenced_invoices(self) -> dict:
		rows = self._get_reference_rows()

		if not rows:
			return {}

		reference_names = [row.reference_name for row in rows]

		if len(reference_names) != len(set(reference_names)):
			frappe.throw(_("The same Sales Invoice cannot be selected twice."))

		invoices = {
			invoice.name: invoice
			for invoice in frappe.get_list(
				"Sales Invoice",
				filters={
					"name": ["in", reference_names],
					"customer": self.customer,
					"docstatus": 1,
				},
				fields=["name", "currency", "total", "outstanding_amount"],
			)
		}

		if len(invoices) != len(reference_names):
			frappe.throw(_("One or more Sales Invoices are invalid."))

		if any((invoice.currency or "USD") != "USD" for invoice in invoices.values()):
			frappe.throw(_("Sales Invoices must use USD."))

		return invoices

	def _set_reference_details(self, invoices: dict) -> None:
		for row in self._get_reference_rows():
			invoice = invoices[row.reference_name]
			outstanding_amount = max(flt(invoice.outstanding_amount, 2), 0)

			if not outstanding_amount:
				frappe.throw(
					_("Sales Invoice {0} has no outstanding amount.").format(
						frappe.bold(row.reference_name)
					)
				)

			row.reference_doctype = "Sales Invoice"
			row.currency = invoice.currency or "USD"
			row.total_amount = flt(invoice.total, 2)
			row.outstanding_amount = outstanding_amount

	def _allocate_paid_amount(self) -> None:
		remaining_amount = flt(self.paid_amount, 2)

		for row in self._get_reference_rows():
			row.allocated_amount = min(
				remaining_amount, flt(row.outstanding_amount, 2)
			)
			remaining_amount = flt(
				remaining_amount - row.allocated_amount, 2
			)

	def _set_totals(self) -> None:
		self.total_allocated_amount = flt(
			sum(flt(row.allocated_amount, 2) for row in self._get_reference_rows()), 2
		)
		self.unallocated_amount = max(
			flt(self.paid_amount - self.total_allocated_amount, 2), 0
		)

	def _validate_received_amount(self) -> None:
		if flt(self.received_amount, 2) <= 0:
			frappe.throw(_("Received Amount must be greater than zero."))

	def _validate_allocations(self) -> None:
		for row in self.entries:
			allocated_amount = flt(row.allocated_amount, 2)

			if allocated_amount < 0:
				frappe.throw(_("Allocated Amount cannot be negative."))

			if allocated_amount > flt(row.outstanding_amount, 2):
				frappe.throw(
					_("Allocated Amount cannot exceed the outstanding amount of {0}.").format(
						frappe.bold(row.reference_name)
					)
				)

		self._validate_allocation_total()

	def _validate_allocation_total(self) -> None:
		if flt(self.total_allocated_amount, 2) > flt(self.paid_amount, 2):
			frappe.throw(_("Total Allocated Amount cannot exceed Paid Amount."))

	def _get_reference_rows(self) -> list:
		if any(not row.reference_name for row in self.entries):
			frappe.throw(_("Every row must reference a Sales Invoice."))

		return list(self.entries)

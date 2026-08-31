from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestPaymentEntry(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		self.savepoint = f"payment_entry_{frappe.generate_hash(length=8)}"
		frappe.db.savepoint(self.savepoint)
		self.addCleanup(frappe.db.rollback, save_point=self.savepoint)

		suffix = frappe.generate_hash(length=8)
		self.customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"full_name": f"_Test Payment Customer {suffix}",
			}
		).insert()
		self.item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_name": f"_Test Payment Item {suffix}",
				"type": "Regular",
			}
		).insert()
		self.mode_of_payment = frappe.get_doc(
			{
				"doctype": "Mode Of Payment",
				"name": f"_Test Cash USD {suffix}",
				"enabled": 1,
				"type": "Cash",
				"currency": "USD",
			}
		).insert()
		self.nio_mode_of_payment = frappe.get_doc(
			{
				"doctype": "Mode Of Payment",
				"name": f"_Test Cash NIO {suffix}",
				"enabled": 1,
				"type": "Cash",
				"currency": "NIO",
			}
		).insert()

	def make_invoice(self, total):
		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": self.customer.name,
				"customer_name": self.customer.full_name,
				"currency": "USD",
				"total": total,
				"items": [{"item": self.item.name, "amount": total}],
			}
		).insert()
		invoice.submit()
		return invoice

	def make_payment(
		self,
		received_amount,
		allocations,
		currency="USD",
		exchange_rate=1,
		mode_of_payment=None,
	):
		return frappe.get_doc(
			{
				"doctype": "Payment Entry",
				"customer": self.customer.name,
				"posting_date": nowdate(),
				"mode_of_payment": mode_of_payment or self.mode_of_payment.name,
				"currency": currency,
				"exchange_rate": exchange_rate,
				"received_amount": received_amount,
				"entries": [
					{
						"reference_doctype": "Sales Invoice",
						"reference_name": invoice.name,
						"allocated_amount": allocated_amount,
					}
					for invoice, allocated_amount in allocations
				],
			}
		).insert()

	def test_nio_payment_uses_manual_exchange_rate(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(
			3662.43,
			[(invoice, 100)],
			currency="NIO",
			exchange_rate=36.624300,
			mode_of_payment=self.nio_mode_of_payment.name,
		)

		payment.submit()

		invoice.reload()
		payment.reload()
		self.assertEqual(payment.received_amount, 3662.43)
		self.assertEqual(payment.paid_amount, 100)
		self.assertEqual(payment.total_allocated_amount, 100)
		self.assertEqual(payment.unallocated_amount, 0)
		self.assertEqual(invoice.outstanding_amount, 0)
		self.assertEqual(invoice.status, "Paid")

	def test_nio_payment_requires_manual_exchange_rate(self):
		invoice = self.make_invoice(100)

		with self.assertRaises(frappe.ValidationError):
			self.make_payment(
				3662.43,
				[(invoice, 100)],
				currency="NIO",
				exchange_rate=0,
				mode_of_payment=self.nio_mode_of_payment.name,
			)

	def test_nio_payment_rejects_one_to_one_exchange_rate(self):
		invoice = self.make_invoice(100)

		with self.assertRaises(frappe.ValidationError):
			self.make_payment(
				3662.43,
				[(invoice, 100)],
				currency="NIO",
				exchange_rate=1,
				mode_of_payment=self.nio_mode_of_payment.name,
			)

	def test_payment_rejects_unsupported_currency(self):
		payment = frappe.new_doc("Payment Entry")
		payment.currency = "EUR"
		payment.exchange_rate = 0.9
		payment.received_amount = 90

		with self.assertRaises(frappe.ValidationError):
			payment._set_paid_amount()

	def test_draft_does_not_change_invoice(self):
		invoice = self.make_invoice(100)

		payment = self.make_payment(40, [(invoice, 40)])

		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 100)
		self.assertEqual(payment.total_allocated_amount, 40)
		self.assertEqual(payment.unallocated_amount, 0)

	def test_locked_invoices_use_for_update(self):
		first_invoice = self.make_invoice(60)
		second_invoice = self.make_invoice(40)
		payment = self.make_payment(
			100,
			[(second_invoice, 40), (first_invoice, 60)],
		)

		with patch("frappe.get_doc", wraps=frappe.get_doc) as get_doc:
			invoices = payment._get_locked_invoices()

		self.assertEqual(list(invoices), sorted([first_invoice.name, second_invoice.name]))
		for invoice_name in invoices:
			get_doc.assert_any_call(
				"Sales Invoice", invoice_name, for_update=True
			)

	def test_locked_validation_rejects_stale_allocation(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(70, [(invoice, 70)])
		invoice.db_set("outstanding_amount", 30)

		invoices = payment._get_locked_invoices()

		with self.assertRaises(frappe.ValidationError):
			payment._validate_locked_invoices(invoices)

		self.assertEqual(payment.entries[0].outstanding_amount, 30)

	def test_locked_validation_rejects_another_customer(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(40, [(invoice, 40)])
		other_customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"full_name": f"_Test Other Customer {frappe.generate_hash(length=8)}",
			}
		).insert()
		invoice.db_set("customer", other_customer.name)

		invoices = payment._get_locked_invoices()

		with self.assertRaises(frappe.ValidationError):
			payment._validate_locked_invoices(invoices)

	def test_apply_outstanding_delta_updates_status(self):
		invoice = self.make_invoice(100)

		invoice._apply_outstanding_delta(-40)
		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 60)
		self.assertEqual(invoice.status, "Partly Paid")

		invoice._apply_outstanding_delta(-60)
		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 0)
		self.assertEqual(invoice.status, "Paid")

		invoice._apply_outstanding_delta(100)
		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 100)
		self.assertEqual(invoice.status, "Unpaid")

	def test_apply_invoice_allocations_reduces_outstanding(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(40, [(invoice, 40)])
		invoices = payment._get_locked_invoices()
		payment._validate_locked_invoices(invoices)

		payment._apply_invoice_allocations(invoices, -1)

		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 60)
		self.assertEqual(invoice.status, "Partly Paid")

	def test_submit_partial_payment(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(40, [(invoice, 40)])

		payment.submit()

		invoice.reload()
		payment.reload()
		self.assertEqual(payment.docstatus, 1)
		self.assertEqual(invoice.outstanding_amount, 60)
		self.assertEqual(invoice.status, "Partly Paid")

	def test_payment_rejects_zero_allocated_row(self):
		invoice = self.make_invoice(100)

		with self.assertRaises(frappe.ValidationError):
			self.make_payment(40, [(invoice, 0)])

	def test_submit_multiple_invoices(self):
		first_invoice = self.make_invoice(60)
		second_invoice = self.make_invoice(50)
		payment = self.make_payment(
			90,
			[(first_invoice, 60), (second_invoice, 30)],
		)

		payment.submit()

		first_invoice.reload()
		second_invoice.reload()
		self.assertEqual(first_invoice.outstanding_amount, 0)
		self.assertEqual(first_invoice.status, "Paid")
		self.assertEqual(second_invoice.outstanding_amount, 20)
		self.assertEqual(second_invoice.status, "Partly Paid")

	def test_submit_overpayment_preserves_unallocated_amount(self):
		invoice = self.make_invoice(40)
		payment = self.make_payment(50, [(invoice, 40)])

		payment.submit()

		invoice.reload()
		payment.reload()
		self.assertEqual(invoice.outstanding_amount, 0)
		self.assertEqual(invoice.status, "Paid")
		self.assertEqual(payment.total_allocated_amount, 40)
		self.assertEqual(payment.unallocated_amount, 10)

	def test_second_stale_payment_is_rejected(self):
		invoice = self.make_invoice(100)
		first_payment = self.make_payment(70, [(invoice, 70)])
		second_payment = self.make_payment(70, [(invoice, 70)])
		first_payment.submit()

		with self.assertRaises(frappe.ValidationError):
			second_payment.submit()

		invoice.reload()
		second_payment.reload()
		self.assertEqual(invoice.outstanding_amount, 30)
		self.assertEqual(invoice.status, "Partly Paid")
		self.assertEqual(second_payment.docstatus, 0)

	def test_before_submit_validates_all_locked_invoices_before_mutation(self):
		first_invoice = self.make_invoice(60)
		second_invoice = self.make_invoice(50)
		payment = self.make_payment(
			100,
			[(first_invoice, 60), (second_invoice, 40)],
		)
		second_invoice.db_set("outstanding_amount", 20)

		with self.assertRaises(frappe.ValidationError):
			payment.before_submit()

		first_invoice.reload()
		second_invoice.reload()
		payment.reload()
		self.assertEqual(first_invoice.outstanding_amount, 60)
		self.assertEqual(first_invoice.status, "Unpaid")
		self.assertEqual(second_invoice.outstanding_amount, 20)
		self.assertEqual(payment.docstatus, 0)

	def test_cancel_validation_rejects_over_restoration(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(100, [(invoice, 100)])
		payment.submit()
		invoice.db_set("outstanding_amount", 50)
		invoices = payment._get_locked_invoices()

		with self.assertRaises(frappe.ValidationError):
			payment._validate_locked_invoices_for_cancel(invoices)

	def test_cancel_restores_outstanding(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(40, [(invoice, 40)])
		payment.submit()

		payment.cancel()

		invoice.reload()
		payment.reload()
		self.assertEqual(payment.docstatus, 2)
		self.assertEqual(invoice.outstanding_amount, 100)
		self.assertEqual(invoice.status, "Unpaid")

	def test_cancel_full_payment_restores_outstanding(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(100, [(invoice, 100)])
		payment.submit()

		payment.cancel()

		invoice.reload()
		payment.reload()
		self.assertEqual(payment.docstatus, 2)
		self.assertEqual(invoice.outstanding_amount, 100)
		self.assertEqual(invoice.status, "Unpaid")

	def test_cancel_old_payment_preserves_later_payment(self):
		invoice = self.make_invoice(100)
		first_payment = self.make_payment(40, [(invoice, 40)])
		first_payment.submit()
		second_payment = self.make_payment(30, [(invoice, 30)])
		second_payment.submit()

		first_payment.cancel()

		invoice.reload()
		second_payment.reload()
		self.assertEqual(second_payment.docstatus, 1)
		self.assertEqual(invoice.outstanding_amount, 70)
		self.assertEqual(invoice.status, "Partly Paid")

	def test_invoice_with_submitted_payment_cannot_be_cancelled(self):
		invoice = self.make_invoice(100)
		payment = self.make_payment(40, [(invoice, 40)])
		payment.submit()
		invoice.reload()
		cancel_savepoint = f"cancel_invoice_{frappe.generate_hash(length=8)}"
		frappe.db.savepoint(cancel_savepoint)

		try:
			with self.assertRaises(frappe.LinkExistsError):
				invoice.cancel()
		finally:
			frappe.db.rollback(save_point=cancel_savepoint)

		invoice.reload()
		self.assertEqual(invoice.docstatus, 1)
		self.assertEqual(invoice.outstanding_amount, 60)
		self.assertEqual(invoice.status, "Partly Paid")

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, in_words


class SalesInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.grupo_express_invoice_tool.doctype.sales_invoice_item.sales_invoice_item import SalesInvoiceItem

		amended_from: DF.Link | None
		currency: DF.Link
		customer: DF.Link
		customer_name: DF.Data
		in_words: DF.Data | None
		items: DF.Table[SalesInvoiceItem]
		outstanding_amount: DF.Currency
		posting_date: DF.Date | None
		posting_time: DF.Time | None
		status: DF.Literal["Draft", "Unpaid", "Partly Paid", "Paid", "Cancelled"]
		total: DF.Currency
		whatsapp: DF.Check
	# end: auto-generated types

	def before_validate(self):
		self._set_status()

	def before_submit(self):
		self.outstanding_amount = self.total
		self._set_status()

	def before_cancel(self):
		self.outstanding_amount = 0.00
		self._set_status()

	def _set_status(self) -> None:
		if self.docstatus == 0:
			self.status = "Draft"
		elif self.docstatus == 2:
			self.status = "Cancelled"
		elif self.outstanding_amount <= 0:
			self.status = "Paid"
		elif self.outstanding_amount < self.total:
			self.status = "Partly Paid"
		else:
			self.status = "Unpaid"

	def _apply_outstanding_delta(self, delta: float) -> None:
		if self.docstatus != 1:
			frappe.throw(_("Sales Invoice must be submitted."))

		outstanding_amount = flt(self.outstanding_amount + delta, 2)

		if outstanding_amount < 0 or outstanding_amount > flt(self.total, 2):
			frappe.throw(_("Outstanding Amount must remain between zero and Total."))

		self.outstanding_amount = outstanding_amount
		self._set_status()
		self.db_set({"outstanding_amount": self.outstanding_amount, "status": self.status}, notify=True)

	@frappe.whitelist(allow_guest=False)
	def money_in_words(self) -> None:
		whole, _, fraction = str(self.total).partition('.')  # Split the number and the fraction. Even if number is integer

		out = '{0} dólares'.format(in_words(whole)[:-1] if whole[-1:] == '1' else in_words(whole))  # Ends with 1 then trim last char

		if fraction and fraction[:2] not in ['0', '00']:  # same as float(number).is_integer(). check if 2 first digits are zeros
			out += ' con {0}/100'.format(fraction[:2] + '0' if len(fraction[:2]) == 1 else fraction[:2])  # Fraction is one digit add a zero

		self.in_words = out.capitalize()


@frappe.whitelist(allow_guest=False)
@frappe.validate_and_sanitize_search_inputs
def items_with_pricing_rule_query(doctype, txt, searchfield, start, page_len, filters):
	""" This query the item name related to a customer """

	return frappe.db.sql(
		"""select item
		   from `tabPricing Rule`
		   where parent = %(parent)s and item like %(txt)s
		   order by idx desc
		   limit %(start)s, %(page_len)s
		""", {
			'parent': filters.get('customer'),
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),  # this is unused but leave it
			'start': start,
			'page_len': page_len
		})

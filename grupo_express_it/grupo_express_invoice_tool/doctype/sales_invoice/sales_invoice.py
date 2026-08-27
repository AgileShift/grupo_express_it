import time

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import in_words


class SalesInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from grupo_express_it.grupo_express_invoice_tool.doctype.sales_invoice_item.sales_invoice_item import SalesInvoiceItem

		customer: DF.Link
		customer_name: DF.Data
		in_words: DF.Data | None
		items: DF.Table[SalesInvoiceItem]
		posting_date: DF.Date | None
		posting_time: DF.Time | None
		total: DF.Currency
		whatsapp: DF.Check
	# end: auto-generated types

	pass


@frappe.whitelist(allow_guest=False)
def send_sales_invoice(doc_name: str, customer_name: str, total: float) -> None:
	template_name = 'sales_invoice_whatsapp_notification-es'
	template_status = frappe.db.get_value('WhatsApp Templates', template_name, 'status')

	message = (
		f"Hola!\n\n"
		f"Factura de *{customer_name}*\n"
		f"*{doc_name}*\n"
		f"Por un valor de *{frappe.utils.fmt_money(total, precision=2, currency='USD')}*\n\n"
		f"Adjunto el documento."
	)

	# Remember -> No Diacritics in file names, because URL encoding issues may arise
	pdf_bytes = frappe.get_print('Sales Invoice', doc_name, print_format='Sales Invoice WhatsApp', as_pdf=True, pdf_options={}, pdf_generator='wkhtmltopdf')

	file = frappe.new_doc(
		doctype='File',
		attached_to_doctype='Sales Invoice',
		attached_to_name=doc_name,
		file_name=f"{doc_name}.pdf",  # Frappe automatically append a unique hash if file with same name exists
		file_type='pdf',
		is_private=False,
		content=pdf_bytes
	).insert(ignore_permissions=True)

	for recipient in frappe.get_all('WhatsApp Recipient', pluck='mobile_number'):
		whatsapp_message = frappe.new_doc(
			doctype='WhatsApp Message',
			type='Outgoing',
			to=recipient,
			label=f"PDF: {doc_name} | {recipient}",
			attach=file.file_url,
			file_name=f"{doc_name} - {customer_name}.pdf",
			content_type='document',
			reference_doctype='Sales Invoice',
			reference_name=doc_name,
		)

		if template_status == 'APPROVED':
			whatsapp_message.use_template = True
			whatsapp_message.template = template_name
		else:
			whatsapp_message.use_template = False
			whatsapp_message.message = message

		whatsapp_message.insert(ignore_permissions=True)
		time.sleep(0.15)  # To avoid rate limiting

	success_message = (
		'PDF enviado mediante plantilla por WhatsApp'
		if template_status == 'APPROVED' else 'PDF enviado mediante Mensaje por WhatsApp.'
	)

	frappe.db.set_value('Sales Invoice', doc_name, 'whatsapp', True, update_modified=False)  # Mark as sent

	frappe.msgprint(success_message, _('Success'), indicator='green')


@frappe.whitelist(allow_guest=False)
def money_in_words(number) -> str:
	whole, _, fraction = number.partition('.')  # Split the number and the fraction. Even if number is integer

	out = '{0} dólares'.format(in_words(whole)[:-1] if whole[-1:] == '1' else in_words(whole))  # Ends with 1 then trim last char

	if fraction and fraction[:2] not in ['0', '00']:  # same as float(number).is_integer(). check if 2 first digits are zeros
		out += ' con {0}/100'.format(fraction[:2] + '0' if len(fraction[:2]) == 1 else fraction[:2])  # Fraction is one digit add a zero

	return out.capitalize()


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


""" Save this Piece of Code to later on Work on jpg Mode
	elif mode == 'jpg':
		import fitz
		pdf = fitz.open(stream=pdf_bytes, filetype='pdf')  # Open PDF from bytes(frappe.get_print)

		for i, page in enumerate(pdf, start=1):
			pix = page.get_pixmap(dpi=210)
			image_bytes = pix.tobytes('jpg')

			send_whatsapp_message(image_bytes, f"{doc_name}. Pagina {i}.jpg", f"{doc_name}. Pagina {i} JPG")  # Send each page as image
	else:
		frappe.throw('Modo no válido. Use "pdf" o "jpg".')
"""

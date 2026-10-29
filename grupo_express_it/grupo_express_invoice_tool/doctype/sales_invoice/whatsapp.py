import time

import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def send_sales_invoice(doc_name: str, customer_name: str, total: float) -> None:
	template_name = 'sales_invoice_whatsapp_notification-es'
	template_status = frappe.db.get_value('WhatsApp Templates', template_name, 'status')

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

		whatsapp_message.insert(ignore_permissions=True)
		time.sleep(0.15)  # To avoid rate limiting

	success_message = (
		'PDF enviado mediante plantilla por WhatsApp'
		if template_status == 'APPROVED' else 'PDF enviado mediante Mensaje por WhatsApp.'
	)

	frappe.db.set_value('Sales Invoice', doc_name, 'whatsapp', True, update_modified=False)  # Mark as sent

	frappe.msgprint(success_message, _('Success'), indicator='green')


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

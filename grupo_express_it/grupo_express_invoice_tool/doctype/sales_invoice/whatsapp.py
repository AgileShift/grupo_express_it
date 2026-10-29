from html import escape

import frappe
from frappe import _
from whatsapp.whatsapp.api.messages import _submit
from whatsapp.whatsapp.api.utils import humanize_error_message, run_access_guards


@frappe.whitelist(allow_guest=False)
def send_sales_invoice(doc_name: str, customer_name: str, total: float) -> None:
	run_access_guards()
	frappe.get_doc('Sales Invoice', doc_name).check_permission('read')
	account = frappe.db.get_single_value('WA Settings', 'default_account')

	if not account:
		frappe.throw(_('Configurá la cuenta predeterminada de WhatsApp.'))

	recipients = frappe.get_all('WA Profile', filters={
		'whatsapp_account': account,
		'status': 'Active',
	}, fields=['name', 'profile_name', 'phone_number'])

	if not recipients:
		frappe.throw(_('No hay destinatarios de WhatsApp configurados.'))

	progress_title = _('Enviando por WhatsApp')
	total_steps = len(recipients) + 1
	frappe.publish_progress(1, title=progress_title, description=_('Generando PDF...'))

	# Remember -> No Diacritics in file names, because URL encoding issues may arise
	pdf_bytes = frappe.get_print('Sales Invoice', doc_name, print_format='Sales Invoice WhatsApp', as_pdf=True, pdf_options={}, pdf_generator='chrome')

	file = frappe.new_doc(
		doctype='File',
		attached_to_doctype='Sales Invoice',
		attached_to_name=doc_name,
		file_name=f"{doc_name} - {customer_name}.pdf",  # The new app takes the document name from the File
		file_type='pdf',
		is_private=False,
		content=pdf_bytes
	).insert(ignore_permissions=True)

	sent_recipients = 0
	failed_recipients = 0
	summary = [[_('Destinatario'), _('Resultado'), _('Detalle')]]
	for index, recipient in enumerate(recipients, start=1):
		recipient_label = recipient.profile_name or recipient.phone_number or _('Destinatario sin nombre')
		frappe.publish_progress(
			100 * index / total_steps,
			title=progress_title,
			description=_('Enviando a {0} — {1} de {2}...').format(recipient_label, index, len(recipients)),
		)
		message = frappe.new_doc(
			doctype='WA Message',
			direction='Outgoing',
			to=recipient.name,
			whatsapp_account=account,
			is_template=False,
			message='',
			attach=file.name,
			media_url=file.file_url,
			mime_type='application/pdf',
			reference_doctype='Sales Invoice',
			reference_docname=doc_name,
		).insert(ignore_permissions=True)

		_submit(message, f'Failed to send invoice {doc_name} to {recipient.name}')
		result = frappe.db.get_value('WA Message', message.name, ['status', 'error_message'], as_dict=True)
		recipient_to = escape(recipient_label)

		if result and result.status in ('Sent', 'Delivered', 'Read'):
			sent_recipients += 1
			summary.append([recipient_to, _('Enviado'), ''])
		else:
			error = humanize_error_message(result.error_message if result else None) or _('No se confirmó el envío.')
			failed_recipients += 1
			summary.append([recipient_to, _('No enviado'), escape(error)])

		frappe.publish_progress(
			100 * (index + 1) / total_steps,
			title=progress_title,
			description=_('Procesados {0} de {1} destinatarios.').format(index, len(recipients)),
		)

	if not failed_recipients:
		frappe.db.set_value('Sales Invoice', doc_name, 'whatsapp', True, update_modified=False)  # Mark as sent

	frappe.msgprint(
		summary,
		title=_('Resultado del envío: {0} enviados, {1} no enviados').format(sent_recipients, failed_recipients),
		as_table=True, wide=True,
		indicator='orange' if failed_recipients and sent_recipients else ('red' if failed_recipients else 'green'),
	)

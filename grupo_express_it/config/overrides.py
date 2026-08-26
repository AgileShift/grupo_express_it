from urllib.parse import unquote, urlparse

from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_message.whatsapp_message import WhatsAppMessage


class CustomWhatsAppMessage(WhatsAppMessage):

	def notify(self, data):
		# Adding Extra paramenter to add Document Name, so we don't receive a message with attachment as 'Untitled'
		if self.content_type == 'document' and 'document' in data:
			filename = self.get('file_name') or unquote(urlparse(self.attach or '').path.rsplit('/', 1)[-1])
			if filename:
				data['document']['filename'] = filename

		super().notify(data)

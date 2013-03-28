from Headers import Headers, HeaderFormatError

class HTTP_Message:

	def __init__(self, unparsed_message):
		unparsed_message = unparsed_message.replace('\r\n\r', '\n', 1)
		try:
			headers, data = unparsed_message.split('\n\n', 1)
			headers = headers.replace('\r', '')
			self.headers = Headers(headers)
		except (ValueError, HeaderFormatError) as e:
			self.headers = Headers("")
			data = unparsed_message
		
		self.data = data

	def reform(self):
		message = self.headers.reform() + "\n\n" + self.data
		#message = message.replace('\n', '\n\r')
		return message

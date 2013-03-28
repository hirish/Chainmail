from Headers import Headers, HeaderFormatError

class HTTP_Message:

	def __init__(self, unparsed_message):
		unparsed_message = unparsed_message.replace('\r\n\r', '\n', 1)
		headers, data = unparsed_message.split('\n\n', 1)
		headers = headers.replace('\r', '')
		
		try:
			self.headers = Headers(headers)
		except HeaderFormatError as e:
			print e

		self.data = data

	def reform(self):
		message = self.headers.reform() + "\n\n" + self.data
		#message = message.replace('\n', '\n\r')
		return message

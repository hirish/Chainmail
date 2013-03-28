from Cookies import Cookies

class Headers:

	# Eventually populated with the different header types from HTTP messages.
	headers = {}

	# Defines the functions to parse each different type of header.
	functions = {}

	def __init__(self, request):
		# Register parsing functions
		self.functions['Request'] = self._parse_request
		self.functions['Cookie'] = self._parse_cookies

		# Take the header section of a message
		unparsed_headers = self.extract_headers(request)
		# Parse the header section
		self.parse_headers(unparsed_headers)
	
	def extract_headers(self, request):
		# Messages often have two types of newline characters. Strip one.
		request = request.replace('\r', '')
		# Header section finishes with a double newline.
		header_section = request.split('\n\n')[0]
		# Each header type is on a different line.
		unparsed_headers = header_section.split('\n')
		return unparsed_headers
	
	def parse_headers(self, unparsed_headers):
		first = True
		for unparsed_header in unparsed_headers:
			# First line is special, and doesn't follow usual header format.
			if first:
				first = False
				# A server response is preceeded with HTTP/1.1 usually.
				if unparsed_header[:4].lower() == "http":
					header_type, header_values = 'Response', unparsed_header.strip()
				# A request is preceeded by one of GET, POST, HEAD etc.
				elif unparsed_header[-8:-4].lower() == "http":
					header_type, header_values = 'Request', unparsed_header.strip()
				else:
					raise HeaderFormatError()
			else:
				# Usual headers follow form "type: value"
				header_type, header_values = unparsed_header.split(':', 1)
				header_values = header_values.strip()

			# Call a parsing function, if it exists.
			if header_type in self.functions:
				self.headers[header_type] = self.functions[header_type](header_values)
			# Otherwise just a raw dump.
			else:
				self.headers[header_type] = {"value": header_values}
	
	def _parse_request(self, values):
		# Requests are of the form 'method url httpversion'
		# e.g. "GET google.co.uk HTTP/1.1"
		try:
			method, url, http_version = values.split()
		except ValueError:
			print values
			exit()

		url = url.replace('http://','')
		try:
			host, port = url.split(':', 1)
		except:
			host, port = url, 80

		return {'method': method, 'host': host, 'port': port, 'http_version': http_version}

	def _parse_cookies(self, cookie_string):
		return Cookies(cookie_string)


class HeaderFormatError:
	'''Headers class unable to parse given header data'''

	def __str__(self):
		return "Header incorrectly formatted"


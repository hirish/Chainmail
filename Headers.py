from Cookies import Cookies

class Headers:

	# Eventually populated with the different header types from HTTP messages.
	headers = {}

	# Defines the functions to parse each different type of header.
	functions = {}

	def __init__(self, request):
		# Register parsing functions
		self.functions['Request'] = (self._parse_request, self._reform_request)
		self.functions['Cookie'] = (self._parse_cookies, self._reform_cookies)

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
				self.headers[header_type] = self.functions[header_type][0](header_values)
			# Otherwise just a raw dump.
			else:
				self.headers[header_type] = {"value": header_values}

	def reform(self, header_types = None):
		if header_types == None:
			header_types = headers.keys()

		# Move request/response header to beginning.
		if "Request" in header_types:
			header_types.remove("Request")
			output = [self.functions['Request'][1]()]
		elif "Response" in header_types:
			header_types.remove("Response")
			output = [self.functions['Response'][1]()]

		for header_type in header_types:
			try:
				output.append(self.functions[header_type][1]())
			except KeyError:
				output.append("%s: %s" % (header_type, headers[header_type][value]))
		
		return "\n".join(output)
	
	def _parse_request(self, values):
		# Requests are of the form 'method url httpversion'
		# e.g. "GET google.co.uk HTTP/1.1"
		try:
			method, url, http_version = values.split()
		except ValueError:
			print values
			exit()
		
		http_in_url = "http://" in url
		url = url.replace('http://','')
		try:
			host, port = url.split(':', 1)
			port = int(port)
		except:
			host, port = url, 80

		return  {
					'method': method,
					'host': host,
					'port': port,
					'http_version': http_version,
					'http_in_url': http_in_url
				}

	def _reform_request(self):
		method = self.headers['Request']['method']
		host = self.headers['Request']['host']
		port = self.headers['Request']['port']
		http_version = self.headers['Request']['http_version']
		http_in_url = self.headers['Request']['http_in_url']

		if http_in_url:
			host = "http://" + host

		if not port == 80:
			return "%s %s:%s %s" % (method, host, str(port), http_version)
		else:
			return "%s %s %s" % (method, host, http_version)

	def _parse_cookies(self, cookie_string):
		return Cookies(cookie_string)

	def _reform_cookies(self):
		return self.headers['Cookie'].reform()


class HeaderFormatError:
	'''Headers class unable to parse given header data'''

	def __str__(self):
		return "Header incorrectly formatted"


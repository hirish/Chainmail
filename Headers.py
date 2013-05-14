import Cookies


class Headers:

    # Defines the functions to parse each different type of header.
    functions = {}
    new_line = "\r\n"

    def __init__(self, request):
        # Eventually populated with the different header types.
        self.headers = {}
        self.header_types = []

        # Register parsing functions
        self.functions['Request'] = (self._parse_request, self._reform_request)
        self.functions['Response'] = (self._parse_response,
                                      self._reform_response)
        self.functions['Cookie'] = (self._parse_cookies, self._reform_cookies)
        self.functions['Set-Cookie'] = (self._parse_set_cookie,
                                        self._reform_set_cookie)

        if request == '':
            return

        # Take the header section of a message
        unparsed_headers = self.extract_headers(request)
        # Parse the header section
        self.parse_headers(unparsed_headers)

    def extract_headers(self, request):
        # Messages often have two types of newline characters. Strip one.
        # Header section finishes with a double newline.
        # Each header type is on a different line.
        unparsed_headers = request.split(self.new_line)
        return unparsed_headers

    def parse_headers(self, unparsed_headers):
        first = True
        for unparsed_header in unparsed_headers:
            # First line is special, and doesn't follow usual header format.
            if first:
                first = False
                # A server response is preceeded with HTTP/1.1 usually.
                if unparsed_header[:4].lower() == "http":
                    header_type = 'Response'
                    header_values = unparsed_header.strip()
                # A request is preceeded by one of GET, POST, HEAD etc.
                elif unparsed_header[-8:-4].lower() == "http":
                    header_type = 'Request'
                    header_values = unparsed_header.strip()
                else:
                    raise HeaderFormatError()
            elif len(unparsed_header) > 0:
                # Usual headers follow form "type: value"
                header_type, header_values = unparsed_header.split(':', 1)
                header_values = header_values.strip()

            # Call a parsing function, if it exists.
            if header_type in self.functions:
                function = self.functions[header_type][0]
                self.headers[header_type] = function(header_values)
            # Otherwise just a raw dump.
            else:
                self.headers[header_type] = {"value": header_values}

            self.header_types.append(header_type)

    def reform(self, header_types=None):
        if header_types is None:
            header_types = self.header_types

        output = []

        for header_type in header_types:
            try:
                output.append(self.functions[header_type][1]())
            except KeyError:
                output.append("%s: %s" % (header_type,
                                          self.headers[header_type]['value']))
            except TypeError:
                # This occurs if a reform function is "None".
                # This is the case for headers we don't want to pass on.
                pass

        return self.new_line.join(output)

    def encrypt_data(self):
        try:
            self.set_cookies = Cookies.encrypt_set_cookies(self.set_cookies)
        except:
            pass

    def decrypt_data(self):
        try:
            self.cookies = Cookies.decrypt_cookies(self.cookies)
        except:
            pass

    def _parse_request(self, values):
        # Requests are of the form 'method url httpversion'
        # e.g. "GET google.co.uk HTTP/1.1"
        try:
            method, url, http_version = values.split()
        except ValueError:
            print values
            exit()

        http_in_url = "http://" in url
        url = url.replace('http://', '')
        try:
            host, port = url.split(':', 1)
            port = int(port)
        except:
            host, port = url, 80

        return {'method': method,
                'host': host,
                'port': port,
                'http_version': http_version,
                'http_in_url': http_in_url}

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

    def _parse_response(self, values):
        return {'value': values}

    def _reform_response(self):
        return self.headers["Response"]['value']

    def _parse_set_cookie(self, new_cookie_string):
        try:
            self.set_cookies
        except:
            self.set_cookies = []

        self.set_cookies.append(Cookies.extract_set_cookie(new_cookie_string))

        return self.set_cookies

    def _reform_set_cookie(self):
        to_return = []
        for set_cookie in self.set_cookies:
            key, value, metacookie = set_cookie
            if not metacookie == "":
                to_return.append("Set-Cookie: %s=\"%s\";%s" % set_cookie)
            else:
                to_return.append("Set-Cookie: %s=\"%s\"" % key, value)
        return "\n".join(to_return)

    def _parse_cookies(self, cookie_string):
        try:
            self.cookies
        except:
            self.cookies = {}

        unparsed_cookies = cookie_string.split(";")
        for unparsed_cookie in unparsed_cookies:
                key, value = Cookies.extract_cookie_value(unparsed_cookie)
                self.cookies[key] = value

        return self.cookies

    def _reform_cookies(self):
        combined = ["%s=\"%s\"" % (k, v) for k, v in self.cookies.iteritems()]
        return "Cookie: " + "; ".join(combined) + ";"


class HeaderFormatError:
    '''Headers class unable to parse given header data'''

    def __str__(self):
        return "Header incorrectly formatted"

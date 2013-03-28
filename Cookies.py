class Cookies:

	# To contains the cookie names and values.
	cookies = {}

	def __init__(self, cookie_string):
		# Cookies are stored as a string of "key1=val1; key2=val2;".
		# Break it down first by ;, then strip the whitespace.
		unparsed_cookies = cookie_string.split(";")
		for unparsed_cookie in unparsed_cookies:
			unparsed_cookie = unparsed_cookie.strip()
			key, value = unparsed_cookie.split("=", 1)
			self.cookies[key] = value
	
	def __str__(self):
		return "<Cookies: %s>" % self.cookie_string()
	
	def cookie_string(self, keys = None):
		# Turn the cookie dictionary back into a HTTP compatible string.
		if keys == None:
			keys = cookies.keys()
		combined = ["%s=%s" % (key, cookies[key]) for key in keys]
		return "; ".join(combined) + ";"

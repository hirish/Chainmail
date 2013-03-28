import socket
from Headers import Headers, HeaderFormatError

class Connection:

	# Two computers involved in the connection.
	client = None
	server = None

	def __init__(self, client):
		self.client = client
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def connect_server(self, server_host, port = 80):
		try:
			# Connect the server to the specified host.
			self.server.connect((server_host, port))
			return True
		except Exception as e:
			print e
			return False

	def send_data(self, from_socket, data):
		'''Takes some data, and the socket it was sent from, then sends the
		data to the opposite socket'''
		if from_socket == self.client:
			self._send_to_server(data)
		elif from_socket == self.server:
			self._send_to_client(data)
		else:
			# If it's not from a socket we know, then ProxyServer is broken.
			print "!!!!!!!!!!!!!!"
			print data
			print "!!!!!!!!!!!!!!"
			exit()

	def _send_to_client(self, data):
		'''Send data to the client (initator of connection).'''
		try:
			# Extract headers.
			headers = Headers(data)
		except HeaderFormatError as e:
			# Failed to extract headers; we'll just forward as usual.
			continue

		# Send data.
		self.client.send(data)
		print "<<<<<<<<<<<<<<"
		print data
		print "<<<<<<<<<<<<<<"
	
	def _send_to_server(self, data):
		''' Send data to the server the client initated the connection to.'''
		try:
			# Extract headers.
			headers = Headers(data)
		except HeaderFormatError as e:
			# Failed to extract headers; we'll just forward as usual.
			continue

		# Send data.
		self.server.send(data)
		print ">>>>>>>>>>>>>>"
		print data
		print ">>>>>>>>>>>>>>"

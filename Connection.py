import socket

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

	def send_data(self, from_socket, raw_message_data):
		'''Takes some data, and the socket it was sent from, then sends the
		data to the opposite socket'''
		print raw_message_data
		print ''
		message_data = HTTP_message(raw_message_data)
		if from_socket == self.client:
			self._send_to_server(message_data)
		elif from_socket == self.server:
			self._send_to_client(message_data)
		else:
			# If it's not from a socket we know, then ProxyServer is broken.
			print "!!!!!!!!!!!!!!"
			print message_data.reform()
			print "!!!!!!!!!!!!!!"
			exit()

	def _send_to_client(self, message_data):
		'''Send data to the client (initator of connection).'''
		headers = message_data.headers
		if headers:
			continue

		# Send data.
		self.client.send(message_data.reform())
		print "<<<<<<<<<<<<<<"
		print message_data.reform()
		print "<<<<<<<<<<<<<<"
	
	def _send_to_server(self, message_data):
		''' Send data to the server the client initated the connection to.'''
		headers = message_data.headers
		if headers:
			continue

		# Send data.
		self.server.send(message_data.reform())
		print ">>>>>>>>>>>>>>"
		print message_data.reform()
		print ">>>>>>>>>>>>>>"

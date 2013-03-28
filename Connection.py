import socket
from Headers import Headers

class Connection:

	client = None
	server = None

	def __init__(self, client):
		self.client = client
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def connect_server(self, server_host, port = 80):
		try:
			self.server.connect((server_host, port))
			return True
		except Exception as e:
			print e
			return False

	def send_data(self, from_socket, data):
		print ">>>>>>>>>>>>>>"
		print data
		print "<<<<<<<<<<<<<<"
		try:
			headers = Headers(data)
			if from_socket == self.client:
				self.send_to_server(data)
			elif from_socket == self.server:
				self.send_to_client(data)
			else:
				print "ERROR"
				print headers
				exit()
		except Exception as e:
			print e
			print "No Headers"

	def send_to_client(self, data):
		self.client.send(data)
	
	def send_to_server(self, data):
		self.server.send(data)

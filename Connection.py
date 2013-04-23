import socket
import ssl
import threading
from HTTP import HTTP_Message

BUFFER_SIZE = 8192

class Listener(threading.Thread):

	def run(self):
		print "Starting", self.__class__.__name__
		while (True):
			data = self.listen_socket.recv(BUFFER_SIZE)	
			if len(data) == 0:
				break
			self.send(data)
		self.listen_socket.close()
		self.output_socket.close()
	
	def send(self, data):
		message = HTTP_Message(data)
		self.alter(message)
		self.output_socket.send(message.reform())
		self.print_send(message.reform())

	def __init__(self, client_socket, server_socket):
		raise NotImplementedError("Use a subclass of Listener")

	def print_send(self, data):
		raise NotImplementedError("Listener.print_send not implemented")

	def alter(self, message):
		raise NotImplementedError("Listener.alter not implemented")

class ClientListener(Listener):

	def __init__(self, client_socket, server_socket):
		threading.Thread.__init__(self)
		self.listen_socket = client_socket
		self.output_socket = server_socket

	def print_send(self, data):
		print ">>>>>>>>>>>>>>\n%s\n>>>>>>>>>>>>>>" % data

	def alter(self, message):
		headers = message.headers.headers

		if "Accept-Encoding" in headers:
			headers["Accept-Encoding"] = {'value': 'identity'}


class ServerListener(Listener):

	def __init__(self, client_socket, server_socket):
		threading.Thread.__init__(self)
		self.listen_socket = server_socket
		self.output_socket = client_socket

	def print_send(self, data):
		print "<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % data

	def alter(self, message):
		return True

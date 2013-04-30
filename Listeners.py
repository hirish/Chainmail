import ssl
import threading
import select
from HTTP import HTTP_Message

BUFFER_SIZE = 32768

class Listener(threading.Thread):

	def run(self):
		print "Starting", self.__class__.__name__
		self.listen_socket.setblocking(0)
		count = 0
		while not self.stop:
			if count > 20:
				break

			try:
				ready = select.select([self.listen_socket], [], [], 0.1)
			except:
				break

			if ready[0]:
				count = 0

				try:
					data = self.listen_socket.recv(BUFFER_SIZE)	
				except ssl.SSLError:
					break

				if len(data) == 0:
					break
				self.send(data)
			else:
				count += 1
		self.stop = True
		self.listen_socket.close()
		if paired_listener:
			paired_listener.stop = True
	
	def send(self, data):
		message = HTTP_Message(data)
		self.alter(message)
		self.output_socket.send(message.reform())
		self.print_send(message.reform())
	
	def set_paired_listener(self, paired_listener):
		self.paired_listener = paired_listener

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
		self.paired_listener = None
		self.stop = False

	def print_send(self, data):
		print ">>>>>>>>>>>>>>\n%s\n>>>>>>>>>>>>>>" % data

	def alter(self, message):
		headers = message.headers.headers

		if "Accept-Encoding" in headers:
			headers["Accept-Encoding"] = {'value': 'gzip'}


class ServerListener(Listener):

	def __init__(self, client_socket, server_socket):
		threading.Thread.__init__(self)
		self.listen_socket = server_socket
		self.output_socket = client_socket
		self.paired_listener = None
		self.stop = False

	def print_send(self, data):
		print "<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % data

	def alter(self, message):
		message.decompress()
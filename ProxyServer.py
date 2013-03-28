import socket
import select
import time
from Headers import Headers
from Connection import Connection

buffer_size = 8192
delay = 0.0001

class ProxyServer:
	input_list = []
	channel = {}
	connections = {}

	def __init__(self, host, port):
		self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.proxy_socket.bind((host, port))
		self.proxy_socket.listen(200)

	def main_loop(self):
		self.input_list.append(self.proxy_socket)
		while True:
			time.sleep(delay)
			inputready, _, _ = select.select(self.input_list, [], [])
			for socket in inputready:
				if socket == self.proxy_socket:
					self.accept()
					break

				self.data = socket.recv(buffer_size)
				if len(self.data) == 0:
					self.close(socket)
				else:
					self.connections[socket].send_data(socket, self.data)

	def accept(self):
		# A connection has been attempted, accept it.
		client_socket, clientaddr = self.proxy_socket.accept()
		# Take some data from the connection, so we can see who to proxy to.
		request = client_socket.recv(buffer_size)
		if request == "":
			return

		# Interpret the headers and pull out the host and port.
		headers = Headers(request)
		try:
			host = headers.headers['Request']['host'].split('/')[0]
			port = headers.headers['Request']['port']
		except KeyError:
			print ""
			print "KeyError!"
			print ""
			print request
			exit()

		# Connect to the remote server we're proxying to.
		connection = Connection(client_socket)
		# Success - register the sockets for listening, as well as
		# the connection
		if connection.connect_server(host, port):
			print "Connection between %s and %s:%s established" % (clientaddr, host, str(port))
			self.input_list.append(connection.client)
			self.input_list.append(connection.server)
			self.connections[connection.client] = connection
			self.connections[connection.server] = connection
			if headers.headers['Request']['method'] == "CONNECT":
				message = 'HTTP/1.1 200 Connection established\nProxy-agent: ChainMail/1.0\n\n'
				print "<<<<<<<<<<<<<<"
				print message
				print "<<<<<<<<<<<<<<"
				client_socket.send(message)
			else:
				connection.send_data(client_socket, request)
		# Failure - close the client connection and display error message.
		else:
			print "Can't establish connection with server %s." % host
			print "Closing connection with client %s." % str(clientaddr)
			connection.client.close()

	def close(self, socket):
		print socket.getpeername(), "has disconnected"
		connection = self.connections[socket]

		# Stop checking sockets
		self.input_list.remove(connection.client)
		self.input_list.remove(connection.server)

		# Close connections.
		connection.client.close()
		connection.server.close()

		# Delete from connections dict.
		del self.connections[connection.client]
		del self.connections[connection.server]

import socket
import ssl
from Headers import Headers
from Connection import ClientListener, ServerListener

BUFFER_SIZE = 8192
CONNECT_RESPONSE = 'HTTP/1.1 200 Connection established\nProxy-agent: ChainMail/1.0\n\n'
KEYFILE = "../Certificates/Chainmail.key"
CERTFILE = "../Certificates/Chainmail.crt"

class ProxyServer:
	input_list = []
	channel = {}
	connections = {}

	def __init__(self, host, port):
		self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.proxy_socket.bind((host, port))
		self.proxy_socket.listen(200)
		print "Listening on ", self.proxy_socket
			
	def run(self):
		while True:
			# A connection has been attempted, accept it.
			client_socket, client_address = self.proxy_socket.accept()

			# Take some data from the connection, so we can see who to proxy to.
			data = client_socket.recv(BUFFER_SIZE)
			if data == "":
				print "Empty request"
				continue

			# Interpret the headers and pull out the host and port.
			headers = Headers(data)
			try:
				server_host = headers.headers['Request']['host'].split('/')[0]
				server_port = headers.headers['Request']['port']
				server_address = (server_host, server_port)
			except KeyError:
				print "Invalid request\n", data
				continue
			
			if headers.headers['Request']['method'] == "CONNECT":
				print ">>>>>>>>>>>>>>\n%s\n>>>>>>>>>>>>>>" % data
				print "<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % CONNECT_RESPONSE
				client_socket.send(CONNECT_RESPONSE)

				client_socket = ssl.wrap_socket(client_socket,
												keyfile = KEYFILE,
												certfile = CERTFILE,
												server_side = True,
												do_handshake_on_connect = False)
				client_socket.do_handshake()

				server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				server_socket = ssl.wrap_socket(server_socket)

				data = ""

			else:
				server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			server_socket.connect(server_address)

			client_listener = ClientListener(client_socket, server_socket)
			server_listener = ServerListener(client_socket, server_socket)

			server_listener.setDaemon(True)
			client_listener.setDaemon(True)

			client_listener.send(data)

			client_listener.start()
			server_listener.start()


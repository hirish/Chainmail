import socket
import time
import traceback
import ssl
import Logger
from makecert import CertStore
from select import select
from Headers import Headers
from Listeners import ClientListener, ServerListener, SocketClosed
from backports.ssl_match_hostname import match_hostname, CertificateError

BUFFER_SIZE = 32768
CONNECT_RESPONSE = 'HTTP/1.1 200 Connection established\n' + \
                   'Proxy-agent: ChainMail/1.0\n\n'

CERTS = "/etc/ssl/certs/ca-certificates.crt"

DELAY = 0.0001


class ProxyServer:

    def __init__(self, host, port):
        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.proxy_socket.bind((host, port))
        self.proxy_socket.listen(200)

        self.cert_store = CertStore()

        self.sockets = [self.proxy_socket]
        self.listeners = {self.proxy_socket: None}
        self.pairs = {}

        Logger.i("Listening on ", self.proxy_socket)

    def run(self):
        while True:
            time.sleep(DELAY)
            received, _, _ = select(self.sockets, [], [])

            for socket in received:
                if socket == self.proxy_socket:
                    try:
                        self.accept_connection()
                    except Exception as e:
                        Logger.e("Failed to accept connection.")
                        Logger.e(traceback.format_exc())
                else:
                    try:
                        self.listeners[socket].receive()
                    except SocketClosed:
                        Logger.i("Closing socket pair...")
                        self.close_connection(socket)
                    except Exception as e:
                        Logger.e("Exception occurred, closing sockets...")
                        Logger.e(str(e))
                        Logger.e(traceback.format_exc())
                        self.close_connection(socket)

    def close_connection(self, socket):
        paired_socket = self.pairs[socket]

        socket.close()
        paired_socket.close()

        self.sockets.remove(socket)
        self.sockets.remove(paired_socket)

        del self.listeners[socket]
        del self.listeners[paired_socket]

        del self.pairs[socket]
        del self.pairs[paired_socket]

    def accept_connection(self):
        # A connection has been attempted, accept it.
        client_socket, client_address = self.proxy_socket.accept()

        # Take some data from the connection, so we can see who to proxy to
        data = client_socket.recv(BUFFER_SIZE)
        if data == "":
            Logger.e("Empty request")
            return

        # Interpret the headers and pull out the host and port.
        try:
            headers = Headers(data)
        except Exception as e:
            Logger.e("Header exception when accepting connection")
            Logger.e(traceback.format_exc())
            Logger.e(data)
            raise e

        try:
            server_host = headers.headers['Request']['host'].split('/')[0]
            server_port = headers.headers['Request']['port']
            server_address = (server_host, server_port)
            Logger.i("Connecting to %s on port %s" % server_address)
        except KeyError:
            Logger.e("Invalid request\n", data)
            return

        if headers.headers['Request']['method'] == "CONNECT":
            Logger.v("==============\n%s\n==============" % data)
            Logger.v("<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % CONNECT_RESPONSE)
            client_socket.send(CONNECT_RESPONSE)

            cert_file, key_file = self.cert_store.get_cert(server_host, [])

            client_socket = ssl.wrap_socket(client_socket,
                                            keyfile=key_file,
                                            certfile=cert_file,
                                            server_side=True,
                                            do_handshake_on_connect=False)
            try:
                client_socket.do_handshake()
            except (ssl.SSLError, socket.error) as error:
                Logger.e("SSL Error", error)
                return

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                server_socket = ssl.wrap_socket(server_socket,
                                                #cert_reqs=ssl.CERT_REQUIRED,
                                                #ca_certs=CERTS,
                                                #"/home/henry/CA/cacert.pem",
                                                ssl_version=ssl.PROTOCOL_SSLv3
                                                )
                server_socket.connect(server_address)
                #match_hostname(server_socket.getpeercert(), server_host)
            except ssl.SSLError:
                Logger.e("Server certificate not signed by trusted authority.")
                return
            except CertificateError as ce:
                Logger.e("Server certificate does not match hostname.")
                Logger.e(str(ce))
                return

            # The data received was a "CONNECT" request, we don't need to
            # forward this to the server...
            data = None

        else:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(server_address)

        client_listener = ClientListener(client_socket, server_socket)
        server_listener = ServerListener(client_socket, server_socket)

        self.pairs[client_socket] = server_socket
        self.pairs[server_socket] = client_socket

        self.sockets += [client_socket, server_socket]
        self.listeners[client_socket] = client_listener
        self.listeners[server_socket] = server_listener

        if data:
            Logger.e("WRITING DATA", data)
            client_listener.receive(prereceived_data = data)

import ssl
import threading
import select
import Logger
from HTTP import HTTP_Message
from Encryption import Encryption
from ChainmailError import ChainmailError

BUFFER_SIZE = 32768


class Listener(threading.Thread):

    def run(self):
        Logger.e("Starting", self.__class__.__name__)
        self.listen_socket.setblocking(0)
        count = 0
        while not self.stop:
            if count > 20:
                Logger.e(self.__class__.__name__, ": Socket timeout.")
                break

            ready = select.select([self.listen_socket], [], [], 0.1)

            if not ready[0]:
                count += 1
                continue

            count = 0
            data = ""
            try:
                while ready[0]:
                    data += self.listen_socket.recv(BUFFER_SIZE)
                    ready = select.select([self.listen_socket], [], [], 0.1)
            except ssl.SSLError as e:
                Logger.e(self.__class__.__name__, ": SSL Error." + str(e))

            if len(data) == 0:
                break

            try:
                self.send(data)
            except Exception as e:
                Logger.e("Error: " + str(e))
                break

        Logger.i("Quitting", self.__class__.__name__)
        self.stop = True
        self.listen_socket.close()
        if self.paired_listener:
            self.paired_listener.stop = True

    def send(self, data):
        message = HTTP_Message(data)
        self.alter(message)
        self.output_socket.sendall(message.reform())
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
        Logger.v(">>>>>>>>>>>>>>\n%s\n>>>>>>>>>>>>>>" % data)

    def alter(self, message):
        message.headers.decrypt_data()

        headers = message.headers.headers

        if "Accept-Encoding" in headers:
            headers["Accept-Encoding"] = {'value': 'identity'}

        if "chainmail-client-id" in headers:
            encrypted_id = headers["chainmail-client-id"]["value"]
            encryption = Encryption()
            Logger.e("Chainmail ID: " + encryption.decrypt(encrypted_id))
        else:
            raise ChainmailError("No chainmail ID in request")


class ServerListener(Listener):

    def __init__(self, client_socket, server_socket):
        threading.Thread.__init__(self)
        self.listen_socket = server_socket
        self.output_socket = client_socket
        self.paired_listener = None
        self.stop = False

    def print_send(self, data):
        Logger.v("<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % data)

    def alter(self, message):
        message.headers.encrypt_data()
        message.decompress()

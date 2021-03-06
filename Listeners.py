import re
import threading
import Logger
from HTTP import HTTP_Message
from Dechunker import Dechunker

BUFFER_SIZE = 32768


class Listener(threading.Thread):

    def receive(self):
        raise NotImplementedError("Listener.receive not implemented")

    def send_received_data(self, close_socket = False):
        self.send(self.data)
        self.data = ""

        if close_socket:
            raise SocketClosed()

    def send(self, data = None):
        message = HTTP_Message(data)

        self.alter(message)

        message.recalculate_content_length()
        self.output_socket.sendall(message.reform())

        #Logger.e(data)
        self.print_send(message)

    def _print_send(self, message, symbol):
        Logger.w(symbol * 20)
        header_text = message.headers.reform()
        try:
            split_headers = header_text.split("\n", 1)
            Logger.w(split_headers[0])
            Logger.d(split_headers[1] + "\n")
        except IndexError:
            Logger.w(header_text)
        if (len(message.data) > 500):
            Logger.v(message.data[:100])
            Logger.v("...")
            Logger.v(message.data[-100:])
        elif (len(message.data) > 0):
            Logger.v(message.data)
        Logger.w(symbol * 20)

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

        self.data = ""
        self.message_length = 0
        self.headers_complete = False

        self.dechunker = None

    def receive(self, prereceived_data = None):
        received = ""
        if prereceived_data:
            received = prereceived_data

        received += self.listen_socket.recv(BUFFER_SIZE)
        Logger.v("=============\n", received, "\n=============")

        if len(received) == 0:
            self.send_received_data()

        if not self.headers_complete:
            try:
                headers, received = received.split("\r\n\r\n", 1)
                self.data += headers + "\r\n\r\n"
                self.headers_complete = True
            except ValueError:
                self.data += received
                return

            self.header_length = len(self.data)

            if re.findall("Transfer-Encoding:\W+chunked", self.data):
                self.dechunker = Dechunker()

            elif "Content-Length:" in self.data:
                splitted = self.data.split()
                position = splitted.index("Content-Length:")
                self.message_length = int(splitted[position + 1])

        if not self.dechunker is None:
            try:
                self.dechunker.feed(received)
            except SocketClosed as e:
                self.data = re.sub("Transfer-Encoding:\W+chunked",
                                   "Content-Length: 0",
                                   self.data)
                self.data += self.dechunker.dump()
                self.send_received_data()
        else:
            self.data += received

            if self.headers_complete and len(self.data) >= self.message_length:
                self.send_received_data()

    #def receive(self):
        #received = self.listen_socket.recv(BUFFER_SIZE)
        #if received.lower() == received.upper():
            #return
        #self.send(received)

    def print_send(self, message):
        self._print_send(message, '>')
        #Logger.v(">>>>>>>>>>>>>>\n%s\n>>>>>>>>>>>>>>" % data)

    def alter(self, message):
        headers = message.headers.headers

        if "Accept-Encoding" in headers:
            headers["Accept-Encoding"] = {'value': 'identity'}


class ServerListener(Listener):

    def __init__(self, client_socket, server_socket):
        threading.Thread.__init__(self)
        self.listen_socket = server_socket
        self.output_socket = client_socket
        self.paired_listener = None
        self.stop = False

        self.data = ""
        self.message_length = 0
        self.headers_complete = False

        self.dechunker = None

    def receive(self):
        received = self.listen_socket.recv(BUFFER_SIZE)

        if len(received) == 0:
            self.send_received_data(close_socket = True)

        if not self.headers_complete:
            try:
                headers, received = received.split("\r\n\r\n", 1)
                self.data = headers + "\r\n\r\n"
                self.headers_complete = True
            except ValueError:
                self.data = received
                return

            self.header_length = len(self.data)

            if re.findall("Transfer-Encoding:\W+chunked", self.data):
                self.dechunker = Dechunker()

            elif "Content-Length:" in self.data:
                splitted = self.data.split()
                position = splitted.index("Content-Length:")
                self.message_length = int(splitted[position + 1])

        if not self.dechunker is None:
            try:
                self.dechunker.feed(received)
            except SocketClosed:
                self.data = re.sub("Transfer-Encoding:\W+chunked",
                                   "Content-Length: 0",
                                   self.data)
                self.data += self.dechunker.dump()
                self.send_received_data(close_socket = True)
        else:
            self.data += received

            if self.headers_complete and len(self.data) >= self.message_length:
                self.send_received_data(close_socket = True)

    def print_send(self, message):
        self._print_send(message, '<')
        #Logger.v("<<<<<<<<<<<<<<\n%s\n<<<<<<<<<<<<<<" % data)

    def alter(self, message):
        message.inject_sunlight()
        #message.decompress()


class SocketClosed(Exception):
    pass

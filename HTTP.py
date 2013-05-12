import gzip
import StringIO
from Headers import Headers, HeaderFormatError


class HTTP_Message:

    def __init__(self, unparsed_message):
        self.raw = unparsed_message
        try:
            headers, data = unparsed_message.split('\r\n\r\n', 1)
            headers = headers.replace('\r', '')
            self.headers = Headers(headers)
        except (ValueError, HeaderFormatError):
            self.headers = Headers("")
            data = unparsed_message

        self.data = data

    def reform(self):
        message = self.headers.reform() + "\n\n" + self.data
        #message = message.replace('\n', '\n\r')
        return message

    def decompress(self):
        try:
            if self.headers.headers["Content-Encoding"]['value'] == 'gzip':
                d = "\r\n".join(self.data.split('\r\n')[1:-3])
                self.data = gzip.GzipFile('',
                                          'rb',
                                          9,
                                          StringIO.StringIO(d)).read()
                del(self.headers.headers["Content-Encoding"])
                del(self.headers.headers["Transfer-Encoding"])
        except KeyError:
            # Not compressed.
            pass

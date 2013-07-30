import gzip
import StringIO
from Headers import Headers, HeaderFormatError


class HTTP_Message:

    def __init__(self, unparsed_message):
        self.raw = unparsed_message
        try:
            headers, data = unparsed_message.split('\r\n\r\n', 1)
            #headers = headers.replace('\r', '')
            self.headers = Headers(headers)
        except (ValueError, HeaderFormatError):
            self.headers = Headers("")
            data = unparsed_message

        self.data = data
        self.send = True

    def reform(self):
        message = self.headers.reform() + "\r\n\r\n" + self.data
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

    def recalculate_content_length(self):
        try:
            self.headers.headers["Content-Length"]['value'] = len(self.data)
        except KeyError:
            pass

    def inject_sunlight(self):
        sunlight = '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.0.2/jquery.min.js"></script>'
        sunlight += '<script src="https://sunlight.henryirish.com/jquery.hammer.min.js"></script>'
        sunlight += '<script src="https://sunlight.henryirish.com/sunlight.js"></script>'
        if "<html" in self.data and "</body>" in self.data:
            self.data = self.data.replace("</body>", sunlight + "</body>")

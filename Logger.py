from termcolor import colored
import time

LEVELS = [
    {'name': 'ERROR', 'colour': 'red'},
    {'name': 'WARNING', 'colour': 'orange'},
    {'name': 'INFORMATION', 'colour': 'yellow'},
    {'name': 'DEBUG', 'colour': 'green'},
    {'name': 'VERBOSE', 'colour': 'blue'},
    {'name': 'VERBOSE VERBOSE', 'colour': 'magenta'},
]

HEADER_COLOUR = 'grey'


class Logger:

    file_logging = True
    console_logging = True
    output_level = 5

    log_file = None

    def __init__(self, file_log=True, console_log=True, output_level=5):
        self.file_logging = file_log
        self.console_logging = console_log
        self.output_level = output_level

        self.get_log_file()

    def get_log_file(self):
        if self.file_logging:
            self.log_file = open("log", "w+")

    def file_printer(self, messages):
        for message in messages:
            self.log_file.write(message)
        self.log_file.write("\n")

    def console_printer(self, coloured_messages):
        for coloured_message in coloured_messages:
            message, colour = coloured_message
            print colored(message, colour),
        print ""  # Trailing new line.

    def printer(self, messages, level):
        if level <= self.output_level:
            now = time.asctime(time.localtime(time.time()))
            header_string = "%s: %s\n" % (now, LEVELS[level]['name'])

            headered_messages = [header_string] + messages

            if self.file_logging:
                self.file_printer(headered_messages)

            if self.console_logging:
                colour = LEVELS[level]['colour']

                coloured_header_string = (header_string, HEADER_COLOUR)
                coloured_messages = zip(messages, [colour] * len(messages))
                coloured_headered_messages = ([coloured_header_string]
                                              + coloured_messages)

                self.console_printer(coloured_headered_messages)

    def e(self, *messages):
        self.printer(messages, 0)

    def w(self, *messages):
        self.printer(messages, 1)

    def i(self, *messages):
        self.printer(messages, 2)

    def d(self, *messages):
        self.printer(messages, 3)

    def v(self, *messages):
        self.printer(messages, 4)

    def vv(self, *messages):
        self.printer(messages, 5)

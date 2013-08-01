import time
from termcolor import colored

# Format: (name, colour, background colour, attributes, add timestamp?,
# print to file?, print to console?).
FORMATS = [
    ('ERROR', 'white', 'on_red', ['bold'], True, True, True),
    ('WARNING', 'white', 'on_yellow', ['bold'], True, True, True),
    ('SYSINFO', 'white', 'on_blue', [], True, True, True),
    ('ERROR', 'red', None, [], True, True, True),
    ('WARNING', 'yellow', None, [], True, True, True),
    ('INFO', 'blue', None, ['bold'], True, True, True),
    ('INFO', 'blue', None, [], False, True, False),
    ('OTHER', 'grey', None, [], False, True, False),
]

HEADER_COLOUR = 'grey'


class Logger:
    file_logging = True
    console_logging = True

    log_file = None


def file_printer(messages):
    if not Logger.log_file:
        Logger.log_file = open("log", "a")
    Logger.log_file.write(messages[0] + " ".join(messages[1:]) + "\n\n")


def console_printer(messages):
    print messages[0] + " ".join(messages[1:])


def printer(messages, formatting):
    name, colour, bg, attributes, timestamp, to_file, to_console = formatting

    now = time.asctime(time.localtime(time.time()))
    header_string = "%s: %s\n" % (now, name)

    messages = map(str, messages)

    if Logger.file_logging and to_file:
        if timestamp:
            headered_messages = [header_string] + messages
        else:
            headered_messages = [""] + messages

        file_printer(headered_messages)

    if Logger.console_logging and to_console:
        header_string = colored(header_string, HEADER_COLOUR)
        messages = [colored(message, colour, bg, attrs=attributes)
                    for message in messages]

        if timestamp:
            headered_messages = [header_string] + messages
        else:
            headered_messages = [""] + messages

        console_printer(headered_messages)


def syserr(*messages):
    printer(messages, FORMATS[0])


def syswarn(*messages):
    printer(messages, FORMATS[1])


def sysinfo(*messages):
    printer(messages, FORMATS[2])


def dataerr(*messages):
    printer(messages, FORMATS[3])


def datawarn(*messages):
    printer(messages, FORMATS[4])


def databold(*messages):
    printer(messages, FORMATS[5])


def datainfo(*messages):
    printer(messages, FORMATS[6])


def other(*messages):
    printer(messages, FORMATS[7])

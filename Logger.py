import time
from termcolor import colored

LEVELS = [
    ('ERROR', 'white', 'on_red', ['bold'], True),
    ('WARNING', 'white', 'on_yellow', ['bold'], True),
    ('SYSINFO', 'white', 'on_blue', [], True),
    ('ERROR', 'red', None, [], True),
    ('WARNING', 'yellow', None, [], True),
    ('INFO', 'blue', None, ['bold'], True),
    ('INFO', 'blue', None, [], False),
    ('OTHER', 'grey', None, [], False),
]

HEADER_COLOUR = 'grey'


class Logger:
    file_logging = True
    console_logging = True
    output_level = 7

    log_file = None


def file_printer(messages):
    if not Logger.log_file:
        Logger.log_file = open("log", "a")
    Logger.log_file.write(messages[0] + " ".join(messages[1:]) + "\n\n")


def console_printer(messages):
    print messages[0] + " ".join(messages[1:])


def printer(messages, level):
    if level <= Logger.output_level:
        level_info = LEVELS[level]
        name, colour, on_colour, attributes, timestamp = level_info

        now = time.asctime(time.localtime(time.time()))
        header_string = "%s: %s\n" % (now, name)

        messages = map(str, messages)

        if Logger.file_logging:
            if timestamp:
                headered_messages = [header_string] + messages
            else:
                headered_messages = [""] + messages

            file_printer(headered_messages)

        if Logger.console_logging:
            header_string = colored(header_string, HEADER_COLOUR)
            messages = [colored(message, colour, on_colour, attrs=attributes)
                        for message in messages]

            if timestamp:
                headered_messages = [header_string] + messages
            else:
                headered_messages = [""] + messages

            console_printer(headered_messages)


def syserr(*messages):
    printer(messages, 0)


def syswarn(*messages):
    printer(messages, 1)


def sysinfo(*messages):
    printer(messages, 2)


def dataerr(*messages):
    printer(messages, 3)


def datawarn(*messages):
    printer(messages, 4)


def databold(*messages):
    printer(messages, 5)


def datainfo(*messages):
    printer(messages, 6)


def other(*messages):
    printer(messages, 7)


def e(*messages):
    printer(messages, 0)


def w(*messages):
    printer(messages, 1)


def i(*messages):
    printer(messages, 2)


def d(*messages):
    printer(messages, 3)


def v(*messages):
    printer(messages, 4)


def vv(*messages):
    printer(messages, 5)

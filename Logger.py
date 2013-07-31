import time
from termcolor import colored

LEVELS = [
    {'name': 'ERROR', 'colour': 'red', 'attributes': ['bold']},
    {'name': 'WARNING', 'colour': 'yellow', 'attributes': ['bold']},
    {'name': 'INFORMATION', 'colour': 'magenta', 'attributes': []},
    {'name': 'DEBUG', 'colour': 'blue', 'attributes': []},
    {'name': 'VERBOSE', 'colour': 'cyan', 'attributes': []},
    {'name': 'VERBOSE VERBOSE', 'colour': 'green', 'attributes': []},
]

HEADER_COLOUR = 'grey'


class Logger:
    file_logging = True
    console_logging = True
    output_level = 5

    log_file = None


def file_printer(messages):
    if not Logger.log_file:
        Logger.log_file = open("log", "a")

    Logger.log_file.write(messages[0] + " ".join(messages[1:]) + "\n\n")


def console_printer(messages):
    print messages[0] + " ".join(messages[1:])


def printer(messages, level):
    if level <= Logger.output_level:
        now = time.asctime(time.localtime(time.time()))
        header_string = "%s: %s\n" % (now, LEVELS[level]['name'])

        headered_messages = [header_string] + list(messages)

        if Logger.file_logging:
            file_printer(headered_messages)

        if Logger.console_logging:
            colour = LEVELS[level]['colour']
            attributes = LEVELS[level]['attributes']

            header_string = colored(header_string, HEADER_COLOUR)
            messages = [colored(message, colour, attrs=attributes)
                        for message in messages]
            headered_messages = [header_string] + messages

            console_printer(headered_messages)


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

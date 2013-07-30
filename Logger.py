from termcolor import colored

FILE_LOGGING = True

if FILE_LOGGING:
    try:
        log_file
    except NameError:
        log_file = open("log", "w+")

def printer(messages, colour):
    for message in messages:
        message = str(message).replace("\r", "")
        print colored(message, colour),

        if FILE_LOGGING:
            log_file.write(message)

    print ""
    if FILE_LOGGING:
        log_file.write("\n")


def e(*messages):
    printer(messages, 'red')


def i(*messages):
    printer(messages, 'green')


def v(*messages):
    printer(messages, 'yellow')


def d(*messages):
    printer(messages, 'magenta')


def w(*messages):
    printer(messages, 'blue')

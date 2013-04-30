from termcolor import colored

def printer(messages, colour):
	for message in messages:
		print colored(str(message), colour),
	print ""

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

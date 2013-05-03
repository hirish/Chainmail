from Encryption import Encryption
from Encryption import EncryptionError
import Logger

def extract_set_cookie(unparsed_value):
	try:
		cookie, metacookie = unparsed_value.split(";", 1)
	except ValueError:
		cookie = unparsed_value.rstrip(";")
		metacookie = ""
	
	key, value = extract_cookie_value(cookie)
	return key, value, metacookie

def extract_cookie_value(unparsed_cookie):
	unparsed_cookie = unparsed_cookie.strip()
	key, value = unparsed_cookie.split("=", 1)
	if len(value) > 1 and (value[0] == value[-1] == '"'):
		value = value[1:-1]
	return key, value

def encrypt_set_cookies(set_cookies):
	encryption = Encryption()
	encrypted = []
	for key, value, metadata in set_cookies:
		Logger.e("Encrypting " + str((key, value, metadata)))
		try:
			encrypted_value = encryption.encrypt(value, True)
		except EncryptionError as e:
			Logger.e("Couldn't encrypt key:%s - value:%s\n\t%s" % (key, value, str(e)))
		encrypted.append((key, encrypted_value, metadata))
	return encrypted

def decrypt_cookies(cookies):
	encryption = Encryption()
	decrypted = {}
	for key, value in cookies.iteritems():
		try:
			decrypted[key] = encryption.decrypt(value, True)
		except EncryptionError:
			pass
	return decrypted


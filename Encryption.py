import Crypto.PublicKey.RSA as RSA
import Crypto.Cipher.PKCS1_OAEP as PKCS1_OAEP
import base64
import Logger


class Encryption:

    cipher = None

    def __init__(self):
        if not self.cipher:
            Logger.e("Loading certificate")
            with open("../Certificates/server.der") as key_file:
                key = RSA.importKey(key_file.read())

            self.cipher = PKCS1_OAEP.new(key)

    def encode(self, value):
        return base64.b64encode(value)

    def decode(self, value):
        return base64.b64decode(value)

    def encrypt(self, value):
        unencrypted_values = self._chunks(value, 80)
        encrypted_values = [self._encrypt(v) for v in unencrypted_values]
        return " ".join(encrypted_values)

    def _encrypt(self, value):
        return self.encode(self.cipher.encrypt(value))

    def decrypt(self, value):
        encrypted_values = value.split()
        unencrypted_values = [self._decrypt(v) for v in encrypted_values]
        return "".join(unencrypted_values)

    def _decrypt(self, value):
        Logger.e(len(self.decode(value)))
        return self.cipher.decrypt(self.decode(value))

    def _chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]


class EncryptionError(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return "EncryptionError: %s" % self.message

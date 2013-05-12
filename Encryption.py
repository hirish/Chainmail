import Crypto.PublicKey.RSA as RSA
import Crypto.Cipher.PKCS1_OAEP as PKCS1_OAEP
import Logger


class Encryption:

    cipher = None

    def __init__(self):
        if not self.cipher:
            Logger.e("Loading certificate")
            with open("../Certificates/server.pem") as key_file:
                key = RSA.importKey(key_file.read())

            self.cipher = PKCS1_OAEP.new(key)

    def make_transmittable(self, value):
        if value[:9] == "chainmail":
            raise EncryptionError("Value passed is already a transmittable")
        else:
            ord_values = [ord(c) for c in value]
            hash_values = ["{0:x}".format(c) for c in ord_values]
            return "chainmail:" + ":".join(hash_values)

    def unmake_transmittable(self, value):
        if value[:9] == "chainmail":
            trimmed_value = value[10:]
            hash_values = trimmed_value.split(":")
            ord_values = [int(c, 16) for c in hash_values]
            chr_values = [chr(c) for c in ord_values]
            return "".join(chr_values)
        else:
            raise EncryptionError("Value passed is not a transmittable")

    def encrypt(self, value, make_transmittable=False):
        if value == "":
            return ""
        elif make_transmittable:
            return self.make_transmittable(self.cipher.encrypt(value))
        else:
            return self.cipher.encrypt(value)

    def decrypt(self, value, unmake_transmittable=False):
        if value == "":
            return ""
        elif unmake_transmittable:
            return self.cipher.decrypt(self.unmake_transmittable(value))
        else:
            return self.cipher.decrypt(value)


class EncryptionError(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return "EncryptionError: %s" % self.message

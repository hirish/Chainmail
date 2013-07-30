import OpenSSL
import os
import time
import tempfile
import shutil

def dummy_cert(filename, ca, commonname, sans):
    """
        Generates and writes a certificate to fp.

        ca: Path to the certificate authority file, or None.
        commonname: Common name for the generated certificate.
        sans: A list of Subject Alternate Names.

        Returns cert path if operation succeeded, None if not.
    """
    ss = []
    for i in sans:
        ss.append("DNS: %s"%i)
    ss = ", ".join(ss)

    raw = file(ca, "rb").read()
    ca = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, raw)
    key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, raw)

    pkey = OpenSSL.crypto.PKey()
    pkey.generate_key(OpenSSL.crypto.TYPE_RSA, 1024)

    req = OpenSSL.crypto.X509Req()
    subj = req.get_subject()

    subj.CN = commonname

    req.set_pubkey(pkey)
    req.sign(pkey, "sha1")

    if ss:
        req.add_extensions([OpenSSL.crypto.X509Extension("subjectAltName", True, ss)])

    cert = OpenSSL.crypto.X509()
    cert.gmtime_adj_notBefore(-3600)
    cert.gmtime_adj_notAfter(60 * 60 * 24 * 30)
    cert.set_issuer(ca.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_serial_number(int(time.time()*10000))
    if ss:
        cert.set_version(2)
        cert.add_extensions([OpenSSL.crypto.X509Extension("subjectAltName", True, ss)])
    cert.set_pubkey(req.get_pubkey())
    cert.sign(key, "sha1")

    cert_file = filename
    key_file = filename[:-4] + '-key.pem'

    with open(cert_file, 'wb') as fp:
        fp.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))

    with open(key_file, 'wb') as fp:
        fp.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pkey))

    return cert_file, key_file


class CertStore:
    """
        Implements an on-disk certificate store.
    """
    def __init__(self, certdir=None):
        """
            certdir: The certificate store directory. If None, a temporary
            directory will be created, and destroyed when the .cleanup() method
            is called.
        """
        if certdir:
            self.remove = False
            self.certdir = certdir
        else:
            self.remove = True
            self.certdir = tempfile.mkdtemp(prefix="certstore")

    def check_domain(self, commonname):
        try:
            commonname.decode("idna")
            commonname.decode("ascii")
        except:
            return False
        if ".." in commonname:
            return False
        if "/" in commonname:
            return False
        return True

    def get_cert(self, commonname, sans, cacert="/home/henry/chainmail/certs/ca.pem"):
        """
            Returns the path to a certificate.

            commonname: Common name for the generated certificate. Must be a
            valid, plain-ASCII, IDNA-encoded domain name.

            sans: A list of Subject Alternate Names.

            cacert: An optional path to a CA certificate. If specified, the
            cert is created if it does not exist, else return None.

            Return None if the certificate could not be found or generated.
        """
        if not self.check_domain(commonname):
            return None

        certpath = os.path.join(self.certdir, commonname + ".pem")
        keypath = certpath[:-4] + "-key.pem"
        if os.path.exists(certpath) and os.path.exists(keypath):
            return certpath, keypath

        return dummy_cert(certpath, cacert, commonname, sans)

    def cleanup(self):
        if self.remove:
            shutil.rmtree(self.certdir)


#cs = CertStore()
#print cs.get_cert("*.henryirish.com", [])

from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
import config

class SubKeyGenerator:
    def __init__(self):
        self.password = ""
        self.salt = ""
        self.counter = 0

    def create_private_key(self, password, salt):
        self.password=config.HASH_FUNCTION(password.encode())
        self.salt=config.HASH_FUNCTION(salt.encode())
        
        self.counter=0
        self.master_key = PBKDF2(password, salt, count=10000)
        self.RSA_key = RSA.generate(2048, randfunc=self.my_rand)
        return self.RSA_key.exportKey().decode("ascii")

    def create_public_key(self, password, salt):
        self.password=config.HASH_FUNCTION(password.encode())
        self.salt=config.HASH_FUNCTION(salt.encode())
        self.counter=0
        self.master_key = PBKDF2(password, salt, count=10000)
        self.RSA_key = RSA.generate(2048, randfunc=self.my_rand) ### this causes slow execution(for more: https://stackoverflow.com/questions/50477926/why-pycryptodome-rsa-public-key-generation-is-so-slow)
        return self.RSA_key.public_key().exportKey().decode("ascii")

    def get_private_key(self):
        return self.RSA_key.exportKey().decode("ascii")

    def get_public_key(self):
        return self.RSA_key.public_key().exportKey().decode("ascii")

    def my_rand(self, n):
        self.counter += 1
        return PBKDF2(self.master_key, "my_rand:%d" % self.counter, dkLen=n, count=1)

###
# THE PREVIOUS CODE WAS TAKEN AND MODIFIED, ORIGIN OF CODE IS GIVEN IN LINK BELOW
# https://stackoverflow.com/questions/20483504/making-rsa-keys-from-a-password-in-python
###
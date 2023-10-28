from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

keyPair = RSA.generate(3072)

pubKey = keyPair.publickey()
print(f"Public key:  (n={hex(pubKey.n)}, e={hex(pubKey.e)})")
pubKeyPEM = pubKey.exportKey()
print(pubKeyPEM.decode('ascii'))

print(f"Private key: (n={hex(pubKey.n)}, d={hex(keyPair.d)})")
privKeyPEM = keyPair.exportKey()
print(privKeyPEM.decode('ascii'))

msg = b'A message for encryption'
encryptor = PKCS1_OAEP.new(pubKey)
encrypted = encryptor.encrypt(msg)
print("Encrypted:", binascii.hexlify(encrypted))

decryptor = PKCS1_OAEP.new(keyPair)
decrypted = decryptor.decrypt(encrypted)
print('Decrypted:', decrypted)

print("\n\n\n\n\n")
print("=====================================")
print("=====================================")

private_key_file = open("keys/private3.pem", "w")
private_key_file.write(privKeyPEM.decode("ascii"))
private_key_file.close()

public_key_file = open("keys/public3.pem", "w")
public_key_file.write(pubKeyPEM.decode("ascii"))
public_key_file.close()

public_key_file = open("keys/public.pem", "r")
p1 = public_key_file.read()
print(p1)
public_key_file.close()

print("\n\n")

msg = b'A message for encryption'
encryptor = PKCS1_OAEP.new(RSA.importKey(open('keys/public.pem').read()))
encrypted = encryptor.encrypt(msg)
print("Encrypted:", binascii.hexlify(encrypted))

key = RSA.importKey(open('keys/private.pem').read())
cipher = PKCS1_OAEP.new(key)
message = cipher.decrypt(encrypted)
print(f"Message: {message}")
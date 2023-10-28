import json
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import config
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import sub_key_generator

subKeyGenerator = sub_key_generator.SubKeyGenerator()

def get_private_key():
    linesKey = []
    print("Insert private key: ")
    while True:
        user_input = input()

        if user_input == '':
            break
        else:
            linesKey.append(user_input + '\n')

    privateKey = ""
    for i in linesKey:
        privateKey += i

    privateKey = privateKey[0:len(privateKey) - 1]

    #ja ovde podrazumijevam da je chain izmedju cvorova sto bi se reklo dogovoren tj. uskladjen
    #oni su uspostavili veze izmedju sebe
    #i radili su replace chain
    #Zasto trazim sa cvora 5001? Pa zato sto predpostavljamo da su uskladjeni
    #Kako bi ste Vi uskladili da to trebate odraditi?
        #pa kada svaki put dodamo neki blok tj. odradimo mining pozvali bismo replace chain nad ostalima tj u ovom slucaju 5002, 5003
    #OVO SAM PODRAZUMIJAVAO JER NIJE NAVEDENO U TEKSTU ZADATKA

    res = requests.get("http://127.0.0.1:5001/get-chain")
    response = json.loads(res.text)

    result = 0
    for i in response["chain"]:
        #print(i)

        for j in i["transactions"]:
            subPrivateKey = subKeyGenerator.create_private_key(privateKey, i["timestamp"])
            decryptor = PKCS1_OAEP.new(RSA.importKey(subPrivateKey))

            #samo ako je uspjesno dekriptovanje citamo sadrzaj(takodje provjeravamo i signature)
            try:
                data = json.loads(decryptor.decrypt(base64.b64decode(j["data"])).decode("UTF-8"))

                print(data)

                key = RSA.import_key(requests.post(f'http://127.0.0.1:4999/get-sub-public-key-check-all', json={
                    "hashPublic": data["sender"],
                    "salt": i["timestamp"]
                }).json()["subPublicKey"])

                h = SHA256.new(json.dumps(data).encode())

                signa = j["signature"]
                preSignature = b"" + signa.encode()
                preSignature = base64.b64decode(preSignature)

                try:
                    pkcs1_15.new(key).verify(h, preSignature)
                    #print("The signature is valid.")

                    result += data["amount"]
                except (ValueError, TypeError):
                    #print("The signature is not valid.")
                    {}
            except:
                {}

    return result;

print("\n=====================================")
print("============ WALLET =================")
print("=====================================\n")

flag = True
while flag:
    print("\n==========================================")
    print("=== Input Private Key ================ [1]")
    print("=== Exit ============================= [2]")
    print("==========================================\n")

    option = input("Enter option number: ")

    if option.__eq__("1"):
        print(f"Money in the wallet: {get_private_key()}")
    elif option.__eq__("2"):
        flag = False

#36ff9977821fcb303d730cc978568394919293c074f8678f6342ba6d50e73a88
#9cb530c590ac66e8af949d27d306e93ebc1697574dcffe0fabd43a0a1319ce9e
#acd502e3887e341d9d9d55969f5155cbe0cab0c78ed6e3f6ec0623fa7c13bfec

###
### BEFORE APP STARTS THEY ARE ALL CONNECTED(precondition) AND REPLACE CHAIN DONE
###
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

def read_file():
    filename = "json_data/data.txt" ### file which stores json value
    file = open(filename, 'r')
    lines = file.readlines()
    
    linesKey = []
    print("Insert private key: ") ### the values are encrypted using a public key, so we need a private key now to decrepy the values
    while True:
        user_input = input()

        if user_input == '':
            break
        else:
            linesKey.append(user_input + '\n')

    ### read the private key, line by line
    privateKey = ""
    for i in linesKey:
        privateKey += i

    ### read line by line from file which stores json value
    jsonData = ""
    for i in lines:
        jsonData+=i

    jsonData = json.loads(jsonData) ### convert now to json object

    ### for every object do something
    for i in jsonData:
        decryptor = PKCS1_OAEP.new(RSA.importKey(privateKey)) ### load/create the key for decryption
        asd = decryptor.decrypt(base64.b64decode(i["data"])).decode("UTF-8") ### decode the value in data field

        asdd = "{" + asd + "}"

        myJson = json.loads(asdd)

        print("\n")
        print("=======================================================================================================")
        print("=======================================================================================================")
        print(f"======= Index: {i['index']}")
        print(f"======= Timestamp: {i['timestamp']}")
        print(f"======= Proof: {i['proof']}")
        print(f"======= Previous Hash: {i['previous_hash']}")
        print(f"======= Data:")
        print(f"=========== Land surface: {myJson['land_surface']}")
        print(f"=========== Sale price: {myJson['sale_price']}")
        print(f"=========== Previous owner: {myJson['previous_owner']}")
        print(f"=========== Current owner: {myJson['current_owner']}")
        print(f"=========== Date: {myJson['date_of_transaction']}")
        print(f"=========== Address: {myJson['address']}")
        print("=======================================================================================================")
        print("=======================================================================================================")
        print("\n")


flag = True
while flag:
    print("\n==================================")
    print("=== Read File ================ [1]")
    print("=== Exit ===================== [2]")
    print("==================================\n")

    option = input("Enter option number: ")

    if option.__eq__("1"):
        read_file()
    elif option.__eq__("2"):
        flag = False
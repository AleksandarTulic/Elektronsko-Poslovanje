import config
from flask import Flask, jsonify, request
import os
import sub_key_generator;

PRIVATE_FILE_START = 'private'
PUBLIC_FILE_START = 'public'

# mozemo ovo shvatiti kao centralni repozitorijum gdje se nalaze svi master kljucevi korisnika(public i private)
# preko ovoga mozete da dobijete samo odgovarajuce vrijednosti public kljuceva
# private kljucevi ne mogu da se dohvate odavde, samo mozemo da dobijemo public kljuvece koji su izvedeni iz master kljuca
# koji master private kljuc odgovara nekom korisniku zavisi od njegovog uparenog master public kljuca
class KeyManager:
    def __init__(self):
        self.nodes = []
        self.keys = []
        self.get_keys()
        self.subKeyGenerator = sub_key_generator.SubKeyGenerator()

    def get_keys(self):
        for i in os.listdir(os.getcwd() + "\\master_keys"):
           if i.startswith(PRIVATE_FILE_START):
               f = open(os.getcwd() + "\\master_keys\\" + i, "r")
               str1 = i.split("private")
               str2 = str1[1].split(".")
               obj = {"privateKey": f.read(), "publicKey": self.get_public_key(str2[0])}
               self.keys.append(obj)
        
        flag = False
        if flag == True:
            for i in self.keys:
                print(i["privateKey"])
                print(i["publicKey"])

    ### get public key from corresponding private key - READING FROM FILE
    def get_public_key(self, number):
        f = open(os.getcwd() + f"\\master_keys\\{PUBLIC_FILE_START}{number}.pem", "r")
        return f.read()

    ### given hash value of master public key and salt get sub public key
    ### first create hash of sent master public key and compare to the library of master public keys
    ### if there exists master public key in library that has an equal hash create sub public key(we give corresponding private key and salt - passed from the requester)
    def get_sub_public_key(self, hashMasterPublic, salt):
        for i in self.keys:
            if config.HASH_FUNCTION(i["publicKey"].encode()).hexdigest() == hashMasterPublic:
                return self.subKeyGenerator.create_public_key(i["privateKey"], salt)
    
    ### given hash of sub public key and salt get corresponding sub public key
    ### 1. for every master public key generate sub public key using private key and salt(this is timestamp of mine_block)
    ### 2. make a hash of generated sub public key
    ### 3. compare to passed hash of sub public key
    ### if equal return create sub public key
    ### for more look up main.py
    def get_sub_public_key_check_all(self, hashPublic, salt):
        for i in self.keys:
            subPublicKey = self.subKeyGenerator.create_public_key(i["privateKey"], salt)
            if config.HASH_FUNCTION(subPublicKey.encode()).hexdigest() == hashPublic:
                return subPublicKey
    
    ### user gives his master private key so that you can get hash value of his master public key
    def get_hash_of_corresponding_master_public_key(self, privateKey):
        for i in self.keys:
            if (i["privateKey"] == privateKey):
                return config.HASH_FUNCTION(i["publicKey"].encode()).hexdigest()


keyManager = KeyManager()

# ======================= FLASK APP ===========================================

#Create a Web App (Flask-based)
app = Flask(__name__)

### Retrieve sub public key for encryption, and address value(receiver field in transaction)
@app.route('/get-sub-public-key', methods=['POST'])
def get_1():
    json = request.get_json()

    response = {
        'subPublicKey' : keyManager.get_sub_public_key(json["hashMasterPublic"], json["salt"]) 
    }
    return jsonify(response), 200

### Retrieve sub public key for verification => digital signature
@app.route('/get-sub-public-key-check-all', methods=['POST'])
def get_2():
    json = request.get_json()

    response = {
        'subPublicKey' : keyManager.get_sub_public_key_check_all(json["hashPublic"], json["salt"]) 
    }
    return jsonify(response), 200

### given master public key get corresponding hash master public key
### look up node1.py line 191
@app.route('/get-hash-of-corresponding-master-public-key', methods=['POST'])
def get_3():
    json = request.get_json()

    response = {
        'hashMasterPublic' : keyManager.get_hash_of_corresponding_master_public_key(json["privateKey"]) 
    }
    return jsonify(response), 200

app.run(host=config.HOST, port=4999)
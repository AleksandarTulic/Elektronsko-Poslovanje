import datetime
import hashlib
import json
import config
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import os

class Blockchain:
    def __init__(self):
        self.chain = []

        ### creating the initial block(genesis block) - using some default data
        self.new_block(proof = 1, previous_hash = '0', data = {'land_surface': 1, 'sale_price': 1.00, 'previous_owner': 'p_owner', 'current_owner': 'c_owner', 'date_of_transaction': '2023-05-12', 'address': 'Ulica'}, publicKey="-----BEGIN PUBLIC KEY-----\n"
+ "MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAsHv8x5hDIAIkr9Q/7CEx\n"
+ "/Rn96F9WzK/TGIVnn/3z5X2Iv0t0FRY/j7wJI8wQc+KkR4rT+hKytqaB7dL+0IRT\n"
+ "dik//86UbU6kbIUjsw9FFybSWVrnuUcclMKjfM01y91uMWve+l8vAyz5PMJZnhXd\n"
+ "n8mRGB84MtpMgROF6bcQFeW98UfuQKEzibUJibkHWD1ETuOWbXzTUacpDlr0XjHF\n"
+ "YbQ9g8y3Pgy+sPQ52CPbv65ZVQRoVrkutWvhQth9TsWP2aKHF0gHlwUC5WIyNnZV\n"
+ "Fdv6LGpnFne1eGS8CbxWW/OpBtsaEaGwNwaA51dlXy8SZ8JFNd3z5ngh6LfD4CEg\n"
+ "BecoBe6CFXhQOfJWO46msmVhw0TOsfzr2uqCFuj4JHOf575sNJm5hO7axSMMfuAV\n"
+ "KeWDFifC6odRVp/KwpC3kdqmLS1LS9RHu12T/gGtppmg8bSPFCOPUBvuqli7HrRL\n"
+ "v+S9RdLA5UVoR57XID4Ps1Uf/RDbezi4yrHRw5UuQcvHAgMBAAE=\n"
+ "-----END PUBLIC KEY-----")

    def new_block(self, proof, previous_hash, data, publicKey):
        encryptor = PKCS1_OAEP.new(RSA.importKey(publicKey)) ### using public key for encryption

        ### formatting the value that will be encrypted in the right way
        data["previous_owner"] = '"' + data["previous_owner"] + '"'
        data["current_owner"] = '"' + data["current_owner"] + '"'
        data["date_of_transaction"] = '"' + data["date_of_transaction"] + '"'
        data["address"] = '"' + data["address"] + '"'
        message = f'"land_surface": {data["land_surface"]}, "sale_price": {data["sale_price"]}, "previous_owner": {data["previous_owner"]}, "current_owner": {data["current_owner"]}, "date_of_transaction": {data["date_of_transaction"]}, "address": {data["address"]}'
        message = f"{message}" ### the value that will be encrypted

        block = {
            "index": len(self.chain) + 1,
            "timestamp" : str(datetime.datetime.now()),
            "proof" : proof,
            "previous_hash" : previous_hash,
            "data": base64.b64encode(encryptor.encrypt(message.encode("UTF-8")))
        }

        value = f"{block['data']}"
        block["data"] = value[2:len(value) - 1]

        self.chain.append(block)
        self.write_to_file()
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(config.BLOCKCHAIN_PROBLEM_OPERATION_LAMBDA(previous_proof, new_proof)).encode()).hexdigest()

            if hash_operation[:len(config.LEADING_ZEROS)] == config.LEADING_ZEROS:
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    ### i have modified this a little bit because it would not work with the encrypted data
    def hash_of_block(self, block):
        encoded_block = json.dumps(block).encode("UTF-8")
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_of_block(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(config.BLOCKCHAIN_PROBLEM_OPERATION_LAMBDA(previous_proof, proof)).encode()).hexdigest()
            
            if hash_operation[:len(config.LEADING_ZEROS)] != config.LEADING_ZEROS:
                return False

            previous_block = block
            block_index += 1

        return True
    
    ### writing the chain to a file in json form
    def write_to_file(self):
        filename = "json_data/data.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(json.dumps(self.chain, indent=2))
            f.close()
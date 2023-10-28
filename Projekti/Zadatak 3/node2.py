
import datetime
import hashlib
import json
import config
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request
from uuid import uuid4
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import os
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import sub_key_generator;

class Blockchain:
    def __init__(self):
        self.generator = sub_key_generator.SubKeyGenerator()
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash, privateKey=""):
        arrData = []
        
        timeBefore = str(datetime.datetime.now())
        if privateKey != "":
            for i in self.transactions:
                print(i)

                senderPrivateKey = self.generator.create_private_key(privateKey, timeBefore)
                senderPublicKey = self.generator.create_public_key(privateKey, timeBefore)

                i["sender"]=config.HASH_FUNCTION(senderPublicKey.encode()).hexdigest()

                receiverPublicKey = requests.post(f'http://127.0.0.1:4999/get-sub-public-key', json={
                    "hashMasterPublic": i["receiver"],
                    "salt": timeBefore
                }).json()["subPublicKey"]

                i["receiver"]=config.HASH_FUNCTION(receiverPublicKey.encode()).hexdigest()

                encryptor = PKCS1_OAEP.new(RSA.importKey(receiverPublicKey))
                value1 = base64.b64encode(encryptor.encrypt(json.dumps(i).encode("UTF-8")))
                value2 = f"{value1}"
                value3 = value2[2:len(value2) - 1]

                key1 = RSA.import_key(senderPrivateKey);
                signature = pkcs1_15.new(key1).sign(SHA256.new(json.dumps(i).encode()));
                value1 = base64.b64encode(signature)
                value2 = f"{value1}"
                value4 = value2[2:len(value2) - 1]

                arrData.append({"data": value3, "signature": value4})

        block = {'index': len(self.chain) + 1,
                 'previous_hash' : previous_hash,
                 'proof' : proof,
                 'timestamp' : timeBefore,
                 'transactions' : arrData,
                 }
        
        self.transactions = []

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
    
    def add_transaction(self, sender, receiver, amount, flagDefault):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        
        if flagDefault == False:
            self.transactions.append({'sender':sender,
                                    'receiver':sender,
                                    'amount': (-1*amount)})

        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)

        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get-chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and requests.get(f'http://{node}/is-valid').json()["message"].__eq__("The Blockchain is valid!"):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            self.write_to_file()
            return True

        return False
    
    ### writing the chain to a file in json form
    def write_to_file(self):
        filename = "json_data/data2.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(json.dumps(self.chain, indent=2))
            f.close()
                
    
    
    
# ======================= FLASK APP ===========================================

#Create a Web App (Flask-based)
app = Flask(__name__)

#Creating an address for node on Port 5000
node_address = str(uuid4()).replace('-', '')

#Create a Blockchain
blockchain = Blockchain()

#Minig a block
@app.route('/mine-block', methods=['GET'])
def mine_block():
    #Get the previous proof
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    #Get previous hash 
    previous_hash = blockchain.hash_of_block(previous_block)
    #Add new block to the blockchain
    block = blockchain.create_block(proof, previous_hash, privateKey=request.json["privateKey"])
    #Add transactions (the receiver is the miner, an award for mining a block)
    blockchain.add_transaction(sender = '', receiver = requests.post(f'http://127.0.0.1:4999/get-hash-of-corresponding-master-public-key', json={"privateKey": request.json["privateKey"]}).json()["hashMasterPublic"], amount = 1, flagDefault = True)

    #Generate a response as a dictionary
    response = {'message':'Congratulations! You have just mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200

#Getting the full Blockchain
@app.route('/get-chain', methods=['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length': len(blockchain.chain) 
                }
    return jsonify(response), 200

#Checking if the blockchain is valid
@app.route('/is-valid', methods=['GET'])
def is_blockchain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message':'The Blockchain is valid!'}
    else:
        response = {'message':'The Blockchain is not valid!'}
    return jsonify(response), 200
    

#Adding a new transaction to the Blockchain
@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    #Get the JSON file posted in Postman, or by calling this endpoint
    json = request.get_json()
    #Check all the keys in the received JSON
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'ERROR: Some elements of the transaction JSON are missing!', 400 #Bad Request code
    #Add transaction to the next block,
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'], flagDefault = False)
    response = {'message' : f'This transaction will be added to block {index}'}
    return jsonify(response), 201 #Created code
    
#Decentralize a Blockchain

#Connecting new nodes
@app.route('/connect-node', methods=['POST'])
def connect_node():
    json = request.get_json()
    #Connect a new node
    nodes = json.get('nodes') #List of addresses
    #Make sure that the list is not empty
    if nodes is None:
        return "ERROR: No node", 400
    #Loop over the nodes and add them one by one
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'All the nodes are now connected.',
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201 #Created code

#Replacing the chain by the longest chain if needed
@app.route('/replace-chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message':'The node had different chains, so the chain was replaced by the longest one!',
                    'new_chain' : blockchain.chain}
    else:
        response = {'message':' All good. The chain is the largest one.',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200

#Running the app
app.run(host=config.HOST, port=5002)
        
                     
             
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

                
                
                
            
            
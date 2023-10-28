import blockchain
import config
from flask import Flask, jsonify, request

app = Flask(__name__)
blockchain = blockchain.Blockchain()

@app.route("/mine-block", methods=["POST"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)

    previous_hash = blockchain.hash_of_block(previous_block)
    block = blockchain.new_block(proof, previous_hash, config.LAND_DATA_FUNCTION(request.json["land_surface"],
                                                                                    request.json["sale_price"],
                                                                                    request.json["previous_owner"],
                                                                                    request.json["current_owner"],
                                                                                    request.json["date_of_transaction"],
                                                                                    request.json["address"] ), request.json["publicKey"])

    response = {
        'message':'Congratulations! You have just mined a block!',
        'index' : block['index'],
        'timestamp' : block['timestamp'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash'],
        "data": block["data"]
    }

    return jsonify(response), 200

@app.route('/get-chain', methods=['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length': len(blockchain.chain) 
                }
    return jsonify(response), 200

app.run(host=config.HOST, port=config.PORT)
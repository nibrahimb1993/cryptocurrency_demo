# Module 1 Create a BlockChain
import datetime
import hashlib
import json
from flask import Flask, jsonify


# Building a BlockChain

class BlockChain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_of_work(previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        if not chain:
            return False

        previous_block = chain[0]
        for block in chain[1:]:
            if block["previous_hash"] != self.hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block

        return True


# Mining BlockChain

app = Flask(__name__)
block_chain = BlockChain()


@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    previous_block = block_chain.get_previous_block()
    previous_proof = previous_block["proof"]
    proof = block_chain.proof_of_work(previous_proof)
    previous_hash = block_chain.hash(previous_block)
    block = block_chain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': block_chain.chain,
        'length': len(block_chain.chain)
    }
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {
        'chan_status': block_chain.is_chain_valid(block_chain.chain)
    }
    return jsonify(response), 200


app.run(host='0.0.0.0', port=5000)

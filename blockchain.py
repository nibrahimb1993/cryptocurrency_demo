# Module 1 Create a BlockChain
import datetime
import hashlib
import json
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify


# Building a BlockChain

class BlockChain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash="0")
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.transactions,
        }
        self.transactions = []
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
            if hash_operation[:4] == "0000":
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
            if hash_operation[:4] != "0000":
                return False

            previous_block = block

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
        })
        previous_block = self.get_previous_block()
        return previous_block["index"] + 1

    def add_node(self, node_address):
        parsed_url = urlparse(node_address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

        # Mining BlockChain


app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace("-", "")
block_chain = BlockChain()


@app.route("/mine_block", methods=["GET", "POST"])
def mine_block():
    previous_block = block_chain.get_previous_block()
    previous_proof = previous_block["proof"]
    proof = block_chain.proof_of_work(previous_proof)
    previous_hash = block_chain.hash(previous_block)
    block_chain.add_transaction(node_address, "Ibrahim", 1000)
    block = block_chain.create_block(proof, previous_hash)
    response = {
        "message": "Congratulations, you just mined a block!",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
        "transactions": block["transactions"],

    }
    return jsonify(response), 200


@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = {
        "chain": block_chain.chain,
        "length": len(block_chain.chain)
    }
    return jsonify(response), 200


@app.route("/is_valid", methods=["GET"])
def is_valid():
    response = {
        "chan_status": block_chain.is_chain_valid(block_chain.chain)
    }
    return jsonify(response), 200


@app.route("/add_transaction", methods=["POST"])
def add_transaction(request):
    data = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
    if not all(key in data for key in transaction_keys):
        raise KeyError("some elements of the transaction are missing")
    index = block_chain.add_transaction(**data)
    response = {"message": f"This transaction will be added to block {index}."}
    return jsonify(response), 201


app.run(host="0.0.0.0", port=5000)

import time
import hashlib
import json
from .crypto_utils import sign_data, verify_signature

class Block:
    def __init__(self, index, block_type, actor_id, public_key, transaction, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.block_type = block_type
        self.actor_id = actor_id
        self.public_key = public_key
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = 0
        self.signature = None
        self.current_hash = self.compute_hash()

    def compute_hash(self):
        data = f"{self.index}{self.timestamp}{self.block_type}{self.actor_id}{self.public_key}{json.dumps(self.transaction, sort_keys=True)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def sign_block(self, private_key_b64):
        data_to_sign = {"current_hash": self.current_hash}
        self.signature = sign_data(private_key_b64, data_to_sign)

    def verify_signature(self):
        if not self.signature:
            return False
        data_to_verify = {"current_hash": self.current_hash}
        return verify_signature(self.public_key, data_to_verify, self.signature)

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'block_type': self.block_type,
            'actor_id': self.actor_id,
            'public_key': self.public_key,
            'transaction': self.transaction,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'signature': self.signature,
            'current_hash': self.current_hash
        }

    @staticmethod
    def from_dict(data):
        block = Block(
            data['index'], data['block_type'], data['actor_id'],
            data['public_key'], data['transaction'], data['previous_hash']
        )
        block.timestamp = data['timestamp']
        block.nonce = data['nonce']
        block.signature = data['signature']
        block.current_hash = data['current_hash']
        return block
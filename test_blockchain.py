import sys, os
sys.path.insert(0, os.getcwd())
from app import blockchain, Block, generate_key_pair

# Test genesis
assert blockchain.is_chain_valid()
print("Genesis valid")

# Test add block
priv, pub = generate_key_pair()
last = blockchain.get_last_block()
tx = {"test": "data"}
new_block = Block(last.index+1, "TEST", "tester", pub, tx, last.current_hash)
ok, msg = blockchain.add_block(new_block, priv)
assert ok
print("Block added")

# Test tamper
blockchain.chain[1].transaction["test"] = "changed"
blockchain.chain[1].current_hash = blockchain.chain[1].compute_hash()
assert not blockchain.is_chain_valid()
print("Tamper detected")

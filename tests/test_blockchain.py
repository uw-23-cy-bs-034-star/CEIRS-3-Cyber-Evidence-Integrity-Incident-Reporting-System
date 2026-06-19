# tests/test_blockchain.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair

def test_blockchain():
    # Initialize blockchain
    bc = Blockchain("blockchain/chain.json")
    print("Chain valid?", bc.is_chain_valid())

    # Generate a victim key pair
    victim_priv, victim_pub = generate_key_pair()
    # Generate an investigator key pair
    inv_priv, inv_pub = generate_key_pair()

    # Create an INCIDENT block
    incident_tx = {
        "case_id": "CASE-001",
        "title": "Phishing Attack",
        "description": "Fake bank email received",
        "victim_id": "victim_alice",
        "severity": "High"
    }
    last_block = bc.get_last_block()
    incident_block = Block(
        index=last_block.index + 1,
        block_type="INCIDENT",
        actor_id="victim_alice",
        public_key=victim_pub,
        transaction=incident_tx,
        previous_hash=last_block.current_hash,
        nonce=0
    )
    # In a real system we would mine to satisfy PoW, but we'll brute-force nonce
    # For simplicity, we'll re-hash with increasing nonce until hash starts with '00'
    # (This simulates mining)
    while not incident_block.current_hash.startswith("00"):
        incident_block.nonce += 1
        incident_block.current_hash = incident_block.compute_hash()
    success, msg = bc.add_block(incident_block, victim_priv)
    print("Add incident block:", success, msg)

    # Create EVIDENCE block
    evidence_tx = {
        "evidence_id": "EVI-001",
        "case_id": "CASE-001",
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "file_name": "screenshot.png",
        "uploader_id": "victim_alice"
    }
    last_block = bc.get_last_block()
    evidence_block = Block(
        index=last_block.index + 1,
        block_type="EVIDENCE",
        actor_id="victim_alice",
        public_key=victim_pub,
        transaction=evidence_tx,
        previous_hash=last_block.current_hash,
        nonce=0
    )
    while not evidence_block.current_hash.startswith("00"):
        evidence_block.nonce += 1
        evidence_block.current_hash = evidence_block.compute_hash()
    success, msg = bc.add_block(evidence_block, victim_priv)
    print("Add evidence block:", success, msg)

    # Test tamper detection: manually modify a block in memory
    print("\n--- Tamper Test ---")
    tampered_block = bc.chain[1]   # incident block
    tampered_block.transaction["title"] = "Changed by attacker"
    tampered_block.current_hash = tampered_block.compute_hash()   # recompute but signature will fail
    if not bc.is_chain_valid():
        print("Tampering detected: chain is invalid!")
    else:
        print("ERROR: Tampering not detected!")

    # Restore from file (should be valid again because we didn't save)
    bc.load_chain()
    print("After reload from file, chain valid?", bc.is_chain_valid())

if __name__ == "__main__":
    test_blockchain()
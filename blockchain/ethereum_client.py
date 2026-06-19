# blockchain/ethereum_client.py
import os
import json
from web3 import Web3
from flask import current_app

class EthereumClient:
    def __init__(self):
        """
        Initializes the Ethereum client using the Web3 provider and contract details
        from the Flask app configuration.
        """
        self.w3 = Web3(Web3.HTTPProvider(current_app.config['WEB3_PROVIDER']))
        self.contract_address = current_app.config['CONTRACT_ADDRESS']
        
        # Load contract ABI from the contracts folder
        abi_path = os.path.join(current_app.root_path, 'contracts', 'EvidenceStorage_abi.json')
        with open(abi_path, 'r') as f:
            self.contract_abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )

    def store_evidence(self, case_id, evidence_id, cid, private_key):
        """
        Stores the IPFS CID on the Ethereum blockchain using the backend wallet.
        """
        # Get account from private key
        account = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        # Build transaction
        txn = self.contract.functions.storeEvidence(case_id, evidence_id, cid).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.to_wei('20', 'gwei')
        })
        
        # Sign transaction
        signed_txn = account.sign_transaction(txn)
        
        # Send raw transaction – use raw_transaction for web3.py >= 6.0.0
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def get_evidence(self, evidence_id):
        """
        Retrieves evidence details from the smart contract by evidenceId.
        """
        result = self.contract.functions.getEvidence(evidence_id).call()
        return {
            'caseId': result[0],
            'evidenceId': result[1],
            'cid': result[2],
            'timestamp': result[3],
            'uploader': result[4]
        }
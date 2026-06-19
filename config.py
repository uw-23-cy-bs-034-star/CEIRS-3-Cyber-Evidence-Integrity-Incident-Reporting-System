import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SESSION_TYPE = 'filesystem'           # Required
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = './flask_session'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    EVIDENCE_VAULT_DIR = os.path.join(BASE_DIR, 'evidence_vault')

    # Pinata (IPFS)
    PINATA_JWT = os.getenv('PINATA_JWT')

    # Ethereum
    WEB3_PROVIDER = os.getenv('ETHEREUM_RPC_URL')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
    ETH_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
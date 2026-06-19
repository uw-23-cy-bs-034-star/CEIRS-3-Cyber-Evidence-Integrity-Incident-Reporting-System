import os
from config import Config
from .encryptor import encrypt_file

def store_encrypted_evidence(case_id, evidence_id, file_data):
    case_dir = os.path.join(Config.EVIDENCE_VAULT_DIR, f"case_{case_id}")
    os.makedirs(case_dir, exist_ok=True)
    enc_data = encrypt_file(file_data)
    path = os.path.join(case_dir, f"{evidence_id}.enc")
    with open(path, 'wb') as f:
        f.write(enc_data)
    return path

def retrieve_encrypted_evidence(file_path):
    with open(file_path, 'rb') as f:
        return f.read()
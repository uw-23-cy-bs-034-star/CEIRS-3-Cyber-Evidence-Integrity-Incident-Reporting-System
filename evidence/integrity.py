import os
from .vault import retrieve_encrypted_evidence
from .hasher import sha256_data

def verify_evidence_integrity(file_path, stored_hash):
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'rb') as f:
        enc_data = f.read()
    from .encryptor import decrypt_file
    dec_data = decrypt_file(enc_data)
    current_hash = sha256_data(dec_data)
    return current_hash == stored_hash
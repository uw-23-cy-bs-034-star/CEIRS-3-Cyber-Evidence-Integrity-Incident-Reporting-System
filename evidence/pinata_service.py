import requests
from flask import current_app

def upload_to_ipfs(file_data, filename):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    jwt = current_app.config.get('PINATA_JWT')
    if not jwt:
        raise Exception("PINATA_JWT not configured")
    headers = {"Authorization": f"Bearer {jwt}"}
    files = {'file': (filename, file_data)}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Pinata error {response.status_code}: {response.text}")
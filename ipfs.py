import requests
import json

PINATA_API_KEY = '38da8d631102f70347b9'
PINATA_SECRET_API_KEY = 'c1d21cc823c9b6a952d4e4ecc693ebacd8c470b66fd3cdbd421d1c983e51b77c'
PINATA_PIN_FILE_URL = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
PINATA_GATEWAY_URL = 'https://gateway.pinata.cloud/ipfs/'

def pin_to_ipfs(data):
    assert isinstance(data, dict), "Error: pin_to_ipfs expects a dictionary"

    # Your Pinata API credentials
    pinata_api_key = "a2cd687fe44848166a56"  # Replace with your actual key
    pinata_secret_api_key = "c8008f094efa729e3b404c712c0c825beff2dc05ee0c83fa30e1758dc3cad118"  # Replace with your actual secret key

    # Pinata API endpoint for pinning JSON
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    # Headers for authentication
    headers = {
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_api_key,
        'Content-Type': 'application/json',
    }

    # The payload includes your data
    payload = {
        "pinataContent": data
    }

    # Send the POST request to Pinata
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Parse the response to get the IPFS Content Identifier (CID)
        result = response.json()
        cid = result["IpfsHash"]
        return cid
    else:
        # Provide error information if the request failed
        raise Exception(f"Failed to pin data: {response.status_code} - {response.text}")

def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), "Error: get_from_ipfs accepts a CID string"

    # Construct the URL using a public IPFS gateway
    gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"

    # Fetch the data from the gateway
    response = requests.get(gateway_url)

    if response.status_code == 200:
        # Parse and return the JSON data
        data = response.json()
        assert isinstance(data, dict), "Error: get_from_ipfs should return a dict"
        return data
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

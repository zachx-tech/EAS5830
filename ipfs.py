import requests
import json

PINATA_API_KEY = 'f193d79143472c874f97'
PINATA_SECRET_API_KEY = 'fad8fd96dc528d6ce5eb420590a1bd9857fc9956db0e401e158408f35ec3b29e'
PINATA_PIN_FILE_URL = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
PINATA_GATEWAY_URL = 'https://gateway.pinata.cloud/ipfs/'

def pin_to_ipfs(data):
  assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
  # Convert dictionary to JSON format
  json_data = json.dumps(data)

  # Prepare headers with authentication
  headers = {
      'pinata_api_key': PINATA_API_KEY,
      'pinata_secret_api_key': PINATA_SECRET_API_KEY,
      'Content-Type': 'application/json'
  }

  # Send POST request to Pinata to pin JSON to IPFS
  response = requests.post(PINATA_PIN_FILE_URL, data=json_data, headers=headers)

  # Check if the request was successful
  if response.status_code == 200:
      cid = response.json()["IpfsHash"]
      return cid
  else:
      raise Exception(f"Error pinning to IPFS: {response.status_code}, {response.text}")

def get_from_ipfs(cid,content_type="json"):
  assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
  # Build the URL for retrieving data from Pinata's gateway
  pinata_cat_url = f'{PINATA_GATEWAY_URL}{cid}'

  # Send GET request to retrieve data from the IPFS gateway
  response = requests.get(pinata_cat_url)

  # Check if the request was successful
  if response.status_code == 200:
      data = json.loads(response.text)
      assert isinstance(data, dict), f"get_from_ipfs should return a dict"
      return data
  else:
      raise Exception(f"Error retrieving from IPFS: {response.status_code}, {response.text}")

import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.providers.rpc import HTTPProvider
from web3 import EthereumTesterProvider

'''
If you use one of the suggested infrastructure providers, the url will be of the form
now_url  = f"https://eth.nownodes.io/{now_token}"
alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
'''

def connect_to_eth():
	url = "https://mainnet.infura.io/v3/e261d32b37184d0cb02c36b1dc7ec5fc"  # FILL THIS IN
	w3 = Web3(HTTPProvider(url))
	assert w3.is_connected(), f"Failed to connect to provider at {url}"
	return w3


def connect_with_middleware(contract_json):
    with open(contract_json, "r") as f:
        d = json.load(f)
        d = d['bsc']
        address = d['address']
        abi = d['abi']

    bsc_url = "https://bsc-dataseed.binance.org/"  # BSC mainnet public RPC

    
    w3 = Web3(HTTPProvider(bsc_url))
    assert w3.is_connected(), f"Failed to connect to BSC provider at {bsc_url}"

    
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    

    checksum_address = Web3.to_checksum_address(address)
    contract = w3.eth.contract(address=checksum_address, abi=abi)

    return w3, contract


if __name__ == "__main__":
	w3_eth = connect_to_eth()
    w3_bnb, contract_bnb = connect_with_middleware("contract_info.json")

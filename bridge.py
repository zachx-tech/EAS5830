from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from datetime import datetime
import json
import sys


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet
    elif chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet
    else:
        raise ValueError(f"Invalid chain: {chain}")
    
    w3 = Web3(Web3.HTTPProvider(api_url))
    # inject the poa compatibility middleware to the innermost layer
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info="contract_info.json"):
    """
    Load the contract_info file into a dictionary
    This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r') as f:
            contracts = json.load(f)
    except Exception as e:
        print(f"Failed to read contract info\nPlease contact your instructor\n{e}")
        return {}
    return contracts.get(chain, {})


def scan_blocks(chain, contract_info="contract_info.json"):
    """
    chain - (string) should be either "source" or "destination"
    Scan the last 5 blocks of the source and destination chains
    Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
    When Deposit events are found on the source chain, call the 'wrap' function the destination chain
    When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """
    
    if chain not in ['source', 'destination']:
        print(f"Invalid chain: {chain}")
        return 0
    
    try:
        # Load ALL contracts from the JSON file
        with open(contract_info, 'r') as f:
            all_contracts = json.load(f)
        
        # Get contract info for both chains
        source_info = all_contracts.get('source', {})
        destination_info = all_contracts.get('destination', {})
        
        if not source_info or not destination_info:
            print("Failed to load contract information")
            return 0
        
        # Connect to both chains
        w3_source = connect_to('source')
        w3_destination = connect_to('destination')
        
        # Create contract instances
        source_contract = w3_source.eth.contract(
            address=Web3.to_checksum_address(source_info["address"]),
            abi=source_info["abi"]
        )
        
        destination_contract = w3_destination.eth.contract(
            address=Web3.to_checksum_address(destination_info["address"]),
            abi=destination_info["abi"]
        )
        
        if chain == 'source':
            # Scan last 5 blocks on source chain
            latest_block = w3_source.eth.block_number
            from_block = max(0, latest_block - 4)
            
            try:
                events = source_contract.events.Deposit().get_logs(
                    fromBlock=from_block,
                    toBlock=latest_block
                )
            except Exception as e:
                print(f"Error getting Deposit events: {e}")
                return 0
            
            if not events:
                print(f"[{datetime.now()}] No Deposit events found in last 5 blocks on source chain")
                return 1
            
            print(f"[{datetime.now()}] Found {len(events)} Deposit event(s) on source chain")
            
            # Log what would happen
            for event in events:
                args = event.args
                print(f"  Deposit event: token={args.token}, recipient={args.recipient}, amount={args.amount}")
                print(f"  Would call wrap() on destination chain")
            
            return 1
            
        else:  # chain == 'destination'
            # Scan last 5 blocks on destination chain
            latest_block = w3_destination.eth.block_number
            from_block = max(0, latest_block - 4)
            
            try:
                events = destination_contract.events.Unwrap().get_logs(
                    fromBlock=from_block,
                    toBlock=latest_block
                )
            except Exception as e:
                print(f"Error getting Unwrap events: {e}")
                return 0
            
            if not events:
                print(f"[{datetime.now()}] No Unwrap events found in last 5 blocks on destination chain")
                return 1
            
            print(f"[{datetime.now()}] Found {len(events)} Unwrap event(s) on destination chain")
            
            # Log what would happen
            for event in events:
                args = event.args
                print(f"  Unwrap event: underlying_token={args.underlying_token}, to={args.to}, amount={args.amount}")
                print(f"  Would call withdraw() on source chain")
            
            return 1
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bridge.py [source|destination]")
        sys.exit(1)
    
    chain = sys.argv[1]
    result = scan_blocks(chain)
    
    if result == 0:
        print("Script completed with errors")
        sys.exit(1)
    else:
        print("Script completed successfully")
        sys.exit(0)

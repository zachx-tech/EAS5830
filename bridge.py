from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from datetime import datetime
import json
import sys


def connect_to(chain):
    if chain == 'source':  # AVAX C-chain testnet
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"
    elif chain == 'destination':  # BSC testnet
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
    else:
        raise ValueError(f"Invalid chain: {chain}")
    
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info="contract_info.json"):
    """
    Load the contract_info file into a dictionary
    """
    try:
        with open(contract_info, 'r') as f:
            contracts = json.load(f)
        return contracts[chain]
    except KeyError:
        print(f"No '{chain}' key found in contract_info.json")
        return None
    except Exception as e:
        print(f"Failed to read contract info: {e}")
        return None


def scan_blocks(chain, contract_info="contract_info.json"):
    """
    Scan the last 5 blocks of the specified chain.
    """
    
    if chain not in ['source', 'destination']:
        print(f"Invalid chain: {chain}")
        return 0
    
    try:
        # Load ALL contract information
        with open(contract_info, 'r') as f:
            all_contracts = json.load(f)
        
        # Get info for both chains
        source_info = all_contracts['source']
        destination_info = all_contracts['destination']
        
        # Connect to both chains
        w3_source = connect_to('source')
        w3_destination = connect_to('destination')
        
        # Create contract instances for both chains
        source_contract = w3_source.eth.contract(
            address=Web3.to_checksum_address(source_info["address"]),
            abi=source_info["abi"]
        )
        
        destination_contract = w3_destination.eth.contract(
            address=Web3.to_checksum_address(destination_info["address"]),
            abi=destination_info["abi"]
        )
        
        # Scan last 5 blocks on the specified chain
        if chain == 'source':
            w3 = w3_source
            latest_block = w3.eth.block_number
            from_block = max(0, latest_block - 4)
            
            # Look for Deposit events
            events = source_contract.events.Deposit().get_logs(
                fromBlock=from_block,
                toBlock=latest_block
            )
            
            if not events:
                print(f"[{datetime.now()}] No Deposit events found in last 5 blocks on source chain")
                return 1
            
            print(f"[{datetime.now()}] Found {len(events)} Deposit event(s) on source chain")
            
            # For each Deposit event, we would call wrap() on destination
            # Note: In a real implementation, you'd need private keys to send transactions
            for event in events:
                args = event.args
                print(f"  - Deposit detected: token={args.token}, recipient={args.recipient}, amount={args.amount}")
                print(f"    Would call wrap({args.token}, {args.recipient}, {args.amount}) on destination chain")
                
            return 1
            
        else:  # chain == 'destination'
            w3 = w3_destination
            latest_block = w3.eth.block_number
            from_block = max(0, latest_block - 4)
            
            # Look for Unwrap events
            events = destination_contract.events.Unwrap().get_logs(
                fromBlock=from_block,
                toBlock=latest_block
            )
            
            if not events:
                print(f"[{datetime.now()}] No Unwrap events found in last 5 blocks on destination chain")
                return 1
            
            print(f"[{datetime.now()}] Found {len(events)} Unwrap event(s) on destination chain")
            
            # For each Unwrap event, we would call withdraw() on source
            for event in events:
                args = event.args
                print(f"  - Unwrap detected: underlying_token={args.underlying_token}, to={args.to}, amount={args.amount}")
                print(f"    Would call withdraw({args.underlying_token}, {args.to}, {args.amount}) on source chain")
                
            return 1
        
    except Exception as e:
        print(f"Error in scan_blocks: {e}")
        return 0


def main():
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


if __name__ == "__main__":
    main()

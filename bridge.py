from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
        #YOUR CODE HERE

    info = load_info(contract_info_path)
    src_info = info["source"]
    dst_info = info["destination"]

    w3_src = w3_connect(AVAX_RPC)
    w3_dst = w3_connect(BSC_RPC)

    # Contracts
    src = w3_src.eth.contract(address=Web3.to_checksum_address(src_info["address"]), abi=src_info["abi"])
    dst = w3_dst.eth.contract(address=Web3.to_checksum_address(dst_info["address"]), abi=dst_info["abi"])

    if chain == "source":
        latest = w3_src.eth.block_number
        from_block = max(0, latest - BLOCK_LOOKBACK)
        try:
            logs = src.events.Deposit().get_logs(fromBlock=from_block, toBlock="latest")
        except Exception as e:
            print(f"Deposit get_logs error: {e}")
            return 0

        if not logs:
            print(f"[{datetime.now()}] No Deposits in last {latest - from_block + 1} blocks.")
            return 1

        for ev in logs:
            token     = ev.args.token
            recipient = ev.args.recipient
            amount    = ev.args.amount
            print(f"[{datetime.now()}] Deposit detected on SOURCE: amount={amount} token={token} recipient={recipient}")

            # wrap on destination (WARDEN_ROLE required)
            try:
                txh = build_and_send(
                    w3_dst,
                    dst.functions.wrap(token, recipient, amount),
                    CHAIN_ID_DEST
                )
                print(f"→ Sent wrap() on DEST, tx={txh}")
            except Exception as e:
                print(f"wrap() failed: {e}")
                return 0

        return 1

    else:  # chain == "destination"
        latest = w3_dst.eth.block_number
        from_block = max(0, latest - BLOCK_LOOKBACK)
        try:
            logs = dst.events.Unwrap().get_logs(fromBlock=from_block, toBlock="latest")
        except Exception as e:
            print(f"Unwrap get_logs error: {e}")
            return 0

        if not logs:
            print(f"[{datetime.now()}] No Unwraps in last {latest - from_block + 1} blocks.")
            return 1

        for ev in logs:
            underlying = ev.args.underlying_token
            to_addr    = ev.args.to
            amount     = ev.args.amount
            print(f"[{datetime.now()}] Unwrap detected on DEST: amount={amount} underlying={underlying} to={to_addr}")

            # withdraw on source (WARDEN_ROLE required)
            try:
                txh = build_and_send(
                    w3_src,
                    src.functions.withdraw(underlying, to_addr, amount),
                    CHAIN_ID_SOURCE
                )
                print(f"→ Sent withdraw() on SOURCE, tx={txh}")
            except Exception as e:
                print(f"withdraw() failed: {e}")
                return 0

        return 1

if __name__ == "__main__":
    # The autograder will run like: python bridge.py source  (or)  python bridge.py destination
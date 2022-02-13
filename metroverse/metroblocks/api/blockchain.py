import json
import time
import os
import requests
import dotenv

from collections import defaultdict
from datetime import datetime

from web3 import Web3
from ens import ENS

import data

dotenv.load_dotenv()

ETHERSCAN_KEY = os.environ["ETHERSCAN_KEY"]
ETHERSCAN_API = "https://api.etherscan.io/api"

INFURA_KEY = os.environ["INFURA_KEY"]

NULL_ADDRESS = "0x0000000000000000000000000000000000000000"
BLOCK_TOKEN_CONTRACT_ADDRESS = "0x0e9d6552b85BE180d941f1cA73Ae3E318D2D4F1F"
VAULT_CONTRACT_ADDRESS = "0xaB93F992D9737Bd740113643e79fe9F8B6B34696"

# TODO: get this by calling etherscan instead.
METROVERSE_ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"},{"indexed":false,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"bool","name":"staked","type":"bool"}],"name":"BlockMinted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"MAX_BLOCKS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_BLOCKS_PER_ADDRESS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PRICE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"baseTokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"checkWhitelist","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disableWhitelist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"enableWhitelist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getBlockScore","outputs":[{"internalType":"uint256","name":"score","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"tokenIds","type":"uint256[]"}],"name":"getHoodBoost","outputs":[{"internalType":"uint256","name":"score","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bool","name":"stake","type":"bool"}],"name":"mintNFT","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"signatureR","type":"bytes32"},{"internalType":"bytes32","name":"signatureVS","type":"bytes32"},{"internalType":"bool","name":"stake","type":"bool"}],"name":"mintNFTWhitelist","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"saleActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"baseURI","type":"string"}],"name":"setBaseURI","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_proxyRegistryAddress","type":"address"}],"name":"setProxyRegistryAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_scoresAddress","type":"address"}],"name":"setScores","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"signer","type":"address"}],"name":"setSignerAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_vaultAddress","type":"address"}],"name":"setVault","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"signerAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"startSale","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"stopSale","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"tokensOfOwner","outputs":[{"internalType":"uint256[]","name":"ownerTokens","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"supply","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"hash","type":"bytes32"},{"internalType":"bytes32","name":"signatureR","type":"bytes32"},{"internalType":"bytes32","name":"signatureVS","type":"bytes32"}],"name":"verifyHash","outputs":[{"internalType":"address","name":"signer","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

w3 = Web3(Web3.WebsocketProvider(f'wss://mainnet.infura.io/ws/v3/{INFURA_KEY}'))
ns = ENS.fromWeb3(w3)

contract = w3.eth.contract(BLOCK_TOKEN_CONTRACT_ADDRESS, abi=METROVERSE_ABI)


def refresh_staked_blocks():
    staked = contract.functions.tokensOfOwner(VAULT_CONTRACT_ADDRESS).call()
    with open('data/staked.txt', 'w') as f:
        f.write('\n'.join([str(s) for s in staked]))
    return staked


def load_staked():
    with open('data/staked.txt', 'r') as f:
        return [int(l) for l in f.read().splitlines()]


def get_erc721_transactions(wallet, contract, endblock=99999999):
    params = {
        "apikey": ETHERSCAN_KEY,
        "module": "account",
        "action": "tokennfttx",
        "contractAddress": contract,
        "address": wallet,
        "page": 1,
        "offset": 1000,  # max 1000
        "startblock": 0,  # can make this higher
        "endblock": endblock,
        "sort": "desc",
    }
    r = requests.get(ETHERSCAN_API, params=params)
    if r.ok:
        parsed = json.loads(r.content)
        if parsed['result'] is not None:
            return parsed['result']
        else:
            print(f"didn't find expected results")
            print(json.dumps(parsed, indent=2))
            return []
    else:
        print(f"error: {r.status_code}, {r.content}")
        return []


def get_vault_transactions(endblock=99999999):
    return get_erc721_transactions(VAULT_CONTRACT_ADDRESS, BLOCK_TOKEN_CONTRACT_ADDRESS, endblock=endblock)


def get_staked_owners(owners, staked):
    print(ETHERSCAN_KEY)
    print(f"Finding owners for {len(staked)} staked blocks...")
    unresolved = defaultdict(set)
    seen = set()
    ts = None
    ethblock = None
    while len(seen) < len(staked):
        print(f"Staked: {len(staked)}; Seen: {len(seen)}; Last ETH block processed: {ethblock}; Last timestamp: {ts}")
        time.sleep(1)
        txns = get_vault_transactions(ethblock)
        for txn in txns:
            ethblock = int(txn['blockNumber'])
            ts = datetime.fromtimestamp(int(txn['timeStamp']))
            blocknum = int(txn['tokenID'])
            if txn['from'] == VAULT_CONTRACT_ADDRESS.lower():
                # print("  Ignoring transaction OUT of the vault")
                continue  # Only interested in transactions INTO
            if blocknum in seen:
                #print(f"  Ignoring block that we've already seen (block {blocknum})")
                continue  # Only track the first time (last time) we see a block enter the vault
            if blocknum in staked:  # ignore blocks that have since been unstaked.
                # print(f"  Block {blocknum}: {txn['from']} => {txn['to']}")
                if txn['from'] == NULL_ADDRESS:
                    unresolved[txn['hash']].add(blocknum)
                else:
                    # Most recent time we saw this block enter the vault.
                    owners[txn['from'].lower()].add(blocknum)
                seen.add(blocknum)

    print(f"Done finding staked owners")
    return owners, unresolved


def get_unstaked_owners(owners, unstaked):
    print(f"Finding owners for {len(unstaked)} unstaked blocks...")
    for i in unstaked:
        owner = contract.functions.ownerOf(i).call()
        if owner.lower() == VAULT_CONTRACT_ADDRESS.lower():
            print(f"WARNING: didn't expect vault to own unstaked block {i}")
        else:
            owners[owner.lower()].add(i)

    return owners


def get_immediate_stakers(owners, unresolved):
    print(f"Finding owners for {len(unresolved)} transactions at mint-time")
    for txn in unresolved:
        t = w3.eth.get_transaction(txn)
        if 'from' in t:
            owners[t['from'].lower()].update(unresolved[txn])

    return owners


def get_all_owners():
    all_blocks = set([i+1 for i in range(10000)])
    staked = refresh_staked_blocks()
    unstaked = all_blocks.difference(staked)

    owners = defaultdict(set)
    # 1) Get owners of staked blocks by using Etherscan.
    owners, unresolved = get_staked_owners(owners, staked)
    save_owners(owners, 'data/owners_staked.json')

    # 2) Resolve owners who staked at mint-time.
    owners = get_immediate_stakers(owners, unresolved)

    # 3) Get owners of unstaked blocks by calling Token contract directly.
    owners = get_unstaked_owners(owners, unstaked)
    save_owners(owners, 'data/owners_all.json')


def save_owners(owners, file):
    # Convert from {str->set} to {str->list}
    o = {k: list(v) for k, v in owners.items()}
    data.save(o, file)


def reverse_ens(addresses):
    reversed = {}
    for addr in addresses:
        ethname = ns.name(addr)
        if ethname:
            reversed[addr] = ethname
    return reversed


# Save/update known
# known = load("data/known.json")
# owners = load("data/owners_all.json")
# reversed = reverse_ens(owners.keys())
# known.update(reversed)
# save(known, "data/known.json")

#get_all_owners()
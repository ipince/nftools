from web3 import Web3
import abi

w3 = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/70d50b0c9cf14c7f93ec1c4e2c909318'))

# https://etherscan.io/token/0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f#readContract
# vault: 0xaB93F992D9737Bd740113643e79fe9F8B6B34696

def refresh_staked_blocks():
  addr = Web3.toChecksumAddress('0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f')
  contract = w3.eth.contract(addr, abi=abi.METROVERSE_ABI)
  staked = contract.functions.tokensOfOwner('0xaB93F992D9737Bd740113643e79fe9F8B6B34696').call()    
  with open('data/staked.txt', 'w') as f:
    f.write('\n'.join([str(s) for s in staked]))
  return len(staked)


#refresh_staked_blocks()

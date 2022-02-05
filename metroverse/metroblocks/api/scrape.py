import requests
import json
import time
import redis

r = redis.Redis()

MD = "https://ipfs.io/ipfs/QmR2wmDSCcbZnByZJrhJk92ZxtSmxxw5965cyJ4veV8qXA"

def fetch_all(limit=10000):
    all_blocks = []
    for i in range(limit):
        b = metadata(i+1)
        if b is not None:
            all_blocks.append(b)

    return all_blocks

def metadata(num):
    #print(f"getting data for block {num}")
    jsonblock = r.get(num)
    if jsonblock is not None:
        block = json.loads(jsonblock)
        return block

    print(f"block {num} not in redis, fetching")
    try:
        req = requests.get(f"{MD}/{num}")
        if req.status_code == 200:
            block = json.loads(req.content)
            jsonblock = json.dumps(block)
            r.set(num, jsonblock)
            return block
        else:
            print(f"failed to fetch block {num}")
    except Exception as e:
        print("failed.. sleeping")
        print(e)
        time.sleep(4)



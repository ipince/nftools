import json
import os
import redis
import dotenv

from datetime import datetime


dotenv.load_dotenv()
r = redis.Redis(host=os.getenv("REDIS_HOST"))
# r = redis.Redis()


def save(data, file):
    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=2))


def load(file):
    last_updated = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M UTC")
    with open(file, 'r') as f:
        return json.loads(f.read()), last_updated


def rset(k, v):
    r.set(k, v)


def rget(k):
    return r.get(k)


def save_staked(staked, ts):
    rset("staked", json.dumps(staked))
    rset("staked_ts", ts.isoformat())


def load_staked():
    try:
        return json.loads(rget("staked"))
    except Exception:
        return []


def load_staked_ts():
    return datetime.fromisoformat(rget("staked_ts").decode("utf-8"))

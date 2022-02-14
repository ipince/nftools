import json
import os

from datetime import datetime


def save(data, file):
    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=2))


def load(file):
    last_updated = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M UTC")
    with open(file, 'r') as f:
        return json.loads(f.read()), last_updated

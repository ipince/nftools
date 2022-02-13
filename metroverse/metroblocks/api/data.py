import json


def save(data, file):
    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=2))


def load(file):
    with open(file, 'r') as f:
        return json.loads(f.read())

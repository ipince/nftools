
import sys
import json

public = None
with open('data/buildings_public.json', 'r') as f:
  public = json.loads(f.read())

names = list(map(lambda p : p['name'], public))
#print(names)

lines = iter(sys.stdin.readlines())
boosts = []
while True:
  boost_name = next(lines, None)
  if boost_name is None:
    break

  boost_name = boost_name.strip()
  if boost_name == "":
    continue
  b1 = next(lines).strip()
  b2 = next(lines).strip()
  b3 = next(lines).strip()
  boost = int(next(lines)[:-2])

  b = {
    'name': boost_name,
    'buidings': [b1, b2, b3],
    'pct': boost
  }
  boosts.append(b)

print(json.dumps(boosts, indent=2))
#print(public[0])

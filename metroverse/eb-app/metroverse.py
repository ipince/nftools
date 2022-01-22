import requests
import json
import sys
import time
from collections import defaultdict

BEST = [
  # 1
  "RDC Tower",

  # 15
  "Soccer Stadium",
  "Football Stadium",

  # 20 res
"Winter Mega-Mansion",
"Radiant Towers Tall",
"Woodridge Center Tall",
"Hoodville Towers Tall",

  # 20 comm
"Metro Trade Center Tall",
"Metro Finance Tower Tall",
"Metsurance Building Tall",
"Baseball Stadium",

  # 20 indus
"MetroMaker Towers Tall",
"Industrial Center Tall",
"Metro Industrial Tall",
"Rocket Launch Site",

  # 25
"Nuclear Power Plant",

  # 30 res
"Organic Mansion",
"Radiant Towers Medium",
"Woodridge Center Medium",
"Hoodville Towers Medium",

  # 30 comm
"Metro Trade Center Medium",
"Metro Finance Tower Medium",
"Metsurance Building Medium",

  # 30 indus
"MetroMaker Towers Medium",
"Industrial Center Medium",
"Metro Industrial Medium",
"Solar Farm",
"Crypto Mining Facility",
"UnbelieVALTable",
]


def load_data():
  blocks = read_json("data/all_blocks_slim.json")
  buildings = read_json("data/buildings_non_public.json")
  public = read_json("data/buildings_public.json")
  boosts = read_json("data/boosts.json")
  return (blocks, buildings, public, boosts)

def read_json(path):
  with open(path, 'r') as f:
    data = json.loads(f.read())
    return data

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


def printb(block):
  print(bstr(block))

def bstr(block):
  strs = []
  types = ['res', 'com', 'ind']
  for t in types:
    bldg_strs = []
    bldgs = list(block['buildings'][t].values())
    bldgs = sorted(bldgs, key=lambda b: b['weight'])
    for build in bldgs:
      s = f"    {build['name']} (score {build['score']}, weight {build['weight']}) "
      if build['weight'] <= 40:
        s += "*"

      if 'boost_name' in build:
        s += f" <b>[{build['boost_name']} - {build['pct']}%]</b>"
      bldg_strs.append(s+"\n")
    strs.append(bldg_strs)

  pubs = []
  for pub in block['buildings']['pub'].values():
    s = f"    {pub['name']}"
    if 'boost_name' in pub:
      s += f" <b>[{pub['boost_name']} - {pub['pct']}%]</b>"
    pubs.append(s)

  return f"\
<b>{block['name']} (see on <a href='https://blocks.metroverse.com/{block['name'][7:]}'>Metroverse</a>)</b>\n\
  <p>Total Score: <b>{block['scores']['Score: Total']}</b>\n\
  <p>Residential (Score {block['scores']['Score: Residential']}):\n<ul><li>{'<li>'.join(strs[0])}</ul>\n\
  <p>Commercial (Score {block['scores']['Score: Commercial']}):\n<ul><li>{'<li>'.join(strs[1])}</ul>\n\
  <p>Industrial (Score {block['scores']['Score: Industrial']}):\n<ul><li>{'<li>'.join(strs[2])}</ul>\n\
  <p>Public:\n<ul><li>{'<li>'.join(pubs)}</ul>\n\
"

def check(block):
  total_rarity = 0
  for group in buildings:
    for b in group:
      if b in SCORES:
        score = SCORES[b][1]
        if score <= 30:
          print(f"Great find!  This block has a {b} (score {score})")
        elif score <= 50:
          print(f"Decent find! This block has a {b} (score {score})")
        total_rarity += score
  print()
  print(f"Total rarity score is **{total_rarity}** (lower is better)")


def find(blocks, bname):
  names = []
  for b in blocks:
    if bname in b['buildings']['all']:
      names.append(b['name'])
  return names

def has_building(block, building):
  for trait in block['attributes']:
    if trait['value'] == building:
      return True
  return False

def score(block):
  for trait in block['attributes']:
    if trait['trait_type'] == 'Score: Total':
      return trait['value']
  return False
  

def fetch_all(limit=10000):
  all_blocks = []
  for i in range(limit):
    b = metadata(i+1)
    if b is not None:
      all_blocks.append(b)

  return all_blocks


def compute_score(block, bmap, pmap):
  scores = defaultdict(float)
  boosts = defaultdict(int)
  for building in block['buildings']['all'].values():
    if building['type'] == 'public':
      boosts['res'] += building['res_boost']
      boosts['com'] += building['com_boost']
      boosts['ind'] += building['ind_boost']
    else:
      scores[building['type']] += building['score']

  print(scores)
  print(boosts)

  scores['residential'] = scores['residential'] * (1 + 1.0*boosts['res']/100)
  scores['commercial'] = scores['commercial'] * (1 + 1.0*boosts['com']/100)
  scores['industrial'] = scores['industrial'] * (1 + 1.0*boosts['ind']/100)

  print(scores)

#blocks = fetch_all(limit=10000)
#alljson = json.dumps(blocks, indent=2)
#print(alljson)

#blocks = read_json("data/all_blocks_slim.json")

def transform_buildings(buildings, public, boosts):
  bmap = {}
  for b in buildings:
    bmap[b['name']] = b

  pmap = {}
  for p in public:
    pmap[p['name']] = p

  for boost in boosts:
    for blg in boost['buildings']:
      if blg in bmap:
        bmap[blg]['boost_name'] = boost['name']
        bmap[blg]['pct'] = boost['pct']
      elif blg in pmap:
        pmap[blg]['boost_name'] = boost['name']
        pmap[blg]['pct'] = boost['pct']

  return (bmap, pmap)

def transform(blocks, buildings, public):
  transformed = []
  for b in blocks:
    transformed.append(transform_block(b, buildings, public))
  return transformed

def transform_block(block, buildings, public):
  # TODO: handle repeated!
  scores = {}
  bldgs = defaultdict(dict)
  for trait in block['attributes']:
    ttype = trait['trait_type']
    value = trait['value']
    if "Score" in ttype:
      scores[ttype] = value
    elif ttype == "Buildings: Residential":
      bldgs['res'][value] = buildings[value]
      bldgs['all'][value] = buildings[value]
    elif ttype == "Buildings: Commercial":
      bldgs['com'][value] = buildings[value]
      bldgs['all'][value] = buildings[value]
    elif ttype == "Buildings: Industrial":
      bldgs['ind'][value] = buildings[value]
      bldgs['all'][value] = buildings[value]
    elif ttype == "Buildings: Public":
      bldgs['pub'][value] = public[value]
      bldgs['all'][value] = public[value]

  block['scores'] = scores
  block['buildings'] = bldgs

  return block

#(blocks, buildings, public, boosts) = load_data()
#(buildings, public) = transform_buildings(buildings, public, boosts)
#blocks = transform(blocks, buildings, public)

#print(find(blocks, "Metroverse Museum"))
#printb(blocks[0])

#printb(blocks[3])
#compute_score(blocks[3], buildings, public)


#bnum = sys.argv[1]
#block = metadata(bnum)
#print_block(block)

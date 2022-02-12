import json
import os
import api.blockchain

from collections import defaultdict
from datetime import datetime

DATA_PATH = "data/"

PATHWAY_BOOSTS = [
    {
        "name": "Railway Pathway",
        "pathway": "rail",
        "pct": 4,
    },
    {
        "name": "River Pathway",
        "pathway": "river",
        "pct": 8,
    },
]


def last_stake_update():
    return datetime.fromtimestamp(os.path.getmtime(DATA_PATH + "staked.txt")).strftime("%Y-%m-%d %H:%M UTC")


def load_owners():
    file = DATA_PATH + "owners_all.json"
    last_updated = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M UTC")
    owners = api.blockchain.load(file)
    owners = api.blockchain.sorted_owners(owners)
    return owners, last_updated


def load_all():
    (blocks, buildings, public, boosts, staked) = load_data()
    (buildings, public) = transform_buildings(buildings, public, boosts)
    blocks = transform(blocks, buildings, public, boosts, staked)
    buildings_by_rarity(blocks, buildings, public)
    rank_blocks(blocks)
    return blocks, boosts, buildings, public


def load_data():
    blocks = read_json(DATA_PATH + "all_blocks_slim.json")
    buildings = read_json(DATA_PATH + "buildings_non_public.json")
    public = read_json(DATA_PATH + "buildings_public.json")
    boosts = read_json(DATA_PATH + "boosts.json")
    staked = read_staked(DATA_PATH + "staked.txt")
    return blocks, buildings, public, boosts, staked


def read_staked(path):
    with open(path, 'r') as f:
        staked = list(map(int, f.read().splitlines()))
        return staked


def read_json(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
        return data


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


def buildings_by_rarity(all_blocks, buildings, public):
    all_buildings = buildings.copy()
    all_buildings.update(public)

    counts = defaultdict(int)
    bcounts = defaultdict(int)
    for block in all_blocks:
        counted_for_block = False
        for b in block['buildings']['all']:
            counts[b] += 1
            if not counted_for_block:
                bcounts[b] += 1

    for bname in bcounts:
        all_buildings[bname]['count'] = bcounts[bname]

    sorted_buildings = sorted(all_buildings, key=lambda b: bcounts[b])
    return sorted_buildings, bcounts, counts


def compute_score(block):
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

    scores['residential'] = scores['residential'] * (1 + 1.0 * boosts['res'] / 100)
    scores['commercial'] = scores['commercial'] * (1 + 1.0 * boosts['com'] / 100)
    scores['industrial'] = scores['industrial'] * (1 + 1.0 * boosts['ind'] / 100)

    print(scores)


def transform_buildings(buildings, public, boosts):
    """
    Converts the lists of buildings into dictionaries, keyed by the
    building names.

    Also enriches each building entry with boost that it is a part of, if any.
    """
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

    return bmap, pmap


def transform(blocks, buildings, public, boosts, staked):
    transformed = []
    for b in blocks:
        transformed.append(transform_block(b, buildings, public, boosts, staked))
    return transformed


def transform_block(block, buildings, public, boosts, staked):
    # TODO: handle repeated!
    scores = {}
    bldgs = defaultdict(dict)
    for trait in block['attributes']:
        ttype = trait['trait_type']
        value = trait['value']
        if "Score" in ttype:
            scores[ttype] = value  # deprecate others
            if ttype == "Score: Total":
                scores['total'] = value
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

    pathwayx = block['entities'][0]['entity_type']['name']
    if pathwayx == 'river-x-river':
        block['pathway'] = 'river'
    elif pathwayx == 'rail-x-rail':
        block['pathway'] = 'rail'
    else:
        block['pathway'] = None

    block['num'] = int(block['name'][7:])
    block['buildings'] = bldgs
    block['scores'] = scores
    (bscore, tboost) = boosted_score([block], boosts)
    block['scores']['boosted'] = bscore
    block['scores']['pct'] = tboost
    block['staked'] = block['num'] in staked

    return block


def rank_blocks(blocks):
    block_dict = {}
    for b in blocks:
        block_dict[b['num']] = b

    sorted_blocks = sorted(blocks, key=lambda b: b['scores']['total'], reverse=True)
    for i, b in enumerate(sorted_blocks):
        block_dict[b['num']]['raw_rank'] = i + 1

    sorted_blocks = sorted(blocks, key=lambda b: b['scores']['boosted'], reverse=True)
    for i, b in enumerate(sorted_blocks):
        block_dict[b['num']]['rank'] = i + 1


# Return the boosts that these blocks qualify for (TODO: and their counts)
def total_boost(blocks, boosts):
    names = set()
    if blocks is not None:  # when is it None?
        for b in blocks:
            names.update(b['buildings']['all'].keys())

    active_bboosts = []
    for boost in boosts:
        if set(boost['buildings']).issubset(names):
            active_bboosts.append(boost)

    active_pboosts = []
    for pboost in PATHWAY_BOOSTS:
        count = 0
        for b in blocks:
            if b['pathway'] == pboost['pathway']:
                count += 1
                if count == 3:
                    # got boost!
                    active_pboosts.append(pboost)
                    break

    return active_bboosts, active_pboosts


# Return the total boosted score of these blocks.
def boosted_score(blocks, boosts):
    (bboosts, pboosts) = total_boost(blocks, boosts)
    tboost = sum([b['pct'] for b in bboosts]) + sum([b['pct'] for b in pboosts])
    raw_score = sum(map(lambda b: b['scores']['total'], blocks))
    boostedscore = round(raw_score * (1 + 1.0 * tboost / 100), 2)
    return boostedscore, tboost


def best_expansions(hood, blocks, boosts):
    # brute force: try adding every other block and calculate!
    hood_nums = [b['num'] for b in hood]
    hood_copy = hood.copy()
    hood_copy.append(None)  # optimization: pre-allocate and reuse array
    options = []
    for block in blocks:
        if block['num'] in hood_nums:
            continue
        hood_copy[-1] = block
        (new_score, new_boost) = boosted_score(hood_copy, boosts)
        options.append({'score': new_score, 'boost': new_boost, 'block': block})

    best_by_score = sorted(options, key=lambda o: (o['score'], o['boost']), reverse=True)
    best_by_boost = sorted(options, key=lambda o: (o['boost'], o['score']), reverse=True)

    return best_by_score, best_by_boost

# blocks = read_json("data/all_blocks.json")
# print(len(blocks))
# i = 0
# for block in blocks:
#    if i > 200:
#        break
#    for entity in block['entities']:
#        etype = entity['entity_type']
#        if "pathway" in etype['zone'] and "-x-" in etype['name']:
#            print(f"{block['name']}: zone: {etype['zone']} | name: {etype['name']}")
#    i += 1

# (blocks, boosts, buildings, public) = load_all()
# (byscore, byboost) = best_expansions(blocks[0:2], blocks, boosts)
# print(byscore[:2])

# print(find(blocks, 'Wildlife Waystation'))
# compute_score(blocks[3], buildings, public)

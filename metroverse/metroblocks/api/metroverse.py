import json
import os

from collections import defaultdict
from collections import Counter
from datetime import datetime

import api.data

DATA_PATH = "data/"

BOOSTS_DICT = {}
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
    owners = api.data.load(file)
    owners = sorted_owners(owners)
    return owners, last_updated


def load_all():
    (blocks, buildings, public, boosts, staked) = load_data()
    global BOOSTS_DICT
    for boost in boosts:
        BOOSTS_DICT[boost["name"]] = boost
        BOOSTS_DICT[boost["name"]]["pct"] *= 100

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


def total_boostv2(blocks, boosts):
    """Returns a dict of active boosts, where the value is the number of times the boost is active.

    For example, a return value may be { "Safety": 2, "Education": 2 }
    """
    buildings_in_hood = []
    if blocks is not None:
        for b in blocks:
            buildings_in_hood.extend(list(b['buildings']['all'].keys()))

    buildings_counter = Counter(buildings_in_hood)

    gotten = {}
    for boost in boosts:
        buildings_in_boost_counter = [buildings_counter[building] for building in boost["buildings"]]
        num_stacked_boost = min(buildings_in_boost_counter)
        if num_stacked_boost == 0:
            continue
        gotten[boost["name"]] = num_stacked_boost

    return gotten


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


def boost_formula(num_blocks, num_stacked_boost, boost_perc):
    HOOD_THRESHOLD = 10

    # What we want: if a hood has 3 stacked boosts, then,
    # if the hood has <10 blocks, the boost should stack as 1+0.5+0.5^2
    # if the hood has >10 blocks,
    spreaded_boost_multiplier = 1000 * num_stacked_boost * HOOD_THRESHOLD // max(num_blocks, HOOD_THRESHOLD)

    if spreaded_boost_multiplier >= 3000:
        spreaded_boost_multiplier = 1750
    elif spreaded_boost_multiplier >= 2000:
        spreaded_boost_multiplier = 1500 + (spreaded_boost_multiplier-2000)//4
    elif spreaded_boost_multiplier > 1000:
        spreaded_boost_multiplier = 1000 + (spreaded_boost_multiplier-1000)//2

    return boost_perc * spreaded_boost_multiplier


def boosted_scorev2(blocks, boosts):
    tboost = 0
    gotten = total_boostv2(blocks, boosts)
    for boost in gotten:
        print(f"checking {boost}")
        theoretical_boost_perc = BOOSTS_DICT[boost]['pct']
        actual_boost_perc = boost_formula(len(blocks), gotten[boost], theoretical_boost_perc)
        tboost += actual_boost_perc

    score = sum(map(lambda b: b['scores']['total'], blocks))

    boosted_score = (score * (10000 + tboost // 1000)) // 10000
    return boosted_score, tboost // 1000



# Return the total boosted score of these blocks.
def boosted_score(blocks, boosts):
    (bboosts, pboosts) = total_boost(blocks, boosts)
    tboost = sum([b['pct'] for b in bboosts]) + sum([b['pct'] for b in pboosts])
    tboost = tboost / 100
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


def sorted_owners(owners):
    sorted_keys = sorted(owners.keys(), key=lambda o: (-len(owners[o]), min(owners[o])))
    sorted_owners = [(k, sorted(list(owners[k]))) for k in sorted_keys]
    return sorted_owners


def print_owners(owners):
    total = 0
    for (owner, blocks) in sorted_owners(owners):
        print(f"{owner}: {blocks}")
        total += len(blocks)
    print(f"Found {len(owners)} distinct owners for {total} BLOCKS")


# low scores low boosts (10): 543,689,799,1996,2894,3317,4395,4691,4886,7213
# high scores low boosts (10):


# low scores with no boosts: 7213,4395,2800,2538,8411,4527,5527,9242,2542,8444
# high scores with no boosts: 6188,8565,9124,1900,3678,764,484,1677,7229,9804
# transport boost: 9977, 9979, 9983

# 20-block with 4-transport boost: 7213,4395,2800,2538,8411,4527,5527,9242,2542,8444,6188,8565,9124,1900,3678,1677,484,9977,9979,9963 => 6399
# 10-block low-end: 7213,4395,2800,2538,8411,4527,484,9242,2542,9963 => 2848
# 10-block high-end: 5527,8444,6188,8565,9124,1900,3678,1677,9977,9979 => 3523

# blocks, boosts, buildings, public = load_all()
# for block in blocks:
#     active_boosts = total_boostv2([block], boosts)
    # if any(active_boosts.values()):
    #    print(f"block {block['num']} has {active_boosts}")
#
# indeces = [168,227,282,350,484,570,764,797,806,853,917,979,1845,3665,3712,6290,9242,9922,9979,9983]
# selected = []
# for i in indeces:
#     selected.append(blocks[i-1])
# s = sorted(selected, key=lambda b: b['scores']['total'])
# print([b['num'] for b in s])

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

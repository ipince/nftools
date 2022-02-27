import json
import os

from collections import defaultdict
from collections import Counter
from datetime import datetime

from engine import data

# globals loaded later, but needed for code to "compile"
BLOCKS = None
BOOSTS = None  # List of boosts
BUILDINGS = None
PUBLIC = None

HOOD_THRESHOLD = 10
DATA_PATH = "data/"


def last_stake_update():
    return datetime.fromtimestamp(os.path.getmtime(DATA_PATH + "staked.txt")).strftime("%Y-%m-%d %H:%M UTC")


def load_owners():
    file = DATA_PATH + "owners_all.json"
    owners, last_updated = data.load(file)
    owners = sorted_owners(owners)
    return owners, last_updated


def load_all():
    print("Loading game data...")
    (blocks, buildings, public, boosts, staked) = load_data()
    global BOOSTS, BLOCKS, BUILDINGS, PUBLIC
    BOOSTS = boosts

    (buildings, public) = transform_buildings(buildings, public, boosts)
    blocks = transform(blocks, buildings, public, boosts, staked)
    rank_blocks(blocks)
    buildings_by_rarity(blocks, buildings, public)

    global BLOCKS, BUILDINGS, PUBLIC
    BLOCKS = blocks
    BUILDINGS = buildings
    PUBLIC = public


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
        for building in boost['buildings']:
            building_name = building["name"]
            if building_name in bmap:
                bmap[building_name]['boost_name'] = boost['name']
                bmap[building_name]['pct'] = boost['pct']
            elif building_name in pmap:
                pmap[building_name]['boost_name'] = boost['name']
                pmap[building_name]['pct'] = boost['pct']

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
        block['pathway'] = "Double River"
    elif pathwayx == 'rail-x-rail':
        block['pathway'] = "Double Rail"
    else:
        block['pathway'] = None

    block['num'] = int(block['name'][7:])
    block['buildings'] = bldgs
    block['scores'] = scores
    (bscore, tboost) = hood_boost([block])
    block['scores']['boosted'] = bscore
    block['scores']['pct'] = tboost/100
    block['staked'] = block['num'] in staked

    return block


# TODO: how is this being used? wtf
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


def active_boosts(blocks):
    """Returns a dict of active boosts, where the value is the number of times the boost is active.

    For example, a return value may be:
    {
        "Safety": { "full": 2, "partial": 1 },
        "Education": { "full": 1, "partial": 0 },
    }
    """
    buildings_in_hood = []
    if blocks is not None:
        for b in blocks:
            buildings_in_hood.extend(list(b['buildings']['all'].keys()))
            buildings_in_hood.append(b["pathway"])

    building_counts = Counter(buildings_in_hood)  # e.g. {"Hospital": 3}

    actives = {}
    for boost in BOOSTS:
        building_stacks = [building_counts[building["name"]] // building["count"]
                           for building in boost["buildings"] if building["count"] > 0]
        num_stacked_boost = min(building_stacks)  # looks like [2, 1, 0]

        remainders = [building_counts[building["name"]] - num_stacked_boost * building["count"]
                      for building in boost["buildings"] if building["count"] > 0]

        if len(remainders) == 1:  # assumption: only 1 building has count > 1
            partial = remainders[0]
        else:
            partial = sum(1 if count >= 1 else 0 for count in remainders)

        actives[boost["name"]] = {
            "full": num_stacked_boost,
            "partial": partial,
        }

    return actives


def large_hood_multiplier(num_blocks):
    return 1000 * HOOD_THRESHOLD // max(num_blocks, HOOD_THRESHOLD)


def boost_formula(num_blocks, num_stacked_boost):
    """Diminishing returns"""
    # What we want: if a hood has 3 stacked boosts, then,
    # if the hood has <10 blocks, the boost should stack as 1+0.5+0.5^2
    # if the hood has >10 blocks,
    stacked_boost_multiplier = num_stacked_boost * large_hood_multiplier(num_blocks)

    if stacked_boost_multiplier >= 3000:
        stacked_boost_multiplier = 1750
    elif stacked_boost_multiplier >= 2000:
        stacked_boost_multiplier = 1500 + (stacked_boost_multiplier-2000)//4
    elif stacked_boost_multiplier > 1000:
        stacked_boost_multiplier = 1000 + (stacked_boost_multiplier-1000)//2

    return stacked_boost_multiplier


def hood_boost(blocks):
    tboost = 0
    actives = active_boosts(blocks)
    for boost_name in actives:
        for candidate in BOOSTS:  # TODO: use a dict instead
            if candidate["name"] == boost_name:
                theoretical_boost_perc = candidate["bps"]
                actual_boost_perc = boost_formula(len(blocks), actives[boost_name]["full"]) * theoretical_boost_perc
                tboost += actual_boost_perc

    score = sum(map(lambda b: b['scores']['total'], blocks))

    boosted_score = (score * (10000 + tboost // 1000)) // 10000
    return boosted_score, tboost // 1000


def best_expansions(hood):
    """Returns two sorted lists containing the best expansions for a hood.

    "Best" is subjective. This function returns the best single new block
    to expand the hood with. The first list optimizes by score, and the
    second one optimizes by boost.

    If you want to add more than 1 block, calling this function repeatedly
    might not yield the best-optimized hood (i.e. optimization is not greedy).

    Each of the resulting lists looks like this:
        [ { "score": 1400, "boost": 750 (bps), "block": <Full Block> } ]
    """
    # brute force: try adding every other block and calculate!
    hood_nums = [b['num'] for b in hood]
    hood_copy = hood.copy()
    hood_copy.append(None)  # optimization: pre-allocate and reuse array
    options = []
    for block in BLOCKS:
        if block['num'] in hood_nums:
            continue
        hood_copy[-1] = block
        (new_score, new_boost) = hood_boost(hood_copy)
        options.append({'score': new_score, 'boost': new_boost, 'block': block})

    best_by_score = sorted(options, key=lambda o: (o['score'], o['boost']), reverse=True)
    best_by_boost = sorted(options, key=lambda o: (o['boost'], o['score']), reverse=True)

    return best_by_score, best_by_boost


def sorted_owners(owners):
    """Return the owners list ordered by number of blocks, and then min block #"""
    sorted_keys = sorted(owners.keys(), key=lambda o: (-len(owners[o]), min(owners[o])))
    sorted_owners = [(k, sorted(list(owners[k]))) for k in sorted_keys]
    return sorted_owners


def print_owners(owners):
    total = 0
    for (owner, blocks) in sorted_owners(owners):
        print(f"{owner}: {blocks}")
        total += len(blocks)
    print(f"Found {len(owners)} distinct owners for {total} BLOCKS")


# Load the game data needed for this module.
load_all()


# Unused, but useful stuff below
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

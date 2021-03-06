from engine import blockchain
from engine import data
from engine import metroverse as mv


def update_hoods_metadata(refresh_owners=False):
    if refresh_owners:
        print("Refreshing ownership data from the blockchain")
        blockchain.get_all_owners()
    print("Reading owner data")
    owners = data.load_owners()

    print("Calculating hood size/score/boost")
    hoods = {}
    for owner, indeces in owners.items():
        hood_blocks = list(filter(lambda b: b['num'] in indeces, mv.BLOCKS))
        tscore, tboost = mv.hood_boost(hood_blocks)

        hoods[owner] = {}
        hoods[owner]['blocks'] = indeces
        hoods[owner]['size'] = len(indeces)
        hoods[owner]['blocks'] = indeces
        hoods[owner]['score'] = tscore
        hoods[owner]['boost'] = tboost / 100

    # Calculate global score rank
    print("Calculating global score ranks")
    byscore = sorted(owners.keys(), key=lambda o: hoods[o]['score'], reverse=True)
    i = 1
    for o in byscore:
        hoods[o]['score_rank'] = i
        i += 1

    # Calculate global boost rank
    print("Calculating global boost ranks")
    byboost = sorted(owners.keys(), key=lambda o: hoods[o]['boost'], reverse=True)
    i = 1
    for o in byboost:
        hoods[o]['boost_rank'] = i
        i += 1

    # Calculate boost rank within same size hoods
    print("Calculating per-size boost ranks")
    byboost = sorted(owners.keys(), key=lambda o: (hoods[o]['size'], hoods[o]['boost']), reverse=True)
    last_size = None
    for o in byboost:
        if last_size != hoods[o]['size']:  # New size, reset rankings
            i = 1
            j = 0
        elif last_boost > hoods[o]['boost']:  # Diff boost, increase ranking
            i += 1 + j
            j = 0
        else:  # Same boost, keep ranking, increase next jump.
            j += 1
        hoods[o]['boost_rank_in_size'] = i
        last_size = hoods[o]['size']
        last_boost = hoods[o]['boost']

    data.save_hoods(hoods)


if __name__ == "__main__":
    update_hoods_metadata(refresh_owners=False)
    # blockchain.refresh_staked_blocks()

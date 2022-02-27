from engine import metroverse as mv


def blocks_from_indeces(indeces, all_blocks=None):
    if not all_blocks:
        collection = mv.BLOCKS
    return list(filter(lambda b: b['num'] in indeces, collection))


def all_blocks():
    # Maybe transform these in order to hide the internal and external object.
    return mv.BLOCKS


def hood(blocknums):
    """Returns the Hood formed by the block numbers passed in.

    The Hood includes the total scores, as well as information about all the
    hood boosts that are active.
    """
    # TODO: validate?
    blocks = blocks_from_indeces(blocknums)

    lhm = mv.large_hood_multiplier(len(blocknums))
    active_boosts = mv.active_boosts(blocks)

    # TODO: note, this is re-doing the same work. Make it more efficient.
    boosted_score, total_boost = mv.hood_boost(blocks)

    boosts = []
    for bboost in mv.BOOSTS:
        stacked = active_boosts[bboost['name']]["full"]
        partial = active_boosts[bboost['name']]["partial"]
        adjusted_stack = stacked * lhm
        stacked_boost_multiplier = mv.boost_formula(len(blocks), stacked)
        earned_boost_bps = (stacked_boost_multiplier * bboost['bps'])//1000  # undo multiplier
        boosts.append({
            "name": bboost["name"],
            "base_boost_bps": bboost["bps"],
            "num_stacked": stacked,
            "progress_to_next_stack": partial,
            "adjusted_num_stacked": adjusted_stack,
            "stacked_boost_multiplier": stacked_boost_multiplier,
            "earned_boost_bps": earned_boost_bps,
        })

    data = {
        "raw_score": sum([b["scores"]["total"] for b in blocks]),
        "boosted_score": boosted_score,
        "earned_boost_bps": total_boost,
        "blocks": [{"num": i, "collection": "genesis"} for i in blocknums],
        "boosts": boosts,
        "large_hood_multiplier": lhm,
    }
    return data


# TODO: implement proper pagination
def hood_expansions(blocknums, exclude_staked=False, limit=100):
    blocks = blocks_from_indeces(blocknums)
    (byscore, byboost) = mv.best_expansions(blocks)

    # Apply limits
    byscore = byscore[:limit]
    byboost = byboost[:limit]

    # No need to export all info about a block, so minimize here.
    for expansions in [byscore, byboost]:
        for entry in expansions:
            entry["block"] = {
                "num": entry["block"]["num"],
                "name": entry["block"]["name"],
                "staked": entry["block"]["staked"],
            }

    data = {
        "by_score": byscore,
        "by_boost": byboost,
    }

    return data

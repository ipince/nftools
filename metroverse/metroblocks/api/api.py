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
    active_bboosts = mv.active_boosts(blocks)
    active_pboosts = mv.get_active_pathway_boosts(blocks)  # TODO

    # TODO: note, this is re-doing the same work. Make it more efficient.
    boosted_score, total_boost = mv.hood_boost(blocks)

    boosts = []
    # TODO: merge with pathway boosts
    for bboost in mv.BOOSTS:
        stacked = active_bboosts[bboost['name']] if bboost['name'] in active_bboosts else 0
        adjusted_stack = stacked * lhm
        stacked_boost_multipler = mv.boost_formula(len(blocks), stacked)
        earned_boost_bps = (stacked_boost_multipler * bboost['pct'])//1000  # undo multiplier
        boosts.append({
            "name": bboost["name"],
            "base_boost_bps": bboost["pct"],
            "num_stacked": stacked,
            "progress_to_next_stack": 0,  # TODO: implement
            "adjusted_num_stacked": adjusted_stack,
            "stacked_boost_multiplier": stacked_boost_multipler,
            "earned_boost_bps": earned_boost_bps,
        })
    for pboost_name, pboost in mv.PATHWAY_BOOSTS.items():
        stacked = active_pboosts[pboost['name']] if pboost['name'] in active_pboosts else 0
        adjusted_stack = stacked * lhm
        stacked_boost_multipler = mv.boost_formula(len(blocks), stacked)
        earned_boost_bps = (stacked_boost_multipler * pboost['pct'])//1000  # undo multiplier
        boosts.append({
            "name": pboost_name,
            "base_boost_bps": pboost["pct"],
            "num_stacked": stacked,
            "progress_to_next_stack": 0,  # TODO: implement
            "adjusted_num_stacked": adjusted_stack,
            "stacked_boost_multiplier": stacked_boost_multipler,
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

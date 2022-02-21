from . import metroverse as mv
import json


def blocks_from_indeces(indeces, all_blocks):
    return list(filter(lambda b: b['num'] in indeces, all_blocks))


def hood(blocknums):
    blocks = blocks_from_indeces(blocknums, mv.BLOCKS)

    lhm = mv.large_hood_multiplier(len(blocknums))
    active_bboosts = mv.total_boostv2(blocks, mv.BOOSTS)
    active_pboosts = mv.get_active_pathway_boosts(blocks)  # TODO

    # TODO: note, this is re-doing the same work. Make it more efficient.
    boosted_score, total_boost = mv.boosted_scorev2(blocks, mv.BOOSTS)

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
            "large_hood_multiplier": lhm,
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
            "large_hood_multiplier": lhm,
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
    }
    return as_json(data)


def as_json(object):
    return json.dumps(object, indent=2)

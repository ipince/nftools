import traceback

# TODO: replace with api import
from engine import metroverse as mv
from api import api

from . import blocks as blockspage
from . import boost
from . import content
from . import util


def hood(blocks=None):
    """Renders the Hood Simulator page"""
    if blocks is None or blocks == "":
        return content.with_body(HOOD_LANDING, 'hoods')
    try:
        # TODO: Validate input
        indeces = list(map(lambda s: int(s.strip()), blocks.split(",")))
        if len(indeces) > 120:
            return content.with_body("Please limit your input to 120 blocks", 'hoods')

        blocks = api.blocks_from_indeces(indeces)
        hood_data = api.hood(indeces)

        boosted_score = hood_data["boosted_score"]
        tboost = hood_data["earned_boost_bps"]
        score = hood_data["raw_score"]
        lhm = hood_data["large_hood_multiplier"]

        last_stake_update = mv.last_stake_update()

        # Title
        names = [b['name'] for b in blocks]
        body = f"""
        <h1>Hood Simulator</h1>
        <p>Analyzing hood with {len(blocks)} block(s): {', '.join(names)}.
        <p>Your total hood boost is <span style="font-size: 18"><b>{tboost/100}%</b></span>.
        <p>This hood would produce <b><span style="font-size: 16">{score}<span></b> MET per day without boosting,
        and <b><span style="font-size: 16">{boosted_score}</span></b> MET per day with boosting.
        """
        if len(blocks) > 10:
            body += f"""
            <p><em>NOTE</em>: Because your hood is larger than 10 blocks, you have a large hood
            multiplier of <b>{lhm/1000}</b> (calculated as <code>10/number_of_blocks</code>).
            <br/>Please note that you will <b>not</b> be better off splitting your hood into smaller hoods.
            Try it out and see for yourself :)
            """

        # Boost table
        body += f"""
        <div>{boost.render_boosts(blocks, highlight=True, render_stacked=True)}</div>
        <div>{boost.render_pathway_boosts(blocks)}</div>
        """

        # Expansions
        (byscore, byboost) = mv.best_expansions(blocks, mv.BLOCKS, mv.BOOSTS)
        body += render_expansions(indeces, byscore, byboost, boosted_score, last_stake_update)

        # Blocks
        for b in blocks:
            body += f"<div class='row'>{blockspage.render_block(b)}</div>"
        return content.with_body(body, 'hoods')

    except Exception as e:
        traceback.print_exc()
        return content.with_body(
            "Failed to understand input. Please use comma-separated list of block numbers, like this: <code><a href='/hood/1,2,3'>1,2,3</a></code>",
            'hoods')


def render_expansions(indeces, byscore, byboost, boosted_score, last_stake_update):
    body = """
    <h2>Expansions</h2>
    This is an ordered list of which blocks will best expand your current hood. We consider two
    ways to optimize: by score and by boost. If you only optimize by score, then the list will
    most likely be topped by blocks that have a large total score. But there might be some great blocks
    with a lower total score that may add a lot to your particular neighborhood by unlocking boosts.
    <p>If you're only going to add one block, you probably
    want to optimize by score. If you're going to add multiple blocks, then you might be better
    off optimizing by boost.
    <p>
    <div class="row">
    """
    # By score
    body += f"""
    <div class="column"><h3>By Score (top 100)</h3>
    <table>
    <tr><th>Block</th><th>Staked?<br><small>as of {last_stake_update}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
    """
    for i in range(100):
        delta = util.fmt_score(byscore[i]['score'] - boosted_score)
        expand = f"/hood/{','.join(map(str, indeces + [byscore[i]['block']['num']]))}"
        staked = 'Yes' if byscore[i]['block'][
            'staked'] else f"No (<a href={util.opensea(byscore[i]['block'])}>OpenSea</a>)"
        body += f"""
        <tr><td><a href="/b/{byscore[i]['block']['num']}">{byscore[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
        <td>{staked}</td>
        <td>{byscore[i]['boost'] / 100}%</td>
        <td>{util.fmt_score(byscore[i]['score'])}</td>
        <td>{delta}</td></tr>"""
    body += """
    </table></div>
    """
    # By boost
    body += f"""
    <div class="column"><h3>By Boost (top 100)</h3><table>
    <tr><th>Block</th><th>Staked?<br><small>as of {last_stake_update}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
    """
    for i in range(100):
        delta = util.fmt_score(byscore[i]['score'] - boosted_score)
        expand = f"/hood/{','.join(map(str, indeces + [byboost[i]['block']['num']]))}"
        staked = 'Yes' if byboost[i]['block'][
            'staked'] else f"No (<a href={util.opensea(byboost[i]['block'])}>OpenSea</a>)"
        body += f"""
        <tr><td><a href="/b/{byboost[i]['block']['num']}">{byboost[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
        <td>{staked}</td>
        <td>{byboost[i]['boost'] / 100}%</td>
        <td>{util.fmt_score(byboost[i]['score'])}</td>
        <td>{delta}</td></tr>"""

    body += """
    </table></div>
    </div>
    <p>
    """

    return body


HOOD_LANDING = """
<h1>Hood Simulator</h1>
The Hood Simulator lets you check which neighborhood boosts you would get if you were to stake a set of blocks. Try it out with an example: <a href="/hood/1,2,3">1,2,3</a>.
"""

import traceback

from . import boost
from . import content
from . import util

from engine import metroverse as mv

instructions = '''
<h1>Block Explorer</h1>
Welcome to the block explorer. This is a simple web service to view Metaverse block information.<br />

<p>Just append <code>b/</code> and a block number to the URL (for example: <code><a href="/b/1">/b/1</a></code>) to view a block's info at a glance.
'''


def index():
    return content.with_body(instructions, 'blocks')


def block(block_number):
    """Render the Block page"""
    try:
        idx = int(block_number)
        block = mv.BLOCKS[idx - 1]
        body = f"""
        <div class="row">
            <div class="column">{render_block(block)}</div>
            <div class="column">{boost.render_boosts([block])}</div>
        </div>
        """
        return content.with_body(body, 'blocks')
    except Exception:
        traceback.print_exc()
        return content.with_body("Please enter a block number between 1 and 10000", 'blocks')


def render_block(block):
    strs = []
    types = ['res', 'com', 'ind']
    for t in types:
        bldg_strs = []
        bldgs = list(block['buildings'][t].values())
        bldgs = sorted(bldgs, key=lambda b: b['weight'])
        for build in bldgs:
            s = f"        {build['name']} (score {build['score']}, weight {build['weight']}) "

            if 'boost_name' in build:
                s += f" <b>[{build['boost_name']} - {build['pct']//100}%]</b>"
            bldg_strs.append(s + "\n")
        strs.append(bldg_strs)

    pubs = []
    for pub in block['buildings']['pub'].values():
        s = f"        {pub['name']}"
        if 'boost_name' in pub:
            s += f" <b>[{pub['boost_name']} - {pub['pct']//100}%]</b>"
        pubs.append(s)

    bnum = block['num']
    pathway_emoji = "🚆" if block['pathway'] == ['rail'] else ("🚢" if block['pathway'] == 'river' else "")
    return f"""
<div>
<h1 style="margin-bottom: 0"><a id="{block['num']}">{block['name']}</a> (<a href="/ranks">rank</a> {block['rank']}/10000)</h1>
<small>(view on <a href='https://blocks.metroverse.com/{bnum}'>Metroverse</a>; view on <a href={util.opensea(block)}>OpenSea</a>; this block is {"" if block['staked'] else "<b>not</b>"} staked as of {mv.last_stake_update()})
</small>

<p>Total Score: <b>{block['scores']['Score: Total']}</b>
<p>Pathway Boost (2 of same kind): {block['pathway']} {pathway_emoji}
<p>Residential (Score {block['scores']['Score: Residential']}):
    <ul><li>{'<li>'.join(strs[0])}</ul>
<p>Commercial (Score {block['scores']['Score: Commercial']}):
    <ul><li>{'<li>'.join(strs[1])}</ul>
<p>Industrial (Score {block['scores']['Score: Industrial']}):
    <ul><li>{'<li>'.join(strs[2])}</ul>
<p>Public:
    <ul><li>{'<li>'.join(pubs)}</ul>
</div>
"""


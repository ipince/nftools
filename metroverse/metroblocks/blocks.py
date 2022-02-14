import content
import api.metroverse as mv
import traceback

from api import data

instructions = '''
<h1>Block Explorer</h1>
Welcome to the block explorer. This is a simple web service to view Metaverse block information.<br />

<p>Just append <code>b/</code> and a block number to the URL (for example: <code><a href="/b/1">/b/1</a></code>) to view a block's info at a glance.
'''

hood_instructions = """
<h1>Hood Simulator</h1>
The Hood Simulator lets you check which neighborhood boosts you would get if you were to stake a set of blocks. Try it out with an example: <a href="/hood/1,2,3">1,2,3</a>.
"""


def index():
    return content.with_body(instructions, 'blocks')


def get_block(block_number):
    try:
        idx = int(block_number)
        block = BLOCKS[idx - 1]
        body = f"""
        <div class="row">
            <div class="column">{render_block(block)}</div>
            <div class="column">{render_boosts([block])}</div>
        </div>
        """
        return content.with_body(body, 'blocks')
    except Exception:
        traceback.print_exc()
        return content.with_body("Please enter a block number between 1 and 10000", 'blocks')


def hood(blocks=None):
    if blocks is None or blocks == "":
        return content.with_body(hood_instructions, 'hoods')
    try:
        indeces = list(map(lambda s: int(s.strip()), blocks.split(",")))
        if len(indeces) > 120:
            return content.with_body("Please limit your input to 120 blocks", 'hoods')
        blocks = list(filter(lambda b: b['num'] in indeces, BLOCKS))

        boosted_score, tboost = mv.boosted_scorev2(blocks, BOOSTS)
        score = sum(map(lambda b: b['scores']['total'], blocks))

        # Find best expansions:
        (byscore, byboost) = mv.best_expansions(blocks, BLOCKS, BOOSTS)

        # Boost table
        names = [b['name'] for b in blocks]
        body = f"""
        <h1>Hood Simulator</h1>
        <p>Analyzing hood with {len(blocks)} block(s): {', '.join(names)}.
        <p>Your total hood boost is <span style="font-size: 18"><b>{tboost/100}%</b></span>.
        <p>This hood would produce <b><span style="font-size: 16">{score}<span></b> MET per day without boosting, and <b><span style="font-size: 16">{boosted_score}</span></b> MET per day with boosting.
        """
        if len(blocks) > 10:
            lhm = mv.large_hood_multiplier(len(blocks))
            body += f"""
            <p><em>NOTE</em>: Because your hood is larger than 10 blocks, you have a large hood
            multiplier of <b>{lhm/1000}</b> (calculated as <code>10/number_of_blocks</code>).
            <br/>Please note that you will <b>not</b> be better off splitting your hood into smaller hoods.
            Try it out and see for yourself :)
            """

        body += f"""
        <div>{render_boosts(blocks, highlight=True, render_stacked=True)}</div>
        <div>{render_pathway_boosts(blocks)}</div>
        """

        # Expansions
        body += """
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
        <tr><th>Block</th><th>Staked?<br><small>as of {mv.last_stake_update()}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
        """
        for i in range(100):
            delta = fmt_score(byscore[i]['score'] - boosted_score)
            expand = f"/hood/{','.join(map(str, indeces + [byscore[i]['block']['num']]))}"
            staked = 'Yes' if byscore[i]['block'][
                'staked'] else f"No (<a href={opensea(byscore[i]['block'])}>OpenSea</a>)"
            body += f"""
            <tr><td><a href="/b/{byscore[i]['block']['num']}">{byscore[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
            <td>{staked}</td>
            <td>{byscore[i]['boost']/100}%</td>
            <td>{fmt_score(byscore[i]['score'])}</td>
            <td>{delta}</td></tr>"""
        body += """
        </table></div>
        """
        # By boost
        body += f"""
        <div class="column"><h3>By Boost (top 100)</h3><table>
        <tr><th>Block</th><th>Staked?<br><small>as of {mv.last_stake_update()}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
        """
        for i in range(100):
            delta = fmt_score(byscore[i]['score'] - boosted_score)
            expand = f"/hood/{','.join(map(str, indeces + [byboost[i]['block']['num']]))}"
            staked = 'Yes' if byboost[i]['block'][
                'staked'] else f"No (<a href={opensea(byboost[i]['block'])}>OpenSea</a>)"
            body += f"""
            <tr><td><a href="/b/{byboost[i]['block']['num']}">{byboost[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
            <td>{staked}</td>
            <td>{byboost[i]['boost']/100}%</td>
            <td>{fmt_score(byboost[i]['score'])}</td>
            <td>{delta}</td></tr>"""

        body += """
        </table></div>
        </div>
        <p>
        """

        # Blocks
        for b in blocks:
            body += f"<div class='row'>{render_block(b)}</div>"
        return content.with_body(body, 'hoods')
    except Exception as e:
        traceback.print_exc()
        return content.with_body(
            "Failed to understand input. Please use comma-separated list of block numbers, like this: <code><a href='/hood/1,2,3'>1,2,3</a></code>",
            'hoods')


def owners():
    hoods, last_updated = data.load("data/hoods.json")  # TODO: load once into memory
    sorted_owners = sorted(hoods.keys(),
                           key=lambda o: (hoods[o]['size'], -hoods[o]['boost_rank_in_size'], -min(hoods[o]['blocks'])),
                           reverse=True)
    body = f"""
    <h1>Owners (aka Whale Watch)</h1>
    <p>This is a list of all block owners, <em>including owners of staked blocks</em>, as of <b>{last_updated}</b>.
    <p>In total, there are <b>{len(hoods)}</b> <em>true</em> distinct owners.
    <p>
    <table style="table-layout: fixed; overflow: scroll; width: 100%">
    <tr>
    <th style='width: 5%'>Rank<br/><small style="font-weight: normal">(by total score)</small></th>
    <th style='width: 30%'>Address</th>
    <th style='width: 50%'>Hood</th>
    <th style='width: 5%'>Daily MET</th>
    <th style='width: 5%'>Hood Boost</th>
    <th style='width: 5%'>Boost Rank<br/><small style="font-weight: normal">(within hoods of same size)</small></th>
    </tr>
    """
    for owner in sorted_owners:
        hood = hoods[owner]
        blockstrs = [str(b) for b in sorted(hood['blocks'])]
        hrefs = [f"<a href='/b/{b}'>#{b}</a>" for b in blockstrs]
        emoji = ""
        if hood['size'] >= 30:
            emoji = "🐋 "
        body += f"<tr><td>{hood['score_rank']}</td>"
        body += f"<td style='overflow: scroll'>{emoji}{KNOWN[owner] if owner in KNOWN else owner} ({hood['size']})<br/>"
        body += f"<a target='_blank' href='{opensea_profile(owner)}'>OpenSea</a> | "
        body += f"<a target='_blank' href='https://etherscan.io/address/{owner}'>Etherscan</a> | "
        body += f"see <a target='_blank' href='/hood/{','.join(blockstrs)}'>Hood</a></td>"
        body += f"<td>{', '.join(hrefs)}</td>"
        body += f"<td>{hood['score']}</td>"
        body += f"<td>{hood['boost']}%</td>"
        body += f"<td>{hood['boost_rank_in_size']}</td>"
        body += "</tr>"
    body += "</table>"

    return content.with_body(body, 'owners')


def fmt_score(score):
    return "{:.0f}".format(score)


def buildings():
    body = """
    <h1>Buildings</h1>
    <p>Curious about which buildings are most rare? Ask no more!
    <p>
    <table>
    """
    # TODO: pre-compute this. add type. fix total counts.
    (buildings, bcounts, counts) = mv.buildings_by_rarity(BLOCKS, BUILDINGS, PUBLIC)
    body += "<tr><th>Building Name</th><th>Number of Blocks that have it</th></tr>"
    for b in buildings:
        body += "<tr>"
        body += f"<td>{b}</td><td>{bcounts[b]}</td>"  # <td>{counts[b]}</td>"
        body += "</tr>"

    body += "</table>"

    return content.with_body(body, 'buildings')


def render_block_list(title, blocks):
    """Renders a table of blocks with just the block name (and link)"""
    body = f"""<p>{title} ({len(blocks)})</p>
    <table>
    <tr><th>Block</th></tr>
    """
    for block in blocks:
        body += f"<tr><td><a href='/b/{block['num']}'>{block['name']}</a></td></tr>"
    body += "</table>"
    return body


def pathways():
    double_river = [b for b in BLOCKS if b['pathway'] == 'river']
    double_rail = [b for b in BLOCKS if b['pathway'] == 'rail']
    body = f"""
    <h1>Pathways</h1>
    <p>Curious about which blocks have double river or double rail? Here you go!
    <p>
    <div class="row">
        <div class="column">{render_block_list("Blocks with Double River", double_river)}</div>
        <div class="column">{render_block_list("Blocks with Double Rail", double_rail)}</div>
    </div>
    """

    return content.with_body(body, 'pathways')


def ranks():
    body = """<h1>Block Ranks</h1>

    <p>Note, these are calculated based on the MET-producing power, not on rarity. <br/>
    Also, I chose to use the "boosted" rank as the rank because that will be the true MET-producing power of the block once boosts are actually implemented.
    <p>
    <table>
    """
    sorted_blocks = sorted(BLOCKS, key=lambda b: b['rank'])
    body += f"<tr><th>Block Name</th><th>Staked?<br><small>as of {mv.last_stake_update()}</small></th><th>Score (unboosted)</th><th>Rank (of unboosted score)</th><th>Boost (pct)</th><th>Score (boosted)</th><th style='background: darkseagreen'>Rank (of boosted score)</th></tr>"
    for b in sorted_blocks:
        body += f"""
        <tr><td><a href='b/{b['num']}'>{b['name']}</a> (<a href={opensea(b)}>OpenSea</a>)</td>
        <td>{'Yes' if b['staked'] else 'No'}</td>
        <td>{b['scores']['total']}</td>
        <td>{b['raw_rank']}</td>
        <td>{b['scores']['pct']/100}%</td>
        <td>{b['scores']['boosted']}</td>
        <td>{b['rank']}</td></tr>
        """

    body += "</table>"
    return content.with_body(body, 'ranks')


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
<small>(view on <a href='https://blocks.metroverse.com/{bnum}'>Metroverse</a>; view on <a href={opensea(block)}>OpenSea</a>; this block is {"" if block['staked'] else "<b>not</b>"} staked as of {mv.last_stake_update()})
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


def opensea_profile(address):
    return f"https://opensea.io/{address}"


def opensea(block):
    return f"https://opensea.io/assets/0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f/{block['num']}"


def render_boosts(blocks=None, highlight=False, render_stacked=False):
    active_bboosts = mv.total_boostv2(blocks, BOOSTS)

    names = set()
    if blocks is not None:
        for b in blocks:
            names.update(b['buildings']['all'].keys())
    s = """
    <h2 style="margin-bottom: 2">Building Boosts</h2>
    <small>(reference <a href='https://docs.metroverse.com/overview/neighborhood-boost#list-of-neighborhood-boosts'>docs</a>)</small>
    <p>
    <table>
    """
    s += """<tr>
    <th>Name</th>
    <th>Boost % (base)</th>
    <th>Building 1</th>
    <th>Building 2</th>
    <th>Building 3</th>
    """
    if render_stacked:
        s += """
        <th>Stacked boosts</th>
        <th>Total Boost %<br><small style="font-weight: normal">(includes large hood multiplier)</small></th>
        """
    s += "</tr>"

    for boost in BOOSTS:
        s += f"<tr><td>{boost['name']}</td>"
        s += f"<td>{boost['pct']//100}%</td>"

        for b in boost['buildings']:
            # which blocks have building b?
            blocks_with_b = [block for block in blocks if b in block['buildings']['all']]
            count = 0
            if b in BUILDINGS:
                count = BUILDINGS[b]['count']
            else:
                count = PUBLIC[b]['count']
            pct = 100.0*count/10000
            if len(blocks_with_b) > 0:
                # TODO: move to highlight_if
                s += f"""<td style='background: darkseagreen'>{b} ({pct}%)<br/>"""
                for block in blocks_with_b:
                    if highlight:
                        s += f""" <a href="#{block['num']}">#{block['num']}</a>"""
                s += "</td>"
            else:
                s += f"<td>{b} ({pct}%)</td>"

        if render_stacked:
            stacked = active_bboosts[boost['name']] if boost['name'] in active_bboosts else 0
            s += f"<td {highlight_if(stacked>0)}>{stacked}</td>"

            total_boost = mv.boost_formula(len(blocks), stacked, boost['pct'])//1000/100
            s += f"<td {highlight_if(total_boost>0)}>{total_boost}%</td>"

        s += "</tr>"
    #        s += f"<li><b>{b['name']} ({b['pct']}%):</b> {', '.join(b['buildings'])}</li>"
    return s + "</table>"


def highlight_if(condition):
    HIGHLIGHT_COLOR = "darkseagreen"
    if condition:
        return f"style='background: {HIGHLIGHT_COLOR}'"
    return ""


def render_pathway_boosts(blocks):
    pboosts = mv.get_active_pathway_boosts(blocks)
    pboosts_names = pboosts.keys()
    s = """
    <h2 style="margin-bottom: 2">Pathway Boosts</h2>
    <small>(reference <a href='https://docs.metroverse.com/overview/pathway-boost#pathway-boost'>docs</a>)</small>
    <p><table>
    <tr><th>Name</th>
    <th>Boost % (base)</th>
    <th>Blocks with 2 of same kind</th>
    <th>Stacked boosts</th>
    <th>Total Boost %<br><small style="font-weight: normal">(includes large hood multiplier)</small></th>
    </tr>
    """
    for pboost in mv.PATHWAY_BOOSTS.values():
        some = False

        # Boost name and %
        s += f"<tr><td>{pboost['name']}</td>"
        s += f"<td>{pboost['pct']//100}%</td>"

        # Buildings
        if pboost['name'] in pboosts_names:
            s += "<td style='background: darkseagreen'>"
        else:
            s += "<td>"
        for block in blocks:
            if block['pathway'] == pboost['pathway']:
                some = True
                s += f"""<a href="#{block['num']}">#{block['num']}</a>    """
        if not some:
            s += "None :("
        s += "</td>"

        # Stacked
        stacked = pboosts[pboost['name']] if pboost['name'] in pboosts else 0
        s += f"<td {highlight_if(stacked > 0)}>{stacked}</td>"

        # Total boost
        total_boost = mv.boost_formula(len(blocks), stacked, pboost['pct']) // 1000 / 100
        s += f"<td {highlight_if(total_boost > 0)}>{total_boost}%</td>"

        s += "</tr>"

    s += "</table>"
    return s


(BLOCKS, BOOSTS, BUILDINGS, PUBLIC) = mv.load_all()
KNOWN = mv.read_json('data/known.json')
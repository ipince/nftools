from . import content
from . import util

from engine import metroverse as mv


def ranks():
    body = """<h1>Block Ranks</h1>

    <p>Note, these are calculated based on the MET-producing power, not on rarity. <br/>
    Also, I chose to use the "boosted" rank as the rank because that will be the true MET-producing power of the block once boosts are actually implemented.
    <p>
    <table>
    """
    sorted_blocks = sorted(mv.BLOCKS, key=lambda b: b['rank'])
    body += f"<tr><th>Block Name</th><th>Staked?<br><small>as of {mv.last_stake_update()}</small></th><th>Score (unboosted)</th><th>Rank (of unboosted score)</th><th>Boost (pct)</th><th>Score (boosted)</th><th style='background: darkseagreen'>Rank (of boosted score)</th></tr>"
    for b in sorted_blocks:
        body += f"""
        <tr><td><a href='b/{b['num']}'>{b['name']}</a> (<a href={util.opensea(b)}>OpenSea</a>)</td>
        <td>{'Yes' if b['staked'] else 'No'}</td>
        <td>{b['scores']['total']}</td>
        <td>{b['raw_rank']}</td>
        <td>{b['scores']['pct']/100}%</td>
        <td>{b['scores']['boosted']}</td>
        <td>{b['rank']}</td></tr>
        """

    body += "</table>"
    return content.with_body(body, 'ranks')

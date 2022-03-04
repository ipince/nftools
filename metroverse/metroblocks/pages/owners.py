from . import content
from . import util

from engine import data
from engine import metroverse as mv


def owners():
    hoods, last_updated = data.load("data/hoods.json")  # TODO: load once into memory
    sorted_owners = sorted(hoods.keys(),
                           key=lambda o: (hoods[o]['size'], -hoods[o]['boost_rank_in_size'], -hoods[o]['score_rank']),
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
        body += f"<a target='_blank' href='{util.opensea_profile(owner)}'>OpenSea</a> | "
        body += f"<a target='_blank' href='https://etherscan.io/address/{owner}'>Etherscan</a> | "
        body += f"see <a target='_blank' href='/hood/{','.join(blockstrs)}'>Hood</a></td>"
        body += f"<td>{', '.join(hrefs)}</td>"
        body += f"<td>{hood['score']}</td>"
        body += f"<td>{hood['boost']}%</td>"
        body += f"<td>{hood['boost_rank_in_size']}</td>"
        body += "</tr>"
    body += "</table>"

    return content.with_body(body, 'owners')


KNOWN = mv.read_json('data/known.json')

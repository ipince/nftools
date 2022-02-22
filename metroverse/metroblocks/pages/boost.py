from . import util

from engine import metroverse as mv


def render_boosts(blocks=None, highlight=False, render_stacked=False):
    active_bboosts = mv.total_boostv2(blocks, mv.BOOSTS)

    names = set()
    if blocks is not None:
        for b in blocks:
            names.update(b['buildings']['all'].keys())
    large_hood = len(blocks) > 10  # TODO: move elsewhere
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
        """
        if large_hood:
            s += """
            <th>"Adjusted" stacked boosts<br/><small style="font-weight: normal">(for large hoods)</small></th>
            """
        s += """
        <th>Stacked boost multiplier<br/><small style="font-weight: normal">(after diminishing returns)</small></th>
        <th>Earned Boost %<br><small style="font-weight: normal">(stacked multiplier * base boost)</small></th>
        """
    s += "</tr>"

    for boost in mv.BOOSTS:
        s += f"<tr><td>{boost['name']}</td>"
        s += f"<td>{boost['pct']//100}%</td>"

        for b in boost['buildings']:
            # which blocks have building b?
            blocks_with_b = [block for block in blocks if b in block['buildings']['all']]
            count = 0
            if b in mv.BUILDINGS:
                count = mv.BUILDINGS[b]['count']
            else:
                count = mv.PUBLIC[b]['count']
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
            s += f"<td {util.highlight_if(stacked>0)}>{stacked}</td>"

            if large_hood:
                # Adjusted stacked
                adjusted_stacked = stacked * mv.large_hood_multiplier(len(blocks))
                s += f"<td {util.highlight_if(adjusted_stacked>0)}>{adjusted_stacked/1000}</td>"

            stacked_boost_multiplier = mv.boost_formula(len(blocks), stacked)
            s += f"<td {util.highlight_if(stacked_boost_multiplier>0)}>{stacked_boost_multiplier/1000}</td>"

            total_boost = (stacked_boost_multiplier * boost['pct'])//1000/100
            s += f"<td {util.highlight_if(total_boost>0)}><b>{total_boost}%</b></td>"

        s += "</tr>"
    #        s += f"<li><b>{b['name']} ({b['pct']}%):</b> {', '.join(b['buildings'])}</li>"
    return s + "</table>"


def render_pathway_boosts(blocks):
    pboosts = mv.get_active_pathway_boosts(blocks)
    pboosts_names = pboosts.keys()
    large_hood = len(blocks) > 10  # TODO: move elsewhere
    s = """
    <h2 style="margin-bottom: 2">Pathway Boosts</h2>
    <small>(reference <a href='https://docs.metroverse.com/overview/pathway-boost#pathway-boost'>docs</a>)</small>
    <p><table>
    <tr><th>Name</th>
    <th>Boost % (base)</th>
    <th>Blocks with 2 of same kind</th>
    <th>Stacked boosts</th>
    """
    if large_hood:
        s += """
        <th>"Adjusted" stacked boosts<br/><small style="font-weight: normal">(for large hoods)</small></th>
        """
    s += """
    <th>Stacked boost multiplier<br/><small style="font-weight: normal">(after diminishing returns)</small></th>
    <th>Earned Boost %<br><small style="font-weight: normal">(stacked multiplier * base boost)</small></th>
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
        s += f"<td {util.highlight_if(stacked > 0)}>{stacked}</td>"

        if large_hood:
            # Adjusted stacked
            adjusted_stacked = stacked * mv.large_hood_multiplier(len(blocks))
            s += f"<td {util.highlight_if(adjusted_stacked > 0)}>{adjusted_stacked / 1000}</td>"

        # Stacked boost multiplier
        stacked_boost_multiplier = mv.boost_formula(len(blocks), stacked)
        s += f"<td {util.highlight_if(stacked_boost_multiplier > 0)}>{stacked_boost_multiplier / 1000}</td>"

        # Total boost
        total_boost = (mv.boost_formula(len(blocks), stacked)*pboost['pct']) // 1000 / 100
        s += f"<td {util.highlight_if(total_boost > 0)}><b>{total_boost}%</b></td>"

        s += "</tr>"

    s += "</table>"
    return s


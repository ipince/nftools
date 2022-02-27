from . import util

from engine import metroverse as mv


def render_boosts(blocks=None, highlight=False, render_stacked=False):
    active_bboosts = mv.active_boosts(blocks)

    names = set()
    if blocks is not None:
        for block in blocks:
            names.update(block['buildings']['all'].keys())
    large_hood = len(blocks) > 10  # TODO: move elsewhere
    s = """
    <h2 style="margin-bottom: 2">Hood Boosts</h2>
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
        s += f"<td>{boost['pct']}%</td>"

        for building in boost['buildings']:
            building_name = building["name"]
            # which blocks have the building?
            blocks_with_b = [block for block in blocks
                             if building_name in block['buildings']['all']
                             or building_name == block["pathway"]]
            count = 0
            if building_name in mv.BUILDINGS:
                count = mv.BUILDINGS[building_name]['count']
            elif building_name in mv.PUBLIC:
                count = mv.PUBLIC[building_name]['count']
            pct = 100.0*count/10000

            s += f"""<td {util.highlight_if(len(blocks_with_b) > 0)}>
            {building_name} {"(" + str(pct) + "%)" if count > 0 else ""}
            """
            if len(blocks_with_b) > 0:
                s += "<br />"
                for block in blocks_with_b:
                    if highlight:
                        s += f""" <a href="#{block['num']}">#{block['num']}</a>"""
            s += "</td>"

        if render_stacked:
            stacked = active_bboosts[boost['name']] if boost['name'] in active_bboosts else 0
            s += f"<td {util.highlight_if(stacked>0)}>{stacked}</td>"

            if large_hood:
                # Adjusted stacked
                adjusted_stacked = stacked * mv.large_hood_multiplier(len(blocks))
                s += f"<td {util.highlight_if(adjusted_stacked>0)}>{adjusted_stacked/1000}</td>"

            stacked_boost_multiplier = mv.boost_formula(len(blocks), stacked)
            s += f"<td {util.highlight_if(stacked_boost_multiplier>0)}>{stacked_boost_multiplier/1000}</td>"

            total_boost = (stacked_boost_multiplier * boost['bps'])//1000/100
            s += f"<td {util.highlight_if(total_boost>0)}><b>{total_boost}%</b></td>"

        s += "</tr>"
    return s + "</table>"


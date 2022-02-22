from . import content

from engine import metroverse as mv


def buildings():
    body = """
    <h1>Buildings</h1>
    <p>Curious about which buildings are most rare? Ask no more!
    <p>
    <table>
    """
    # TODO: pre-compute this. add type. fix total counts.
    (buildings, bcounts, counts) = mv.buildings_by_rarity(mv.BLOCKS, mv.BUILDINGS, mv.PUBLIC)
    body += "<tr><th>Building Name</th><th>Number of Blocks that have it</th></tr>"
    for b in buildings:
        body += "<tr>"
        body += f"<td>{b}</td><td>{bcounts[b]}</td>"  # <td>{counts[b]}</td>"
        body += "</tr>"

    body += "</table>"

    return content.with_body(body, 'buildings')


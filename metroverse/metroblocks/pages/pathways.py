from . import content

from engine import metroverse as mv


def pathways():
    double_river = [b for b in mv.BLOCKS if b['pathway'] == 'river']
    double_rail = [b for b in mv.BLOCKS if b['pathway'] == 'rail']
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

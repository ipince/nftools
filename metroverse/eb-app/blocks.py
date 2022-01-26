import content
import metroverse as mv
import traceback

instructions = '''
<h1>Block Explorer</h1>
Welcome to the block explorer. This is a simple web service to view Metaverse block information.<br />

<p>Just append <code>b/</code> and a block number to the URL (for example: <code><a href="/b/1">/b/1</a></code>) to view a block's info at a glance.
'''

hood_instructions = """
<h1>Hood Simulator</h1>
The Hood Simulator lets you check which neighborhood boosts you would get if you were to stake a set of blocks. Try it out with an example: <a href="/hood/1,2,3">1,2,3</a>.
"""

hood_warning = """
<div style="width: 800"><small><em>WARNING:</em> the neighborhood boosts feature is not released yet, and we don't yet know whether these boosts are stackable or not. I think it makes more sense to not make them stackable, so this simulator only tells you whether you get a particular boost or not, and not how many of that boost you get.</small></div>
"""

def index():
  return content.with_body(instructions, 'blocks')

def get_block(block_number):
  try:
    idx = int(block_number)
    block = BLOCKS[idx-1]
    body = f"""
    <div class="row">
      <div class="column">{render_block(block)}</div>
      <div class="column">{render_boosts([block])}</div>
    </div>
    """
    return content.with_body(body, 'blocks')
  except Exception as e:
    traceback.print_exc()
    return content.with_body("Please enter a block number between 1 and 10000", 'blocks')

def hood(blocks=None):
  if blocks is None or blocks == "":
    return content.with_body(hood_instructions, 'hoods')
  try:
    indeces = list(map(lambda s: int(s.strip()), blocks.split(",")))
    if len(indeces) > 100:
      return content.with_body("Please limit your input to 100 blocks", 'hoods')
    blocks = list(filter(lambda b: b['num'] in indeces, BLOCKS))

    gotten = mv.total_boost(blocks, BOOSTS)
    tboost = 0
    for boost in gotten:
      tboost += boost['pct']

    score = sum(map(lambda b: b['scores']['total'], blocks))
    boosted_score = round(score * (1+1.0*tboost/100), 2) # keep in sync w mv.boosted_score()

    # Find best expansions:
    (byscore, byboost) = mv.best_expansions(blocks, BLOCKS, BOOSTS)
    
    # Boost table
    names = [b['name'] for b in blocks]
    body = f"""
    <h1>Hood Simulator</h1>
    <p>Analyzing hood with {len(blocks)} block(s): {', '.join(names)}. Your total hood boost is <span style="font-size: 18"><b>{tboost}%</b></span>.<br/>
    This hood would produce <b><span style="font-size: 16">{score}<span></b> MET per day (now), and <b><span style="font-size: 16">{boosted_score}</span></b> MET per day after boosting is released.
    <p>{hood_warning}
    <div>{render_boosts(blocks, highlight=True)}</div>
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
    <tr><th>Block</th><th>Staked?<br><small>as of {mv.LAST_STAKE_UPDATE}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
    """
    for i in range(100):
      delta = fmt_score(byscore[i]['score'] - boosted_score)
      expand = f"/hood/{','.join(map(str, indeces + [byscore[i]['block']['num']]))}"
      staked = 'Yes' if byscore[i]['block']['staked'] else f"No (<a href={opensea(byscore[i]['block'])}>OpenSea</a>)"
      body += f"""
      <tr><td><a href="/b/{byscore[i]['block']['num']}">{byscore[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
      <td>{staked}</td>
      <td>{byscore[i]['boost']}%</td>
      <td>{fmt_score(byscore[i]['score'])}</td>
      <td>{delta}</td></tr>"""
    body += """
    </table></div>
    """
    # By boost
    body += f"""
    <div class="column"><h3>By Boost (top 100)</h3><table>
    <tr><th>Block</th><th>Staked?<br><small>as of {mv.LAST_STAKE_UPDATE}</small></th><th>New Boost</th><th>New Score</th><th>Score Delta</th></tr>
    """
    for i in range(100):
      delta = fmt_score(byscore[i]['score'] - boosted_score)
      expand = f"/hood/{','.join(map(str, indeces + [byboost[i]['block']['num']]))}"
      staked = 'Yes' if byboost[i]['block']['staked'] else f"No (<a href={opensea(byboost[i]['block'])}>OpenSea</a>)"
      body += f"""
      <tr><td><a href="/b/{byboost[i]['block']['num']}">{byboost[i]['block']['name']}</a> (<a href={expand}>expand!</a>)</td>
      <td>{staked}</td>
      <td>{byboost[i]['boost']}%</td>
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
    return content.with_body("Failed to understand input. Please use comma-separated list of block numbers, like this: <code><a href='/hood/1,2,3'>1,2,3</a></code>", 'hoods')

def fmt_score(score):
  return "{:.2f}".format(score)

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
    body += f"<td>{b}</td><td>{bcounts[b]}</td>"#<td>{counts[b]}</td>"
    body += "</tr>"

  body += "</table>"

  return content.with_body(body, 'buildings')

def ranks():
  body = """<h1>Block Ranks</h1>

  <p>Note, these are calculated based on the MET-producing power, not on rarity. <br/>
  Also, I chose to use the "boosted" rank as the rank because that will be the true MET-producing power of the block once boosts are actually implemented.
  <p>
  <table>
  """
  sorted_blocks = sorted(BLOCKS, key=lambda b: b['rank'])
  body += f"<tr><th>Block Name</th><th>Staked?<br><small>as of {mv.LAST_STAKE_UPDATE}</small></th><th>Score (unboosted)</th><th>Rank (of unboosted score)</th><th>Boost (pct)</th><th>Score (boosted)</th><th style='background: darkseagreen'>Rank (of boosted score)</th></tr>"
  for b in sorted_blocks:
    body += f"<tr><td><a href='b/{b['num']}'>{b['name']}</a> (<a href={opensea(b)}>OpenSea</a>)</td><td>{'Yes' if b['staked'] else 'No'}</td><td>{b['scores']['total']}</td><td>{b['raw_rank']}</td><td>{b['scores']['pct']}%</td><td>{b['scores']['boosted']}</td><td>{b['rank']}</td></tr>"

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
      s = f"    {build['name']} (score {build['score']}, weight {build['weight']}) "

      if 'boost_name' in build:
        s += f" <b>[{build['boost_name']} - {build['pct']}%]</b>"
      bldg_strs.append(s+"\n")
    strs.append(bldg_strs)

  pubs = []
  for pub in block['buildings']['pub'].values():
    s = f"    {pub['name']}"
    if 'boost_name' in pub:
      s += f" <b>[{pub['boost_name']} - {pub['pct']}%]</b>"
    pubs.append(s)

  bnum = block['num']
  return f"""
<div>
<h1 style="margin-bottom: 0"><a id="{block['num']}">{block['name']}</a> (<a href="/ranks">rank</a> {block['rank']}/10000)</h1>
<small>(view on <a href='https://blocks.metroverse.com/{bnum}'>Metroverse</a>; view on <a href={opensea(block)}>OpenSea</a>; this block is {"" if block['staked'] else "<b>not</b>"} staked as of {mv.LAST_STAKE_UPDATE})
</small>

<p>Total Score: <b>{block['scores']['Score: Total']}</b>
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

def opensea(block):
  return f"https://opensea.io/assets/0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f/{block['num']}"

def render_boosts(blocks=None, highlight=False):
  gotten = list(map(lambda x: x['name'], mv.total_boost(blocks, BOOSTS)))

  names = set()
  if blocks is not None:
    for b in blocks:
      names.update(b['buildings']['all'].keys())
  s = """
<h2 style="margin-bottom: 2">Neighborhoods Boosts</h2>
<small>(reference <a href='https://docs.metroverse.com/overview/neighborhood-boost#list-of-neighborhood-boosts'>docs</a>)</small>
<p>
<table>
"""
  s += "<tr><th>Name</th><th>Building 1</th><th>Building 2</th><th>Building 3</th><th>Boost %</th></tr>"
  for boost in BOOSTS:
    s += f"<tr><td>{boost['name']}</td>"
    for b in boost['buildings']:
      # which blocks have building b?
      blocks_with_b = [block for block in blocks if b in block['buildings']['all']]
      if len(blocks_with_b) > 0:
        s += f"""<td style='background: darkseagreen'>{b}<br/>"""
        for block in blocks_with_b:
          if highlight:
            s += f""" <a href="#{block['num']}">#{block['num']}</a>"""
        s += "</td>"
      else:
        s += f"<td>{b}</td>"
    if boost['name'] in gotten:
      s += f"<td style='background: darkseagreen'>{boost['pct']}%</td>"
    else:
      s += f"<td>{boost['pct']}%</td>"
    s += "</tr>"
#    s += f"<li><b>{b['name']} ({b['pct']}%):</b> {', '.join(b['buildings'])}</li>"
  return s+"</table>"


(BLOCKS, BOOSTS, BUILDINGS, PUBLIC) = mv.load_all()


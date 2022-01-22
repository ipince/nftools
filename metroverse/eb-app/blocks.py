import content
import metroverse as mv

instructions = '''
<h1>Block Explorer</h1>
Welcome to the block explorer. This is a simple web service to view Metaverse block information.<br />

<p>Just append <code>b/</code> and a block number to the URL (for example: <code><a href="/b/1">/b/1</a></code>) to view a block's info at a glance.

'''

def index():
  return content.with_body(instructions, 'blocks')

def get_block(block_number):
  try:
    idx = int(block_number)
    block = BLOCKS[idx-1]
    body = f"""
    <div class="row">
      <div class="column">{render_block(block)}</div>
      <div class="column">{render_boosts(block)}</div>
    </div>
    """
    return content.with_body(body, 'blocks')
  except Exception as e:
    print("got exception...")
    print(e)
    return "Please enter a block number between 1 and 10000"



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

  bnum = block['name'][7:]
  return f"""
<div>
<h1 style="margin-bottom: 0">{block['name']}</h1>
<small>(view on <a href='https://blocks.metroverse.com/{bnum}'>Metroverse</a>; view on <a href='https://opensea.io/assets/0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f/{bnum}'>OpenSea</a>)
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

def render_boosts(block):
  names = block['buildings']['all'].keys()
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
      if b in names:
        s += f"<td style='background: darkseagreen'>{b}</td>"
      else:
        s += f"<td>{b}</td>"
    s += f"<td>{boost['pct']}%</td>"
    s += "</tr>"
#    s += f"<li><b>{b['name']} ({b['pct']}%):</b> {', '.join(b['buildings'])}</li>"
  return s+"</table>"


def load_blocks():
  (blocks, buildings, public, boosts) = mv.load_data()
  (buildings, public) = mv.transform_buildings(buildings, public, boosts)
  blocks = mv.transform(blocks, buildings, public)
  print("loaded")
  return (blocks, boosts)

(BLOCKS, BOOSTS) = load_blocks()


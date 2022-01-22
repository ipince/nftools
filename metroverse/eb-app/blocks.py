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
    return content.with_body(mv.bstr(BLOCKS[idx-1]) + boosts_str(), 'blocks')
  except Exception as e:
    print("got exception...")
    print(e)
    return "Please enter a block number between 1 and 10000"



def render_block(block):
  return ""

def load_blocks():
  (blocks, buildings, public, boosts) = mv.load_data()
  (buildings, public) = mv.transform_buildings(buildings, public, boosts)
  blocks = mv.transform(blocks, buildings, public)
  print("loaded")
  return (blocks, boosts)

(BLOCKS, BOOSTS) = load_blocks()

def boosts_str():
  s = "---<br><br>Neighborhoods Boosts reference (from <a href='https://docs.metroverse.com/overview/neighborhood-boost#list-of-neighborhood-boosts'>docs</a>):<br/><ul>"
  for b in BOOSTS:
    s += f"<li><b>{b['name']} ({b['pct']}%):</b> {', '.join(b['buildings'])}</li>"
  return s+"</ul>"


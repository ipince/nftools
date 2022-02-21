import json

# Read the blocks data and write the slim version.
def slimify():
  blocks = load_blocks()
  slims = []
  for block in blocks:
    slim = {}
    # Only keep name, attributes, and the pathway-x entity.
    slim['name'] = block['name']
    slim['attributes'] = block['attributes']
    slim['entities'] = only_pathway_x(block['entities'])
    slims.append(slim)
  with open("../data/all_blocks_slim.json", 'w') as f:
    f.write(json.dumps(slims, indent=2))

def load_blocks():
  with open("../data/all_blocks.json", "r") as f:
    return json.loads(f.read())

def only_pathway_x(entities):
  for entity in entities:
    if entity['entity_type']['zone'] == 'pathway-x':
      return [entity]
  raise Exception("did not find pathway-x entity")

slimify()

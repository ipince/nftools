from flask import Flask, request

import blocks
import content
import json

from api import blockchain
from api import api

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.url_map.strict_slashes = False


@application.route('/')
def index():
    return blocks.index()


@application.route('/api/hood', methods=["GET", "POST"])
@application.route('/api/hood/<blocknums>', methods=["GET", "POST"])
def api_hood(blocknums=None):
    if blocknums:
        # Parse from query string
        blocknums = list(map(lambda s: int(s.strip()), blocknums.split(",")))
        pass
    else:
        try:
            blocknums = request.get_json(force=True)
        except Exception:
            return json.dumps({"error": "Unable to parse input. It should be valid JSON and look like '[1, 2, 3]'"})

    # TODO: validate input is numbers.
    return api.hood(blocknums)


@application.route('/refresh-staked-blocks')
def refresh_staked_blocks():
    # TODO: protect this somehow!
    num = blockchain.refresh_staked_blocks()
    return f"there are {num} staked blocks"


@application.route('/read')
def read():
    with open('data/test.txt', 'r') as f:
        return f.read()


@application.route('/write/<data>')
def write(data):
    with open('data/test.txt', 'w') as f:
        f.write(data)
        return "written"


application.add_url_rule('/b/<block_number>', 'block', blocks.get_block)

application.add_url_rule('/hood', 'hood', blocks.hood)
application.add_url_rule('/hood/<blocks>', 'hood', blocks.hood)

application.add_url_rule('/buildings', 'buildings', blocks.buildings)
application.add_url_rule('/pathways', 'pathways', blocks.pathways)
application.add_url_rule('/ranks', 'ranks', blocks.ranks)
application.add_url_rule('/owners', 'owners', blocks.owners)
application.add_url_rule('/faq', 'faq', content.faq)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

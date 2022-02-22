import json

from flask import Flask, request

import pages

from api import api
from engine import blockchain


# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.url_map.strict_slashes = False


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


@application.route('/')
def index():
    return pages.index()


application.add_url_rule('/b/<block_number>', 'block', pages.block)

application.add_url_rule('/hood', 'hood', pages.hood)
application.add_url_rule('/hood/<blocks>', 'hood', pages.hood)

application.add_url_rule('/buildings', 'buildings', pages.buildings)
application.add_url_rule('/pathways', 'pathways', pages.pathways)
application.add_url_rule('/ranks', 'ranks', pages.ranks)
application.add_url_rule('/owners', 'owners', pages.owners)
application.add_url_rule('/faq', 'faq', pages.faq)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

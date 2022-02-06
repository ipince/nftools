from flask import Flask

import blocks
import content
import json

from api import blockchain

# EB looks for an 'application' callable by default.
application = Flask(__name__)


@application.route('/')
def index():
    return blocks.index()


@application.route('/api/hood/<blocknums>')
def api_hood(blocknums):
    # Return some dummy data for frontend development.
    data = {
        "blocks": [
            {
                "num": 1,
                "name": "Block #1",
                "score": 123,
                "buildings": [
                    {
                        "name": "Hospital",
                        "type": "Public",
                    },  # more...
                ],
                "pathway": None,
            },
            {
                "num": 2,
                "name": "Block #2",
                "score": 130,
                "buildings": [
                    {
                        "name": "Fire Station",
                        "type": "Public",
                    },  # more...
                ],
                "pathway": "Railway",
            },  # more...
        ],
        "building_boosts": [
            {
                "name": "Safety",
                "enabled": True,
                "pct": 5,
                "buildings": [
                    {
                        "name": "Hospital",
                        "blocks": [1],
                    },
                    {
                        "name": "Police Station",
                        "blocks": [],
                    },
                    {
                        "name": "Fire Station",
                        "blocks": [1, 2],
                    }
                ]
            },  # more...
        ],
        "pathway_boosts": [
            {
                "name": "Railway Pathway",
                "enabled": True,
                "pct": 4,
                "blocks": [2],
            },
            {
                "name": "River Pathway",
                "enabled": False,
                "pct": 8,
                "blocks": [],
            },
        ]
    }
    return json.dumps(data, indent=2)


@application.route('/refresh-staked-blocks')
def refresh_staked_blocks():
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
application.add_url_rule('/ranks', 'ranks', blocks.ranks)
application.add_url_rule('/faq', 'faq', content.faq)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

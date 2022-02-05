from flask import Flask
from datetime import datetime

import blocks
import blockchain
import content
import donate

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route('/')
def index():
  return blocks.index()


@application.route('/refresh-staked-blocks')
def refresh_staked_blocks():
  num = blockchain.refresh_staked_blocks()
  return f"there are {num} staked blocks"


@application.route('/donate')
def donation():
  return donate.donate()

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

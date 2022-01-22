from flask import Flask

import blocks
import content

# EB looks for an 'application' callable by default.
application = Flask(__name__)

application.add_url_rule('/', 'index', blocks.index)
application.add_url_rule('/b/<block_number>', 'block', blocks.get_block)

application.add_url_rule('/hood', 'hood', blocks.hood)
application.add_url_rule('/hood/<blocks>', 'hood', blocks.hood)

application.add_url_rule('/buildings', 'buildings', blocks.buildings)
application.add_url_rule('/faq', 'faq', content.faq)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

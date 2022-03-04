import json
import traceback
import redis
import dotenv
import os

from flask import Flask, request

import pages
import cronjob

from api import api

dotenv.load_dotenv()  # TODO: make localhost easy
r = redis.Redis(host=os.getenv("REDIS_HOST"))

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.url_map.strict_slashes = False


@application.route("/redis/set/<key>/<value>")
def redis_set(key, value):
    r.set(key, value)
    return f"{key} = {value}"


@application.route("/redis/get/<key>")
def redis_get(key):
    return f"{key} = {r.get(key)}"


# @application.route("/env")
def env():
    ks = sorted(os.environ.keys())
    r = ""
    for k in ks:
        r += f"{k}={os.environ[k]}<br/>"
    return r


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
    return as_json(api.hood(blocknums))


@application.route("/api/expansions", methods=["POST"])
def api_expand():
    # TODO: have better input: { "blocks": [1, 2, 3], "exclude_staked": true (default=false), "limit": 20 (default 100, max 100) }
    try:
        blocknums = request.get_json(force=True)
        return as_json(api.hood_expansions(blocknums))
    except Exception:
        traceback.print_exception()
        return json.dumps({"error": "Unable to parse input. It should be valid JSON"})


def as_json(object):
    return json.dumps(object, indent=2)


@application.route('/refresh/owners')
def refresh_staked_blocks():
    if os.getenv("ENV") != "test":
        return "Skipping refresh because this is not the test env"

    try:
        # This will refresh staked blocks too.
        cronjob.update_hoods_metadata(refresh_owners=True)
        return "done"
    except Exception as e:
        return e.with_traceback()


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
    application.debug = os.getenv("ENV") != "prod"
    application.run()

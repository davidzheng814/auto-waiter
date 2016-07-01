"""APIs for delivering information from the database to the app."""
from flask import Blueprint, render_template
from flask_restful import Resource, Api, reqparse
import os
import json

from config import PREF_DIR

MAIN_BLUEPRINT = Blueprint('main', __name__)

@MAIN_BLUEPRINT.route('/')
def index():
    return render_template("index.html")

@MAIN_BLUEPRINT.route('/thanks/')
def thanks():
    return render_template("thanks.html")

API_BLUEPRINT = Blueprint("api", __name__, url_prefix="/api")
PERF_API = Api(API_BLUEPRINT)

prefs = {}

def is_valid(pref):
    return True

def load_prefs():
    for file in os.listdir(PREF_DIR):
        with open(os.path.join(PREF_DIR, file), 'r') as f:
            pref = json.loads(f.read())
            prefs[pref['username']] = pref

class Preferences(Resource):
    """Returns a list of subtable names for perf_report."""
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username', required=True)
    post_parser.add_argument('password', required=True)
    post_parser.add_argument('preference', required=True)
    def post(self):
        pref = Preferences.post_parser.parse_args()

        if is_valid(pref):
            prefs[pref['username']] = pref
            with open(os.path.join(PREF_DIR, pref['username'] + '.json'), 'w') as f:
                text = json.dumps(pref, sort_keys=True, indent=4, separators=(',', ': '))
                f.write(text)

            return True

        return False

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('username', required=True)
    get_parser.add_argument('password', required=True)
    def get(self):
        args = Preferences.get_parser.parse_args()
        if not args['username'] or not args['password']:
            return False

        username = args['username']
        password = args['password']
        if not username in prefs:
            return False

        pref = prefs[username]
        if pref['password'] != password:
            return False

        return pref

load_prefs()

PERF_API.add_resource(Preferences, '/preferences/')
"""APIs for delivering information from the database to the app."""
from flask import Blueprint, render_template
from flask_restful import Resource, Api, reqparse
import os
import json
from collections import OrderedDict

from config import PREF_DIR
from api import *

MAIN_BLUEPRINT = Blueprint('main', __name__)

FOOD_SECTIONS = OrderedDict()
FOOD_SECTIONS['cuisines'] = ['indian', 'mediterranean', 'italian', 'american', 'mexican', 'asian']
FOOD_SECTIONS['meats'] = ['pork', 'beef', 'lamb', 'poultry', 'seafood']
FOOD_SECTIONS['vegetables'] = ['leaves (eg spinach)', 'beans (eg green beans)', 'flowers (eg broccoli)', 'roots (eg potato)']

@MAIN_BLUEPRINT.route('/')
def index():
    return render_template("index.html", sections=FOOD_SECTIONS)

@MAIN_BLUEPRINT.route('/thanks/')
def thanks():
    return render_template("thanks.html")

API_BLUEPRINT = Blueprint("api", __name__, url_prefix="/api")
PERF_API = Api(API_BLUEPRINT)

prefs = load_prefs()

def parse_pref(pref):
    if not pref['username'] or not pref['password']:
        return False

    restrictions = [x.strip().lower() for x in pref['restrictions'].split(',') if x]
    favorites = [x.strip().lower() for x in pref['favorites'].split(',') if x]
    scores = {}
    for score in pref['scores'].split(','):
        tokens = score.split('-')
        scores.setdefault(tokens[0], {})[tokens[1]] = int(tokens[2])

    return {
        'username': pref['username'],
        'password': pref['password'],
        'preferences': {
            'favorites': favorites,
            'restrictions': restrictions,
            'scores': scores
        }
    }

class Preferences(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username', required=True)
    post_parser.add_argument('password', required=True)
    post_parser.add_argument('restrictions', required=True)
    post_parser.add_argument('favorites', required=True)
    post_parser.add_argument('scores', required=True)
    def post(self):
        pref = Preferences.post_parser.parse_args()

        pref = parse_pref(pref)
        if pref:
            prefs[pref['username']] = pref
            with open(os.path.join(PREF_DIR, pref['username'] + '.json'), 'w') as f:
                text = json.dumps(pref, sort_keys=True, indent=4, separators=(',', ': '))
                f.write(text)

            session = {
                'cookie': login(pref['username'], pref['password']),
                'preferences': pref['preferences'],
                'username': pref['username']
            }

            log('Registered new preferences for user {}'.format(pref['username']))

            # Make an order right away so the user gets some immediate feedback
            menus = [get_menus(session['cookie'], day, force=True) for day in range(get_day_of_week(), NUM_DAYS)]
            do_order(session, menus)

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

        return pref['preferences']

PERF_API.add_resource(Preferences, '/preferences/')

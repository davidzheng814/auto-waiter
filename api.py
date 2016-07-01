import os
import requests
import json
from datetime import datetime
from config import *
from util import *
from rank import pick_food

PREVIOUS_MENUS = os.path.join(MENU_DIR, 'previous_menus{}.json')

def login(username, password):
    data = {
        'username':username,
        'password':password,
        'response_type':'code',
        'redirect_uri':'https%3A%2F%2Fwww.waiter.com%2Foauth%2Fcallback'
    }
    r = requests.post('https://www.waiter.com/api/v1/login', data=data)
    res = r.json()

    if 'access_token' in res:
        access_token = res['access_token']
        user_id = res['user_id']
    else:
        return False

    r = requests.get('https://www.waiter.com/home/{token}'.format(token=access_token))
    session_cookie = r.cookies

    return session_cookie

def add_item(session_cookie, item):
    assert session_cookie
    r = requests.post('https://www.waiter.com/api/v1/cart_items.json', cookies=session_cookie, data=item)

def get_menus(session_cookie, day, force=False):
    '''
    Get the menus available on day (Monday=0, etc), or None if no menus available
    If force, get menus even if menus not yet update
    '''
    assert session_cookie

    menus = []
    try:
        menus = [get_menu(metadata) for metadata in get_menu_metadata(session_cookie, day)]
    except get_menu_error:
        log('Error getting menus from Waiter.com')
        return None

    if force:
        # Ignore menu update status
        log('Force menus requested, ignoring previous menus')
        return menus

    # Check if menus have been updated
    menu_file = PREVIOUS_MENUS.format(day)
    try:
        with open(menu_file, 'r') as f:
            if menus == json.loads(f.read()):
                # Menus the same, not yet updated
                log('Menus not yet updated')
                return None
    except IOError:
        # No previous menu file, continue as normal
        pass

    # Serialize the menus so that, next time, we can check if the menus have been updated
    with open(menu_file, 'w') as f:
        log('Writing menu file {}'.format(menu_file))
        f.write(json.dumps(menus))

    return menus

def get_cart_ids(session_cookie, day):
    menu_page = get_menu_page(session_cookie, day)
    all_ids = json.loads(try_get_pattern(r'var cartIds = (\[[0-9,]*\])', menu_page, group=1))
    return sorted(all_ids)[day*4:day*4 + 4]

def load_prefs():
    prefs = {}
    for pref_file in os.listdir(PREF_DIR):
        with open(os.path.join(PREF_DIR, pref_file), 'r') as f:
            pref = json.loads(f.read())
            prefs[pref['username']] = pref
    return prefs

def get_user_sessions():
    '''
    Return a list of sessions for all users. A session is a dictionary with the following structure:
    cookie: a session_cookie that grants access to Waiter.com endpoints
    preferences: a dictionary of preferences used to choose an order for the user
    '''
    sessions = []
    for username, pref in load_prefs().items():
        sessions.append({
            'cookie': login(username, pref['password']),
            'preferences': pref['preferences'],
            'username': username
        })

    return sessions

def do_order(session, day_of_week, menus):
    '''
    If force, submit a new order for a user even if the menus have not been updated
    '''
    log('Preparing order for {user}, day {day}'.format(user=session['username'], day=day_of_week))

    order_id = pick_food(menus, session['preferences'])

    # TODO: Each day has 4 cart IDs. We arbitrarily add the order to the first one. This will need
    # to be tested, and if it doesn't work, we'll have to find out which cart ID goes with which
    # restaurant
    cart_id = get_cart_ids(session['cookie'], day_of_week)[0]

    item = {
        'cart_id': cart_id,
        'menu_item_id': order_id,
        'menu_item_option_choice_ids': 5862793, # TODO what is this?
        'quantity': 1
    }

    add_item(session['cookie'], item)

def get_day_of_week():
    return datetime.today().weekday()

import os
import requests
import json
from config import *
from util import *

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

def get_menus(session_cookie, day):
    '''
    Get the menus available on day (Monday=0, etc), or None if no menus available
    '''
    assert session_cookie

    menus = []
    try:
        menus = [get_menu(metadata) for metadata in get_menu_metadata(session_cookie, day)]
    except get_menu_error:
        log('Error getting menus from Waiter.com')
        return None

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
            'preferences': pref['preferences']
        })

    return sessions

def do_order(session, day_of_week, menus=None):
    log('Preparing order for day {day}'.format(day=day_of_week))
    if menus is None:
        menus = get_menus(session['cookie'], day_of_week)
    # TODO select and order and make it

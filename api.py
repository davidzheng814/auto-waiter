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

    log('Adding item {item} with options {options} to cart {cart}'.format(
        item=item['menu_item_id'], cart=item['cart_id'], options=item['menu_item_option_choice_ids']))

    url = 'https://www.waiter.com/api/v1/cart_items.json'
    r = requests.post(url, cookies=session_cookie, data=item)
    if r.status_code != 200:
        log('POST {url} failed: {status} {message}'.format(url=url, status=r.status_code, message=r.json().get('message')))

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
        raise get_menu_error

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
                raise get_menu_error
    except IOError:
        # No previous menu file, continue as normal
        pass

    # Serialize the menus so that, next time, we can check if the menus have been updated
    with open(menu_file, 'w') as f:
        log('Writing menu file {}'.format(menu_file))
        f.write(json.dumps(menus))

    return menus

def get_cart_id(session_cookie, day, restaurant):
    menu_page = get_menu_page(session_cookie, day)

    cart_ids = json.loads(try_get_pattern(r'var cartIds = (\[[0-9,]*\])', menu_page, group=1))
    cart_ids = sorted(cart_ids)[day*NUM_STORES:day*NUM_STORES + NUM_STORES]

    store_ids = sorted(get_menu_ids(session_cookie, day))
    index = store_ids.index(restaurant)
    if index == -1:
        log('Store {store} is not availabe on day {day}'.format(store=restaurant, day=day))
        return

    return cart_ids[index]

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

def do_order(session, menus):
    log('Preparing order for {user}'.format(user=session['username']))

    orders = pick_food(menus, session['preferences'])

    for day in range(get_day_of_week(), NUM_DAYS):
        # Everything is offset by the day we're starting at
        index = day - get_day_of_week()

        cart_id = get_cart_id(session['cookie'], day, orders[index]['restaurant_id'])
        order_id = orders[index]['id']
        options = orders[index]['option_id']
        item = {
            'cart_id': cart_id,
            'menu_item_id': order_id,
            'menu_item_option_choice_ids': options,
            'quantity': 1
        }

        add_item(session['cookie'], item)

def get_day_of_week():
    return datetime.today().weekday()

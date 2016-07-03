import os
import json
from datetime import datetime
from config import *
from util import *
from rank import pick_food

PREVIOUS_MENUS = os.path.join(MENU_DIR, 'previous_menus{}.json')

def login(username, password):
    log('Log in user {username}', INFO, username=username)

    data = {
        'username':username,
        'password':password,
        'response_type':'code',
        'redirect_uri':'https%3A%2F%2Fwww.waiter.com%2Foauth%2Fcallback'
    }

    try:
        res = post(make_url(API_URL, 'login'), data=data).json()
    except http_error:
        log('Could not log in {username}: invalid credentials', ERROR, username=username)
        return False

    if 'access_token' in res:
        access_token = res['access_token']
    else:
        log('Could not log in {username}: no access token', ERROR, username=username)
        return False

    try:
        r = get('https://www.waiter.com/home/{token}'.format(token=access_token))
        return r.cookies
    except http_error:
        log('Could not log in {username}: no session cookie', ERROR, username=username)
        return False

def add_item(session_cookie, item):
    assert session_cookie

    log('Adding item {item} with options {options} to cart {cart}', INFO,
        item=item['menu_item_id'],
        cart=item['cart_id'],
        options=item['menu_item_option_choice_ids'])

    try:
        post(make_url(API_URL, 'cart_items.json'), cookies=session_cookie, data=item)
        return True
    except http_error:
        return False

def clear_order(session_cookie, day):
    assert session_cookie

    order = get_order(session_cookie, day)
    if type(order) != type([]):
        order = [order]
    for item in order:
        try:
            delete(make_url(API_URL, 'cart_items', '{item}.json'.format(item=item)),
                   cookies=session_cookie)
        except http_error:
            return False
    return True

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
        log('Error getting menus from Waiter.com', ERROR)
        raise get_menu_error

    if force:
        # Ignore menu update status
        log('Force menus requested, ignoring previous menus', WARNING|INFO)
        return menus

    # Check if menus have been updated
    menu_file = PREVIOUS_MENUS.format(day)
    try:
        with open(menu_file, 'r') as f:
            if menus == json.loads(f.read()):
                # Menus the same, not yet updated
                log('Menus not yet updated', INFO)
                raise get_menu_error('not updated')
    except IOError:
        # No previous menu file, continue as normal
        pass

    # Serialize the menus so that, next time, we can check if the menus have been updated
    with open(menu_file, 'w') as f:
        log('Writing menu file {}', INFO, menu_file)
        f.write(json.dumps(menus))

    return menus

def get_cart_id(session_cookie, day, restaurant):
    assert session_cookie

    cart_ids = get_cart_ids(session_cookie, day)
    store_ids = sorted(get_menu_ids(session_cookie, day))
    index = store_ids.index(restaurant)
    if index == -1:
        log('Store {store} is not available on day {day}', ERROR, store=restaurant, day=day)
        raise invalid_restaurant_error(restaurant, day)

    return cart_ids[index]

def get_cart_ids(session_cookie, day):
    assert session_cookie

    menu_page = get_menu_page(session_cookie)

    cart_ids = json.loads(try_get_pattern(r'var cartIds = (\[[0-9,]*\])', menu_page, group=1))
    return sorted(cart_ids)[day*NUM_STORES:day*NUM_STORES + NUM_STORES]

def get_order(session_cookie, day):
    assert session_cookie

    order = []
    for cart_id in get_cart_ids(session_cookie, day):
        payload = {
            'cart_id': cart_id,
            'all': 1
        }
        r = get(make_url(API_URL, 'cart_items'), params=payload, cookies=session_cookie)
        order += r.json()['results']
    return order

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
        cookie = login(username, pref['password'])
        if not cookie:
            continue

        sessions.append({
            'cookie': cookie,
            'preferences': pref['preferences'],
            'username': username
        })

    return sessions

def do_order(session, menus, force=False):
    log('Preparing order for {user}', INFO, user=session['username'])

    orders = pick_food(menus, session['preferences'])

    for day in range(get_day_of_week(), NUM_DAYS):
        if force:
            log('Force requested. Clearing existing order.', WARNING|INFO)
            if not clear_order(session['cookie'], day):
                log('Unable to clear order. Skipping.', ERROR)
                continue

        # Only order if the user has not already (unless forced)
        if get_order(session['cookie'], day):
            log('User {user} already ordered for day {day}. Skipping.', INFO,
                user=session['username'], day=day)
            continue

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

    log('Completed order for {user}', INFO, user=session['username'])

def get_day_of_week():
    today = datetime.today().weekday()
    if today >= NUM_DAYS:
        # Start the next week
        return 0
    else:
        return today

import requests
import re
import json

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
    Get the menus available on day (Monday=0, etc)
    '''
    assert session_cookie
    return [get_menu(menu_id) for menu_id in get_menu_ids(session_cookie, day)]

# Helpers

def extract_services(menu_page):
    '''
    Somewhere in the page loaded by waiter.com is an API call that takes a JSON struct containing
    all the purestorage services. Parse the page and return this JSON struct. The result will be
    a list of dictionaries, where each dict is a service.
    '''

    # Function call that indicates our JSON struct is coming.
    # If this string changes, our app breaks. Oh well.
    indicator_function = 'WaiterApp.Models.services.addMissing('
    start = menu_page.find(indicator_function)
    if start == -1:
        raise Exception('/vcs/purestorage-dinner format has changed')

    # Move to the start of the JSON struct
    index = start + len(indicator_function)
    if menu_page[index] != '[':
        raise Exception('/vcs/purestorage-dinner format has changed')

    # Get the JSON list. Just bracket matching
    json_string = ''
    bracket_stack = 0
    while True:
        json_string += menu_page[index]

        if menu_page[index] == '[':
            bracket_stack += 1
        elif menu_page[index] == ']':
            bracket_stack -= 1

        if bracket_stack == 0:
            break

        index += 1

    return json.loads(json_string)

def get_menu(menu_id):
    '''
    Get the menu (a dictionary) with the given menu_id
    '''
    url = 'https://www.waiter.com/api/v1/menus/{}.json?wrap=1'.format(menu_id)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('GET {} failed'.format(url))
    return r.json()

def get_menu_ids(session_cookie, day):
    '''
    Get the ids of the menus available on day (Monday=0, etc)
    '''
    assert session_cookie

    if day < 0 or day > 3:
        raise ValueError('day must be in the range [0, 4)')

    menu_page_url = 'https://www.waiter.com/vcs/purestorage-dinner'
    menu_page = requests.get(menu_page_url, cookies=session_cookie)
    if menu_page.status_code != 200:
        raise Exception('GET %s failed: %d', menu_page_url, menu_page.status_code)

    # A list of all vendors for the week
    services = extract_services(menu_page.text)

    # Salad spot is available every day. So we remove it, find the day's unique options, and
    # then always add in salad spot
    not_salad_spot = [service for service in services if service['name'] != 'Salad Spot']
    salad_spot = [service for service in services if service['name'] == 'Salad Spot'][0]
    ids = [service['menu_id'] for service in not_salad_spot][3*day:3*day + 3]
    ids.append(salad_spot['menu_id'])

    return ids

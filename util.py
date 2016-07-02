import requests
import json
import ntpath
from datetime import datetime
import re
from config import *
import traceback

# Logging

def log(_message, *args, **kwargs):
    message = repr(_message).format(*args, **kwargs)

    today = datetime.today()
    timestamp = '{y:04d}-{mo:02d}-{d:02d} {h}:{m:02d}:{s:02d}'.format(
        y=today.year, mo=today.month, d=today.day, h=today.hour, m=today.minute, s=today.second)

    frame = traceback.extract_stack(limit=2)[0]
    source_file = ntpath.basename(frame[0])
    source_line = frame[1]
    source = '{file}:{line}'.format(file=source_file, line=source_line)

    with open(LOG_FILE, 'a') as f:
        f.write('{time} {source} {message}\n'.format(time=timestamp, source=source, message=message))

# Exceptions

class get_menu_error(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        return repr(self.value)

class http_error(Exception):
    def __init__(self, response):
        Exception.__init__(self, response.text)
        self.value = '{status} {message}'.format(
            status=response.status_code, message=response.jsons().get('message'))
        self.response = response

    def __str__(self):
        return repr(self.value)

class invalid_restaurant_error(Exception):
    def __init__(self, restaurant, day):
        self.value = 'Restaurant "{store}" is not available on day {day}'.format(
            store=restaurant, day=day)
        Exception.__init__(self, self.value)

# HTTP

def get(url, **kwargs):
    '''
    Wrapper to send a GET request. Accepts the same kwargs as requests.get(). If the request is
    successful, the server response is returned. Otherwise, an http_error is raised.
    '''
    return _request('get', url, **kwargs)

def post(url, **kwargs):
    return _request('post', url, **kwargs)

def delete(url, **kwargs):
    return _request('delete', url, **kwargs)

def _request(method, url, **kwargs):
    '''
    Helper function for the other http functions
    '''
    func = eval('.'.join(['requests', method]))
    method = method.upper()

    r = func(url, **kwargs)
    log('{method} {url}', method=method, url=r.url)

    if r.status_code != 200:
        log('{method} {url} failed: {status} {message}',
            method=method, url=url, status=r.status_code, message=r.json().get('message'))
        raise http_error(r)

    return r

# API helpers

def make_url(*args):
    return '/'.join(args)

def try_get_pattern(pattern, source, group=0):
    '''
    Try matching a pattern against Waiter.com source code and returning a group. Using this
    function means the pattern is believed to be a match, and if the match fails then Waiter.com
    must have changed their source.
    '''
    match = _try_get_pattern(pattern, source)
    return match.group(group)

def try_get_pattern_index(pattern, source, end=False, group=0):
    '''
    Same as above, but returns the start index of the matched group. (If end, then the end index
    if returned instead)
    '''
    match = _try_get_pattern(pattern, source)
    if end:
        return match.end(group)
    else:
        return match.start(group)

def _try_get_pattern(pattern, source):
    match = re.search(pattern, source)
    if match is None:
        raise Exception('/vcs/purestorage-dinner format has changed')
    return match

def get_menu_page(session_cookie, cached_pages={}):
    '''
    Memoized function to get the purestorage vcs html page. Requests the page from the Waiter
    server at most once per day
    '''
    key = datetime.today().date

    if key not in cached_pages:
        try:
            r = get(VCS_URL, cookies=session_cookie)
            cached_pages[key] = r.text
        except http_error as e:
            raise get_menu_error(repr(e))

    return cached_pages[key]

def extract_services(menu_page):
    '''
    Somewhere in the page loaded by waiter.com is an API call that takes a JSON struct containing
    all the purestorage services. Parse the page and return this JSON struct. The result will be
    a list of dictionaries, where each dict is a service.
    '''

    # Function call that indicates our JSON struct is coming.
    # If this string changes, our app breaks. Oh well.
    indicator_function = r'(WaiterApp\.Models\.services\.addMissing\()\['
    index = try_get_pattern_index(indicator_function, menu_page, end=True, group=1)

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

def get_menu(metadata):
    '''
    Get the menu (a dictionary) with the given menu_id
    '''
    try:
        url = make_url(API_URL, 'menus', '{}.json'.format(metadata['menu_id']))
        payload = {
            'wrap': 1
        }
        menu = get(url, params=payload).json()

        # Additional data not provided by the Waiter API
        menu['cuisine_types'] = metadata['cuisine_types']

        return menu
    except http_error as e:
        raise get_menu_error(repr(e))

def get_menu_ids(session_cookie, day):
    metadata = get_menu_metadata(session_cookie, day)
    return [menu['menu_id'] for menu in metadata]

def get_menu_metadata(session_cookie, day):
    '''
    Get data used to retrieve the menus available on day (Monday=0, etc)
    '''
    assert session_cookie
    assert day >= 0 and day < NUM_DAYS

    menu_page = get_menu_page(session_cookie)

    # A list of all vendors for the week
    services = extract_services(menu_page)

    data = None
    if HAS_SALAD_SPOT:
        # Salad spot is available every day. So we remove it, find the day's unique options, and
        # then always add in salad spot
        not_salad_spot = [service for service in services if service['name'] != 'Salad Spot']
        salad_spot = [service for service in services if service['name'] == 'Salad Spot'][0]
        data = [extract_menu_metadata(service) for service in not_salad_spot][(NUM_STORES-1)*day:(NUM_STORES-1)*day + (NUM_STORES-1)]
        data.append(extract_menu_metadata(salad_spot))
    else:
        data = [extract_menu_metadata(service) for service in services][NUM_STORES*day:NUM_STORES*day + NUM_STORES]

    return data

def extract_menu_metadata(menu):
    '''
    Extract useful metadata from a JSON struct
    '''
    return {
        'menu_id': menu['menu_id'],
        'cuisine_types': menu['cuisine_types']
    }

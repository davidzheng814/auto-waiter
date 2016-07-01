import os
import requests
import json

def guarantee_existence(dirs):
    '''
    For each directory in the given list, create it if it does not already exist
    '''
    for dirname in dirs:
        if not os.path.exists(dirname):
            os.makedirs(dirname)

# Exceptions

class get_menu_error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# API helpers

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

def get_menu(metadata):
    '''
    Get the menu (a dictionary) with the given menu_id
    '''
    url = 'https://www.waiter.com/api/v1/menus/{}.json?wrap=1'.format(metadata['menu_id'])
    r = requests.get(url)
    if r.status_code != 200:
        raise get_menu_error('GET {} failed'.format(url))
    menu = r.json()

    # Additional data not provided by the Waiter API
    menu['cuisine_types'] = metadata['cuisine_types']

    return menu

def get_menu_metadata(session_cookie, day):
    '''
    Get data used to retrieve the menus available on day (Monday=0, etc)
    '''
    assert session_cookie
    assert day >= 0 and day < 4

    menu_page_url = 'https://www.waiter.com/vcs/purestorage-dinner'
    menu_page = requests.get(menu_page_url, cookies=session_cookie)
    if menu_page.status_code != 200:
        raise get_menu_error(
            'GET {url} failed: {status}'.format(url=menu_page_url, status=menu_page.status_code))

    # A list of all vendors for the week
    services = extract_services(menu_page.text)

    # Salad spot is available every day. So we remove it, find the day's unique options, and
    # then always add in salad spot
    not_salad_spot = [service for service in services if service['name'] != 'Salad Spot']
    salad_spot = [service for service in services if service['name'] == 'Salad Spot'][0]
    data = [extract_menu_metadata(service) for service in not_salad_spot][3*day:3*day + 3]
    data.append(extract_menu_metadata(salad_spot))

    return data

def extract_menu_metadata(menu):
    '''
    Extract useful metadata from a JSON struct
    '''
    return {
        'menu_id': menu['menu_id'],
        'cuisine_types': menu['cuisine_types']
    }

import requests

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
    r = requests.post('https://www.waiter.com/api/v1/cart_items.json', cookies=session_cookie, data=item)
    print(r.json())
session_cookie = login('exue@purestorage.com', 'passwordEd')

# test add an item
add_item(session_cookie, {
    'cart_id':3174148,
    'menu_item_id':1173595,
    'menu_item_option_choice_ids':5862793,
    'quantity':1
})

# adding an item !!! 627
add_item(session_cookie, {
    'cart_id':3181894,
    'menu_item_id':1313963,
    'menu_item_option_choice_ids':6662995,
    'quantity':1
})

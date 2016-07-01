#!/usr/bin/python

from time import sleep
from api import *
from util import *

RETRY_INTERVAL = 30
MAX_ATTEMPTS = 10

def do_orders(attempts=0):
    log('Daemon: starting task "do_orders"')

    if attempts > MAX_ATTEMPTS:
        raise get_menu_error('Exceeded maximum retries')

    menus = {}
    for session in get_user_sessions():
        for day_of_week in range(4):
            # We store menus in a dictionary so we only have to get them for the first user
            if day_of_week not in menus:
                log('Getting menus for batch order')
                menus[day_of_week] = get_menus(session['cookie'], day_of_week)
                if menus[day_of_week] is None:
                    # Not available yet, schedule a retry
                    log('Unable to get menus. Will retry in {} seconds.'.format(RETRY_INTERVAL))
                    sleep(RETRY_INTERVAL)
                    return do_orders(attempts=attempts + 1)

            do_order(session, day_of_week, menus[day_of_week])

if __name__ == '__main__':
    do_orders()

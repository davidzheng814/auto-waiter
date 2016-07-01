#!/usr/bin/python

from time import sleep
from api import *
from util import *

RETRY_INTERVAL = 1
MAX_ATTEMPTS = 5

def do_orders(attempts=0):
    log('Daemon: starting task "do_orders"')

    if attempts > MAX_ATTEMPTS:
        raise get_menu_error('Exceeded maximum retries')

    days = range(0, 4)

    menus = [None for day in days]
    sessions = get_user_sessions()
    if not sessions:
        log('No users detected. Exiting.')
        return

    for session in sessions:
        for day in days:
            # We store menus in a dictionary so we only have to get them for the first user
            if menus[day] is None:
                log('Getting menus for batch order')
                menus[day] = get_menus(session['cookie'], day)
                if menus[day] is None:
                    # Not available yet, schedule a retry
                    log('Unable to get menus. Will retry in {} seconds.'.format(RETRY_INTERVAL))
                    sleep(RETRY_INTERVAL)
                    return do_orders(attempts=attempts + 1)

        do_order(session, menus)

if __name__ == '__main__':
    do_orders()

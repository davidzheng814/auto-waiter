#!/usr/bin/python

from time import sleep
from api import *
from util import *
from config import *

RETRY_INTERVAL = 1
MAX_ATTEMPTS = 5

def do_orders(attempts=0):
    log('Daemon: starting task "do_orders"')

    if attempts > MAX_ATTEMPTS:
        raise get_menu_error('Exceeded maximum retries')

    days = range(get_day_of_week(), NUM_DAYS)
    if not days:
        log('No more days to order for this week')
        return

    menus = None
    sessions = get_user_sessions()
    if not sessions:
        log('No users detected. Exiting.')
        return

    for session in sessions:
        if menus is None:
            log('Getting menus for batch order')
            try:
                menus = [get_menus(session['cookie'], day) for day in days]
            except get_menu_error:
                # Not available yet, schedule a retry
                log('Unable to get menus. Will retry in {} seconds.'.format(RETRY_INTERVAL))
                sleep(RETRY_INTERVAL)
                return do_orders(attempts=attempts + 1)

        do_order(session, menus)

if __name__ == '__main__':
    do_orders()

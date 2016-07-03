#!/usr/bin/python

from time import sleep
from api import *
from util import *
from config import *

RETRY_INTERVAL = 1
MAX_ATTEMPTS = 5

parse_args()

def do_orders(attempts=0):
    log('Starting task "do_orders"', TRACE)

    if attempts > MAX_ATTEMPTS:
        log('"do_orders" exceed maximum retires. Exiting.', ERROR)
        raise get_menu_error('Exceeded maximum retries')

    days = range(get_day_of_week(), NUM_DAYS)
    if not days:
        log('No more days to order for this week', INFO)
        return

    menus = None
    sessions = get_user_sessions()
    if not sessions:
        log('No users detected. Exiting.', WARNING)
        return

    for session in sessions:
        if menus is None:
            log('Getting menus for batch order', TRACE)
            try:
                menus = [get_menus(session['cookie'], day) for day in days]
            except get_menu_error:
                # Not available yet, schedule a retry
                log('Unable to get menus. Will retry in {} seconds.', WARNING|INFO, RETRY_INTERVAL)
                sleep(RETRY_INTERVAL)
                return do_orders(attempts=attempts + 1)

        # Don't let an error for one user stop other users from ordering
        try:
            do_order(session, menus)
        except Exception as e:
            log('Error while ordering for user {username}: {error}', ERROR,
                username=session['username'], error=repr(e))

if __name__ == '__main__':
    do_orders()

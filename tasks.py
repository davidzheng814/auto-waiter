from celery import Celery
from api import *
from util import *

app = Celery('tasks')
app.config_from_object('celeryconfig')

RETRY_INTERVAL = 30
MAX_ATTEMPTS = 10

@app.task
def do_orders(attempts=0):
    if attempts > MAX_ATTEMPTS:
        raise get_menu_error

    menus = {}
    for session in get_user_sessions():
        for day_of_week in range(4):
            # We store menus in a dictionary so we only have to get them for the first user
            if day_of_week not in menus[day_of_week]:
                menus[day_of_week] = get_menus(session['cookie'], day_of_week)
                if menus[day_of_week] is None:
                    # Not available yet, schedule a retry
                    do_orders.apply_async(
                        do_orders, kwargs={'attempts':attempts + 1}, countdown=RETRY_INTERVAL)
                    return

            do_order(session, day_of_week, menus[day_of_week])

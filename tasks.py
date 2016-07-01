from celery import Celery
from api import *

app = Celery('tasks')
app.config_from_object('celeryconfig')

RETRY_INTERVAL = 30
MAX_ATTEMPTS = 10

@app.task
def do_orders(attempts=0):
    if attempts > MAX_ATTEMPTS:
        raise get_menu_error

    for session in get_user_sessions():
        for day_of_week in range(4):
            menus = get_menus(session, day_of_week)
            if menus is None:
                # Not available yet, schedule a retry
                do_orders.apply_async(
                    do_orders, kwargs={'attempts':attempts + 1}, countdown=RETRY_INTERVAL)
                return

            # TODO make an order

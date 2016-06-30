from celery import Celery
from api import *

app = Celery('tasks')
app.config_from_object('celeryconfig')

@app.task
def do_orders():
    # TODO: kick off a round of orders
    pass

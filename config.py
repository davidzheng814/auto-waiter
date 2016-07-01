"""Top level configurations for the app."""

import os
from celery.schedules import crontab

_BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Filesystem
DATA_DIR = os.path.join(_BASEDIR, 'data')
PREF_DIR = os.path.join(DATA_DIR, 'preferences') # User preferences
MENU_DIR = os.path.join(DATA_DIR, 'menus')       # Cached menus
os.makedirs(DATA_DIR)
os.makedirs(PREF_DIR)
os.makedirs(MENU_DIR)

DEBUG = True

# ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 6

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

# celery config
CELERY_TIMEZONE = 'America/Los_Angeles'

CELERYBEAT_SCHEDULE = {
    'do_orders': {
        'task': 'tasks.do_orders',
        'schedule': crontab(minute=20)
    }
}

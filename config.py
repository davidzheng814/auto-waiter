"""Top level configurations for the app."""

import os

_BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Autowaiter settings
BASE_URL = '127.0.0.1:5000'

# Filesystem
def guarantee_existence(dirs):
    '''
    For each directory in the given list, create it if it does not already exist
    '''
    for dirname in dirs:
        if not os.path.exists(dirname):
            os.makedirs(dirname)

DATA_DIR = os.path.join(_BASEDIR, 'data')
PREF_DIR = os.path.join(DATA_DIR, 'preferences') # User preferences
MENU_DIR = os.path.join(DATA_DIR, 'menus')       # Cached menus
guarantee_existence([DATA_DIR, PREF_DIR, MENU_DIR])

LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'auto_waiter.log')

DEBUG = True

# ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 6

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

# Waiter.com settings
VCS_URL = 'https://www.waiter.com/purestorage-dinner'
NUM_STORES = 4
HAS_SALAD_SPOT = True
NUM_DAYS = 3    # Short week because of the holiday. Change back to 4 next week

API_URL = 'https://www.waiter.com/api/v1'

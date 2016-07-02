"""Top level configurations for the app."""

import os

_BASEDIR = os.path.abspath(os.path.dirname(__file__))

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

# VCS settings
VCS_URL = 'https://www.waiter.com/vcs?site=627'
NUM_STORES = 2
HAS_SALAD_SPOT = False
NUM_DAYS = 7

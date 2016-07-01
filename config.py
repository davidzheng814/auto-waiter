"""Top level configurations for the app."""

import os
from util import *

_BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Filesystem
DATA_DIR = os.path.join(_BASEDIR, 'data')
PREF_DIR = os.path.join(DATA_DIR, 'preferences') # User preferences
MENU_DIR = os.path.join(DATA_DIR, 'menus')       # Cached menus
guarantee_existence([DATA_DIR, PREF_DIR, MENU_DIR])

DEBUG = True

# ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 6

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

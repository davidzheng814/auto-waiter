"""Top level configurations for the app."""
import os
_BASEDIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

# ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 6

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

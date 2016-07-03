#!/usr/bin/env python

"""
   Run the server for the app.
   Note: Run as root on production, and user locally.
"""
from getpass import getuser
from app import APP
from util import parse_args

parse_args()


if getuser() == "root":
    APP.run(debug=False, host="172.31.11.17", port=80)
else:
    APP.run(debug=True)

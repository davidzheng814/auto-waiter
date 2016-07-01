"""
   Run the server for the app.
   Note: Run as root on production, and user locally.
"""
from getpass import getuser
from subprocess import call

from app import APP

if getuser() == "root":
    APP.run(debug=False, host="172.31.11.17", port=80)
else:
    APP.run(debug=True)

# Kick off the scheduler
call(['celery', '-A', 'tasks', 'beat', '--detach'])
call(['celery', '-A', 'tasks', 'worker', '--detach'])

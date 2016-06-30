"""
   Run the server for the app.
   Note: Run as root on production, and user locally.
"""
from getpass import getuser
from subprocess import call

from app import APP

if getuser() == "root":
    APP.run(debug=True, host="172.16.110.25", port=80)
else:
    APP.run(debug=True)

# Kick off the scheduler
call(['celery', '-A', 'tasks', 'beat', '--detach'])
call(['celery', '-A', 'tasks', 'worker', '--detach'])
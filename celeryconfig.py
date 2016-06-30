from celery.schedules import crontab

CELERY_TIMEZONE = 'America/Los_Angeles'

CELERYBEAT_SCHEDULE = {
    'do_orders': {
        'task': 'tasks.do_orders',
        'schedule': crontab(minute=20)
    }
}

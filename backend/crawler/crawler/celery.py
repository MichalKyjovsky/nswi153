import os

from celery import Celery
from django.conf import settings

# Set the default value for environment variable so that the Celery knows where to find Django project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")
# Celery instance creation
app = Celery("crawler")
# Load settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")
#  Looks for Celery tasks from applications defined in settings.INSTALLED_APPS
redbeat_redis_url = "redis://localhost:6379/1"

app.conf.update(redbeat_redis_url=redbeat_redis_url, redbeat_lock_key=None)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


def celery_is_active():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = {ERROR_KEY: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the Redis server is running.'
        d = {ERROR_KEY: msg}
    except ImportError as e:
        d = {ERROR_KEY: str(e)}
    return ERROR_KEY not in d.keys()

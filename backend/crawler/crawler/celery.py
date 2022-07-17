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
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y
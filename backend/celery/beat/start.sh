#!/bin/bash

# celery_beat is the Celery beat process for scheduled tasks

set -o errexit
set -o nounset

rm -f './celerybeat.pid'
celery -A crawler beat -l INFO --pool=solo -S redbeat.RedBeatScheduler
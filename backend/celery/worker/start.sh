#!/bin/bash

set -o errexit
set -o nounset

#celery -A crawler worker -l INFO --pool=solo
celery -A crawler worker --scheduler redbeat.RedBeatScheduler -E -B -l INFO
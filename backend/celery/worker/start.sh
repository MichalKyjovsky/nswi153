#!/bin/bash

set -o errexit
set -o nounset

celery -A crawler worker -l INFO --pool=solo
import time

from celery import shared_task
from ..core.inspector.inspector import Inspector


@shared_task
def run_crawler_task(**kwargs):
    nodes = Inspector.crawl_url(kwargs['url'], kwargs['boundary'])
    return nodes

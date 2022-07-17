from celery import shared_task
import celery.schedules
from core.inspector.inspector import Inspector
from redbeat import RedBeatSchedulerEntry
from api.models import WebsiteRecord

from .transformer import transform_graph, persist_graph


@shared_task(name="Website Crawler")
def run_crawler_task(url: str, regex: str, record_id: int) -> None:
    nodes = Inspector.crawl_url(url, regex)
    persist_graph(*transform_graph(nodes, record_id))


def schedule_periodic_crawler_task(url: str, regex: str, record_id: int, interval: int) -> RedBeatSchedulerEntry:
    interval = celery.schedules.schedule(run_every=interval)  # seconds
    entry = RedBeatSchedulerEntry('Scheduled Website Crawler', 'run_crawler_task', interval,
                                  args=[url, regex, record_id])
    entry.save()

    return entry


def manage_tasks(record: WebsiteRecord):
    if record.active and record.interval:
        return schedule_periodic_crawler_task(record.url, record.regex, record.id, record.interval)
    elif not record.active or not record.interval:
        return run_crawler_task.delay(record.url, record.regex, record.id)

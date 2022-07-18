import sys

import celery.schedules
from core.inspector.inspector import Inspector
from redbeat import RedBeatSchedulerEntry
from api.models import WebsiteRecord

from .transformer import transform_graph, persist_graph
from crawler.celery import app


@app.task(bind=True)
def run_crawler_task(self, url: str, regex: str, record_id: int) -> None:
    nodes = Inspector.crawl_url(url, regex)
    persist_graph(*transform_graph(nodes, record_id))


def schedule_periodic_crawler_task(url: str, regex: str, record_id: int, interval: int) -> RedBeatSchedulerEntry:
    interval = celery.schedules.schedule(run_every=interval)  # seconds
    entry = RedBeatSchedulerEntry(f'task:{record_id}', 'tasks.crawler.run_crawler_task', interval,
                                  args=[url, regex, record_id], app=app)
    entry.save()

    return entry


def manage_tasks(record: WebsiteRecord, reschedule: bool = False):
    if 'test' in sys.argv:
        return 0

    if not reschedule:
        if record.interval:
            record.job_id = f'redbeat:task:{record.id}'
            task_id = schedule_periodic_crawler_task(record.url, record.regex, record.id, record.interval).key
            record.save()
            return task_id
        elif not record.interval:
            return run_crawler_task.delay(record.url, record.regex, record.id).id
    else:
        if record.active and record.interval:
            RedBeatSchedulerEntry.from_key(record.job_id, app=app).delete()
            return schedule_periodic_crawler_task(record.url, record.regex, record.id, record.interval).key
        elif not record.active:

            entry = RedBeatSchedulerEntry.from_key(record.job_id, app=app)
            if entry:
                entry.delete()
            return run_crawler_task.delay(record.url, record.regex, record.id).id


def stop_periodic_task(record: WebsiteRecord):
    if 'test' not in sys.argv:
        if record.job_id and record.interval:
            RedBeatSchedulerEntry.from_key(record.job_id, app=app).delete()


def start_periodic_task(record: WebsiteRecord):
    if 'test' not in sys.argv:
        if not record.job_id and record.interval:
            schedule_periodic_crawler_task(record.url, record.regex, record.id, record.interval)

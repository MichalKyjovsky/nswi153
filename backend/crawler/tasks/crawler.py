from celery import shared_task
from core.inspector.inspector import Inspector
from api.models import WebsiteRecord
from transformer import transform_graph, persist_graph


@shared_task
def run_crawler_task(url: str, regex: str, record_id: int) -> None:
    nodes = Inspector.crawl_url(url, regex)
    persist_graph(transform_graph(nodes, record_id))


def manage_tasks(record: WebsiteRecord):
    if record.active and record.interval:
        pass
    elif not record.active:
        run_crawler_task(record.url, record.regex, record.id)

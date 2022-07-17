from ..api.models import Edge, Node, WebsiteRecord
from django.db import transaction
from urllib.parse import urlsplit


def get_domain_graph(record: WebsiteRecord):
    edges = []

    # Get all edges of the current WebsiteRecord
    raw_edges = Edge.objects.filter(owner=record).all()

    for edge in raw_edges:
        edges.append({
            'source': f"{urlsplit(edge.source.url).netloc}",
            'target': f"{urlsplit(edge.target.url).netloc}",
        })

    # Make the edges unique
    return list(set(edges))



def transform_graph(raw_nodes: list, record_id: int) -> [list, list]:
    """
    Transforms raw nodes from crawler into the list of nodes and edges that can be persistable into the database.
    Args:
        raw_nodes: List of raw nodes crawled by Inspector class
        record_id: Actual WebsiteRecord ID

    Returns:
        Lists of nodes and nodes that matches database model definition.
    """
    nodes = []
    edges = []

    for node in raw_nodes:
        nodes.append({
            'title': node['title'],
            'crawl_time': node['crawl_time'],
            'url': node['url'],
            # This is an expensive operation but I am not into implement json serializer
            'owner': WebsiteRecord.objects.filter(id=record_id).first()
        })

        edges += [{'source': node['url'], 'target': target} for target in node['executionTargets']]

    return nodes, edges


def persist_graph(nodes: list, edges: list) -> None:
    """

    Args:
        nodes:
        edges:
    """
    db_nodes = [Node.objects.create_node(raw_node) for raw_node in nodes]

    # Store all nodes securely
    with transaction.atomic():
        for db_node in db_nodes:
            db_node.save()

    # Create list of db_edges
    db_edges = []

    for edge in edges:
        source_node = next((x for x in db_nodes if x.url == edge['source']), None)
        target_node = next((x for x in db_nodes if x.url == edge['target']), None)
        db_edges.append(Edge.objects.create_edge({"source": source_node, "target": target_node}))

    # Store all nodes securely
    with transaction.atomic():
        for db_edge in db_edges:
            db_edge.save()

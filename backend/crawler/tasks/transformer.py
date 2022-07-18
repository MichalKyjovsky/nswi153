import json

from django.core import serializers

from api.models import Edge, Node, WebsiteRecord
from django.db import transaction
from urllib.parse import urlsplit


def get_graph(raw_edges: list, raw_nodes: list, domain: bool = True):
    json_serializer = serializers.get_serializer("json")
    serializer = json_serializer()

    if domain:
        edges_preprocessed = []

        for edge in raw_edges:
            edges_preprocessed.append({
                "model": 'api.edge',
                'source': {
                    "url": f"{urlsplit(edge.source.url).netloc}",
                    "crawl_time": edge.source.crawl_time,
                    "owner": edge.source.owner.id
                },
                'target': {
                    "url": f"{urlsplit(edge.target.url).netloc}",
                    "crawl_time": edge.target.crawl_time,
                    "owner": edge.target.owner.id
                },
            })

        seen = set()
        edges = []

        url_to_id_mapper = dict()
        id_mapper = 1

        # Make nodes and edges unique
        for edge in edges_preprocessed:
            if (edge['source']['url'], edge['target']['url']) not in seen:
                seen.add((edge['source']['url'], edge['target']['url']))
                edges.append(edge)
                # create map of url -> ID from 1
                if edge['source']['url'] not in url_to_id_mapper:
                    url_to_id_mapper[edge['source']['url']] = id_mapper
                    id_mapper += 1
                if edge['target']['url'] not in url_to_id_mapper:
                    url_to_id_mapper[edge['target']['url']] = id_mapper
                    id_mapper += 1

        serialized_nodes = []
        serialized_edges = []

        added_nodes = set()
        for i in range(len(edges)):
            source_id = url_to_id_mapper[edges[i]['source']['url']]
            target_id = url_to_id_mapper[edges[i]['target']['url']]
            # add every node EXACTLY once
            if source_id not in added_nodes:
                serialized_nodes.append(
                    {
                        'model': 'api.node',
                        'pk': source_id,
                        'fields': edges[i]['source']
                    }
                )
                added_nodes.add(source_id)
            if target_id not in added_nodes:
                serialized_nodes.append(
                    {
                        'model': 'api.node',
                        'pk': target_id,
                        'fields': edges[i]['target']
                    }
                )
                added_nodes.add(target_id)
            serialized_edges.append(
                {
                    'model': 'api.edge',
                    'pk': i,
                    'fields': {
                        'source': source_id,
                        'target': target_id
                    }
                }
            )

    else:
        nodes_filtered = raw_nodes
        edges_filtered = raw_edges

        serialized_edges = json.loads(serializer.serialize(edges_filtered))
        serialized_nodes = json.loads(serializer.serialize(nodes_filtered))

    return {"nodes": serialized_nodes, "edges": serialized_edges}


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
            # This is an expensive operation, but I am not into implement json serializer
            'owner': WebsiteRecord.objects.filter(id=record_id).first(),
            'boundary_node': node['boundary_node']
        })

        edges += [{'source': node['url'], 'target': target} for target in node['execution_targets']]

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

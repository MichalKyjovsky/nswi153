from api.models import Edge, Node


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
            'owner': record_id
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

    # Store all nodes
    Node.objects.bulk_create(db_nodes)

    # Create list of db_edges

    db_edges = []

    for source, target in edges:
        source_node = filter(lambda x: x.url == source, db_nodes)
        target_node = filter(lambda x: x.url == target, db_nodes)
        db_edges.append(Edge.objects.create_edge(source_node=source_node, target_node=target_node))

    Edge.objects.bulk_create(db_edges)


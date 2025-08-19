import numpy as np
from skan import Skeleton, summarize
import networkx as nx


def build_graph_from_skeleton(skeleton: np.ndarray):
    """
    Builds a graph representation from a skeleton image.
    Uses skan to analyze the skeleton and extract branches and nodes.
    """
    skel_bool = skeleton.astype(bool)
    graph_obj = Skeleton(skel_bool)
    summary = summarize(graph_obj, separator='_')

    G = nx.Graph()

    # Get node degrees directly from the Skeleton object, which is reliable
    node_degrees = graph_obj.degrees

    # Add all nodes first by iterating through the branches
    for _, branch in summary.iterrows():
        for node_prefix in ['src', 'dst']:
            node_id = int(branch[f'node_id_{node_prefix}'])

            if not G.has_node(node_id):
                # Get the degree of the current node
                degree = node_degrees[node_id]

                # Determine node type
                if degree == 1:
                    kind = 'endpoint'
                elif degree >= 3:
                    kind = 'junction'
                else: # degree 2
                    kind = 'path'

                G.add_node(
                    node_id,
                    pos=(branch[f'coord_{node_prefix}_1'], branch[f'coord_{node_prefix}_0']), # (x, y)
                    kind=kind
                )

    # Add edges
    for _, edge in summary.iterrows():
        u, v = int(edge['node_id_src']), int(edge['node_id_dst'])
        if u != v:
            G.add_edge(
                u, v,
                id=int(edge['skeleton_id']),
                length=edge['branch_distance'],
                coords=graph_obj.path_coordinates(int(edge['skeleton_id']))
            )

    return G, summary


def prune_graph(G: nx.Graph, prune_ratio: float):
    """
    Iteratively prunes short, dangling branches from the graph.
    A dangling branch is an edge connected to a degree-1 node (an endpoint).
    """
    if not G.nodes or not G.edges:
        return G

    edge_lengths = [data['length'] for _, _, data in G.edges(data=True)]
    if not edge_lengths:
        return G

    mean_edge_length = np.mean(edge_lengths)
    threshold = prune_ratio * mean_edge_length

    while True:
        removed = False
        # In NetworkX 2.x, G.degree() is a DegreeView, which is dict-like
        endpoints = [node for node, degree in G.degree() if degree == 1]

        edges_to_remove = []
        for node in endpoints:
            if G.degree(node) != 1: continue # Node degree might have changed in this loop

            neighbor = list(G.neighbors(node))[0]
            edge_data = G.get_edge_data(node, neighbor)

            if edge_data and edge_data['length'] < threshold:
                edges_to_remove.append((node, neighbor))

        if not edges_to_remove:
            break

        for u, v in edges_to_remove:
            if G.has_edge(u, v):
                G.remove_edge(u, v)
                if G.degree(u) == 0:
                    G.remove_node(u)
                if G.degree(v) == 0:
                    G.remove_node(v)
                removed = True

        if not removed:
            break

    return G

def fill_gaps(G: nx.Graph, max_gap_px: float):
    """
    Placeholder for gap-filling logic.
    """
    return G

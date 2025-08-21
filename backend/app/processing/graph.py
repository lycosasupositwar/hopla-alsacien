import numpy as np
from skan import Skeleton, summarize
import networkx as nx


def build_graph_from_skeleton(skeleton: np.ndarray):
    """
    Builds a graph representation from a skeleton image using skan and networkx.
    This version uses manual iteration to ensure no attribute dictionaries are shared,
    which is a robust way to avoid subtle bugs in library helpers.
    """
    skel_bool = skeleton.astype(bool)
    graph_obj = Skeleton(skel_bool)
    summary = summarize(graph_obj)

    G = nx.Graph()

    if summary.empty:
        return G, summary

    # Add nodes and edges manually from the summary DataFrame
    for _, row in summary.iterrows():
        # Add source and destination nodes, if they don't already exist
        for prefix in ['src', 'dst']:
            node_id = int(row[f'node-id-{prefix}'])
            if not G.has_node(node_id):
                degree = graph_obj.degrees[node_id]
                kind = 'path'
                if degree == 1:
                    kind = 'endpoint'
                elif degree >= 3:
                    kind = 'junction'

                # skan provides coords as (row, col), which is (y, x).
                # We store them internally as (x, y) for consistency with shapely/rendering
                pos_x = row[f'coord-{prefix}-1']
                pos_y = row[f'coord-{prefix}-0']
                G.add_node(node_id, kind=kind, pos=(pos_x, pos_y))

        # Add the edge with its own unique attribute dictionary
        u, v = int(row['node-id-src']), int(row['node-id-dst'])
        if u != v:
            # skan provides coords as (row, col), which is (y, x).
            # We store them internally as (x, y).
            # It's crucial to perform this flip ONCE here.
            path_coords = graph_obj.path_coordinates(int(row['skeleton-id']))
            path_coords_xy = np.fliplr(path_coords)

            G.add_edge(
                u,
                v,
                id=int(row['skeleton-id']),
                length=row['branch-distance'],
                coords=path_coords_xy.copy() # Stored as (x, y)
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

    median_edge_length = np.median(edge_lengths)
    threshold = prune_ratio * median_edge_length

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

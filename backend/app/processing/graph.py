import numpy as np
from skan import Skeleton, summarize
import networkx as nx


def build_graph_from_skeleton(skeleton: np.ndarray):
    """
    Builds a graph representation from a skeleton image using skan and networkx.
    This version uses a more robust method of graph creation from a pandas edgelist.
    """
    skel_bool = skeleton.astype(bool)
    # The `skan.Skeleton` object is the main interface to the skeleton data
    graph_obj = Skeleton(skel_bool)
    # The `summarize` function returns a pandas DataFrame with branch information
    summary = summarize(graph_obj)

    # If no branches are found, return an empty graph
    if summary.empty:
        return nx.Graph(), summary

    # Create the graph directly from the pandas DataFrame edgelist
    # This is more robust than manual iteration
    G = nx.from_pandas_edgelist(
        summary,
        source='node-id-src',
        target='node-id-dst',
        edge_attr=['branch-distance', 'skeleton-id'],
    )

    # Add node attributes (like position and kind) after creation
    for node_id in G.nodes:
        # The degree of the node in the context of the whole skeleton
        degree = graph_obj.degrees[node_id]
        kind = 'path' # Default kind
        if degree == 1:
            kind = 'endpoint'
        elif degree >= 3:
            kind = 'junction'
        G.nodes[node_id]['kind'] = kind

        # Find the node's coordinates from its first appearance in the summary
        # Check if it appears as a source node
        src_rows = summary[summary['node-id-src'] == node_id]
        if not src_rows.empty:
            row = src_rows.iloc[0]
            # skan provides coords as (row, col), which is (y, x)
            G.nodes[node_id]['pos'] = (row['coord-src-1'], row['coord-src-0'])
            continue

        # If not found as a source, check as a destination node
        dst_rows = summary[summary['node-id-dst'] == node_id]
        if not dst_rows.empty:
            row = dst_rows.iloc[0]
            G.nodes[node_id]['pos'] = (row['coord-dst-1'], row['coord-dst-0'])

    # Add path coordinates and rename 'branch-distance' to 'length' for consistency
    for u, v, data in G.edges(data=True):
        skeleton_id = data['skeleton-id']
        path_coords = graph_obj.path_coordinates(skeleton_id)
        G[u][v]['coords'] = path_coords
        G[u][v]['length'] = data['branch-distance']
        # The original 'branch-distance' and 'skeleton-id' keys can be removed if desired
        # but leaving them is harmless.

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

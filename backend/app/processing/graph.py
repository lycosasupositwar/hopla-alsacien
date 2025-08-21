import numpy as np
from skan import Skeleton, summarize
import networkx as nx
import pandas as pd

def build_graph_from_skeleton(skeleton: np.ndarray):
    """
    Builds a graph representation from a skeleton image using skan and networkx.
    This version uses skan.summarize() to identify all paths and their IDs,
    then fetches the coordinates for each path ID from the Skeleton object.
    This is more robust than iterating from 0..n_paths.
    """
    skel_bool = skeleton.astype(bool)
    graph_obj = Skeleton(skel_bool)

    # Use summarize to get a dataframe of all branches. The index of this
    # dataframe contains the correct, unique path IDs.
    summary_df = summarize(graph_obj, separator='-')

    G = nx.Graph()
    node_map = {}
    next_node_id = 0

    # Iterate over the paths identified by summarize()
    for path_id, branch_data in summary_df.iterrows():
        # Get start and end node pixel indices from the summary
        start_node_idx = int(branch_data['node-id-src'])
        end_node_idx = int(branch_data['node-id-dst'])

        # Get or create node for the start pixel
        if start_node_idx not in node_map:
            node_map[start_node_idx] = next_node_id
            pos_y, pos_x = np.unravel_index(start_node_idx, skeleton.shape)
            G.add_node(next_node_id, pos=(int(pos_x), int(pos_y)))
            next_node_id += 1

        # Get or create node for the end pixel
        if end_node_idx not in node_map:
            node_map[end_node_idx] = next_node_id
            pos_y, pos_x = np.unravel_index(end_node_idx, skeleton.shape)
            G.add_node(next_node_id, pos=(int(pos_x), int(pos_y)))
            next_node_id += 1

        u = node_map[start_node_idx]
        v = node_map[end_node_idx]

        if u == v:
            continue

        # Fetch the path coordinates using the correct path_id from the summary
        path_coords = graph_obj.path_coordinates(path_id)
        path_coords_xy = np.fliplr(path_coords)

        G.add_edge(
            u,
            v,
            id=int(path_id),
            length=branch_data['branch-distance'],
            coords=path_coords_xy.copy()
        )

    # The rest of the pipeline expects a summary dataframe.
    # We can return the one we generated.
    return G, summary_df


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

    # Using median is more robust to outliers than mean
    median_edge_length = np.median(edge_lengths)
    threshold = prune_ratio * median_edge_length

    while True:
        removed = False
        # We need to compute degrees on each iteration as they change.
        degrees = dict(G.degree())
        endpoints = [node for node, degree in degrees.items() if degree == 1]

        if not endpoints:
            break

        edges_to_remove = []
        for node in endpoints:
            # Node degree might have changed if a connected edge was removed in a previous pass
            # This check is redundant in this specific loop structure but is good practice
            if G.degree(node) != 1: continue

            # There should be exactly one neighbor for a degree-1 node
            neighbor = list(G.neighbors(node))[0]
            edge_data = G.get_edge_data(node, neighbor)

            if edge_data and edge_data['length'] < threshold:
                edges_to_remove.append((node, neighbor))

        if not edges_to_remove:
            break

        for u, v in edges_to_remove:
            if G.has_edge(u, v):
                G.remove_edge(u, v)
                # Check if nodes have become isolated and remove them
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

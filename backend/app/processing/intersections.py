from typing import List, Dict, Any
import numpy as np
import networkx as nx
from shapely.geometry import LineString, MultiLineString, Point
from sklearn.cluster import DBSCAN

# Normative scoring profiles
NORM_PROFILES = {
    "ASTM": {"jonction": 1.5, "régulière": 1.0, "extrémité": 0.5},
    "Circular": {"jonction": 2.0, "régulière": 1.0, "extrémité": 0.5}
}


def detect_and_cluster_intersections(
    motifs: List[Dict[str, Any]],
    graph: nx.Graph,
    epsilon_px: float,
    norm_profile: str = "ASTM"
) -> List[Dict[str, Any]]:
    """
    Detects, clusters, classifies, and scores intersections between motifs and the skeleton graph.
    """
    # 1. Vectorize the skeleton graph into a single MultiLineString for efficient intersection
    all_edges = []
    for u, v, data in graph.edges(data=True):
        # coords from skan are (row, col) -> (y, x)
        coords = data.get('coords')
        if coords is not None and len(coords) >= 2:
            # The graph now stores coords in (x, y) format directly.
            all_edges.append(LineString(coords))

    skeleton_multiline = MultiLineString(all_edges)

    # 2. Detect all raw intersection points
    raw_intersections = []
    motif_ids_map = [] # To track which motif an intersection belongs to

    for motif in motifs:
        motif_geom = motif["geometry"]
        intersection_obj = skeleton_multiline.intersection(motif_geom)

        if intersection_obj.is_empty:
            continue

        points = []
        # A shapely intersection can return a Point, LineString, a multi-part
        # geometry (e.g., MultiPoint), or a collection of geometries.
        # We need to robustly handle all of these cases.
        geoms_to_process = []
        if hasattr(intersection_obj, 'geoms'): # Handles multi-part geometries
            geoms_to_process.extend(intersection_obj.geoms)
        else: # Handles single geometries
            geoms_to_process.append(intersection_obj)

        for geom in geoms_to_process:
            if isinstance(geom, Point):
                points.append(geom)
            elif isinstance(geom, LineString) and not geom.is_empty:
                # If lines overlap, take the start and end points of the overlap
                points.append(Point(geom.coords[0]))
                points.append(Point(geom.coords[-1]))

        for p in points:
            raw_intersections.append([p.x, p.y])
            motif_ids_map.append(motif["id"])

    if not raw_intersections:
        return []

    # 3. Cluster intersections using DBSCAN
    X = np.array(raw_intersections)
    db = DBSCAN(eps=epsilon_px, min_samples=1).fit(X)
    labels = db.labels_

    # 4. Process each cluster to create a single intersection record
    classified_intersections = []

    # Get node positions for classification
    junction_nodes = {data['pos']: nid for nid, data in graph.nodes(data=True) if graph.degree(nid) >= 3}
    endpoint_nodes = {data['pos']: nid for nid, data in graph.nodes(data=True) if graph.degree(nid) == 1}

    score_rules = NORM_PROFILES.get(norm_profile, NORM_PROFILES["ASTM"])

    for cluster_id in set(labels):
        if cluster_id == -1: continue # Noise point, should not happen with min_samples=1

        cluster_points = X[labels == cluster_id]
        cluster_motif_ids = [motif_ids_map[i] for i, label in enumerate(labels) if label == cluster_id]

        # Representative point is the centroid of the cluster
        center_x, center_y = np.mean(cluster_points, axis=0)

        # 5. Classify the cluster
        intersection_type = "régulière" # Default type

        # Check for proximity to a junction node
        is_junction = False
        for pos, nid in junction_nodes.items():
            dist = np.sqrt((center_x - pos[0])**2 + (center_y - pos[1])**2)
            if dist <= epsilon_px:
                intersection_type = "jonction"
                is_junction = True
                break

        # If not a junction, check for proximity to an endpoint node
        if not is_junction:
            for pos, nid in endpoint_nodes.items():
                dist = np.sqrt((center_x - pos[0])**2 + (center_y - pos[1])**2)
                if dist <= epsilon_px:
                    intersection_type = "extrémité"
                    break

        # Assign score
        score = score_rules.get(intersection_type, 1.0)

        classified_intersections.append({
            "id": int(cluster_id) + 1,
            "x": center_x,
            "y": center_y,
            "type": intersection_type,
            "score": score,
            # For simplicity, we assign the motif_id of the first point in the cluster
            "motif_id": cluster_motif_ids[0]
        })

    return classified_intersections

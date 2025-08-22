import sys
from typing import List, Dict, Any
import numpy as np
from shapely.geometry import LineString, Point


def generate_motifs(image_shape: tuple, params: Dict[str, Any], seed: int) -> List[Dict[str, Any]]:
    """
    Generates a list of test patterns (motifs) based on the provided parameters.
    """
    motif_type = params.get("type", "linear")
    rng = np.random.default_rng(seed)

    if motif_type == "linear":
        return _generate_linear_motifs(image_shape, params, rng)
    elif motif_type == "circular":
        return _generate_circular_motifs(image_shape, params, rng)
    else:
        raise ValueError(f"Unknown motif type: {motif_type}")


def _generate_linear_motifs(image_shape: tuple, params: Dict[str, Any], rng) -> List[Dict[str, Any]]:
    debug_log = ["--- MOTIF DEBUG LOG ---"]
    motifs = []
    h, w = image_shape
    debug_log.append(f"Image shape (h, w) = ({h}, {w})")
    debug_log.append(f"Received params = {params}")

    count = params.get("count", 10)
    length_px = params.get("length_px", min(h, w) * 0.8)
    orientations = params.get("orientations", [0, 45, 90, 135])
    debug_log.append(f"Using count={count}, length_px={length_px}, orientations={orientations}")

    for i in range(count):
        debug_log.append(f"\n--- Iteration {i} ---")
        # Choose a random orientation
        angle_deg = rng.choice(orientations)
        angle_rad = np.deg2rad(angle_deg)
        debug_log.append(f"angle_deg={angle_deg}")

        # Define a safe area for the center of the line to be generated
        pad_x = w * 0.1
        pad_y = h * 0.1
        low_x, high_x = pad_x, w - pad_x
        low_y, high_y = pad_y, h - pad_y

        if low_x >= high_x or low_y >= high_y:
            center_x, center_y = w/2, h/2
        else:
            center_x = rng.uniform(low_x, high_x)
            center_y = rng.uniform(low_y, high_y)
        debug_log.append(f"center_x={center_x}, center_y={center_y}")

        # Calculate start and end points
        dx = (length_px / 2) * np.cos(angle_rad)
        dy = (length_px / 2) * np.sin(angle_rad)
        x1, y1 = center_x - dx, center_y - dy
        x2, y2 = center_x + dx, center_y + dy
        debug_log.append(f"line points (x1,y1) to (x2,y2) = ({x1},{y1}) to ({x2},{y2})")

        # Clip line to image boundaries to be safe
        line = LineString([(x1, y1), (x2, y2)])
        bounds = LineString([(0,0), (w,0), (w,h), (0,h), (0,0)])
        clipped_line = line.intersection(bounds.buffer(0.1))

        if clipped_line.is_empty or not isinstance(clipped_line, LineString):
            debug_log.append(f"Skipping: Clipped line is empty or not a LineString. Type is {type(clipped_line)}")
            continue

        final_coords = list(clipped_line.coords)
        debug_log.append(f"Clipped line has {len(final_coords)} points.")

        if len(final_coords) < 2:
            debug_log.append(f"Skipping: Not enough points in clipped line.")
            continue

        motifs.append({
            "id": f"L-{i}",
            "type": "linear",
            "geometry": LineString(final_coords),
            "length_px": clipped_line.length
        })
        debug_log.append(f"OK: Successfully created motif {i}.")

    if not motifs:
        # If we're about to return an empty list, raise an exception with the debug log.
        raise ValueError("Failed to generate any valid motifs. Log:\n" + "\n".join(debug_log))

    return motifs


def _generate_circular_motifs(image_shape: tuple, params: Dict[str, Any], rng) -> List[Dict[str, Any]]:
    motifs = []
    h, w = image_shape
    center_x, center_y = w / 2, h / 2

    count = params.get("count", 3) # Number of concentric circles
    max_radius = min(w, h) / 2 * 0.95

    # Generate 'count' circles with radii evenly spaced up to the max_radius
    radii = np.linspace(max_radius / count, max_radius, count)

    for i, r in enumerate(radii):
        if r > 0:
            # Shapely represents a circle as a point buffer
            circle = Point(center_x, center_y).buffer(r).exterior
            motifs.append({
                "id": f"C-{i}",
                "type": "circular",
                "geometry": circle,
                "length_px": circle.length
            })

    return motifs

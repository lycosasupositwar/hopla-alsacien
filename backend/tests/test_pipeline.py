import os
import cv2
import numpy as np
import pytest
import networkx as nx

# Add project root to path to allow absolute imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.processing.preprocess import preprocess_image
from app.processing.skeleton import skeletonize_image, estimate_border_width
from app.processing.graph import build_graph_from_skeleton
from app.processing.motifs import generate_motifs
from app.processing.intersections import detect_and_cluster_intersections
from app.processing.metrics import compute_final_metrics

# Define paths to test images
INPUT_DIR = os.path.join(os.path.dirname(__file__), '../../examples/input')
STD_VORONOI_IMG_PATH = os.path.join(INPUT_DIR, "synthetic_voronoi_standard.png")
Y_JUNCTION_IMG_PATH = os.path.join(INPUT_DIR, "synthetic_y_junction.png")

# Pytest fixture to load a standard image
@pytest.fixture
def standard_image():
    img = cv2.imread(STD_VORONOI_IMG_PATH, cv2.IMREAD_GRAYSCALE)
    assert img is not None, f"Failed to load image at {STD_VORONOI_IMG_PATH}"
    return img

@pytest.fixture
def y_junction_image():
    img = cv2.imread(Y_JUNCTION_IMG_PATH, cv2.IMREAD_GRAYSCALE)
    assert img is not None, f"Failed to load image at {Y_JUNCTION_IMG_PATH}"
    return img

def test_preprocess_separates_grains(standard_image):
    """Test that preprocessing produces a clean, binary image."""
    binary_img = preprocess_image(standard_image, area_opening_min_size_px=100)

    assert binary_img is not None
    assert binary_img.dtype == np.uint8
    # Check that it's a binary image (only 0 and 255)
    assert np.all(np.unique(binary_img) <= [0, 255])
    # Check that there is significant content
    assert np.mean(binary_img) > 1, "Preprocessing resulted in a nearly empty image."

def test_skeleton_graph_build(standard_image):
    """Test skeletonization and graph construction."""
    binary_img = preprocess_image(standard_image, area_opening_min_size_px=100)
    skeleton = skeletonize_image(binary_img)

    assert skeleton.any(), "Skeletonization resulted in an empty image."

    graph, _ = build_graph_from_skeleton(skeleton)

    assert isinstance(graph, nx.Graph)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

def test_skeleton_graph_detects_junctions(y_junction_image):
    """Use a synthetic Y-junction to ensure junctions are detected correctly."""
    binary_img = preprocess_image(y_junction_image, adaptive_block_size=51, area_opening_min_size_px=10)
    skeleton = skeletonize_image(binary_img)
    graph, _ = build_graph_from_skeleton(skeleton)

    degrees = [d for _, d in graph.degree()]
    # We expect at least one node of degree 3 (the junction)
    assert 3 in degrees, f"Failed to find a junction (degree 3 node). Degrees found: {degrees}"

def test_full_pipeline_and_metrics_calculation(standard_image):
    """
    Test the full pipeline from image to metrics to ensure everything runs
    and produces plausible results.
    """
    # 1. Preprocessing
        # For the clean synthetic image, disable morphological operations
        # that might erase the thin lines.
    params = {
            "gaussian_sigma": 1.0,
            "adaptive_block_size": 101,
            "adaptive_offset": 10,
            "morph_open_kernel": 0,
            "area_opening_min_size_px": 0 # Disable area opening
    }
    binary_img = preprocess_image(standard_image, **params)

    # 2. Skeletonization
    skeleton = skeletonize_image(binary_img)
    border_width = estimate_border_width(binary_img, skeleton)
    assert border_width > 0

    # 3. Graph
    graph, _ = build_graph_from_skeleton(skeleton)

    # 4. Motifs
    h, w = standard_image.shape
    motif_params = {"type": "linear", "count": 5, "length_px": w, "orientations": [0, 90]}
    motifs = generate_motifs((h, w), motif_params, seed=42)
    assert len(motifs) > 0

    # 5. Intersections
    intersections = detect_and_cluster_intersections(motifs, graph, epsilon_px=border_width * 1.5)
    assert len(intersections) > 0, "No intersections were found."

    # 6. Metrics
    pixel_size_um = 1.0 # Assume 1 um/px for test
    metrics, warnings = compute_final_metrics(motifs, intersections, pixel_size_um)

    assert metrics.L_mm > 0
    assert metrics.N_int > 0
    assert metrics.ell_um > 0
    assert metrics.G != 0
    assert "No intersections found" not in " ".join(warnings)
    print(f"Test pipeline successful. Calculated G = {metrics.G:.3f}")

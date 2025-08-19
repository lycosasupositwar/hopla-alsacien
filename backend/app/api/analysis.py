import time
import json
import cv2
import numpy as np
from flask import Blueprint, request, jsonify

from ..schemas.models import AnalysisParameters, AnalysisResult, EdgeStats, Timings, Overlays
from ..utils.image_utils import read_image_from_bytes, encode_image_to_base64, create_overlay_image
from ..processing.preprocess import preprocess_image
from ..processing.skeleton import skeletonize_image, estimate_border_width
from ..processing.graph import build_graph_from_skeleton, prune_graph
from ..processing.motifs import generate_motifs
from ..processing.intersections import detect_and_cluster_intersections
from ..processing.metrics import compute_final_metrics

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_image():
    start_total_time = time.time()

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()

    try:
        original_image = read_image_from_bytes(image_bytes)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Load and merge parameters
    default_params = AnalysisParameters()
    try:
        user_params = json.loads(request.form.get('params', '{}'))
        params = default_params.model_copy(update=user_params)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in params field"}), 400

    pixel_size_um = float(request.form.get('pixel_size_um', 1.0))
    if pixel_size_um <= 0:
        return jsonify({"error": "pixel_size_um must be positive"}), 400

    # --- Full Processing Pipeline ---
    timings = {}

    # 1. Preprocessing
    start_time = time.time()
    binary_image = preprocess_image(
        original_image,
        params.gaussian_sigma,
        params.adaptive_block_size,
        params.adaptive_offset,
        params.morph_open_kernel,
        params.area_opening_min_size_px
    )
    timings["preprocess_s"] = time.time() - start_time

    # 2. Skeletonization & Border Width
    start_time = time.time()
    skeleton = skeletonize_image(binary_image)
    timings["skeleton_s"] = time.time() - start_time

    start_time = time.time()
    border_width = estimate_border_width(binary_image, skeleton)
    timings["border_width_s"] = time.time() - start_time

    # 3. Graph Construction and Pruning
    start_time = time.time()
    graph, _ = build_graph_from_skeleton(skeleton)
    pruned_graph = prune_graph(graph, params.skeleton_prune_ratio)
    timings["graph_s"] = time.time() - start_time

    # 4. Motif Generation
    motifs = generate_motifs(original_image.shape[:2], params.motifs, params.random_seed)

    # 5. Intersection Detection
    start_time = time.time()
    epsilon = border_width * params.epsilon_factor
    intersections = detect_and_cluster_intersections(
        motifs, pruned_graph, epsilon, params.norm_profile
    )
    timings["intersections_s"] = time.time() - start_time

    # 6. Final Metrics Calculation
    metrics, warnings = compute_final_metrics(motifs, intersections, pixel_size_um)

    # --- Assemble Response ---

    # Edge Stats
    edge_lengths = [d['length'] for _, _, d in pruned_graph.edges(data=True)]
    edge_stats = EdgeStats(
        n_nodes=pruned_graph.number_of_nodes(),
        n_edges=pruned_graph.number_of_edges(),
        mean_edge_length_px=np.mean(edge_lengths) if edge_lengths else 0
    )

    # Create Overlays
    annotated_overlay = create_overlay_image(original_image, skeleton, motifs, intersections)
    skeleton_only_overlay = create_overlay_image(np.zeros_like(original_image), skeleton=skeleton)
    motifs_only_overlay = create_overlay_image(np.zeros_like(original_image), motifs=motifs)

    overlays = Overlays(
        annotated_png_base64=encode_image_to_base64(annotated_overlay),
        skeleton_png_base64=encode_image_to_base64(skeleton_only_overlay),
        motifs_png_base64=encode_image_to_base64(motifs_only_overlay)
    )

    timings["total_s"] = time.time() - start_total_time

    final_result = AnalysisResult(
        metrics=metrics,
        intersections=intersections,
        edges_stats=edge_stats,
        overlays=overlays,
        warnings=warnings,
        timings=Timings(**timings),
        params_used=params
    )

    return jsonify(final_result.model_dump())

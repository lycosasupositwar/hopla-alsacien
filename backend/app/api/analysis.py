import time
import json
import cv2
import numpy as np
from flask import Blueprint, request, jsonify

from ..schemas.models import AnalysisParameters, AnalysisResult, EdgeStats, Timings, Overlays, DebugOverlays, DebugStats
from ..utils.image_utils import read_image_from_bytes, encode_image_to_base64, create_overlay_image, draw_graph_on_image
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
    try:
        default_params = AnalysisParameters()
        user_params_dict = json.loads(request.form.get('params', '{}'))

        # Create a new model instance with updated parameters
        # This works for both Pydantic v1 and v2
        updated_params_dict = default_params.dict()
        updated_params_dict.update(user_params_dict)
        params = AnalysisParameters(**updated_params_dict)

    except (json.JSONDecodeError, TypeError) as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400

    pixel_size_um = float(request.form.get('pixel_size_um', 1.0))
    if pixel_size_um <= 0:
        return jsonify({"error": "pixel_size_um must be positive"}), 400

    # --- Full Processing Pipeline ---
    try:
        timings = {}

        # 1. Preprocessing
        start_time = time.time()
        binary_image = preprocess_image(
            original_image,
            params.gaussian_sigma,
            params.adaptive_block_size,
            params.adaptive_offset,
            params.morph_open_kernel,
            params.area_opening_min_size_px,
            params.detect_twins
        )
        timings["preprocess_s"] = time.time() - start_time

        # Encode for debugging
        debug_binary_base64 = encode_image_to_base64(binary_image)

        # 2. Skeletonization & Border Width
        start_time = time.time()
        skeleton = skeletonize_image(binary_image)
        timings["skeleton_s"] = time.time() - start_time

        # Encode for debugging
        # The skeleton is boolean, so we convert to uint8 for encoding
        debug_skeleton_base64 = encode_image_to_base64((skeleton * 255).astype(np.uint8))

        start_time = time.time()
        border_width = estimate_border_width(binary_image, skeleton)
        timings["border_width_s"] = time.time() - start_time

        # 3. Graph Construction and Pruning
        start_time = time.time()
        graph, _ = build_graph_from_skeleton(skeleton)

        # Capture stats before pruning
        nodes_before = graph.number_of_nodes()
        edges_before = graph.number_of_edges()

        pruned_graph = prune_graph(graph.copy(), params.skeleton_prune_ratio) # Important: prune a copy

        # Capture stats after pruning
        nodes_after = pruned_graph.number_of_nodes()
        edges_after = pruned_graph.number_of_edges()

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

    except Exception as e:
        # Catch any unexpected errors during the complex processing pipeline
        # and return a helpful error message.
        return jsonify({
            "error": f"An unexpected error occurred during image processing: {str(e)}"
        }), 500

    # --- Assemble Response ---

    # Draw the pruned graph for debugging
    pruned_graph_image = draw_graph_on_image(pruned_graph, original_image.shape)
    debug_pruned_graph_base64 = encode_image_to_base64(pruned_graph_image)

    # Create overlays for debugging and final output
    motifs_only_overlay = create_overlay_image(np.zeros_like(original_image), motifs=motifs)
    motifs_only_base64 = encode_image_to_base64(motifs_only_overlay)

    # Create debug overlays object
    debug_overlays = DebugOverlays(
        binary_image_base64=debug_binary_base64,
        skeleton_image_base64=debug_skeleton_base64,
        pruned_graph_image_base64=debug_pruned_graph_base64,
        motifs_image_base64=motifs_only_base64,
    )

    # Edge Stats & Geometry
    edge_lengths = [d['length'] for _, _, d in pruned_graph.edges(data=True)]
    edge_geometries = [
        {'coords': d['coords'].tolist()} for _, _, d in pruned_graph.edges(data=True) if 'coords' in d
    ]

    # Create debug stats object now that all stats are calculated
    debug_stats = DebugStats(
        nodes_before_pruning=nodes_before,
        edges_before_pruning=edges_before,
        nodes_after_pruning=nodes_after,
        edges_after_pruning=edges_after,
        edge_geometries_count=len(edge_geometries)
    )

    edge_stats = EdgeStats(
        n_nodes=pruned_graph.number_of_nodes(),
        n_edges=pruned_graph.number_of_edges(),
        mean_edge_length_px=np.mean(edge_lengths) if edge_lengths else 0,
        edges=edge_geometries
    )

    # Create Overlays
    annotated_overlay = create_overlay_image(original_image, skeleton, motifs, intersections)
    skeleton_only_overlay = create_overlay_image(np.zeros_like(original_image), skeleton=skeleton)

    overlays = Overlays(
        annotated_png_base64=encode_image_to_base64(annotated_overlay),
        skeleton_png_base64=encode_image_to_base64(skeleton_only_overlay),
        motifs_png_base64=motifs_only_base64
    )

    timings["total_s"] = time.time() - start_total_time

    # Prepare motifs for JSON serialization
    serializable_motifs = []
    for motif in motifs:
        serializable_motifs.append({
            "id": motif["id"],
            "type": motif["type"],
            "length_px": motif["length_px"],
            "geometry": {"coordinates": list(motif["geometry"].coords)}
        })

    final_result = AnalysisResult(
        metrics=metrics,
        intersections=intersections,
        edges_stats=edge_stats,
        motifs=serializable_motifs,
        overlays=overlays,
        warnings=warnings,
        timings=Timings(**timings),
        params_used=params,
        debug_overlays=debug_overlays,
        debug_stats=debug_stats
    )

    return jsonify(final_result.model_dump())

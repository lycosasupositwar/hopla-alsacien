import uuid
from typing import List, Dict, Any, Optional, Union

from pydantic import BaseModel, Field


class AnalysisParameters(BaseModel):
    gaussian_sigma: float = 1.0
    adaptive_block_size: int = 101
    adaptive_offset: int = 10
    morph_open_kernel: int = 3
    area_opening_min_size_px: int = 500
    skeleton_prune_ratio: float = 0.5
    max_gap_connect_px: float = 100.0 # Will be recalculated based on mean edge length
    epsilon_factor: float = 1.0
    norm_profile: str = "ASTM"
    motifs: Dict[str, Any] = {
        "type": "circular",
        "count": 3
    }
    random_seed: int = 42

    # Gap filling strategy
    gap_filling_strategy: str = "extension_auto" # "extension_auto", "manual", "preserve"


class Metrics(BaseModel):
    L_mm: float
    N_int: float
    ell_mm: float
    ell_um: float
    G: float
    N_AE: float


class Intersection(BaseModel):
    id: int
    x: float
    y: float
    type: str
    score: float
    motif_id: Union[int, str]


class EdgeStats(BaseModel):
    n_nodes: int
    n_edges: int
    mean_edge_length_px: float
    edges: List[Dict[str, Any]] # To hold coordinates for rendering


class Overlays(BaseModel):
    annotated_png_base64: str
    skeleton_png_base64: str
    motifs_png_base64: str


class Timings(BaseModel):
    preprocess_s: float
    border_width_s: float
    skeleton_s: float
    graph_s: float
    intersections_s: float
    total_s: float


class DebugOverlays(BaseModel):
    """
    A model to hold base64 encoded images for debugging the pipeline.
    """
    binary_image_base64: str
    skeleton_image_base64: str
    pruned_graph_image_base64: str
    motifs_image_base64: str


class DebugStats(BaseModel):
    """
    A model to hold statistics for debugging the graph processing steps.
    """
    nodes_before_pruning: int
    edges_before_pruning: int
    nodes_after_pruning: int
    edges_after_pruning: int
    edge_geometries_count: int


class AnalysisResult(BaseModel):
    image_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metrics: Metrics
    intersections: List[Intersection]
    edges_stats: EdgeStats
    motifs: List[Dict[str, Any]] # Add motifs for rendering
    overlays: Overlays
    warnings: List[str]
    timings: Timings
    params_used: AnalysisParameters
    debug_overlays: Optional[DebugOverlays] = None
    debug_stats: Optional[DebugStats] = None

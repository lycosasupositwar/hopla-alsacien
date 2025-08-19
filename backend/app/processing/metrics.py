from typing import List, Dict, Any, Tuple
import numpy as np
from ..schemas.models import Metrics


def compute_final_metrics(
    motifs: List[Dict[str, Any]],
    intersections: List[Dict[str, Any]],
    pixel_size_um: float
) -> Tuple[Metrics, List[str]]:
    """
    Computes the final grain size metrics based on the motifs and intersections.

    Args:
        motifs: The list of generated test patterns.
        intersections: The list of detected and scored intersections.
        pixel_size_um: The size of one pixel in micrometers.

    Returns:
        A tuple containing a Pydantic Metrics object and a list of warnings.
    """
    warnings = []

    # 1. Calculate total length of motifs in mm (L_mm)
    total_length_px = sum(m['length_px'] for m in motifs)
    if total_length_px == 0:
        warnings.append("Total motif length is zero. Cannot compute metrics.")
        # Return a dummy Metrics object
        return Metrics(L_mm=0, N_int=0, ell_mm=0, ell_um=0, G=0, N_AE=0), warnings

    L_mm = (total_length_px * pixel_size_um) / 1000.0

    # 2. Calculate total weighted number of intersections (N_int)
    N_int = sum(i['score'] for i in intersections)

    # 3. Calculate mean intercept length (ell)
    if N_int == 0:
        warnings.append("No intersections found. Grain size cannot be calculated.")
        # Return metrics with ell=0, which will result in G being undefined.
        # We can return G=0 or some other indicator.
        return Metrics(L_mm=L_mm, N_int=N_int, ell_mm=0, ell_um=0, G=0, N_AE=0), warnings

    ell_mm = L_mm / N_int
    ell_um = ell_mm * 1000.0

    # 4. Calculate ASTM grain size number (G)
    # G = -3.288 - 6.643856 * log10(ell_mm)
    # log10 is undefined for ell_mm <= 0. We already handled the N_int=0 case.
    if ell_mm <= 0:
        G = 0.0 # Or handle as an error
        warnings.append(f"Mean intercept length is {ell_mm:.4f} mm, which is invalid for G calculation.")
    else:
        G = -3.288 - 6.643856 * np.log10(ell_mm)

    # 5. Calculate standardized grain density (N_AE)
    # N_AE = 2^(G-1)
    # This can be a very large number if G is large.
    try:
        N_AE = 2**(G - 1)
    except OverflowError:
        N_AE = float('inf')
        warnings.append("Calculated G value is too large, resulting in N_AE overflow.")

    # Create the Pydantic model for the response
    metrics = Metrics(
        L_mm=L_mm,
        N_int=N_int,
        ell_mm=ell_mm,
        ell_um=round(ell_um, 2), # Round as requested
        G=round(G, 3), # Round as requested
        N_AE=N_AE
    )

    if N_int < 50:
        warnings.append(f"Low number of intersections ({int(N_int)}) may lead to statistically insignificant results.")

    return metrics, warnings

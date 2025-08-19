import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.morphology import skeletonize


def skeletonize_image(binary_image: np.ndarray) -> np.ndarray:
    """
    Applies skeletonization to a binary image where grain boundaries are foreground.

    Args:
        binary_image: A binary image (np.uint8, values 0 or 255) with boundaries as foreground.

    Returns:
        A skeletonized binary image (boolean array).
    """
    # Ensure input is boolean for skeletonize
    binary_bool = binary_image > 0
    skeleton = skeletonize(binary_bool)
    return skeleton


def estimate_border_width(binary_image: np.ndarray, skeleton: np.ndarray) -> float:
    """
    Estimates the mean width of the borders in the binary image.
    This is used to set the epsilon for clustering intersections.

    The method calculates the distance from any non-boundary pixel to the
    nearest boundary, then samples this distance along the skeleton. The
    local width is twice this distance.

    Args:
        binary_image: The binary image of boundaries (foreground).
        skeleton: The skeleton of the binary_image.

    Returns:
        The median border width in pixels.
    """
    if np.count_nonzero(binary_image) == 0 or np.count_nonzero(skeleton) == 0:
        return 1.0

    # Invert the image so that grains are foreground (for distance transform)
    # The distance transform will calculate distance from grain pixels to the nearest boundary.
    inverted_binary = (binary_image == 0)

    # Calculate the Euclidean Distance Transform
    # For each foreground pixel, edt stores the distance to the nearest background pixel.
    dist_transform = distance_transform_edt(inverted_binary)

    # Sample the distance transform values only at the skeleton pixels
    # These values represent half the local thickness of the boundary
    skeleton_pixels_distances = dist_transform[skeleton]

    # The actual width is twice the distance
    local_widths = 2 * skeleton_pixels_distances

    if len(local_widths) == 0:
        return 1.0

    # Use median for robustness against outliers (e.g., at junctions)
    median_width = np.median(local_widths)

    # Ensure a minimum width of 1.0
    return max(1.0, float(median_width))

import cv2
import numpy as np
import skimage.filters
from skimage.morphology import remove_small_objects


def _detect_and_remove_twins(binary_image: np.ndarray) -> np.ndarray:
    """
    Detects and removes twins from a binary grain boundary image.
    This function is experimental and works best on images with clear, straight twin lines.
    """
    # Use Hough Line Transform to detect lines
    # Adjust parameters (threshold, minLineLength, maxLineGap) for better detection
    lines = cv2.HoughLinesP(binary_image, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return binary_image # No lines detected

    # Create a mask to draw the detected twin lines
    twin_mask = np.zeros_like(binary_image)

    # Filter and draw lines. Here, we can add more logic to filter for twins
    # (e.g., based on orientation or relationship to grain boundaries)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Draw the line on the mask with a certain thickness
        cv2.line(twin_mask, (x1, y1), (x2, y2), (255), 2)

    # Subtract the twin mask from the original binary image
    # This will remove the twins, potentially leaving gaps.
    result = cv2.subtract(binary_image, twin_mask)

    return result


def preprocess_image(
    image: np.ndarray,
    gaussian_sigma: float = 1.0,
    adaptive_block_size: int = 101,
    adaptive_offset: int = 2,
    morph_open_kernel: int = 3,
    area_opening_min_size_px: int = 500,
    detect_twins: bool = False,
) -> np.ndarray:
    """
    Performs preprocessing on the input image to generate a clean binary image of grain boundaries.

    Args:
        image: Input image as a NumPy array.
        gaussian_sigma: Sigma for the Gaussian blur filter.
        adaptive_block_size: Size of the pixel neighborhood for adaptive thresholding.
        adaptive_offset: Constant subtracted from the mean in adaptive thresholding.
        morph_open_kernel: Kernel size for morphological opening.
        area_opening_min_size_px: Minimum size of objects to keep after area opening.
        detect_twins: If True, attempt to detect and remove twin lines.

    Returns:
        A binary image (np.uint8, values 0 or 255) where 255 represents the grain boundaries.
    """
    # 1. Convert to grayscale if necessary
    if image.ndim == 3 and image.shape[2] in [3, 4]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 2. Apply Gaussian blur to reduce noise
    # The kernel size is determined by sigma. (0,0) lets OpenCV calculate it.
    blurred = cv2.GaussianBlur(gray, (0, 0), gaussian_sigma)

    # 3. Apply adaptive thresholding (Bradley-Roth method)
    # skimage's threshold_local is a robust implementation.
    # The result is a boolean array. We invert it because the algorithm expects
    # dark boundaries on a light background. If blurred > th, it's background (False).
    # We want boundaries, where blurred <= th.
    th = skimage.filters.threshold_local(blurred, adaptive_block_size, method='gaussian', offset=adaptive_offset)
    binary = (blurred <= th)

    # Convert boolean to uint8 for OpenCV operations
    binary_uint8 = binary.astype(np.uint8) * 255

    # 4. Morphological opening to remove small noise speckles
    if morph_open_kernel > 0:
        kernel = np.ones((morph_open_kernel, morph_open_kernel), np.uint8)
        opened = cv2.morphologyEx(binary_uint8, cv2.MORPH_OPEN, kernel)
    else:
        opened = binary_uint8

    # 5. Area opening to remove small, disconnected components
    # remove_small_objects works on boolean arrays
    if area_opening_min_size_px > 0:
        cleaned_bool = remove_small_objects(opened.astype(bool), min_size=area_opening_min_size_px)
        # Invert the image so boundaries are foreground (True) for skeletonization
        final_binary = cleaned_bool.astype(np.uint8) * 255
    else:
        final_binary = opened

    # 6. (Optional) Detect and remove twins
    if detect_twins:
        final_binary = _detect_and_remove_twins(final_binary)


    return final_binary

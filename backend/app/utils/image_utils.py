import base64
import io
import cv2
import networkx as nx
import numpy as np
from PIL import Image


def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Reads image data from bytes and converts it into an OpenCV-compatible NumPy array.
    """
    # Convert bytes to a numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)
    # Decode the numpy array into an image
    # cv2.IMREAD_COLOR ensures it's read as a 3-channel BGR image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image from bytes. The file may be corrupt or in an unsupported format.")
    return img


def encode_image_to_base64(image_array: np.ndarray) -> str:
    """
    Encodes a NumPy array image into a Base64 PNG string.
    """
    # Ensure the image is in a web-compatible format (e.g., RGB for color, L for grayscale)
    if image_array.ndim == 3 and image_array.shape[2] == 3:
        # OpenCV uses BGR, Pillow/web uses RGB. Convert it.
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_array)
    elif image_array.ndim == 2:
        # Grayscale image
        pil_img = Image.fromarray(image_array, 'L')
    else:
        raise ValueError(f"Unsupported image array shape for encoding: {image_array.shape}")

    # Save image to an in-memory buffer
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")

    # Encode buffer to base64
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Prepend the required data URI scheme
    return f"data:image/png;base64,{img_str}"


def create_overlay_image(
    original_image: np.ndarray,
    skeleton: np.ndarray = None,
    motifs: list = None,
    intersections: list = None
) -> np.ndarray:
    """
    Creates an annotated image with overlays for skeleton, motifs, and intersections.
    """
    # Start with the original image, ensure it's a 3-channel color image for drawing
    if original_image.ndim == 2:
        overlay = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    else:
        overlay = original_image.copy()

    # Overlay skeleton (in green)
    if skeleton is not None:
        overlay[skeleton.astype(bool)] = [0, 255, 0] # BGR format

    # Overlay motifs (in blue)
    if motifs is not None:
        for motif in motifs:
            geom = motif['geometry']
            if geom.geom_type == 'LineString':
                coords = np.array(geom.coords, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(overlay, [coords], isClosed=False, color=(255, 0, 0), thickness=2)
            elif geom.geom_type == 'Polygon' or geom.geom_type == 'LinearRing': # Circle
                coords = np.array(geom.exterior.coords, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(overlay, [coords], isClosed=True, color=(255, 0, 0), thickness=2)

    # Overlay intersections (color-coded circles)
    if intersections is not None:
        color_map = {
            "jonction": (0, 0, 255),  # Red
            "régulière": (0, 255, 255), # Yellow
            "extrémité": (255, 255, 0) # Cyan
        }
        for inter in intersections:
            center = (int(round(inter['x'])), int(round(inter['y'])))
            color = color_map.get(inter['type'], (255, 255, 255)) # Default to white
            cv2.circle(overlay, center, radius=8, color=color, thickness=-1) # Filled circle
            cv2.circle(overlay, center, radius=8, color=(0,0,0), thickness=2) # Black outline

    # --- DEBUGGING: Draw a hardcoded diagonal line to test the canvas ---
    h, w, _ = overlay.shape
    cv2.line(overlay, (0, 0), (w - 1, h - 1), (255, 255, 255), 2)


    return overlay


def draw_graph_on_image(graph: nx.Graph, image_shape: tuple) -> np.ndarray:
    """
    Draws the edges of a networkx graph onto a blank image.
    This is useful for debugging the graph structure.
    """
    # Create a blank black image with 3 channels
    image = np.zeros((image_shape[0], image_shape[1], 3), dtype=np.uint8)

    # Iterate through the edges and draw them
    for _, _, data in graph.edges(data=True):
        coords = data.get('coords')
        if coords is not None and len(coords) >= 2:
            # The graph now stores coords in (x, y) format.
            # cv2.polylines expects points as (x, y).
            points = np.array(coords, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=False, color=(0, 255, 0), thickness=1)

    return image

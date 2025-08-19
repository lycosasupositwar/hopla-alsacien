import numpy as np
from scipy.spatial import Voronoi
from PIL import Image, ImageDraw
import os

def create_voronoi_image(points, width, height, line_width=1):
    """
    Creates a rasterized image of a Voronoi diagram.
    """
    # Add points at edges to eliminate open regions
    edge_points = np.array([
        [0, 0], [width, 0], [0, height], [width, height],
        [width/2, 0], [width/2, height], [0, height/2], [width, height/2]
    ])
    points = np.concatenate([points, edge_points])

    vor = Voronoi(points)

    img = Image.new('L', (width, height), 255) # White background
    draw = ImageDraw.Draw(img)

    for ridge_vertices in vor.ridge_vertices:
        if -1 not in ridge_vertices:
            v1 = vor.vertices[ridge_vertices[0]]
            v2 = vor.vertices[ridge_vertices[1]]
            draw.line([(v1[0], v1[1]), (v2[0], v2[1])], fill=0, width=line_width)

    return np.array(img)

def add_scratches(image_array, num_scratches=2, max_width=3):
    """Adds linear scratches to the image."""
    img = Image.fromarray(image_array)
    draw = ImageDraw.Draw(img)
    height, width = img.size

    for _ in range(num_scratches):
        x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
        x2, y2 = np.random.randint(0, width), np.random.randint(0, height)
        line_width = np.random.randint(1, max_width + 1)
        draw.line([(x1, y1), (x2, y2)], fill=0, width=line_width)

    return np.array(img)

def add_blobs(image_array, num_blobs=5, max_radius=20):
    """Adds circular blobs to the image."""
    img = Image.fromarray(image_array)
    draw = ImageDraw.Draw(img)
    height, width = img.size

    for _ in range(num_blobs):
        cx, cy = np.random.randint(0, width), np.random.randint(0, height)
        radius = np.random.randint(5, max_radius)
        draw.ellipse([(cx-radius, cy-radius), (cx+radius, cy+radius)], fill=0)

    return np.array(img)


def main():
    """Generates and saves a set of synthetic microstructure images."""
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'examples', 'input')
    os.makedirs(output_dir, exist_ok=True)

    width, height = 1024, 1024
    np.random.seed(42)

    # --- Image 1: Standard Voronoi ---
    print("Generating: synthetic_voronoi_standard.png")
    points_std = np.random.rand(50, 2) * np.array([width, height])
    img_std = create_voronoi_image(points_std, width, height, line_width=3)
    Image.fromarray(img_std).save(os.path.join(output_dir, "synthetic_voronoi_standard.png"))

    # --- Image 2: Dense Voronoi ---
    print("Generating: synthetic_voronoi_dense.png")
    points_dense = np.random.rand(150, 2) * np.array([width, height])
    img_dense = create_voronoi_image(points_dense, width, height, line_width=2)
    Image.fromarray(img_dense).save(os.path.join(output_dir, "synthetic_voronoi_dense.png"))

    # --- Image 3: Voronoi with Artifacts ---
    print("Generating: synthetic_voronoi_artifacts.png")
    points_art = np.random.rand(40, 2) * np.array([width, height])
    img_art = create_voronoi_image(points_art, width, height, line_width=4)
    img_art_scratched = add_scratches(img_art, num_scratches=3, max_width=5)
    img_art_blobs = add_blobs(img_art_scratched, num_blobs=8, max_radius=30)
    Image.fromarray(img_art_blobs).save(os.path.join(output_dir, "synthetic_voronoi_artifacts.png"))

    # --- Image 4: Simple Y-junction for testing junction detection ---
    print("Generating: synthetic_y_junction.png")
    img_y = Image.new('L', (200, 200), 255)
    draw = ImageDraw.Draw(img_y)
    draw.line([(100, 50), (100, 100)], fill=0, width=3)
    draw.line([(100, 100), (50, 150)], fill=0, width=3)
    draw.line([(100, 100), (150, 150)], fill=0, width=3)
    np_img_y = np.array(img_y)
    Image.fromarray(np_img_y).save(os.path.join(output_dir, "synthetic_y_junction.png"))


    print(f"\nSuccessfully generated 4 synthetic images in '{output_dir}'")

if __name__ == "__main__":
    main()

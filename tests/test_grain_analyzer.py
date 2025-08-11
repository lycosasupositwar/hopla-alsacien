import unittest
import sys
import os
import cv2
import numpy as np

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.astm_e112 import ASTM_E112
from src.core.grain_analyzer import GrainAnalyzer

class TestGrainAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up the test case."""
        self.astm_calculator = ASTM_E112()
        self.grain_analyzer = GrainAnalyzer(self.astm_calculator)
        self.test_image_path = "data/test_image.png"

        # Ensure the test image exists
        if not os.path.exists(self.test_image_path):
            self.fail(f"Test image not found at {self.test_image_path}")

    def test_analysis_with_synthetic_image(self):
        """
        Test the full analysis pipeline with a synthetic image.
        This is an integration test to ensure GrainAnalyzer and ASTM_E112 work together.
        """
        image = cv2.imread(self.test_image_path, cv2.IMREAD_GRAYSCALE)
        self.assertIsNotNone(image, "Failed to load test image.")

        # Invert the image so grains are white and background is black
        image = cv2.bitwise_not(image)

        # Define a scale for the test image. Let's assume the 512x512 image is 5.12mm x 5.12mm.
        # So, the scale is 100 pixels/mm.
        scale_px_per_mm = 100.0

        # Perform the analysis
        results = self.grain_analyzer.analyze_grains(
            image,
            scale_pixels_per_mm=scale_px_per_mm,
            blur_factor=0,
            threshold_value=127,
            min_grain_size=1000, # Min size of circles in test image is pi*30^2 ~= 2827
            max_grain_size=20000 # Max size is pi*70^2 ~= 15393
        )

        self.assertIsNotNone(results)
        self.assertIn('astm_stats', results)

        # Check grain count
        num_grains = results['astm_stats'].get('grain_count')
        self.assertEqual(num_grains, 5, "Should detect 5 grains.")

        # Check ASTM calculation
        # Expected total area = pi * (40^2 + 60^2 + 30^2 + 50^2 + 70^2) = pi * 13500 ~= 42411.5
        # Expected total area in mm^2 = 42411.5 / (100^2) = 4.24115
        # Expected NA = 5 / 4.24115 = 1.1789
        # Expected G = log2(1.1789) + 1 = 0.237 + 1 = 1.237
        astm_g = results['astm_stats'].get('astm_grain_size')
        self.assertAlmostEqual(astm_g, 1.24, places=2)


if __name__ == '__main__':
    unittest.main()

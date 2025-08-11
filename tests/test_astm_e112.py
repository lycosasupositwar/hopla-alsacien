import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.astm_e112 import ASTM_E112

class TestASTM_E112(unittest.TestCase):

    def setUp(self):
        """Set up the test case."""
        self.calculator = ASTM_E112()

    def test_planimetric_method_basic(self):
        """Test the planimetric method with a basic, realistic example."""
        # Example data: 100 grains in an area of 0.5 mm^2
        # NA = 100 / 0.5 = 200 grains/mm^2
        # G = log2(200) + 1 = 7.64 + 1 = 8.64
        total_grains = 100
        total_area_pixels = 500000  # e.g., 500k pixels
        scale_pixels_per_mm = 1000  # 1000 pixels/mm => 1,000,000 pixels^2/mm^2
        # total_area_mm2 = 500000 / (1000*1000) = 0.5 mm^2

        result = self.calculator.planimetric_method(total_grains, total_area_pixels, scale_pixels_per_mm)
        self.assertAlmostEqual(result, 8.64, places=2)

    def test_planimetric_method_zero_grains(self):
        """Test with zero grains, should return 0."""
        result = self.calculator.planimetric_method(0, 10000, 100)
        self.assertEqual(result, 0.0)

    def test_planimetric_method_zero_area(self):
        """Test with zero area, should return 0."""
        result = self.calculator.planimetric_method(100, 0, 100)
        self.assertEqual(result, 0.0)

    def test_planimetric_method_zero_scale(self):
        """Test with zero scale, should return 0."""
        result = self.calculator.planimetric_method(100, 10000, 0)
        self.assertEqual(result, 0.0)

    def test_planimetric_method_large_values(self):
        """Test with larger, more complex values."""
        # Example data: 1542 grains, area of 1.23 mm^2
        # NA = 1542 / 1.23 = 1253.66
        # G = log2(1253.66) + 1 = 10.29 + 1 = 11.29
        total_grains = 1542
        total_area_pixels = 1230000
        scale_pixels_per_mm = 1000

        result = self.calculator.planimetric_method(total_grains, total_area_pixels, scale_pixels_per_mm)
        self.assertAlmostEqual(result, 11.29, places=2)

if __name__ == '__main__':
    unittest.main()

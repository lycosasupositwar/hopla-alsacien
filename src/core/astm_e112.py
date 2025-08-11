import numpy as np
import math

class ASTM_E112:
    """
    Provides methods for calculating ASTM grain size numbers based on the
    ASTM E112 standard.

    Currently, only the planimetric method is implemented.
    """

    def __init__(self):
        pass

    def planimetric_method(self, total_grains: int, total_area_pixels: float, scale_pixels_per_mm: float) -> float:
        """
        Calculates the ASTM grain size number (G) using the planimetric method.

        This method relates the number of grains per unit area to the ASTM
        grain size number. The calculation is performed at 1x magnification.

        Args:
            total_grains (int): The total number of grains counted in the area.
            total_area_pixels (float): The total area of the grains in pixels.
            scale_pixels_per_mm (float): The scale of the image in pixels per millimeter.
                                         This is a critical parameter for accurate measurement.

        Returns:
            float: The calculated ASTM grain size number (G). Returns 0 if the input is invalid.
        """
        if not total_grains > 0 or not total_area_pixels > 0 or not scale_pixels_per_mm > 0:
            return 0.0

        # Convert the area from pixels^2 to mm^2
        # (scale_pixels_per_mm)^2 = pixels^2 / mm^2
        # area_mm2 = area_pixels / (pixels^2 / mm^2)
        total_area_mm2 = total_area_pixels / (scale_pixels_per_mm ** 2)

        # Calculate NA: number of grains per square millimeter at 1x magnification
        if total_area_mm2 == 0:
            return 0.0
        
        grains_per_mm2_at_1x = total_grains / total_area_mm2

        # The ASTM grain size number G is defined by: NA = 2^(G - 1)
        # Solving for G: G = log2(NA) + 1
        if grains_per_mm2_at_1x <= 0:
            return 0.0

        astm_number = math.log2(grains_per_mm2_at_1x) + 1.0
        
        return round(astm_number, 2)

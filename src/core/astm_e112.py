import numpy as np
import math

class ASTM_E112:
    """Implementation of ASTM E112 standard for grain size measurement"""
    
    def __init__(self):
        # ASTM E112 constants
        self.ASTM_CONSTANT = 2.0954  # Constant for circular grain approximation
        
    def calculate_grain_size(self, grains):
        """Calculate ASTM grain size number"""
        if not grains:
            return None, 0
            
        # Calculate mean grain diameter
        diameters = [grain.get('equivalent_diameter', 0) for grain in grains]
        mean_diameter = np.mean(diameters)
        
        # Calculate ASTM grain size number using intercept method
        astm_number = self.intercept_method(grains)
        
        return astm_number, mean_diameter
        
    def intercept_method(self, grains):
        """Calculate grain size using intercept method"""
        if not grains:
            return None
            
        # Calculate average grain diameter
        diameters = [grain.get('equivalent_diameter', 0) for grain in grains]
        mean_diameter = np.mean(diameters)
        
        # Convert to mm (assuming input is in micrometers)
        mean_diameter_mm = mean_diameter / 1000.0
        
        # Calculate ASTM grain size number
        # G = -6.64 * log10(d) - 12.6
        # where d is the mean diameter in mm
        if mean_diameter_mm > 0:
            astm_number = -6.64 * math.log10(mean_diameter_mm) - 12.6
        else:
            astm_number = 0
            
        return round(astm_number, 1)
        
    def planimetric_method(self, grains, magnification=100):
        """Calculate grain size using planimetric method"""
        if not grains:
            return None
            
        # Calculate number of grains per unit area
        total_area = sum(grain.get('area', 0) for grain in grains)
        n_grains = len(grains)
        
        # Grains per square mm at 100x magnification
        grains_per_mm2 = (n_grains / total_area) * (magnification / 100) ** 2
        
        # Calculate ASTM grain size number
        # N = 2^(G-1) where N is grains per square mm at 100x
        if grains_per_mm2 > 0:
            astm_number = math.log2(grains_per_mm2) + 1
        else:
            astm_number = 0
            
        return round(astm_number, 1)
        
    def comparison_method(self, grains):
        """Calculate grain size using comparison method"""
        # This would typically involve comparing with standard charts
        # For now, we'll use a simplified approach based on grain count
        n_grains = len(grains)
        
        # Approximate mapping based on typical grain counts
        if n_grains < 10:
            return 1
        elif n_grains < 25:
            return 2
        elif n_grains < 50:
            return 3
        elif n_grains < 100:
            return 4
        elif n_grains < 200:
            return 5
        elif n_grains < 400:
            return 6
        elif n_grains < 800:
            return 7
        elif n_grains < 1600:
            return 8
        else:
            return 9

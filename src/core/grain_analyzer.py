import cv2
import numpy as np
from scipy import ndimage
from .astm_e112 import ASTM_E112

class GrainAnalyzer:
    """
    Analyzes images to identify grains, calculate their properties, and
    determine the ASTM grain size number.
    """

    def __init__(self, astm_calculator: ASTM_E112):
        """
        Initializes the GrainAnalyzer.

        Args:
            astm_calculator (ASTM_E112): An instance of the ASTM E112 calculator.
        """
        self.grain_data = None
        self.astm_calculator = astm_calculator

    def analyze_grains(self, image, scale_pixels_per_mm: float, blur_factor=1,
                      threshold_value=128, min_grain_size=50, max_grain_size=2000):
        """
        Analyzes an image to find grains and calculate their properties.

        Args:
            image: The input image (grayscale or BGR).
            scale_pixels_per_mm (float): The scale of the image in pixels per millimeter.
            blur_factor (int): The factor for Gaussian blur.
            threshold_value (int): The value for binary thresholding.
            min_grain_size (int): The minimum grain area in pixels to be considered.
            max_grain_size (int): The maximum grain area in pixels to be considered.

        Returns:
            dict: A dictionary containing the analysis results, including grain
                  properties and ASTM statistics.
        """
        try:
            # Preprocessing
            processed = self._preprocess_image(image, blur_factor, threshold_value)
            
            # Segmentation
            labeled_grains, num_grains = self._segment_grains(processed, min_grain_size, max_grain_size)
            
            # Property analysis
            grain_properties = self._analyze_grain_properties(labeled_grains)
            
            # ASTM statistics calculation
            astm_stats = self._calculate_astm_statistics(grain_properties, scale_pixels_per_mm)
            
            self.grain_data = {
                'properties': grain_properties,
                'astm_stats': astm_stats,
                'labeled_image': labeled_grains,
                'processed_image': processed
            }
            
            return self.grain_data
            
        except Exception as e:
            print(f"Error in grain analysis: {str(e)}")
            return None
    
    def _preprocess_image(self, image, blur_factor, threshold_value):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        if blur_factor > 0:
            kernel_size = max(1, int(blur_factor * 2) * 2 + 1)
            gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), blur_factor)
        
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def _segment_grains(self, binary_image, min_grain_size, max_grain_size):
        num_labels, labels = cv2.connectedComponents(binary_image)
        
        filtered_labels = np.zeros_like(labels)
        label_counter = 1
        
        for label in range(1, num_labels):
            mask = (labels == label)
            area = np.sum(mask)
            
            if min_grain_size <= area <= max_grain_size:
                filtered_labels[mask] = label_counter
                label_counter += 1
        
        return filtered_labels, label_counter - 1
    
    def _analyze_grain_properties(self, labeled_image):
        unique_labels = np.unique(labeled_image)
        properties = []
        
        for label in unique_labels[1:]:
            mask = (labeled_image == label).astype(np.uint8)
            
            area = np.sum(mask)
            y_coords, x_coords = np.where(mask)
            centroid = (np.mean(y_coords), np.mean(x_coords))
            equivalent_diameter = 2 * np.sqrt(area / np.pi)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            perimeter = cv2.arcLength(contours[0], True) if contours else 0
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            if contours:
                x, y, w, h = cv2.boundingRect(contours[0])
                aspect_ratio = w / h if h > 0 else 1
                extent = area / (w * h) if w * h > 0 else 0
            else:
                aspect_ratio = 1
                extent = 0
            
            properties.append({
                'label': int(label),
                'area': float(area),
                'centroid': centroid,
                'equivalent_diameter': float(equivalent_diameter),
                'perimeter': float(perimeter),
                'circularity': float(circularity),
                'aspect_ratio': float(aspect_ratio),
                'extent': float(extent)
            })
        
        return properties
    
    def _calculate_astm_statistics(self, properties, scale_pixels_per_mm):
        if not properties:
            return {}
        
        areas = [p['area'] for p in properties]
        total_area_pixels = np.sum(areas)
        num_grains = len(properties)
        
        stats = {
            'grain_count': num_grains,
            'mean_area': np.mean(areas),
            'std_area': np.std(areas),
            'min_area': np.min(areas),
            'max_area': np.max(areas),
            'total_area': total_area_pixels
        }
        
        astm_grain_size = self.astm_calculator.planimetric_method(
            total_grains=num_grains,
            total_area_pixels=total_area_pixels,
            scale_pixels_per_mm=scale_pixels_per_mm
        )
        stats['astm_grain_size'] = astm_grain_size
        
        return stats

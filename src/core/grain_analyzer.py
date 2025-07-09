import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_maxima
from skimage.segmentation import watershed
from skimage.measure import label, regionprops
from .astm_e112 import ASTM_E112

class GrainAnalyzer:
    def __init__(self):
        self.astm = ASTM_E112()
        
    def analyze_grains(self, image):
        """Analyze grains in metallographic image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Preprocess image
        processed = self.preprocess_image(gray)
        
        # Segment grains
        contours, labels = self.segment_grains(processed)
        
        # Extract grain properties
        grains = self.extract_grain_properties(labels, contours)
        
        # Calculate ASTM grain size
        astm_number, mean_diameter = self.astm.calculate_grain_size(grains)
        
        return {
            'grains': grains,
            'contours': contours,
            'labels': labels,
            'astm_number': astm_number,
            'mean_diameter': mean_diameter,
            'grain_count': len(grains)
        }
        
    def preprocess_image(self, image):
        """Preprocess image for grain analysis"""
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel)
        
        return opened
        
    def segment_grains(self, image):
        """Segment grains using watershed algorithm"""
        # Threshold image
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Distance transform
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # Find local maxima (seeds)
        coords = peak_local_maxima(dist_transform, min_distance=10, threshold_abs=0.3)
        seeds = np.zeros_like(binary)
        for coord in coords:
            seeds[coord[0], coord[1]] = 1
            
        # Label seeds
        markers = label(seeds)
        
        # Watershed segmentation
        labels = watershed(-dist_transform, markers, mask=binary)
        
        # Find contours
        contours = []
        for region in regionprops(labels):
            if region.area > 100:  # Filter small regions
                # Create mask for this region
                mask = (labels == region.label).astype(np.uint8) * 255
                region_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if region_contours:
                    contours.append(region_contours[0])
                    
        return contours, labels
        
    def extract_grain_properties(self, labels, contours):
        """Extract properties from segmented grains"""
        grains = []
        
        for i, contour in enumerate(contours):
            # Basic measurements
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            # Equivalent diameter
            equivalent_diameter = np.sqrt(4 * area / np.pi)
            
            # Shape factor (circularity)
            shape_factor = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # Orientation
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                orientation = ellipse[2]
            else:
                orientation = 0
                
            # Aspect ratio
            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 1
            
            grain = {
                'id': i + 1,
                'area': area,
                'perimeter': perimeter,
                'equivalent_diameter': equivalent_diameter,
                'shape_factor': shape_factor,
                'orientation': orientation,
                'aspect_ratio': aspect_ratio,
                'centroid': tuple(np.mean(contour.reshape(-1, 2), axis=0))
            }
            
            grains.append(grain)
            
        return grains

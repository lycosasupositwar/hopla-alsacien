import cv2
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

class GrainAnalyzer:
    def __init__(self):
        self.grain_data = None
        self.processed_image = None
        self.original_image = None
        
    def analyze_grains(self, image, blur_factor=1, threshold_value=128, 
                      min_grain_size=50, max_grain_size=2000):
        """
        Analyse des grains dans l'image
        """
        try:
            self.original_image = image.copy()
            
            # Prétraitement simple
            processed = self._preprocess_image(image, blur_factor, threshold_value)
            
            # Segmentation simple
            labeled_grains = self._segment_grains_simple(processed, min_grain_size, max_grain_size)
            
            # Analyse des propriétés
            grain_properties = self._analyze_grain_properties_simple(labeled_grains)
            
            # Calcul des statistiques
            astm_stats = self._calculate_stats_simple(grain_properties)
            
            self.grain_data = {
                'properties': grain_properties,
                'astm_stats': astm_stats,
                'labeled_image': labeled_grains,
                'processed_image': processed
            }
            
            return self.grain_data
            
        except Exception as e:
            print(f"Erreur dans l'analyse des grains: {str(e)}")
            return None
    
    def _preprocess_image(self, image, blur_factor, threshold_value):
        """Prétraitement simple"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        if blur_factor > 0:
            gray = cv2.GaussianBlur(gray, (blur_factor*2+1, blur_factor*2+1), 0)
        
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        return binary
    
    def _segment_grains_simple(self, binary_image, min_size, max_size):
        """Segmentation simple avec OpenCV"""
        # Recherche des contours
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Création d'une image étiquetée
        labeled = np.zeros_like(binary_image, dtype=np.int32)
        label = 1
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_size <= area <= max_size:
                cv2.fillPoly(labeled, [contour], label)
                label += 1
        
        return labeled
    
    def _analyze_grain_properties_simple(self, labeled_image):
        """Analyse simple des propriétés"""
        unique_labels = np.unique(labeled_image)
        unique_labels = unique_labels[unique_labels > 0]  # Exclure le fond
        
        properties = []
        
        for label in unique_labels:
            mask = labeled_image == label
            area = np.sum(mask)
            
            # Calcul du centroïde
            y_coords, x_coords = np.where(mask)
            centroid_y = np.mean(y_coords)
            centroid_x = np.mean(x_coords)
            
            # Diamètre équivalent
            equivalent_diameter = 2 * np.sqrt(area / np.pi)
            
            properties.append({
                'area': area,
                'centroid': (centroid_y, centroid_x),
                'equivalent_diameter': equivalent_diameter
            })
        
        return properties
    
    def _calculate_stats_simple(self, grain_properties):
        """Calcul simple des statistiques"""
        if not grain_properties:
            return {}
        
        diameters = [prop['equivalent_diameter'] for prop in grain_properties]
        areas = [prop['area'] for prop in grain_properties]
        
        return {
            'grain_count': len(grain_properties),
            'mean_diameter': np.mean(diameters),
            'std_diameter': np.std(diameters),
            'mean_area': np.mean(areas),
            'total_area': sum(areas),
            'min_diameter': min(diameters),
            'max_diameter': max(diameters)
        }
    
    def get_visualization_image(self):
        """Génère une image de visualisation"""
        if self.grain_data is None:
            return None
        
        labeled_image = self.grain_data['labeled_image']
        
        # Création d'une image colorée simple
        colored = np.zeros((*labeled_image.shape, 3), dtype=np.uint8)
        
        unique_labels = np.unique(labeled_image)
        for i, label in enumerate(unique_labels[1:]):  # Exclure le fond
            mask = labeled_image == label
            color = plt.cm.tab10(i % 10)[:3]  # Cycle de couleurs
            colored[mask] = [int(c * 255) for c in color]
        
        return colored
    
    def export_results(self, output_path):
        """Export simple des résultats"""
        if self.grain_data is None:
            return False
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(self.grain_data['properties'])
            stats_df = pd.DataFrame([self.grain_data['astm_stats']])
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Grain_Properties', index=False)
                stats_df.to_excel(writer, sheet_name='ASTM_Statistics', index=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {str(e)}")
            return False

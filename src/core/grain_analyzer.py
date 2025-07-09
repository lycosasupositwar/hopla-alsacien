import cv2
import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks
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
            
            # Prétraitement
            processed = self._preprocess_image(image, blur_factor, threshold_value)
            
            # Segmentation des grains
            labeled_grains = self._segment_grains(processed, min_grain_size, max_grain_size)
            
            # Analyse des propriétés
            grain_properties = self._analyze_grain_properties(labeled_grains)
            
            # Calcul des statistiques ASTM
            astm_stats = self._calculate_astm_statistics(grain_properties)
            
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
        """Prétraitement de l'image"""
        # Conversion en niveaux de gris si nécessaire
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Flou gaussien
        if blur_factor > 0:
            kernel_size = max(1, int(blur_factor * 2) * 2 + 1)
            gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), blur_factor)
        
        # Seuillage
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        # Nettoyage morphologique
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def _segment_grains(self, binary_image, min_grain_size, max_grain_size):
        """Segmentation des grains"""
        # Étiquetage des composants connectés
        num_labels, labels = cv2.connectedComponents(binary_image)
        
        # Filtrage par taille
        filtered_labels = np.zeros_like(labels)
        label_counter = 1
        
        for label in range(1, num_labels):
            mask = (labels == label)
            area = np.sum(mask)
            
            if min_grain_size <= area <= max_grain_size:
                filtered_labels[mask] = label_counter
                label_counter += 1
        
        return filtered_labels
    
    def _analyze_grain_properties(self, labeled_image):
        """Analyse des propriétés des grains"""
        unique_labels = np.unique(labeled_image)
        properties = []
        
        for label in unique_labels[1:]:  # Exclure le fond (label 0)
            mask = (labeled_image == label)
            
            # Calcul des propriétés de base
            area = np.sum(mask)
            
            # Centroïde
            y_coords, x_coords = np.where(mask)
            centroid = (np.mean(y_coords), np.mean(x_coords))
            
            # Diamètre équivalent
            equivalent_diameter = 2 * np.sqrt(area / np.pi)
            
            # Périmètre (approximation)
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            perimeter = cv2.arcLength(contours[0], True) if contours else 0
            
            # Circularité
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # Boîte englobante
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
    
    def _calculate_astm_statistics(self, properties):
        """Calcul des statistiques ASTM"""
        if not properties:
            return {}
        
        areas = [p['area'] for p in properties]
        diameters = [p['equivalent_diameter'] for p in properties]
        circularities = [p['circularity'] for p in properties]
        
        stats = {
            'grain_count': len(properties),
            'mean_area': np.mean(areas),
            'std_area': np.std(areas),
            'min_area': np.min(areas),
            'max_area': np.max(areas),
            'mean_diameter': np.mean(diameters),
            'std_diameter': np.std(diameters),
            'mean_circularity': np.mean(circularities),
            'std_circularity': np.std(circularities),
            'total_area': np.sum(areas)
        }
        
        # Calcul de la taille de grain ASTM (approximation)
        mean_area_mm2 = stats['mean_area'] * 0.0001  # Supposer 1 pixel = 0.01 mm
        astm_grain_size = -6.64 * np.log10(mean_area_mm2) - 3.29 if mean_area_mm2 > 0 else 0
        stats['astm_grain_size'] = astm_grain_size
        
        return stats
    
    def get_visualization_image(self):
        """Génère une image de visualisation"""
        if self.grain_data is None:
            return None
        
        labeled_image = self.grain_data['labeled_image']
        
        # Création d'une image colorée
        colored = np.zeros((*labeled_image.shape, 3), dtype=np.uint8)
        
        # Couleurs prédéfinies
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 165, 0),
            (255, 192, 203), (128, 128, 0), (0, 128, 128), (128, 0, 0)
        ]
        
        unique_labels = np.unique(labeled_image)
        for i, label in enumerate(unique_labels[1:]):  # Exclure le fond
            mask = labeled_image == label
            color = colors[i % len(colors)]
            colored[mask] = color
        
        return colored
    
    def export_results(self, output_path):
        """Export des résultats"""
        if self.grain_data is None:
            return False
        
        try:
            import pandas as pd
            
            # DataFrame des propriétés
            df = pd.DataFrame(self.grain_data['properties'])
            
            # DataFrame des statistiques
            stats_df = pd.DataFrame([self.grain_data['astm_stats']])
            
            # Export vers Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Grain_Properties', index=False)
                stats_df.to_excel(writer, sheet_name='ASTM_Statistics', index=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {str(e)}")
            return False
    
    def get_grain_count(self):
        """Retourne le nombre de grains détectés"""
        if self.grain_data is None:
            return 0
        return self.grain_data['astm_stats'].get('grain_count', 0)
    
    def get_mean_grain_size(self):
        """Retourne la taille moyenne des grains"""
        if self.grain_data is None:
            return 0
        return self.grain_data['astm_stats'].get('mean_diameter', 0)
    
    def get_astm_grain_size(self):
        """Retourne la taille de grain ASTM"""
        if self.grain_data is None:
            return 0
        return self.grain_data['astm_stats'].get('astm_grain_size', 0)

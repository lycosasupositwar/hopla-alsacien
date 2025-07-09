import cv2
import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks
from skimage import measure, morphology, segmentation
from skimage.feature import peak_local_maxima
from skimage.segmentation import watershed
from skimage.filters import gaussian, threshold_otsu
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
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Lissage
        if blur_factor > 0:
            gray = gaussian(gray, sigma=blur_factor)
        
        # Seuillage
        if threshold_value > 0:
            binary = gray > threshold_value
        else:
            threshold_value = threshold_otsu(gray)
            binary = gray > threshold_value
        
        # Nettoyage morphologique
        binary = morphology.remove_small_objects(binary, min_size=50)
        binary = morphology.remove_small_holes(binary, area_threshold=50)
        
        return binary
    
    def _segment_grains(self, binary_image, min_size, max_size):
        """Segmentation des grains individuels"""
        # Calcul de la distance transform
        distance = ndimage.distance_transform_edt(binary_image)
        
        # Recherche des maxima locaux pour les graines
        # Utilisation d'une méthode alternative à peak_local_maxima
        from scipy.ndimage import maximum_filter
        
        # Créer un masque pour les maxima locaux
        local_maxima = maximum_filter(distance, size=20) == distance
        local_maxima = local_maxima & (distance > 5)
        
        # Étiquetage des graines
        markers = measure.label(local_maxima)
        
        # Segmentation par watershed
        labels = watershed(-distance, markers, mask=binary_image)
        
        # Filtrage par taille
        filtered_labels = self._filter_by_size(labels, min_size, max_size)
        
        return filtered_labels
    
    def _filter_by_size(self, labeled_image, min_size, max_size):
        """Filtrage des régions par taille"""
        # Propriétés des régions
        props = measure.regionprops(labeled_image)
        
        # Créer une nouvelle image étiquetée
        filtered = np.zeros_like(labeled_image)
        new_label = 1
        
        for prop in props:
            if min_size <= prop.area <= max_size:
                mask = labeled_image == prop.label
                filtered[mask] = new_label
                new_label += 1
        
        return filtered
    
    def _analyze_grain_properties(self, labeled_image):
        """Analyse des propriétés des grains"""
        props = measure.regionprops(labeled_image)
        
        grain_properties = []
        
        for prop in props:
            grain_info = {
                'area': prop.area,
                'perimeter': prop.perimeter,
                'centroid': prop.centroid,
                'equivalent_diameter': prop.equivalent_diameter,
                'major_axis_length': prop.major_axis_length,
                'minor_axis_length': prop.minor_axis_length,
                'orientation': prop.orientation,
                'solidity': prop.solidity,
                'eccentricity': prop.eccentricity,
                'extent': prop.extent
            }
            grain_properties.append(grain_info)
        
        return grain_properties
    
    def _calculate_astm_statistics(self, grain_properties):
        """Calcul des statistiques selon les normes ASTM"""
        if not grain_properties:
            return {}
        
        # Extraction des diamètres équivalents
        diameters = [prop['equivalent_diameter'] for prop in grain_properties]
        areas = [prop['area'] for prop in grain_properties]
        
        # Statistiques de base
        mean_diameter = np.mean(diameters)
        std_diameter = np.std(diameters)
        mean_area = np.mean(areas)
        
        # Calcul du numéro de grain ASTM (approximation)
        # G = log2(N) - log2(A) où N = nombre de grains, A = surface totale
        total_area = sum(areas)
        grain_count = len(grain_properties)
        
        if total_area > 0:
            astm_grain_number = np.log2(grain_count) - np.log2(total_area / 1000000)  # Normalisation
        else:
            astm_grain_number = 0
        
        return {
            'grain_count': grain_count,
            'mean_diameter': mean_diameter,
            'std_diameter': std_diameter,
            'mean_area': mean_area,
            'total_area': total_area,
            'astm_grain_number': astm_grain_number,
            'min_diameter': min(diameters) if diameters else 0,
            'max_diameter': max(diameters) if diameters else 0
        }
    
    def get_visualization_image(self):
        """Génère une image de visualisation des grains détectés"""
        if self.grain_data is None:
            return None
        
        labeled_image = self.grain_data['labeled_image']
        
        # Création d'une image colorée
        colored_image = measure.label2rgb(labeled_image, bg_label=0)
        
        # Conversion en format uint8 pour affichage
        colored_image = (colored_image * 255).astype(np.uint8)
        
        return colored_image
    
    def export_results(self, output_path):
        """Export des résultats vers un fichier"""
        if self.grain_data is None:
            return False
        
        try:
            import pandas as pd
            
            # Création du DataFrame
            df = pd.DataFrame(self.grain_data['properties'])
            
            # Ajout des statistiques
            stats_df = pd.DataFrame([self.grain_data['astm_stats']])
            
            # Export vers Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Grain_Properties', index=False)
                stats_df.to_excel(writer, sheet_name='ASTM_Statistics', index=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {str(e)}")
            return False

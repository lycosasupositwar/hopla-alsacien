import cv2
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class PhaseAnalyzer:
    def __init__(self):
        self.phase_data = None
        self.processed_image = None
        self.original_image = None
        self.phase_colors = [
            (255, 0, 0),      # Rouge
            (0, 255, 0),      # Vert
            (0, 0, 255),      # Bleu
            (255, 255, 0),    # Jaune
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (128, 0, 128),    # Violet
            (255, 165, 0),    # Orange
        ]
        
    def analyze_phases(self, image, num_phases=2, method='kmeans', 
                      blur_factor=1, noise_reduction=True):
        """
        Analyse des phases dans l'image
        """
        try:
            self.original_image = image.copy()
            
            # Prétraitement
            processed = self._preprocess_image(image, blur_factor, noise_reduction)
            
            # Segmentation des phases
            if method == 'kmeans':
                phase_map = self._segment_phases_kmeans(processed, num_phases)
            elif method == 'threshold':
                phase_map = self._segment_phases_threshold(processed, num_phases)
            else:
                phase_map = self._segment_phases_adaptive(processed, num_phases)
            
            # Analyse des propriétés
            phase_properties = self._analyze_phase_properties(phase_map)
            
            # Calcul des statistiques
            phase_stats = self._calculate_phase_statistics(phase_properties, phase_map)
            
            self.phase_data = {
                'properties': phase_properties,
                'stats': phase_stats,
                'phase_map': phase_map,
                'processed_image': processed,
                'num_phases': num_phases
            }
            
            return self.phase_data
            
        except Exception as e:
            print(f"Erreur dans l'analyse des phases: {str(e)}")
            return None
    
    def _preprocess_image(self, image, blur_factor, noise_reduction):
        """Prétraitement de l'image"""
        # Conversion en niveaux de gris si nécessaire
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Lissage pour réduire le bruit
        if blur_factor > 0:
            gray = cv2.GaussianBlur(gray, (blur_factor*2+1, blur_factor*2+1), 0)
        
        # Réduction du bruit supplémentaire
        if noise_reduction:
            gray = cv2.medianBlur(gray, 3)
        
        return gray
    
    def _segment_phases_kmeans(self, image, num_phases):
        """Segmentation par K-means"""
        # Préparation des données
        data = image.flatten().astype(np.float32)
        data = data.reshape((-1, 1))
        
        # Critères de convergence
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        
        # K-means clustering
        _, labels, centers = cv2.kmeans(data, num_phases, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Reshape des labels
        phase_map = labels.reshape(image.shape)
        
        # Tri des phases par intensité moyenne
        sorted_indices = np.argsort(centers.flatten())
        phase_map_sorted = np.zeros_like(phase_map)
        
        for new_label, old_label in enumerate(sorted_indices):
            phase_map_sorted[phase_map == old_label] = new_label
        
        return phase_map_sorted.astype(np.uint8)
    
    def _segment_phases_threshold(self, image, num_phases):
        """Segmentation par seuillage multiple"""
        # Calcul automatique des seuils
        thresholds = []
        for i in range(1, num_phases):
            threshold = (255 * i) // num_phases
            thresholds.append(threshold)
        
        # Application des seuils
        phase_map = np.zeros_like(image, dtype=np.uint8)
        
        for i, threshold in enumerate(thresholds):
            if i == 0:
                phase_map[image <= threshold] = i
            else:
                phase_map[(image > thresholds[i-1]) & (image <= threshold)] = i
        
        # Dernière phase
        if thresholds:
            phase_map[image > thresholds[-1]] = len(thresholds)
        
        return phase_map
    
    def _segment_phases_adaptive(self, image, num_phases):
        """Segmentation adaptative"""
        # Calcul de l'histogramme
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Lissage de l'histogramme
        hist_smooth = cv2.GaussianBlur(hist.reshape(-1, 1), (5, 1), 0).flatten()
        
        # Recherche des pics dans l'histogramme
        peaks = self._find_histogram_peaks(hist_smooth, num_phases)
        
        # Création des seuils entre les pics
        peaks_sorted = sorted(peaks)
        thresholds = []
        
        for i in range(len(peaks_sorted) - 1):
            # Seuil au point le plus bas entre deux pics
            start = peaks_sorted[i]
            end = peaks_sorted[i + 1]
            valley = start + np.argmin(hist_smooth[start:end])
            thresholds.append(valley)
        
        # Application des seuils
        phase_map = np.zeros_like(image, dtype=np.uint8)
        
        for i, threshold in enumerate(thresholds):
            if i == 0:
                phase_map[image <= threshold] = i
            else:
                phase_map[(image > thresholds[i-1]) & (image <= threshold)] = i
        
        # Dernière phase
        if thresholds:
            phase_map[image > thresholds[-1]] = len(thresholds)
        
        return phase_map
    
    def _find_histogram_peaks(self, hist, num_peaks):
        """Recherche des pics dans l'histogramme"""
        # Méthode simple de détection des pics
        peaks = []
        
        # Recherche des maxima locaux
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > np.max(hist) * 0.1:
                peaks.append(i)
        
        # Si pas assez de pics, ajouter des pics artificiels
        if len(peaks) < num_peaks:
            # Diviser l'histogramme en zones égales
            for i in range(num_peaks):
                peak_pos = (256 * i) // num_peaks + 256 // (2 * num_peaks)
                if peak_pos not in peaks:
                    peaks.append(peak_pos)
        
        # Garder seulement les meilleurs pics
        if len(peaks) > num_peaks:
            peak_values = [(peak, hist[peak]) for peak in peaks]
            peak_values.sort(key=lambda x: x[1], reverse=True)
            peaks = [peak for peak, _ in peak_values[:num_peaks]]
        
        return sorted(peaks)
    
    def _analyze_phase_properties(self, phase_map):
        """Analyse des propriétés de chaque phase"""
        unique_phases = np.unique(phase_map)
        phase_properties = []
        
        for phase_id in unique_phases:
            mask = phase_map == phase_id
            area = np.sum(mask)
            
            if area > 0:
                # Calcul du centroïde
                y_coords, x_coords = np.where(mask)
                centroid_y = np.mean(y_coords)
                centroid_x = np.mean(x_coords)
                
                # Calcul du pourcentage de surface
                total_pixels = phase_map.size
                area_percentage = (area / total_pixels) * 100
                
                # Calcul de la compacité approximative
                contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                perimeter = sum(cv2.arcLength(contour, True) for contour in contours)
                compactness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
                
                phase_info = {
                    'phase_id': int(phase_id),
                    'area': area,
                    'area_percentage': area_percentage,
                    'centroid': (centroid_y, centroid_x),
                    'perimeter': perimeter,
                    'compactness': compactness
                }
                
                phase_properties.append(phase_info)
        
        return phase_properties
    
    def _calculate_phase_statistics(self, phase_properties, phase_map):
        """Calcul des statistiques générales des phases"""
        if not phase_properties:
            return {}
        
        total_area = phase_map.size
        phase_count = len(phase_properties)
        
        # Statistiques par phase
        areas = [prop['area'] for prop in phase_properties]
        percentages = [prop['area_percentage'] for prop in phase_properties]
        
        # Phase dominante
        dominant_phase_idx = np.argmax(areas)
        dominant_phase = phase_properties[dominant_phase_idx]
        
        # Distribution des phases
        phase_distribution = {}
        for prop in phase_properties:
            phase_distribution[f"Phase_{prop['phase_id']}"] = prop['area_percentage']
        
        return {
            'total_phases': phase_count,
            'total_area': total_area,
            'dominant_phase': dominant_phase['phase_id'],
            'dominant_phase_percentage': dominant_phase['area_percentage'],
            'phase_distribution': phase_distribution,
            'mean_area': np.mean(areas),
            'std_area': np.std(areas),
            'uniformity_index': 1.0 - (np.std(percentages) / np.mean(percentages)) if np.mean(percentages) > 0 else 0
        }
    
    def get_visualization_image(self):
        """Génère une image de visualisation des phases"""
        if self.phase_data is None:
            return None
        
        phase_map = self.phase_data['phase_map']
        num_phases = self.phase_data['num_phases']
        
        # Création d'une image colorée
        colored_image = np.zeros((*phase_map.shape, 3), dtype=np.uint8)
        
        for phase_id in range(num_phases):
            mask = phase_map == phase_id
            color = self.phase_colors[phase_id % len(self.phase_colors)]
            colored_image[mask] = color
        
        return colored_image
    
    def get_phase_overlay(self, alpha=0.5):
        """Génère une superposition des phases sur l'image originale"""
        if self.phase_data is None or self.original_image is None:
            return None
        
        # Image des phases en couleur
        phase_colored = self.get_visualization_image()
        
        # Redimensionnement si nécessaire
        if phase_colored.shape[:2] != self.original_image.shape[:2]:
            phase_colored = cv2.resize(phase_colored, 
                                     (self.original_image.shape[1], self.original_image.shape[0]))
        
        # Conversion de l'image originale en couleur si nécessaire
        if len(self.original_image.shape) == 2:
            original_colored = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
        else:
            original_colored = self.original_image.copy()
        
        # Mélange des images
        overlay = cv2.addWeighted(original_colored, 1-alpha, phase_colored, alpha, 0)
        
        return overlay
    
    def export_results(self, output_path):
        """Export des résultats vers un fichier"""
        if self.phase_data is None:
            return False
        
        try:
            import pandas as pd
            
            # DataFrame des propriétés des phases
            df_properties = pd.DataFrame(self.phase_data['properties'])
            
            # DataFrame des statistiques
            stats_data = []
            for key, value in self.phase_data['stats'].items():
                if key == 'phase_distribution':
                    for phase_name, percentage in value.items():
                        stats_data.append({'metric': phase_name, 'value': percentage})
                else:
                    stats_data.append({'metric': key, 'value': value})
            
            df_stats = pd.DataFrame(stats_data)
            
            # Export vers Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_properties.to_excel(writer, sheet_name='Phase_Properties', index=False)
                df_stats.to_excel(writer, sheet_name='Phase_Statistics', index=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {str(e)}")
            return False
    
    def get_phase_histogram(self):
        """Génère un histogramme des phases"""
        if self.phase_data is None:
            return None
        
        try:
            # Données pour l'histogramme
            phase_names = [f"Phase {prop['phase_id']}" for prop in self.phase_data['properties']]
            percentages = [prop['area_percentage'] for prop in self.phase_data['properties']]
            colors = [np.array(self.phase_colors[i % len(self.phase_colors)])/255.0 
                     for i in range(len(phase_names))]
            
            # Création du graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(phase_names, percentages, color=colors)
            
            # Personnalisation
            ax.set_ylabel('Pourcentage de surface (%)')
            ax.set_title('Distribution des phases')
            ax.set_ylim(0, 100)
            
            # Ajout des valeurs sur les barres
            for bar, percentage in zip(bars, percentages):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       f'{percentage:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Erreur lors de la création de l'histogramme: {str(e)}")
            return None

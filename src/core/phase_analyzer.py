import cv2
import numpy as np
from sklearn.cluster import KMeans
from skimage.measure import label, regionprops
from skimage.filters import gaussian

class PhaseAnalyzer:
    def __init__(self):
        self.n_phases = 3  # Default number of phases
        
    def analyze_phases(self, image):
        """Analyze phases in metallographic image"""
        # Convert to LAB color space for better clustering
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Segment phases
        phase_map, phase_labels = self.segment_phases(lab_image)
        
        # Analyze each phase
        phases = self.analyze_phase_properties(phase_map, phase_labels, image)
        
        return {
            'phases': phases,
            'phase_map': phase_map,
            'phase_labels': phase_labels,
            'total_phases': len(phases)
        }
        
    def segment_phases(self, image):
        """Segment phases using K-means clustering"""
        # Reshape image for clustering
        h, w, c = image.shape
        image_reshaped = image.reshape(h * w, c)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=self.n_phases, random_state=42, n_init=10)
        phase_labels = kmeans.fit_predict(image_reshaped)
        
        # Reshape back to image dimensions
        phase_map = phase_labels.reshape(h, w)
        
        # Create colored phase map
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        colored_phase_map = np.zeros((h, w, 3), dtype=np.uint8)
        
        for i in range(self.n_phases):
            mask = phase_map == i
            colored_phase_map[mask] = colors[i % len(colors)]
            
        return colored_phase_map, phase_map
        
    def analyze_phase_properties(self, phase_map, phase_labels, original_image):
        """Analyze properties of each phase"""
        phases = []
        total_area = phase_labels.size
        
        for phase_id in range(self.n_phases):
            # Create mask for this phase
            mask = (phase_labels == phase_id)
            
            # Calculate area and percentage
            area = np.sum(mask)
            percentage = (area / total_area) * 100
            
            # Calculate average color
            if area > 0:
                phase_pixels = original_image[mask]
                avg_color = np.mean(phase_pixels, axis=0)
            else:
                avg_color = [0, 0, 0]
                
            # Find connected components
            labeled_mask = label(mask)
            regions = regionprops(labeled_mask)
            
            phase_info = {
                'id': phase_id,
                'name': f'Phase {phase_id + 1}',
                'area': area,
                'percentage': percentage,
                'avg_color': avg_color.tolist(),
                'num_regions': len(regions),
                'regions': []
            }
            
            # Analyze individual regions
            for region in regions:
                if region.area > 50:  # Filter small regions
                    region_info = {
                        'area': region.area,
                        'centroid': region.centroid,
                        'bbox': region.bbox,
                        'eccentricity': region.eccentricity,
                        'solidity': region.solidity
                    }
                    phase_info['regions'].append(region_info)
                    
            phases.append(phase_info)
            
        return phases

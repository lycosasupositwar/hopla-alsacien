import os
import cv2
from pathlib import Path

class FileHandler:
    def __init__(self):
        self.supported_formats = [
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
        ]
        
    def validate_image_file(self, file_path):
        """Validate if file is a supported image format"""
        if not os.path.exists(file_path):
            return False
            
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats
        
    def get_image_files(self, directory):
        """Get all image files from directory"""
        image_files = []
        
        for file_path in Path(directory).iterdir():
            if file_path.is_file() and self.validate_image_file(str(file_path)):
                image_files.append(str(file_path))
                
        return sorted(image_files)
        
    def load_image(self, file_path):
        """Load image using OpenCV"""
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            return image
        except Exception as e:
            raise ValueError(f"Error loading image: {str(e)}")
            
    def save_image(self, image, file_path):
        """Save image using OpenCV"""
        try:
            cv2.imwrite(file_path, image)
            return True
        except Exception as e:
            raise ValueError(f"Error saving image: {str(e)}")

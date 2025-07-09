from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QPushButton, QSlider, QComboBox,
                           QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
import cv2
import numpy as np

class ImageViewer(QWidget):
    image_clicked = pyqtSignal(int, int)  # Signal pour clic sur l'image
    zoom_changed = pyqtSignal(float)      # Signal pour changement de zoom
    
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.processed_image = None
        self.overlay_image = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Contrôles de visualisation
        controls_group = QGroupBox("Contrôles de visualisation")
        controls_layout = QHBoxLayout()
        
        # Sélecteur de mode d'affichage
        controls_layout.addWidget(QLabel("Mode:"))
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["Original", "Traité", "Superposition"])
        self.display_mode_combo.currentTextChanged.connect(self.update_display)
        controls_layout.addWidget(self.display_mode_combo)
        
        # Contrôle de zoom
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 10% à 500%
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        controls_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        controls_layout.addWidget(self.zoom_label)
        
        # Boutons de zoom
        zoom_fit_btn = QPushButton("Ajuster")
        zoom_fit_btn.clicked.connect(self.zoom_to_fit)
        controls_layout.addWidget(zoom_fit_btn)
        
        zoom_100_btn = QPushButton("100%")
        zoom_100_btn.clicked.connect(self.zoom_to_100)
        controls_layout.addWidget(zoom_100_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Zone d'affichage de l'image
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.mousePressEvent = self.on_image_click
        
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Informations sur l'image
        self.info_label = QLabel("Aucune image chargée")
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
    
    def load_image(self, image_path):
        """Charge une image depuis un fichier"""
        try:
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                raise ValueError("Impossible de charger l'image")
            
            # Conversion BGR vers RGB pour l'affichage
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.processed_image = None
            self.overlay_image = None
            
            self.update_display()
            self.update_info()
            
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {str(e)}")
    
    def set_image(self, image):
        """Définit l'image directement (numpy array)"""
        if image is None:
            return
        
        try:
            # Copie de l'image
            self.original_image = image.copy()
            
            # Conversion si nécessaire
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Supposer que c'est en BGR, convertir en RGB
                if np.max(image) > 1.0:  # Image en 0-255
                    self.original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.processed_image = None
            self.overlay_image = None
            
            self.update_display()
            self.update_info()
            
        except Exception as e:
            print(f"Erreur lors de la définition de l'image: {str(e)}")
    
    def set_processed_image(self, image):
        """Définit l'image traitée"""
        if image is None:
            return
        
        try:
            self.processed_image = image.copy()
            
            # Assurer que l'image est en RGB
            if len(image.shape) == 2:
                self.processed_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                # Vérifier si c'est BGR et convertir
                if np.max(image) > 1.0:
                    self.processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.update_display()
            
        except Exception as e:
            print(f"Erreur lors de la définition de l'image traitée: {str(e)}")
    
    def set_overlay_image(self, image):
        """Définit l'image de superposition"""
        if image is None:
            return
        
        try:
            self.overlay_image = image.copy()
            
            # Assurer que l'image est en RGB
            if len(image.shape) == 2:
                self.overlay_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                if np.max(image) > 1.0:
                    self.overlay_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.update_display()
            
        except Exception as e:
            print(f"Erreur lors de la définition de l'image de superposition: {str(e)}")
    
    def update_display(self):
        """Met à jour l'affichage selon le mode sélectionné"""
        current_mode = self.display_mode_combo.currentText()
        
        display_image = None
        
        if current_mode == "Original" and self.original_image is not None:
            display_image = self.original_image
        elif current_mode == "Traité" and self.processed_image is not None:
            display_image = self.processed_image
        elif current_mode == "Superposition" and self.overlay_image is not None:
            display_image = self.overlay_image
        elif self.original_image is not None:
            display_image = self.original_image
        
        if display_image is not None:
            self.display_numpy_image(display_image)
        else:
            self.image_label.setText("Aucune image disponible pour ce mode")
            self.image_label.setPixmap(QPixmap())
    
    def display_numpy_image(self, image):
        """Affiche une image numpy dans le label"""
        try:
            # Normalisation de l'image
            if image.dtype != np.uint8:
                if np.max(image) <= 1.0:
                    image = (image * 255).astype(np.uint8)
                else:
                    image = np.clip(image, 0, 255).astype(np.uint8)
            
            # Conversion en QImage
            if len(image.shape) == 2:
                height, width = image.shape
                bytes_per_line = width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            else:
                height, width, channels = image.shape
                bytes_per_line = channels * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Création du pixmap avec zoom
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                pixmap.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.current_pixmap = scaled_pixmap
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            
        except Exception as e:
            print(f"Erreur lors de l'affichage de l'image: {str(e)}")
            self.image_label.setText("Erreur d'affichage")
    
    def on_zoom_changed(self, value):
        """Gère le changement de zoom"""
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.update_display()
        self.zoom_changed.emit(self.zoom_factor)
    
    def zoom_to_fit(self):
        """Ajuste le zoom pour faire tenir l'image"""
        if self.original_image is None:
            return
        
        # Calcul du facteur de zoom pour ajuster à la taille disponible
        available_size = self.scroll_area.size()
        image_size = self.original_image.shape[:2]
        
        zoom_x = available_size.width() / image_size[1]
        zoom_y = available_size.height() / image_size[0]
        zoom_factor = min(zoom_x, zoom_y, 1.0)  # Ne pas agrandir au-delà de 100%
        
        zoom_percent = int(zoom_factor * 100)
        self.zoom_slider.setValue(zoom_percent)
    
    def zoom_to_100(self):
        """Remet le zoom à 100%"""
        self.zoom_slider.setValue(100)
    
    def on_image_click(self, event):
        """Gère le clic sur l'image"""
        if self.current_pixmap is None:
            return
        
        # Conversion des coordonnées de l'affichage vers l'image originale
        click_x = event.x() / self.zoom_factor
        click_y = event.y() / self.zoom_factor
        
        self.image_clicked.emit(int(click_x), int(click_y))
    
    def update_info(self):
        """Met à jour les informations sur l'image"""
        if self.original_image is None:
            self.info_label.setText("Aucune image chargée")
            return
        
        shape = self.original_image.shape
        if len(shape) == 2:
            info_text = f"Dimensions: {shape[1]}x{shape[0]} (Niveaux de gris)"
        else:
            info_text = f"Dimensions: {shape[1]}x{shape[0]}x{shape[2]} (Couleur)"
        
        info_text += f" | Zoom: {self.zoom_factor:.1f}x"
        
        if self.processed_image is not None:
            info_text += " | Image traitée disponible"
        
        if self.overlay_image is not None:
            info_text += " | Superposition disponible"
        
        self.info_label.setText(info_text)
    
    def get_current_image(self):
        """Retourne l'image actuellement affichée"""
        current_mode = self.display_mode_combo.currentText()
        
        if current_mode == "Original":
            return self.original_image
        elif current_mode == "Traité":
            return self.processed_image
        elif current_mode == "Superposition":
            return self.overlay_image
        else:
            return self.original_image
    
    def clear_images(self):
        """Efface toutes les images"""
        self.original_image = None
        self.processed_image = None
        self.overlay_image = None
        self.current_pixmap = None
        self.image_label.clear()
        self.image_label.setText("Aucune image chargée")
        self.update_info()

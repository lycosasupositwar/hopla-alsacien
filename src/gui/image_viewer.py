import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QPushButton, QSlider, QCheckBox)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor

class ImageViewer(QWidget):
    point_clicked = pyqtSignal(QPoint)
    
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.display_image = None
        self.grain_contours = None
        self.phase_map = None
        self.scale_factor = 1.0
        self.manual_correction_enabled = False
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("Zoom +")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.zoom_out_btn = QPushButton("Zoom -")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_zoom_btn = QPushButton("Reset")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        self.show_grains_cb = QCheckBox("Afficher grains")
        self.show_grains_cb.setChecked(True)
        self.show_grains_cb.stateChanged.connect(self.update_display)
        
        self.show_phases_cb = QCheckBox("Afficher phases")
        self.show_phases_cb.setChecked(True)
        self.show_phases_cb.stateChanged.connect(self.update_display)
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.reset_zoom_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.show_grains_cb)
        controls_layout.addWidget(self.show_phases_cb)
        
        # Image display
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray")
        self.image_label.mousePressEvent = self.mouse_press_event
        
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def load_image(self, image_path):
        self.original_image = cv2.imread(image_path)
        self.display_image = self.original_image.copy()
        self.grain_contours = None
        self.phase_map = None
        self.update_display()
        
    def overlay_grains(self, grain_analysis):
        if 'contours' in grain_analysis:
            self.grain_contours = grain_analysis['contours']
            self.update_display()
            
    def overlay_phases(self, phase_analysis):
        if 'phase_map' in phase_analysis:
            self.phase_map = phase_analysis['phase_map']
            self.update_display()
            
    def update_display(self):
        if self.original_image is None:
            return
            
        # Start with original image
        display_img = self.original_image.copy()
        
        # Add phase overlay
        if self.phase_map is not None and self.show_phases_cb.isChecked():
            # Blend phase map with original image
            alpha = 0.3
            display_img = cv2.addWeighted(display_img, 1-alpha, self.phase_map, alpha, 0)
            
        # Add grain contours
        if self.grain_contours is not None and self.show_grains_cb.isChecked():
            cv2.drawContours(display_img, self.grain_contours, -1, (0, 255, 0), 2)
            
        # Convert to QImage and display
        self.display_image = display_img
        self.show_image()
        
    def show_image(self):
        if self.display_image is None:
            return
            
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        
        # Create QImage
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image
        scaled_image = qt_image.scaled(
            int(w * self.scale_factor), 
            int(h * self.scale_factor), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(scaled_image)
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())
        
    def zoom_in(self):
        self.scale_factor *= 1.25
        self.show_image()
        
    def zoom_out(self):
        self.scale_factor /= 1.25
        self.show_image()
        
    def reset_zoom(self):
        self.scale_factor = 1.0
        self.show_image()
        
    def enable_manual_correction(self, enabled):
        self.manual_correction_enabled = enabled
        
    def mouse_press_event(self, event):
        if self.manual_correction_enabled and event.button() == Qt.LeftButton:
            # Convert click position to image coordinates
            pos = event.pos()
            scaled_pos = QPoint(
                int(pos.x() / self.scale_factor),
                int(pos.y() / self.scale_factor)
            )
            self.point_clicked.emit(scaled_pos)

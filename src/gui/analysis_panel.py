from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QLabel, QSpinBox, QDoubleSpinBox, QSlider, 
                           QPushButton, QComboBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np

class AnalysisPanel(QWidget):
    analysis_requested = pyqtSignal(str)  # Signal pour demander une analyse
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Paramètres d'analyse des grains
        grain_group = QGroupBox("Analyse des grains")
        grain_layout = QVBoxLayout()
        
        # Facteur de flou
        blur_layout = QHBoxLayout()
        blur_layout.addWidget(QLabel("Facteur de flou:"))
        self.blur_spinbox = QSpinBox()
        self.blur_spinbox.setRange(0, 10)
        self.blur_spinbox.setValue(1)
        blur_layout.addWidget(self.blur_spinbox)
        grain_layout.addLayout(blur_layout)
        
        # Seuil de binarisation
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Seuil:"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(0, 255)
        self.threshold_spinbox.setValue(128)
        threshold_layout.addWidget(self.threshold_spinbox)
        grain_layout.addLayout(threshold_layout)
        
        # Taille minimale des grains
        min_size_layout = QHBoxLayout()
        min_size_layout.addWidget(QLabel("Taille min:"))
        self.min_size_spinbox = QSpinBox()
        self.min_size_spinbox.setRange(1, 10000)
        self.min_size_spinbox.setValue(50)
        min_size_layout.addWidget(self.min_size_spinbox)
        grain_layout.addLayout(min_size_layout)
        
        # Taille maximale des grains
        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("Taille max:"))
        self.max_size_spinbox = QSpinBox()
        self.max_size_spinbox.setRange(1, 50000)
        self.max_size_spinbox.setValue(5000)
        max_size_layout.addWidget(self.max_size_spinbox)
        grain_layout.addLayout(max_size_layout)
        
        # Bouton d'analyse des grains
        self.grain_analysis_btn = QPushButton("Analyser les grains")
        self.grain_analysis_btn.clicked.connect(lambda: self.analysis_requested.emit("grain"))
        grain_layout.addWidget(self.grain_analysis_btn)
        
        grain_group.setLayout(grain_layout)
        layout.addWidget(grain_group)
        
        # Paramètres d'analyse des phases
        phase_group = QGroupBox("Analyse des phases")
        phase_layout = QVBoxLayout()
        
        # Nombre de phases
        num_phases_layout = QHBoxLayout()
        num_phases_layout.addWidget(QLabel("Nombre de phases:"))
        self.num_phases_spinbox = QSpinBox()
        self.num_phases_spinbox.setRange(2, 8)
        self.num_phases_spinbox.setValue(2)
        num_phases_layout.addWidget(self.num_phases_spinbox)
        phase_layout.addLayout(num_phases_layout)
        
        # Méthode de segmentation
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Méthode:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["kmeans", "threshold", "adaptive"])
        method_layout.addWidget(self.method_combo)
        phase_layout.addLayout(method_layout)
        
        # Facteur de flou pour phases
        phase_blur_layout = QHBoxLayout()
        phase_blur_layout.addWidget(QLabel("Flou:"))
        self.phase_blur_spinbox = QSpinBox()
        self.phase_blur_spinbox.setRange(0, 10)
        self.phase_blur_spinbox.setValue(1)
        phase_blur_layout.addWidget(self.phase_blur_spinbox)
        phase_layout.addLayout(phase_blur_layout)
        
        # Réduction du bruit
        self.noise_reduction_cb = QCheckBox("Réduction du bruit")
        self.noise_reduction_cb.setChecked(True)
        phase_layout.addWidget(self.noise_reduction_cb)
        
        # Bouton d'analyse des phases
        self.phase_analysis_btn = QPushButton("Analyser les phases")
        self.phase_analysis_btn.clicked.connect(lambda: self.analysis_requested.emit("phase"))
        phase_layout.addWidget(self.phase_analysis_btn)
        
        phase_group.setLayout(phase_layout)
        layout.addWidget(phase_group)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def get_grain_parameters(self):
        """Retourne les paramètres d'analyse des grains"""
        return {
            'blur_factor': self.blur_spinbox.value(),
            'threshold_value': self.threshold_spinbox.value(),
            'min_grain_size': self.min_size_spinbox.value(),
            'max_grain_size': self.max_size_spinbox.value()
        }
    
    def get_phase_parameters(self):
        """Retourne les paramètres d'analyse des phases"""
        return {
            'num_phases': self.num_phases_spinbox.value(),
            'method': self.method_combo.currentText(),
            'blur_factor': self.phase_blur_spinbox.value(),
            'noise_reduction': self.noise_reduction_cb.isChecked()
        }
    
    def set_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(value)
        if value == 0:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
    
    def enable_analysis(self, enabled=True):
        """Active/désactive les boutons d'analyse"""
        self.grain_analysis_btn.setEnabled(enabled)
        self.phase_analysis_btn.setEnabled(enabled)

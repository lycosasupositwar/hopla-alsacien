from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QGroupBox, QComboBox, 
                             QSlider, QLabel, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal

class ToolsPanel(QWidget):
    analysis_requested = pyqtSignal(str)
    manual_correction_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Analysis group
        analysis_group = QGroupBox("Analyse")
        analysis_layout = QVBoxLayout()
        
        self.grain_btn = QPushButton("Analyse des grains")
        self.grain_btn.clicked.connect(lambda: self.analysis_requested.emit("grain"))
        self.grain_btn.setEnabled(False)
        
        self.phase_btn = QPushButton("Analyse des phases")
        self.phase_btn.clicked.connect(lambda: self.analysis_requested.emit("phase"))
        self.phase_btn.setEnabled(False)
        
        self.combined_btn = QPushButton("Analyse complète")
        self.combined_btn.clicked.connect(lambda: self.analysis_requested.emit("combined"))
        self.combined_btn.setEnabled(False)
        
        analysis_layout.addWidget(self.grain_btn)
        analysis_layout.addWidget(self.phase_btn)
        analysis_layout.addWidget(self.combined_btn)
        analysis_group.setLayout(analysis_layout)
        
        # Parameters group
        params_group = QGroupBox("Paramètres")
        params_layout = QVBoxLayout()
        
        # Grain threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Seuil:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(128)
        self.threshold_label = QLabel("128")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_label.setText(str(v))
        )
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        
        # Min grain size
        min_size_layout = QHBoxLayout()
        min_size_layout.addWidget(QLabel("Taille min:"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(10, 1000)
        self.min_size_spin.setValue(100)
        self.min_size_spin.setSuffix(" px")
        min_size_layout.addWidget(self.min_size_spin)

        # Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Échelle (px/mm):"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 10000)
        self.scale_spin.setValue(100)
        scale_layout.addWidget(self.scale_spin)
        
        # ASTM standard
        astm_layout = QHBoxLayout()
        astm_layout.addWidget(QLabel("Norme:"))
        self.astm_combo = QComboBox()
        self.astm_combo.addItems(["E112", "E1382"])
        astm_layout.addWidget(self.astm_combo)
        
        params_layout.addLayout(threshold_layout)
        params_layout.addLayout(min_size_layout)
        params_layout.addLayout(scale_layout)
        params_layout.addLayout(astm_layout)
        params_group.setLayout(params_layout)
        
        # Manual correction group
        correction_group = QGroupBox("Correction")
        correction_layout = QVBoxLayout()
        
        self.correction_btn = QPushButton("Correction manuelle")
        self.correction_btn.clicked.connect(self.manual_correction_requested.emit)
        self.correction_btn.setEnabled(False)
        
        correction_layout.addWidget(self.correction_btn)
        correction_group.setLayout(correction_layout)
        
        layout.addWidget(analysis_group)
        layout.addWidget(params_group)
        layout.addWidget(correction_group)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def enable_analysis_buttons(self, enabled):
        self.grain_btn.setEnabled(enabled)
        self.phase_btn.setEnabled(enabled)
        self.combined_btn.setEnabled(enabled)
        
    def get_parameters(self):
        return {
            'threshold': self.threshold_slider.value(),
            'min_size': self.min_size_spin.value(),
            'scale': self.scale_spin.value(),
            'astm_standard': self.astm_combo.currentText()
        }

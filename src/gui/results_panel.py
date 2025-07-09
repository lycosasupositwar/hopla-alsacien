from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QTextEdit, QPushButton,
                           QTabWidget, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont
import numpy as np
import cv2

class ResultsPanel(QWidget):
    export_requested = pyqtSignal(str)  # Signal pour export
    
    def __init__(self):
        super().__init__()
        self.current_results = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("Résultats d'analyse")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Tabs pour différents types de résultats
        self.tabs = QTabWidget()
        
        # Tab pour les statistiques
        self.stats_tab = QWidget()
        self.setup_stats_tab()
        self.tabs.addTab(self.stats_tab, "Statistiques")
        
        # Tab pour les données détaillées
        self.details_tab = QWidget()
        self.setup_details_tab()
        self.tabs.addTab(self.details_tab, "Détails")
        
        # Tab pour l'export
        self.export_tab = QWidget()
        self.setup_export_tab()
        self.tabs.addTab(self.export_tab, "Export")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def setup_stats_tab(self):
        """Configuration de l'onglet statistiques"""
        layout = QVBoxLayout()
        
        # Zone de texte pour les statistiques
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        layout.addWidget(self.stats_text)
        
        # Tableau pour les résultats numériques
        self.stats_table = QTableWidget()
        layout.addWidget(self.stats_table)
        
        self.stats_tab.setLayout(layout)
    
    def setup_details_tab(self):
        """Configuration de l'onglet détails"""
        layout = QVBoxLayout()
        
        # Tableau pour les données détaillées
        self.details_table = QTableWidget()
        layout.addWidget(self.details_table)
        
        self.details_tab.setLayout(layout)
    
    def setup_export_tab(self):
        """Configuration de l'onglet export"""
        layout = QVBoxLayout()
        
        # Boutons d'export
        export_group = QGroupBox("Options d'export")
        export_layout = QVBoxLayout()
        
        self.export_excel_btn = QPushButton("Exporter vers Excel")
        self.export_excel_btn.clicked.connect(lambda: self.export_requested.emit("excel"))
        export_layout.addWidget(self.export_excel_btn)
        
        self.export_csv_btn = QPushButton("Exporter vers CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_json_btn = QPushButton("Exporter vers JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_requested.emit("json"))
        export_layout.addWidget(self.export_json_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Zone de statut d'export
        self.export_status = QLabel("Prêt pour l'export")
        layout.addWidget(self.export_status)
        
        self.export_tab.setLayout(layout)
    
    def display_grain_results(self, results):
        """Affiche les résultats d'analyse des grains"""
        self.current_results = results
        
        if not results:
            self.clear_results()
            return
        
        # Statistiques générales
        stats = results['astm_stats']
        stats_text = f"""
        Résultats d'analyse des grains:
        
        Nombre total de grains: {stats['grain_count']}
        Diamètre moyen: {stats['mean_diameter']:.2f} pixels
        Écart-type: {stats['std_diameter']:.2f} pixels
        Surface moyenne: {stats['mean_area']:.2f} pixels²
        Surface totale: {stats['total_area']:.2f} pixels²
        Numéro de grain ASTM: {stats['astm_grain_number']:.2f}
        """
        
        self.stats_text.setText(stats_text)
        
        # Tableau des statistiques
        self.populate_stats_table(stats)
        
        # Tableau des détails
        self.populate_grain_details(results['properties'])
    
    def display_phase_results(self, results):
        """Affiche les résultats d'analyse des phases"""
        self.current_results = results
        
        if not results:
            self.clear_results()
            return
        
        # Statistiques générales
        stats = results['stats']
        stats_text = f"""
        Résultats d'analyse des phases:
        
        Nombre total de phases: {stats['total_phases']}
        Phase dominante: Phase {stats['dominant_phase']} ({stats['dominant_phase_percentage']:.1f}%)
        Surface moyenne: {stats['mean_area']:.2f} pixels²
        Indice d'uniformité: {stats['uniformity_index']:.3f}
        """
        
        self.stats_text.setText(stats_text)
        
        # Tableau des statistiques
        self.populate_stats_table(stats)
        
        # Tableau des détails
        self.populate_phase_details(results['properties'])
    
    def populate_stats_table(self, stats):
        """Remplit le tableau des statistiques"""
        # Filtrer les données numériques
        numeric_stats = {k: v for k, v in stats.items() 
                        if isinstance(v, (int, float)) and k != 'phase_distribution'}
        
        self.stats_table.setRowCount(len(numeric_stats))
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Métrique", "Valeur"])
        
        for i, (key, value) in enumerate(numeric_stats.items()):
            self.stats_table.setItem(i, 0, QTableWidgetItem(key))
            if isinstance(value, float):
                self.stats_table.setItem(i, 1, QTableWidgetItem(f"{value:.3f}"))
            else:
                self.stats_table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        self.stats_table.resizeColumnsToContents()
    
    def populate_grain_details(self, properties):
        """Remplit le tableau des détails des grains"""
        if not properties:
            return
        
        self.details_table.setRowCount(len(properties))
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels([
            "Grain ID", "Surface", "Diamètre équivalent", "Centroïde"
        ])
        
        for i, prop in enumerate(properties):
            self.details_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.details_table.setItem(i, 1, QTableWidgetItem(f"{prop['area']:.0f}"))
            self.details_table.setItem(i, 2, QTableWidgetItem(f"{prop['equivalent_diameter']:.2f}"))
            centroid = prop['centroid']
            self.details_table.setItem(i, 3, QTableWidgetItem(f"({centroid[0]:.0f}, {centroid[1]:.0f})"))
        
        self.details_table.resizeColumnsToContents()
    
    def populate_phase_details(self, properties):
        """Remplit le tableau des détails des phases"""
        if not properties:
            return
        
        self.details_table.setRowCount(len(properties))
        self.details_table.setColumnCount(5)
        self.details_table.setHorizontalHeaderLabels([
            "Phase ID", "Surface", "Pourcentage", "Centroïde", "Compacité"
        ])
        
        for i, prop in enumerate(properties):
            self.details_table.setItem(i, 0, QTableWidgetItem(f"Phase {prop['phase_id']}"))
            self.details_table.setItem(i, 1, QTableWidgetItem(f"{prop['area']:.0f}"))
            self.details_table.setItem(i, 2, QTableWidgetItem(f"{prop['area_percentage']:.1f}%"))
            centroid = prop['centroid']
            self.details_table.setItem(i, 3, QTableWidgetItem(f"({centroid[0]:.0f}, {centroid[1]:.0f})"))
            self.details_table.setItem(i, 4, QTableWidgetItem(f"{prop['compactness']:.3f}"))
        
        self.details_table.resizeColumnsToContents()
    
    def clear_results(self):
        """Efface tous les résultats"""
        self.stats_text.clear()
        self.stats_table.setRowCount(0)
        self.details_table.setRowCount(0)
        self.current_results = None
    
    def set_export_status(self, message):
        """Met à jour le statut d'export"""
        self.export_status.setText(message)
    
    def enable_export(self, enabled=True):
        """Active/désactive les boutons d'export"""
        self.export_excel_btn.setEnabled(enabled)
        self.export_csv_btn.setEnabled(enabled)
        self.export_json_btn.setEnabled(enabled)


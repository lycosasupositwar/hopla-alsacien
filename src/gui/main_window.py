import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QMenuBar, QMenu, QAction, QFileDialog, QStatusBar,
                             QSplitter, QMessageBox, QProgressBar, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon

from .image_viewer import ImageViewer
from .results_panel import ResultsPanel
from .tools_panel import ToolsPanel
from ..core.grain_analyzer import GrainAnalyzer
from ..core.phase_analyzer import PhaseAnalyzer
from ..core.astm_e112 import ASTM_E112
from ..utils.file_handler import FileHandler
from ..utils.export_utils import ExportUtils

class AnalysisThread(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    
    def __init__(self, image_path, analysis_type, parameters):
        super().__init__()
        self.image_path = image_path
        self.analysis_type = analysis_type
        self.parameters = parameters
        
    def run(self):
        try:
            import cv2
            image = cv2.imread(self.image_path)
            
            # Instantiate calculators
            astm_calculator = ASTM_E112()

            if self.analysis_type == "grain":
                analyzer = GrainAnalyzer(astm_calculator)
                self.progress.emit(50)
                results = analyzer.analyze_grains(
                    image,
                    scale_pixels_per_mm=self.parameters['scale'],
                    threshold_value=self.parameters['threshold'],
                    min_grain_size=self.parameters['min_size']
                )
                self.progress.emit(100)
                self.finished.emit({"grain_analysis": results})
                
            elif self.analysis_type == "phase":
                # Assuming PhaseAnalyzer might be refactored similarly in the future
                analyzer = PhaseAnalyzer()
                self.progress.emit(50)
                results = analyzer.analyze_phases(image) # This would also need params
                self.progress.emit(100)
                self.finished.emit({"phase_analysis": results})
                
            elif self.analysis_type == "combined":
                grain_analyzer = GrainAnalyzer(astm_calculator)
                phase_analyzer = PhaseAnalyzer()
                
                self.progress.emit(25)
                grain_results = grain_analyzer.analyze_grains(
                    image,
                    scale_pixels_per_mm=self.parameters['scale'],
                    threshold_value=self.parameters['threshold'],
                    min_grain_size=self.parameters['min_size']
                )
                self.progress.emit(75)
                phase_results = phase_analyzer.analyze_phases(image)
                self.progress.emit(100)
                
                self.finished.emit({
                    "grain_analysis": grain_results,
                    "phase_analysis": phase_results
                })
                
        except Exception as e:
            self.finished.emit({"error": str(e)})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.analysis_thread = None
        
        self.file_handler = FileHandler()
        self.export_utils = ExportUtils()
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("MetalloBox - Analyse Métallographique")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create panels
        self.image_viewer = ImageViewer()
        self.tools_panel = ToolsPanel()
        self.results_panel = ResultsPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.image_viewer)
        splitter.addWidget(self.tools_panel)
        splitter.addWidget(self.results_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 3)  # Image viewer
        splitter.setStretchFactor(1, 1)  # Tools panel
        splitter.setStretchFactor(2, 2)  # Results panel
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Prêt")
        self.status_bar.addWidget(self.status_label)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Fichier")
        
        open_action = QAction("Ouvrir image", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("Ouvrir dossier", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Exporter résultats", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("Analyse")
        
        grain_action = QAction("Analyse des grains", self)
        grain_action.triggered.connect(lambda: self.start_analysis("grain"))
        analysis_menu.addAction(grain_action)
        
        phase_action = QAction("Analyse des phases", self)
        phase_action.triggered.connect(lambda: self.start_analysis("phase"))
        analysis_menu.addAction(phase_action)
        
        combined_action = QAction("Analyse complète", self)
        combined_action.triggered.connect(lambda: self.start_analysis("combined"))
        analysis_menu.addAction(combined_action)
        
        # Help menu
        help_menu = menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        self.tools_panel.analysis_requested.connect(self.start_analysis)
        self.tools_panel.manual_correction_requested.connect(self.manual_correction)
        
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
        )
        
        if file_path:
            self.load_image(file_path)
            
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Ouvrir dossier")
        
        if folder_path:
            image_files = self.file_handler.get_image_files(folder_path)
            if image_files:
                self.load_image(image_files[0])
                self.status_label.setText(f"{len(image_files)} images trouvées")
            else:
                QMessageBox.warning(self, "Attention", "Aucune image trouvée dans le dossier")
                
    def load_image(self, image_path):
        if self.file_handler.validate_image_file(image_path):
            self.current_image_path = image_path
            self.image_viewer.load_image(image_path)
            self.tools_panel.enable_analysis_buttons(True)
            self.status_label.setText(f"Image chargée: {os.path.basename(image_path)}")
        else:
            QMessageBox.critical(self, "Erreur", "Format d'image non supporté")
            
    def start_analysis(self, analysis_type):
        if not self.current_image_path:
            QMessageBox.warning(self, "Attention", "Veuillez charger une image")
            return
            
        # Get analysis parameters
        parameters = self.tools_panel.get_parameters()
        
        # Start analysis thread
        self.analysis_thread = AnalysisThread(
            self.current_image_path, analysis_type, parameters
        )
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.progress.connect(self.update_progress)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Analyse en cours...")
        
        self.analysis_thread.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def on_analysis_finished(self, results):
        self.progress_bar.setVisible(False)
        
        if "error" in results:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'analyse: {results['error']}")
            self.status_label.setText("Erreur d'analyse")
            return
            
        self.current_results = results
        self.results_panel.update_results(results)
        
        # Update image viewer with results
        if "grain_analysis" in results:
            self.image_viewer.overlay_grains(results["grain_analysis"])
        if "phase_analysis" in results:
            self.image_viewer.overlay_phases(results["phase_analysis"])
            
        self.status_label.setText("Analyse terminée")
        
    def manual_correction(self):
        if not self.current_results:
            QMessageBox.warning(self, "Attention", "Aucun résultat à corriger")
            return
            
        # Enable manual correction mode
        self.image_viewer.enable_manual_correction(True)
        self.status_label.setText("Mode correction manuelle activé")
        
    def export_results(self):
        if not self.current_results:
            QMessageBox.warning(self, "Attention", "Aucun résultat à exporter")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter résultats", "", "Excel files (*.xlsx)"
        )
        
        if file_path:
            try:
                self.export_utils.export_to_excel(self.current_results, file_path)
                QMessageBox.information(self, "Succès", "Résultats exportés avec succès")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")
                
    def show_about(self):
        QMessageBox.about(self, "À propos", 
                         "MetalloBox Clone v1.0\n"
                         "Logiciel d'analyse métallographique\n"
                         "Implémentation des normes ASTM E112")

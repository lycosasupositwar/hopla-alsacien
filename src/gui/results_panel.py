import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QTableWidget, QTableWidgetItem, QLabel, QTextEdit)
from PyQt5.QtCore import Qt

class ResultsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_results = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Grain analysis tab
        self.grain_tab = QWidget()
        self.setup_grain_tab()
        self.tab_widget.addTab(self.grain_tab, "Grains")
        
        # Phase analysis tab
        self.phase_tab = QWidget()
        self.setup_phase_tab()
        self.tab_widget.addTab(self.phase_tab, "Phases")
        
        # Statistics tab
        self.stats_tab = QWidget()
        self.setup_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "Statistiques")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def setup_grain_tab(self):
        layout = QVBoxLayout()
        
        # ASTM info
        self.astm_label = QLabel("Indice ASTM: N/A")
        self.diameter_label = QLabel("Diamètre moyen: N/A")
        self.count_label = QLabel("Nombre de grains: N/A")
        
        layout.addWidget(self.astm_label)
        layout.addWidget(self.diameter_label)
        layout.addWidget(self.count_label)
        
        # Grain table
        self.grain_table = QTableWidget()
        self.grain_table.setColumnCount(5)
        self.grain_table.setHorizontalHeaderLabels([
            "ID", "Aire", "Diamètre", "Périmètre", "Facteur forme"
        ])
        layout.addWidget(self.grain_table)
        
        self.grain_tab.setLayout(layout)
        
    def setup_phase_tab(self):
        layout = QVBoxLayout()
        
        # Phase table
        self.phase_table = QTableWidget()
        self.phase_table.setColumnCount(3)
        self.phase_table.setHorizontalHeaderLabels([
            "Phase", "Aire", "Pourcentage"
        ])
        layout.addWidget(self.phase_table)
        
        self.phase_tab.setLayout(layout)
        
    def setup_stats_tab(self):
        layout = QVBoxLayout()
        
        # Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.stats_tab.setLayout(layout)
        
    def update_results(self, results):
        self.current_results = results
        
        if "grain_analysis" in results:
            self.update_grain_results(results["grain_analysis"])
            
        if "phase_analysis" in results:
            self.update_phase_results(results["phase_analysis"])
            
        self.update_statistics()
        
    def update_grain_results(self, grain_data):
        # Update labels
        self.astm_label.setText(f"Indice ASTM: {grain_data.get('astm_number', 'N/A')}")
        self.diameter_label.setText(f"Diamètre moyen: {grain_data.get('mean_diameter', 0):.2f} μm")
        self.count_label.setText(f"Nombre de grains: {len(grain_data.get('grains', []))}")
        
        # Update table
        grains = grain_data.get('grains', [])
        self.grain_table.setRowCount(len(grains))
        
        for i, grain in enumerate(grains):
            self.grain_table.setItem(i, 0, QTableWidgetItem(str(grain.get('id', i))))
            self.grain_table.setItem(i, 1, QTableWidgetItem(f"{grain.get('area', 0):.2f}"))
            self.grain_table.setItem(i, 2, QTableWidgetItem(f"{grain.get('equivalent_diameter', 0):.2f}"))
            self.grain_table.setItem(i, 3, QTableWidgetItem(f"{grain.get('perimeter', 0):.2f}"))
            self.grain_table.setItem(i, 4, QTableWidgetItem(f"{grain.get('shape_factor', 0):.3f}"))
            
    def update_phase_results(self, phase_data):
        phases = phase_data.get('phases', [])
        self.phase_table.setRowCount(len(phases))
        
        for i, phase in enumerate(phases):
            self.phase_table.setItem(i, 0, QTableWidgetItem(phase.get('name', f'Phase {i+1}')))
            self.phase_table.setItem(i, 1, QTableWidgetItem(f"{phase.get('area', 0):.2f}"))
            self.phase_table.setItem(i, 2, QTableWidgetItem(f"{phase.get('percentage', 0):.1f}%"))
            
    def update_statistics(self):
        if not self.current_results:
            return
            
        self.figure.clear()
        
        if "grain_analysis" in self.current_results:
            grain_data = self.current_results["grain_analysis"]
            grains = grain_data.get('grains', [])
            
            if grains:
                # Histogram of grain sizes
                ax = self.figure.add_subplot(111)
                sizes = [grain.get('equivalent_diameter', 0) for grain in grains]
                ax.hist(sizes, bins=20, alpha=0.7, edgecolor='black')
                ax.set_xlabel('Diamètre équivalent (μm)')
                ax.set_ylabel('Fréquence')
                ax.set_title('Distribution des tailles de grains')
                ax.grid(True, alpha=0.3)
                
        self.figure.tight_layout()
        self.canvas.draw()

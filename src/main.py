import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MetalloBox")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MetalloBox Clone")
    
    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Load stylesheet
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

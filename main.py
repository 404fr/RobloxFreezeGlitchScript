"""
RoFreeze Application Entry Point.

This script initializes the PyQt application and the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import Gui

def main():
    """
    Main entry point of the application.
    """
    app = QApplication(sys.argv)
    window = Gui()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

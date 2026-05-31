#!/usr/bin/env python3
# ==============================================================================
# E.V.E. DEVELOPER SUITE - Main Entry Point (PySide6)
# Professional Adobe Premiere-style interface
# ==============================================================================

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Import config and theme
import config
from ai_librarian.pyside6_modules.main_window import EVEMainWindow
from ai_librarian.pyside6_modules.theme_manager import ThemeManager


def main():
    """Launch the EVE Developer Suite."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("E.V.E. Developer Suite")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("EVE Project")
    
    # Apply Premiere-style dark theme
    ThemeManager.apply_dark_theme(app)
    
    # Create and show main window
    window = EVEMainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# ==============================================================================
# THEME MANAGER - Adobe Premiere-style Dark Theme
# ==============================================================================

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class ThemeManager:
    """Manages the Premiere-style dark theme for the EVE Suite."""
    
    # Premiere-inspired color palette
    COLORS = {
        'bg_primary': '#1e1e1e',      # Main background (dark gray)
        'bg_secondary': '#2c2c2c',    # Secondary background (slightly lighter)
        'bg_tertiary': '#3c3c3c',     # Tertiary background (panel headers)
        'bg_hover': '#4a4a4a',        # Hover state
        'accent_blue': '#3498db',      # Primary accent (buttons, links)
        'accent_green': '#1abc9c',    # Success/confirm actions
        'accent_red': '#e74c3c',      # Danger/stop actions
        'accent_orange': '#f39c12',  # Warning/attention
        'accent_purple': '#9b59b6',  # Special actions
        'text_primary': '#ffffff',     # Primary text
        'text_secondary': '#cccccc',   # Secondary text
        'text_disabled': '#666666',   # Disabled text
        'border': '#444444',           # Border color
        'selection': '#3498db',       # Selection highlight
    }
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply the Premiere-style dark theme to the application."""
        
        # Set fusion style for better cross-platform look
        app.setStyle('Fusion')
        
        # Create dark palette
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(ThemeManager.COLORS['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(ThemeManager.COLORS['text_primary']))
        
        # Base colors (for text entry widgets)
        palette.setColor(QPalette.ColorRole.Base, QColor(ThemeManager.COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(ThemeManager.COLORS['bg_tertiary']))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(ThemeManager.COLORS['text_primary']))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(ThemeManager.COLORS['text_disabled']))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(ThemeManager.COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(ThemeManager.COLORS['text_primary']))
        
        # Highlight colors (selection)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(ThemeManager.COLORS['selection']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(ThemeManager.COLORS['text_primary']))
        
        # Tooltip colors
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(ThemeManager.COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(ThemeManager.COLORS['text_primary']))
        
        # Bright text (for accents)
        palette.setColor(QPalette.ColorRole.BrightText, QColor(ThemeManager.COLORS['accent_red']))
        
        # Link color
        palette.setColor(QPalette.ColorRole.Link, QColor(ThemeManager.COLORS['accent_blue']))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(ThemeManager.COLORS['accent_purple']))
        
        app.setPalette(palette)
    
    @staticmethod
    def get_stylesheet():
        """Return the QSS (Qt Style Sheet) for custom widget styling."""
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {ThemeManager.COLORS['bg_primary']};
            border: none;
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            padding: 4px;
            border-bottom: 1px solid {ThemeManager.COLORS['border']};
        }}
        QMenuBar::item {{
            padding: 6px 12px;
            background: transparent;
        }}
        QMenuBar::item:selected {{
            background: {ThemeManager.COLORS['bg_hover']};
        }}
        QMenu {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 24px 6px 20px;
        }}
        QMenu::item:selected {{
            background: {ThemeManager.COLORS['accent_blue']};
        }}
        
        /* Tool Bar */
        QToolBar {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            border: none;
            padding: 4px;
            spacing: 4px;
        }}
        QToolBar::separator {{
            background: {ThemeManager.COLORS['border']};
            width: 1px;
            margin: 4px 6px;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {ThemeManager.COLORS['bg_tertiary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ThemeManager.COLORS['bg_hover']};
            border-color: {ThemeManager.COLORS['accent_blue']};
        }}
        QPushButton:pressed {{
            background-color: {ThemeManager.COLORS['accent_blue']};
        }}
        QPushButton:disabled {{
            color: {ThemeManager.COLORS['text_disabled']};
            background-color: {ThemeManager.COLORS['bg_primary']};
        }}
        
        /* Accent Buttons */
        QPushButton[accent="blue"] {{
            background-color: {ThemeManager.COLORS['accent_blue']};
            border: none;
        }}
        QPushButton[accent="blue"]:hover {{
            background-color: #2980b9;
        }}
        QPushButton[accent="green"] {{
            background-color: {ThemeManager.COLORS['accent_green']};
            border: none;
        }}
        QPushButton[accent="red"] {{
            background-color: {ThemeManager.COLORS['accent_red']};
            border: none;
        }}
        QPushButton[accent="orange"] {{
            background-color: {ThemeManager.COLORS['accent_orange']};
            border: none;
        }}
        
        /* Tree View */
        QTreeWidget {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            border-radius: 4px;
            padding: 4px;
        }}
        QTreeWidget::item {{
            padding: 4px;
        }}
        QTreeWidget::item:selected {{
            background: {ThemeManager.COLORS['selection']};
            color: {ThemeManager.COLORS['text_primary']};
        }}
        QTreeWidget::item:hover {{
            background: {ThemeManager.COLORS['bg_hover']};
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {ThemeManager.COLORS['bg_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            border-top: none;
        }}
        QTabBar::tab {{
            background: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_secondary']};
            padding: 8px 16px;
            border: 1px solid {ThemeManager.COLORS['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background: {ThemeManager.COLORS['bg_primary']};
            color: {ThemeManager.COLORS['text_primary']};
            border-bottom: 2px solid {ThemeManager.COLORS['accent_blue']};
        }}
        QTabBar::tab:hover {{
            background: {ThemeManager.COLORS['bg_hover']};
        }}
        
        /* Text Edit */
        QTextEdit, QPlainTextEdit {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            font-family: 'Segoe UI', 'Monaco', 'Courier New';
        }}
        
        /* Combo Box */
        QComboBox {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            padding: 4px 8px;
            border-radius: 4px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_secondary']};
            border-top: 1px solid {ThemeManager.COLORS['border']};
            padding: 4px;
        }}
        
        /* Scroll Bar */
        QScrollBar:vertical {{
            background: {ThemeManager.COLORS['bg_primary']};
            width: 12px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {ThemeManager.COLORS['bg_hover']};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ThemeManager.COLORS['accent_blue']};
        }}
        QScrollBar:horizontal {{
            background: {ThemeManager.COLORS['bg_primary']};
            height: 12px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {ThemeManager.COLORS['bg_hover']};
            border-radius: 6px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {ThemeManager.COLORS['accent_blue']};
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {ThemeManager.COLORS['bg_secondary']};
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {ThemeManager.COLORS['accent_blue']};
            border-radius: 3px;
        }}
        
        /* Group Box / Frame */
        QGroupBox {{
            color: {ThemeManager.COLORS['text_primary']};
            border: 1px solid {ThemeManager.COLORS['border']};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 8px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        """

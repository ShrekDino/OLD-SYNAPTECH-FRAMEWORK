# ==============================================================================
# DASHBOARD PANEL - Project overview and quick actions
# ==============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QFrame, QGridLayout, QSpacerItem, 
                                QSizePolicy)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont

from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class DashboardPanel(QWidget):
    """Dashboard panel with project stats and quick actions."""
    
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Build the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🧠 E.V.E. Developer Suite")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Experiential Visionary Entity - Knowledge Management System")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        # Stats cards
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        stats_layout = QGridLayout(stats_frame)
        
        stats = [
            ("📚", "Vault Notes", "142", "Total notes in vault"),
            ("🧠", "Model", "gemma4:26b", "Librarian model active"),
            ("📥", "Inbox", "3", "Pending files to process"),
            ("✅", "Status", "Ready", "System operational"),
        ]
        
        for i, (icon, label, value, desc) in enumerate(stats):
            card = self.create_stat_card(icon, label, value, desc)
            stats_layout.addWidget(card, 0, i)
        
        layout.addWidget(stats_frame)
        
        # Quick actions
        actions_label = QLabel("🚀 Quick Actions")
        actions_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        actions_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']}; margin-top: 20px;")
        layout.addWidget(actions_label)
        
        actions_frame = QFrame()
        actions_layout = QGridLayout(actions_frame)
        
        actions = [
            ("📁 Launch Architect", "Open vault manager", self.on_launch_architect),
            ("🌐 Intake URLs", "Process web research", self.on_intake_urls),
            ("📥 Process Inbox", "Handle pending files", self.on_process_inbox),
            ("🔬 Expand Knowledge", "Auto-research notes", self.on_expand_knowledge),
            ("🏗️ Organize Vault", "Auto-categorize", self.on_organize_vault),
            ("🧪 Train E.V.E.", "Fine-tune model", self.on_train_eve),
        ]
        
        for i, (text, desc, handler) in enumerate(actions):
            btn = self.create_action_button(text, desc, handler)
            actions_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(actions_frame)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Recent activity
        activity_label = QLabel("📋 Recent Activity")
        activity_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        activity_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(activity_label)
        
        activity_text = QLabel("No recent activity yet.\nActivity will appear here as you use the suite.")
        activity_text.setStyleSheet(f"color: {ThemeManager.COLORS['text_disabled']}; font-style: italic;")
        layout.addWidget(activity_text)
        
    def create_stat_card(self, icon, label, value, desc):
        """Create a statistics card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['bg_tertiary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 6px;
                padding: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {ThemeManager.COLORS['accent_blue']};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {ThemeManager.COLORS['accent_blue']};")
        layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(label_label)
        
        desc_label = QLabel(desc)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_disabled']}; font-size: 10px;")
        layout.addWidget(desc_label)
        
        return card
    
    def create_action_button(self, text, desc, handler):
        """Create an action button with description."""
        btn = QPushButton(text)
        btn.setToolTip(desc)
        btn.setFixedHeight(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        btn.clicked.connect(handler)
        return btn
    
    # Event handlers
    def on_launch_architect(self):
        # This will switch to vault tab
        pass
        
    def on_intake_urls(self):
        pass
        
    def on_process_inbox(self):
        pass
        
    def on_expand_knowledge(self):
        pass
        
    def on_organize_vault(self):
        pass
        
    def on_train_eve(self):
        pass

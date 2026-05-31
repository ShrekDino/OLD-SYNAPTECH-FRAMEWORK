# ==============================================================================
# MAIN WINDOW - EVE Developer Suite (PySide6)
# Adobe Premiere-style layout with dockable panels
# ==============================================================================

import sys
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                                QHBoxLayout, QDockWidget, QTabWidget, QToolBar,
                                QPushButton, QLabel, QStatusBar, QMessageBox, QSizePolicy,
                                QTextEdit)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QFont

# Import theme manager
sys.path.append(str(Path(__file__).parent.parent.parent))
from ai_librarian.pyside6_modules.theme_manager import ThemeManager

# Import panels
from ai_librarian.pyside6_modules.dashboard_panel import DashboardPanel
from ai_librarian.pyside6_modules.vault_panel import VaultPanel
from ai_librarian.pyside6_modules.intake_panel import IntakePanel
from ai_librarian.pyside6_modules.research_panel import ResearchPanel
from ai_librarian.pyside6_modules.organize_panel import OrganizePanel
from ai_librarian.pyside6_modules.training_panel import TrainingPanel
from ai_librarian.pyside6_modules.wikilink_viewer import WikiLinkViewer
from ai_librarian.pyside6_modules.consciousness_panel import ConsciousnessPanel


class EVEMainWindow(QMainWindow):
    """Main window for EVE Developer Suite - Premiere-style layout."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E.V.E. Developer Suite | Professional Edition")
        self.setGeometry(100, 100, 1800, 1000)
        
        # Apply theme
        app = QApplication.instance()
        if app:
            ThemeManager.apply_dark_theme(app)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Build the main window UI with dockable panels."""
        
        # ---- Menu Bar ----
        self.create_menu_bar()
        
        # ---- Tool Bar ----
        self.create_tool_bar()
        
        # ---- Central Widget (Tabbed) ----
        self.create_central_tabs()
        
        # ---- Left Dock: Vault Tree ----
        self.create_left_dock()
        
        # ---- Right Dock: AI Panel ----
        self.create_right_dock()
        
        # ---- Bottom Dock: Log Console ----
        self.create_bottom_dock()
        
        # ---- Status Bar ----
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create the menu bar with File, Tools, View, Help."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Note", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_note)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        rescan_action = QAction("&Rescan Vault", self)
        rescan_action.triggered.connect(self.on_rescan_vault)
        tools_menu.addAction(rescan_action)
        
        backup_action = QAction("&Backup Now", self)
        backup_action.triggered.connect(self.on_backup_now)
        tools_menu.addAction(backup_action)

        tools_menu.addSeparator()

        consciousness_action = QAction("&Consciousness Dashboard", self)
        consciousness_action.triggered.connect(self.on_consciousness_dashboard)
        tools_menu.addAction(consciousness_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_left = QAction("Toggle &Left Panel", self)
        toggle_left.setShortcut("Ctrl+1")
        toggle_left.triggered.connect(lambda: self.toggle_dock('left'))
        view_menu.addAction(toggle_left)
        
        toggle_right = QAction("Toggle &Right Panel", self)
        toggle_right.setShortcut("Ctrl+2")
        toggle_right.triggered.connect(lambda: self.toggle_dock('right'))
        view_menu.addAction(toggle_right)
        
        toggle_bottom = QAction("Toggle &Bottom Panel", self)
        toggle_bottom.setShortcut("Ctrl+3")
        toggle_bottom.triggered.connect(lambda: self.toggle_dock('bottom'))
        view_menu.addAction(toggle_bottom)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """Create the main tool bar with quick actions."""
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Quick actions
        actions = [
            ("New Note", "📄", self.on_new_note),
            ("Quick AI", "⚡", self.on_quick_ai),
            ("Deep Research", "🔍", self.on_deep_research),
            (None, None, None),  # Separator
            ("Intake URL", "🌐", self.on_intake_url),
            ("Process Files", "📥", self.on_process_files),
            (None, None, None),  # Separator
            ("Train E.V.E.", "🧪", self.on_train_eve),
        ]
        
        for text, icon, handler in actions:
            if text is None:
                toolbar.addSeparator()
            else:
                btn = QPushButton(icon)
                btn.setToolTip(text)
                btn.clicked.connect(handler)
                btn.setFixedSize(40, 40)
                toolbar.addWidget(btn)
        
    def create_central_tabs(self):
        """Create the central tabbed widget with actual panels."""
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Dashboard Panel
        self.dashboard_panel = DashboardPanel()
        self.dashboard_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.dashboard_panel, "📊 Dashboard")
        
        # Vault Panel
        self.vault_panel = VaultPanel()
        self.vault_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.vault_panel, "📁 Vault Manager")
        
        # Intake Panel
        self.intake_panel = IntakePanel()
        self.intake_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.intake_panel, "🌐 Intake Center")
        
        # Research Panel
        self.research_panel = ResearchPanel()
        self.research_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.research_panel, "🔬 Research")
        
        # Organize Panel
        self.organize_panel = OrganizePanel()
        self.organize_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.organize_panel, "🏗️ Organize")
        
        # Training Panel
        self.training_panel = TrainingPanel()
        self.training_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.training_panel, "🧪 Training")

        # Consciousness Dashboard Panel
        self.consciousness_panel = ConsciousnessPanel()
        self.consciousness_panel.log_message.connect(self.on_log_message)
        self.central_tabs.addTab(self.consciousness_panel, "🧠 Consciousness")

        self.setCentralWidget(self.central_tabs)
        
    def create_left_dock(self):
        """Create left dock with vault tree from vault panel."""
        self.left_dock = QDockWidget("📂 Vault Navigator", self)
        self.left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        # Use the tree from vault panel
        if hasattr(self, 'vault_panel'):
            self.left_dock.setWidget(self.vault_panel.tree)
        else:
            self.left_dock.setWidget(QWidget())  # Placeholder
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.left_dock)
        
    def create_right_dock(self):
        """Create right dock with WikiLink Viewer."""
        self.right_dock = QDockWidget("🔗 WikiLink Intersections", self)
        self.right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create WikiLink viewer
        self.wikilink_viewer = WikiLinkViewer()
        self.wikilink_viewer.link_selected.connect(self.on_wikilink_selected)
        self.wikilink_viewer.note_selected.connect(self.on_note_opened)
        self.right_dock.setWidget(self.wikilink_viewer)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)
        
    def on_wikilink_selected(self, link):
        """Handle WikiLink selection."""
        self.log_message.emit(f"WikiLink selected: {link}")
        # Optionally open the related notes in vault panel
        if hasattr(self, 'vault_panel'):
            # Find notes containing this link
            pass

    def on_note_opened(self, path):
        """Handle note selection from WikiLink viewer - open in vault panel."""
        self.log_message.emit(f"Opening note: {path}")
        # Switch to vault tab
        self.central_tabs.setCurrentIndex(1)  # Vault Manager tab
        # Find and select the note in vault tree
        if hasattr(self, 'vault_panel'):
            for i, note_path in enumerate(self.vault_panel.all_notes):
                if note_path == path:
                    self.vault_panel.current_index = i
                    self.vault_panel.load_note()
                    # Select in tree
                    item = self.vault_panel.tree.topLevelItem(i)
                    if item:
                        self.vault_panel.tree.setCurrentItem(item)
                    break
        
    def create_bottom_dock(self):
        """Create bottom dock with log console."""
        self.bottom_dock = QDockWidget("📋 Log Console", self)
        self.bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        
        # Create log text edit
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(200)
        self.log_console.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        self.bottom_dock.setWidget(self.log_console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)
        
    def on_log_message(self, message):
        """Handle log messages from panels."""
        self.log_console.append(message)
        self.log_console.verticalScrollBar().setValue(
            self.log_console.verticalScrollBar().maximum()
        )
        
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.model_label = QLabel("Model: gemma4:26b")
        self.note_count_label = QLabel("Notes: --")
        self.gpu_label = QLabel("GPU: OK")
        
        self.status_bar.addPermanentWidget(self.model_label)
        self.status_bar.addPermanentWidget(self.note_count_label)
        self.status_bar.addPermanentWidget(self.gpu_label)
        
        self.status_bar.showMessage("Ready")
        
    # ---- Event Handlers (Placeholders) ----
    def toggle_dock(self, dock_name):
        """Toggle visibility of a dock widget."""
        dock_map = {
            'left': self.left_dock,
            'right': self.right_dock,
            'bottom': self.bottom_dock,
        }
        dock = dock_map.get(dock_name)
        if dock:
            dock.setVisible(not dock.isVisible())
            
    def on_new_note(self):
        QMessageBox.information(self, "New Note", "New note creation will be implemented soon!")
        
    def on_quick_ai(self):
        QMessageBox.information(self, "Quick AI", "Quick AI processing will be implemented soon!")
        
    def on_deep_research(self):
        QMessageBox.information(self, "Deep Research", "Deep research will be implemented soon!")
        
    def on_intake_url(self):
        self.central_tabs.setCurrentIndex(2)  # Switch to Intake tab
        
    def on_process_files(self):
        QMessageBox.information(self, "Process Files", "File processing will be implemented soon!")
        
    def on_train_eve(self):
        self.central_tabs.setCurrentIndex(5)  # Switch to Training tab

    def on_consciousness_dashboard(self):
        self.central_tabs.setCurrentIndex(6)  # Switch to Consciousness tab
        
    def on_rescan_vault(self):
        QMessageBox.information(self, "Rescan Vault", "Vault rescan will be implemented soon!")
        
    def on_backup_now(self):
        QMessageBox.information(self, "Backup", "Backup functionality will be implemented soon!")
        
    def on_about(self):
        QMessageBox.about(self, "About E.V.E. Suite",
            "E.V.E. Developer Suite v2.0\n\n"
            "Experiential Visionary Entity\n"
            "Professional Knowledge Management System\n\n"
            "Built with PySide6 (Qt6)")

# ==============================================================================
# WIKI LINK VIEWER - Visualize concept intersections in Obsidian
# Shows how concepts link together for knowledge graph visualization
# ==============================================================================

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                                QTreeWidgetItem, QLabel, QPushButton, 
                                QGroupBox, QMessageBox, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *
from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class WikiLinkViewer(QWidget):
    """Widget to visualize WikiLink intersections in the vault."""
    
    link_selected = Signal(str)
    note_selected = Signal(str)  # Emits file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.links = defaultdict(list)  # {target: [source1, source2, ...]}
        self.setup_ui()
        self.scan_vault()
        
    def setup_ui(self):
        """Build the WikiLink viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🔗 WikiLink Intersection Viewer")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Splitter for two panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: All WikiLinks found
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_label = QLabel("📚 All WikiLinks")
        left_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']}; font-weight: bold;")
        left_layout.addWidget(left_label)
        
        self.link_tree = QTreeWidget()
        self.link_tree.setHeaderLabels(["WikiLink Target", "Used in # Notes"])
        self.link_tree.setColumnWidth(0, 250)
        self.link_tree.itemClicked.connect(self.on_link_select)
        left_layout.addWidget(self.link_tree)
        
        splitter.addWidget(left_widget)
        
        # Right: Notes using this WikiLink
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.detail_label = QLabel("Select a WikiLink to see intersections")
        self.detail_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']}; font-weight: bold;")
        right_layout.addWidget(self.detail_label)
        
        self.notes_list = QTreeWidget()
        self.notes_list.setHeaderLabels(["Note Title", "Path"])
        self.notes_list.setColumnWidth(0, 200)
        self.notes_list.itemClicked.connect(self.on_note_select)
        right_layout.addWidget(self.notes_list)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Stats
        self.stats_label = QLabel("Scanning vault...")
        self.stats_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']}; font-style: italic;")
        layout.addWidget(self.stats_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Rescan Vault")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        refresh_btn.clicked.connect(self.scan_vault)
        layout.addWidget(refresh_btn)
        
    def scan_vault(self):
        """Scan all markdown files for WikiLinks."""
        self.links.clear()
        self.link_tree.clear()
        self.notes_list.clear()
        
        note_count = 0
        link_count = 0
        
        for root, dirs, files in os.walk(VAULT_ROOT):
            if ".obsidian" in root or "99_System" in root:
                continue
            for file in files:
                if file.endswith(".md"):
                    note_count += 1
                    file_path = os.path.join(root, file)
                    topic = os.path.splitext(file)[0]
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find all [[WikiLinks]]
                        wikilinks = re.findall(r'\[\[([^\]]+)\]', content)
                        
                        for link in wikilinks:
                            self.links[link].append((topic, file_path))
                            link_count += 1
                    except:
                        pass
        
        # Populate tree
        for target, sources in sorted(self.links.items()):
            item = QTreeWidgetItem([target, str(len(sources))])
            
            # Color-code by frequency
            if len(sources) > 5:
                item.setBackground(0, QColor(ThemeManager.COLORS['accent_green']))
            elif len(sources) > 2:
                item.setBackground(0, QColor(ThemeManager.COLORS['accent_orange']))
            
            self.link_tree.addTopLevelItem(item)
        
        self.stats_label.setText(f"Found {link_count} WikiLinks across {note_count} notes")
        self.detail_label.setText("Select a WikiLink to see intersections")
        
    def on_link_select(self, item, column):
        """Show notes that use this WikiLink."""
        target = item.text(0)
        self.notes_list.clear()
        self.detail_label.setText(f"📍 Notes linking to [[{target}]]")
        
        if target in self.links:
            for topic, path in self.links[target]:
                item = QTreeWidgetItem([topic, path])
                self.notes_list.addTopLevelItem(item)
        
        self.link_selected.emit(target)

    def on_note_select(self, item, column):
        """Handle note selection - emit the file path."""
        path = item.text(1)  # Path is in column 1
        if path:
            self.note_selected.emit(path)

# =============================================================================
# VAULT PANEL - Vault Manager (Refactored from Architect.py)
# Tree view, editor, AI actions (Quick/Deep/Audit/Refine)
# =============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                                QTreeWidgetItem, QTextEdit, QTabWidget,
                                QPushButton, QLabel, QGroupBox, QInputDialog,
                                QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *
from ai_librarian.pyside6_modules.theme_manager import ThemeManager
from ai_librarian.utils.ai_utils import run_ollama, clean_llm_response
from ai_librarian.utils.web_utils import scrape_url


class VaultPanel(QWidget):
    """Vault Manager panel with tree view and editor."""
    
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.all_notes = []
        self.topic_list = []
        self.references = []
        self.setup_ui()
        self.load_vault(repair=False)
        
    def setup_ui(self):
        """Build the vault panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📁 Vault Manager")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Tree view for notes
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Filename", "Type"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 60)
        self.tree.itemClicked.connect(self.on_tree_select)
        layout.addWidget(self.tree)
        
        # Tabbed editor (Think + Editor)
        self.editor_tabs = QTabWidget()
        
        # Main editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Select a note to view/edit...")
        self.editor_tabs.addTab(self.text_edit, "📝 Editor")
        
        # Think area
        self.think_edit = QTextEdit()
        self.think_edit.setPlaceholderText("AI thinking process will appear here...")
        self.think_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }}
        """)
        self.editor_tabs.addTab(self.think_edit, "🧠 Think")
        
        layout.addWidget(self.editor_tabs)
        
        # AI Action buttons
        actions_group = QGroupBox("🚀 AI Actions")
        actions_group.setStyleSheet(self.get_group_style())
        actions_layout = QHBoxLayout(actions_group)
        
        btn_quick = QPushButton("⚡ Quick")
        btn_quick.setStyleSheet(self.get_button_style("green"))
        btn_quick.clicked.connect(self.on_quick)
        actions_layout.addWidget(btn_quick)
        
        btn_deep = QPushButton("🚀 Deep")
        btn_deep.setStyleSheet(self.get_button_style("blue"))
        btn_deep.clicked.connect(self.on_deep)
        actions_layout.addWidget(btn_deep)
        
        btn_audit = QPushButton("🛡️ Audit")
        btn_audit.setStyleSheet(self.get_button_style("red"))
        btn_audit.clicked.connect(self.on_audit)
        actions_layout.addWidget(btn_audit)
        
        btn_refine = QPushButton("✨ Refine")
        btn_refine.setStyleSheet(self.get_button_style("purple"))
        btn_refine.clicked.connect(self.on_refine)
        actions_layout.addWidget(btn_refine)
        
        layout.addWidget(actions_group)
        
        # Source injector
        source_group = QGroupBox("🛰️ Source Injector")
        source_group.setStyleSheet(self.get_group_style())
        source_layout = QHBoxLayout(source_group)
        
        self.url_entry = QTextEdit()
        self.url_entry.setPlaceholderText("Enter URLs (one per line)...")
        self.url_entry.setMaximumHeight(60)
        source_layout.addWidget(self.url_entry)
        
        add_url_btn = QPushButton("➕ Add")
        add_url_btn.setStyleSheet(self.get_button_style("blue"))
        add_url_btn.clicked.connect(self.add_url)
        source_layout.addWidget(add_url_btn)
        
        create_btn = QPushButton("🌐 Create Note")
        create_btn.setStyleSheet(self.get_button_style("orange"))
        create_btn.clicked.connect(self.create_from_refs)
        source_layout.addWidget(create_btn)
        
        layout.addWidget(source_group)
        
    def load_vault(self, repair=False):
        """Load all notes from the vault."""
        self.all_notes = []
        for r, _, fs in os.walk(VAULT_ROOT):
            if ".obsidian" in r:
                continue
            for f in fs:
                if any(f.lower().endswith(e) for e in [".md", ".pdf", ".jpg", ".png"]):
                    self.all_notes.append(os.path.join(r, f))
        
        self.topic_list = [os.path.splitext(os.path.basename(f))[0] for f in self.all_notes]
        self.refresh_tree()
        
        if repair:
            self.log_message.emit("Starting global vault repair...")
            QMessageBox.information(self, "Repair", "Vault repair will be implemented soon!")
        
    def refresh_tree(self):
        """Refresh the tree view."""
        self.tree.clear()
        for path in self.all_notes:
            filename = os.path.basename(path)
            ext = os.path.splitext(path)[1][1:].upper()
            item = QTreeWidgetItem([filename, ext])
            self.tree.addTopLevelItem(item)
        
    def on_tree_select(self, item, column):
        """Handle tree item selection."""
        index = self.tree.indexOfTopLevelItem(item)
        if index >= 0:
            self.current_index = index
            self.load_note()
        
    def load_note(self):
        """Load the selected note into the editor."""
        if not self.all_notes:
            return
        
        path = self.all_notes[self.current_index]
        self.text_edit.clear()
        
        if path.endswith(".md"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read())
            except Exception as e:
                self.text_edit.setText(f"[Error reading file: {e}]")
        elif path.endswith(".pdf"):
            self.text_edit.setText("[PDF viewing not yet implemented]")
        else:
            self.text_edit.setText(f"[Asset: {os.path.basename(path)}]")
        
    def on_quick(self):
        """Quick AI summary."""
        if not self.all_notes or self.current_index >= len(self.all_notes):
            return
        self.log_message.emit("Quick AI action triggered")
        try:
            content = self.text_edit.toPlainText()
            if not content.strip():
                QMessageBox.warning(self, "Empty Note", "No content to process.")
                return
            
            self.think_edit.clear()
            self.think_edit.append("Running Quick AI...")
            
            result = run_ollama(f"Provide a concise summary of: {content[:2000]}", model=WRITER_MODEL)
            self.think_edit.append(result['full'])
            
            if result['clean']:
                self.text_edit.setText(result['clean'])
                self.save_current_note()
                self.log_message.emit("Quick AI complete")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Quick AI failed: {str(e)}")
        
    def on_deep(self):
        """Deep research on current note."""
        if not self.all_notes or self.current_index >= len(self.all_notes):
            return
        topic = os.path.basename(self.all_notes[self.current_index])
        self.log_message.emit(f"Deep research triggered for: {topic}")
        try:
            content = self.text_edit.toPlainText()
            
            self.think_edit.clear()
            self.think_edit.append(f"Researching: {topic}...")
            
            # Generate search query
            search_q = clean_llm_response(
                run_ollama(f"Factual search query for: {content[:300]}", model=SORTER_MODEL)['clean']
            )
            
            # Scrape web for reputable sources
            from ai_librarian.utils.web_utils import search_reputable_sources
            web_data = search_reputable_sources(search_q)
            
            # Deep research prompt
            prompt = f"""
Role: Lead Investigative Researcher.
Standards: DSM-5, .gov, .edu.

TOPIC: {topic}
CONTENT: {content}
WEB: {web_data}

TASK: Synthesize a comprehensive, professional report.
Output ONLY the markdown content.
"""
            result = run_ollama(prompt, model=WRITER_MODEL)
            self.think_edit.append(result['full'])
            
            if result['clean'] and len(result['clean']) > 100:
                self.text_edit.setText(result['clean'])
                self.save_current_note()
                self.log_message.emit(f"Deep research complete for: {topic}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Deep research failed: {str(e)}")
        
    def on_audit(self):
        """Audit current note for issues."""
        if not self.all_notes or self.current_index >= len(self.all_notes):
            return
        content = self.text_edit.toPlainText()
        self.log_message.emit("Audit triggered")
        try:
            prompt = f"""
Role: Expert Research Editor.
TASK: Identify flags, errors, inconsistencies, or missing sections in:
{content}

Respond with bullet points of issues found.
"""
            result = run_ollama(prompt, model=LIBRARIAN_MODEL)
            self.think_edit.clear()
            self.think_edit.append("=== AUDIT REPORT ===")
            self.think_edit.append(result['full'])
            self.log_message.emit("Audit complete")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Audit failed: {str(e)}")
        
    def on_refine(self):
        """Refine and polish current note."""
        if not self.all_notes or self.current_index >= len(self.all_notes):
            return
        topic = os.path.basename(self.all_notes[self.current_index])
        self.log_message.emit(f"Refine triggered for: {topic}")
        try:
            content = self.text_edit.toPlainText()
            
            prompt = f"""
Role: Expert Research Editor.
Standard: DSM-5/.gov/.edu accuracy.

TOPIC: {topic}
EXISTING TOPICS FOR BACKLINKING: {', '.join(self.topic_list[:100])}

TASK: Refine and polish the following note.
- Fix [[WikiLinks]] based on existing topics.
- Improve formatting (headers, lists).
- Ensure accuracy and neutrality.
- Output ONLY the markdown content.

CONTENT:
{content}
"""
            result = run_ollama(prompt, model=LIBRARIAN_MODEL)
            self.think_edit.clear()
            self.think_edit.append("=== REFINING NOTE ===")
            self.think_edit.append(result['full'])
            
            if result['clean'] and len(result['clean']) > 50:
                self.text_edit.setText(result['clean'])
                self.save_current_note()
                self.log_message.emit(f"Refine complete for: {topic}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Refine failed: {str(e)}")
        
    def add_url(self):
        """Add URLs from the text entry."""
        text = self.url_entry.toPlainText().strip()
        if text:
            urls = [u.strip() for u in text.split('\n') if u.strip()]
            self.references.extend(urls)
            self.url_entry.clear()
            self.log_message.emit(f"Added {len(urls)} URL(s)")
        
    def create_from_refs(self):
        """Create a new note from references."""
        title, ok = QInputDialog.getText(self, "New Note", "Enter note title:")
        if ok and title:
            # TODO: Implement note creation with AI
            self.log_message.emit(f"Creating note: {title}")
            QMessageBox.information(self, "Create Note", f"Note creation will be implemented soon!\nTitle: {title}")
        
    def save_current_note(self):
        """Save the current note to disk."""
        if not self.all_notes or self.current_index >= len(self.all_notes):
            return
        path = self.all_notes[self.current_index]
        if path.endswith(".md"):
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.log_message.emit(f"Saved: {os.path.basename(path)}")
            except Exception as e:
                self.log_message.emit(f"Save error: {str(e)}")
        
    def get_group_style(self):
        return f"""
            QGroupBox {{
                color: {ThemeManager.COLORS['text_primary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        
    def get_button_style(self, color="blue"):
        color_map = {
            "blue": ThemeManager.COLORS['accent_blue'],
            "green": ThemeManager.COLORS['accent_green'],
            "red": ThemeManager.COLORS['accent_red'],
            "orange": ThemeManager.COLORS['accent_orange'],
            "purple": ThemeManager.COLORS['accent_purple'],
        }
        return f"""
            QPushButton {{
                background-color: {color_map.get(color, color_map['blue'])};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['accent_blue']};
            }}
        """

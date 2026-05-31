# ==============================================================================
# ORGANIZE PANEL - Taxonomic Organization & Linking
# Integrates import_organizer, Wikilinkgen, organizerandwriter
# ==============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QGroupBox, QCheckBox, QProgressBar,
                                QMessageBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from ai_librarian.pyside6_modules.theme_manager import ThemeManager
from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class OrganizePanel(QWidget):
    """Panel for taxonomic organization and wiki-linking."""
    
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Build the organize panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🏗️ Organize & Link")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Auto-categorization, WikiLinks, and scientific linking")
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        # --- Auto-Categorize Section ---
        cat_group = QGroupBox("🏷️ Auto-Categorize")
        cat_group.setStyleSheet(self.get_group_style())
        cat_layout = QVBoxLayout(cat_group)
        
        cat_desc = QLabel("Automatically categorize files into scientific taxonomy.")
        cat_desc.setWordWrap(True)
        cat_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        cat_layout.addWidget(cat_desc)
        
        # Taxonomy root selector
        root_layout = QHBoxLayout()
        root_label = QLabel("Taxonomy Root:")
        root_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        root_layout.addWidget(root_label)
        
        self.root_combo = QComboBox()
        self.root_combo.addItems([
            "Applied Sciences",
            "Formal Sciences", 
            "Humanities",
            "Natural Sciences",
            "Social Sciences"
        ])
        self.root_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                padding: 4px 8px;
                border-radius: 4px;
            }}
        """)
        root_layout.addWidget(self.root_combo)
        root_layout.addStretch()
        cat_layout.addLayout(root_layout)
        
        cat_btn = QPushButton("🚀 Auto-Categorize Vault")
        cat_btn.setFixedHeight(45)
        cat_btn.setStyleSheet(self.get_button_style("blue", 14))
        cat_btn.clicked.connect(self.on_auto_categorize)
        cat_layout.addWidget(cat_btn)
        
        layout.addWidget(cat_group)
        
        # --- WikiLink Generation Section ---
        wiki_group = QGroupBox("🔗 WikiLink Generator")
        wiki_group.setStyleSheet(self.get_group_style())
        wiki_layout = QVBoxLayout(wiki_group)
        
        wiki_desc = QLabel("Generate taxonomic WikiLinks for graph visualization.")
        wiki_desc.setWordWrap(True)
        wiki_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        wiki_layout.addWidget(wiki_desc)
        
        wiki_btn = QPushButton("🔗 Generate WikiLinks")
        wiki_btn.setFixedHeight(45)
        wiki_btn.setStyleSheet(self.get_button_style("green", 14))
        wiki_btn.clicked.connect(self.on_generate_wikilinks)
        wiki_layout.addWidget(wiki_btn)
        
        layout.addWidget(wiki_group)
        
        # --- Scientific Links Section ---
        verify_group = QGroupBox("🔬 Verify Scientific Links")
        verify_group.setStyleSheet(self.get_group_style())
        verify_layout = QVBoxLayout(verify_group)
        
        verify_desc = QLabel("Verify academic connections between topics.")
        verify_desc.setWordWrap(True)
        verify_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        verify_layout.addWidget(verify_desc)
        
        verify_btn = QPushButton("🔍 Verify & Link")
        verify_btn.setFixedHeight(45)
        verify_btn.setStyleSheet(self.get_button_style("orange", 14))
        verify_btn.clicked.connect(self.on_verify_links)
        verify_layout.addWidget(verify_btn)
        
        layout.addWidget(verify_group)
        
        # --- Progress Bar ---
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"""
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
        """)
        layout.addWidget(self.progress)
        
        # --- Status ---
        self.status_label = QLabel("Ready to organize")
        self.status_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']}; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
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
        
    def get_button_style(self, color="blue", size=12):
        color_map = {
            "blue": ThemeManager.COLORS['accent_blue'],
            "green": ThemeManager.COLORS['accent_green'],
            "red": ThemeManager.COLORS['accent_red'],
            "orange": ThemeManager.COLORS['accent_orange'],
        }
        return f"""
            QPushButton {{
                background-color: {color_map.get(color, color_map['blue'])};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['accent_blue']};
            }}
        """
        
    def on_auto_categorize(self):
        """Auto-categorize all files."""
        from config import VAULT_ROOT, INBOX_DIR
        from ai_librarian.utils.ai_utils import get_taxonomy_path
        import os
        
        selected_root = self.root_combo.currentText()
        self.status_label.setText(f"Auto-categorizing with root: {selected_root}...")
        self.log_message.emit(f"Auto-categorization started with root: {selected_root}")
        
        try:
            # Get all markdown files from inbox
            if not os.path.exists(INBOX_DIR):
                QMessageBox.warning(self, "No Inbox", "00_Inbox directory not found.")
                return
            
            files = [f for f in os.listdir(INBOX_DIR) if f.endswith(('.md', '.txt'))]
            if not files:
                QMessageBox.information(self, "Empty", "No files to categorize in Inbox.")
                return
            
            self.progress.setMaximum(len(files))
            
            for i, filename in enumerate(files):
                file_path = os.path.join(INBOX_DIR, filename)
                self.status_label.setText(f"Categorizing: {filename}...")
                self.log_message.emit(f"Categorizing: {filename}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get taxonomy path
                tax_path = get_taxonomy_path(filename, content[:1500])
                if tax_path != "Uncategorized":
                    # Move to categorized folder
                    target_dir = os.path.join(VAULT_ROOT, tax_path)
                    os.makedirs(target_dir, exist_ok=True)
                    new_path = os.path.join(target_dir, filename)
                    shutil.move(file_path, new_path)
                    self.log_message.emit(f"Moved to: {tax_path}")
                
                self.progress.setValue(i + 1)
            
            self.status_label.setText("Auto-categorization complete!")
            QMessageBox.information(self, "Complete", f"Categorized {len(files)} files!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Categorization failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")
        
    def on_generate_wikilinks(self):
        """Generate WikiLinks for all notes."""
        from config import VAULT_ROOT
        from ai_librarian.utils.ai_utils import get_existing_topics
        import os
        
        self.status_label.setText("Generating WikiLinks...")
        self.log_message.emit("WikiLink generation started")
        
        try:
            topics = get_existing_topics()
            total = len(topics)
            self.progress.setMaximum(total)
            
            for i, topic in enumerate(topics):
                # Find the file
                found = False
                for root, dirs, files in os.walk(VAULT_ROOT):
                    if ".obsidian" in root:
                        continue
                    for file in files:
                        if file == f"{topic}.md":
                            file_path = os.path.join(root, file)
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    continue
                    
                self.status_label.setText(f"Processing: {topic}...")
                self.log_message.emit(f"Generating WikiLinks for: {topic}")
                
                # Check if already processed
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "### 🕸️ Taxonomic Mapping" in content:
                    continue
                
                # Generate WikiLinks using AI
                from ai_librarian.utils.ai_utils import run_ollama, clean_llm_response
                from config import FLASH_MODEL
                
                prompt = f"""
SYSTEM: You are a Graph Database Architect. 
TASK: Categorize '{topic}' into the scientific taxonomy.

ROOT OPTIONS: Applied Sciences, Formal Sciences, Humanities, Natural Sciences, Social Sciences
EXISTING VAULT TITLES: {', '.join(topics[:200])}

OUTPUT RULES:
- Provide a 'breadcrumb' path: [[Root]] > [[Sub-Discipline]] > [[Specific Field]].
- Only use titles from the provided list or the Root Options.
- Format as a single line. No chatter.
"""
                
                result = run_ollama(prompt, model=FLASH_MODEL)
                mapping = result['clean']
                
                # Append to file
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n---\n### 🕸️ Taxonomic Mapping\n**Path:** {mapping}\n**Context:** [[{topic}]]")
                
                self.progress.setValue(i + 1)
            
            self.status_label.setText("WikiLink generation complete!")
            QMessageBox.information(self, "Complete", f"Generated WikiLinks for {total} notes!")
            self.log_message.emit("WikiLink generation complete")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"WikiLink generation failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")
        
    def on_verify_links(self):
        """Verify scientific links between topics."""
        from config import VAULT_ROOT
        from ai_librarian.utils.web_utils import verify_scientific_link
        import os
        
        self.status_label.setText("Verifying scientific links...")
        self.log_message.emit("Scientific link verification started")
        
        try:
            # Get all topics
            topics = []
            for root, dirs, files in os.walk(VAULT_ROOT):
                if ".obsidian" in root:
                    continue
                for file in files:
                    if file.endswith(".md"):
                        topics.append(os.path.splitext(file)[0])
            
            total = len(topics)
            self.progress.setMaximum(total)
            
            verified_count = 0
            for i, topic in enumerate(topics):
                self.status_label.setText(f"Verifying links for: {topic}...")
                self.log_message.emit(f"Verifying: {topic}")
                
                # Check existing links in the file
                file_path = None
                for root, dirs, files in os.walk(VAULT_ROOT):
                    if ".obsidian" in root:
                        continue
                    for file in files:
                        if file == f"{topic}.md":
                            file_path = os.path.join(root, file)
                            break
                    if file_path:
                        break
                
                if not file_path:
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find WikiLinks
                import re
                wikilinks = re.findall(r'\[\[([^\]]+)\]', content)
                
                for link in wikilinks[:5]:  # Limit to 5 per note
                    if verify_scientific_link(topic, link):
                        verified_count += 1
                        self.log_message.emit(f"✅ Verified: {topic} <-> {link}")
                
                self.progress.setValue(i + 1)
            
            self.status_label.setText("Link verification complete!")
            QMessageBox.information(self, "Complete", f"Verified {verified_count} scientific links!")
            self.log_message.emit(f"Link verification complete: {verified_count} links")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Link verification failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")

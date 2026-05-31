# ==============================================================================
# RESEARCH PANEL - Knowledge Expansion & Research
# Integrates KnowledgeCrawl and Import_writer functionality
# ==============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QGroupBox, QCheckBox, QProgressBar,
                                QMessageBox, QTextEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from ai_librarian.pyside6_modules.theme_manager import ThemeManager
from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class ResearchPanel(QWidget):
    """Panel for knowledge expansion and research."""
    
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Build the research panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔬 Research & Expand")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Automated knowledge expansion with reputable sources")
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        # --- Knowledge Crawl Section ---
        crawl_group = QGroupBox("🔬 Knowledge Crawl")
        crawl_group.setStyleSheet(self.get_group_style())
        crawl_layout = QVBoxLayout(crawl_group)
        
        crawl_desc = QLabel("Automatically expand all notes in the vault with deep research.")
        crawl_desc.setWordWrap(True)
        crawl_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        crawl_layout.addWidget(crawl_desc)
        
        crawl_btn = QPushButton("🚀 Start Knowledge Crawl")
        crawl_btn.setFixedHeight(45)
        crawl_btn.setStyleSheet(self.get_button_style("blue", 14))
        crawl_btn.clicked.connect(self.on_start_crawl)
        crawl_layout.addWidget(crawl_btn)
        
        layout.addWidget(crawl_group)
        
        # --- Selective Research Section ---
        selective_group = QGroupBox("📝 Selective Research")
        selective_group.setStyleSheet(self.get_group_style())
        selective_layout = QVBoxLayout(selective_group)
        
        selective_desc = QLabel("Research and expand specific notes with reputable sources.")
        selective_desc.setWordWrap(True)
        selective_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        selective_layout.addWidget(selective_desc)
        
        selective_btn = QPushButton("🔍 Select Notes to Research")
        selective_btn.setFixedHeight(45)
        selective_btn.setStyleSheet(self.get_button_style("green", 14))
        selective_btn.clicked.connect(self.on_selective_research)
        selective_layout.addWidget(selective_btn)
        
        layout.addWidget(selective_group)
        
        # --- Options Section ---
        options_group = QGroupBox("⚙️ Research Options")
        options_group.setStyleSheet(self.get_group_style())
        options_layout = QVBoxLayout(options_group)
        
        self.gov_check = QCheckBox("🏛️ Prioritize .gov/.edu sources")
        self.gov_check.setChecked(True)
        self.gov_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.gov_check)
        
        self.dsm5_check = QCheckBox("📚 Use DSM-5/ICD-11 standards (clinical)")
        self.dsm5_check.setChecked(True)
        self.dsm5_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.dsm5_check)
        
        self.peer_check = QCheckBox("🔬 Peer-reviewed focus (Nature, Science, Lancet)")
        self.peer_check.setChecked(True)
        self.peer_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.peer_check)
        
        layout.addWidget(options_group)
        
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
        self.status_label = QLabel("Ready for research")
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
        
    def on_start_crawl(self):
        """Start full vault knowledge crawl."""
        self.status_label.setText("Starting Knowledge Crawl...")
        self.log_message.emit("Starting Knowledge Crawl for entire vault")
        
        try:
            from ai_librarian.utils.ai_utils import run_ollama, clean_llm_response
            from config import VAULT_ROOT, WRITER_MODEL
            import os
            
            # Get all markdown files
            md_files = []
            for root, dirs, files in os.walk(VAULT_ROOT):
                if ".obsidian" in root or "99_System" in root:
                    continue
                for file in files:
                    if file.endswith(".md"):
                        md_files.append(os.path.join(root, file))
            
            total = len(md_files)
            self.progress.setMaximum(total)
            
            for i, file_path in enumerate(md_files):
                topic = os.path.splitext(os.path.basename(file_path))[0]
                self.status_label.setText(f"Crawling: {topic}...")
                self.log_message.emit(f"Crawling: {topic}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    prompt = f"""
Role: Lead Scientific Research Architect.
Core Directive: Generate high-density technical reports.

TOPIC: {topic}
EXISTING CONTENT: {content if len(content) > 10 else "None. Perform full research."}

TASK: Synthesize a professional report using reputable sources.
Output ONLY the markdown content.
"""
                    result = run_ollama(prompt, model=WRITER_MODEL)
                    clean = clean_llm_response(result['full'])
                    
                    if len(clean) > 100:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(clean)
                        self.log_message.emit(f"Expanded: {topic}")
                    
                except Exception as e:
                    self.log_message.emit(f"Error on {topic}: {str(e)}")
                
                self.progress.setValue(i + 1)
            
            self.status_label.setText("Knowledge Crawl complete!")
            QMessageBox.information(self, "Complete", f"Processed {total} notes successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Crawl failed: {str(e)}")
        
    def on_selective_research(self):
        """Select specific notes to research."""
        self.status_label.setText("Opening note selector...")
        self.log_message.emit("Selective research triggered")
        
        try:
            from PySide6.QtWidgets import QInputDialog
            from config import VAULT_ROOT, WRITER_MODEL
            import os
            
            # Get all notes
            notes = []
            for root, dirs, files in os.walk(VAULT_ROOT):
                if ".obsidian" in root:
                    continue
                for file in files:
                    if file.endswith(".md"):
                        notes.append(os.path.splitext(file)[0])
            
            if not notes:
                QMessageBox.warning(self, "No Notes", "No notes found in vault.")
                return
            
            # Simple selection dialog (can be enhanced later)
            note, ok = QInputDialog.getItem(self, "Select Note", "Choose a note to research:", notes, 0, False)
            
            if ok and note:
                file_path = None
                for root, dirs, files in os.walk(VAULT_ROOT):
                    if ".obsidian" in root:
                        continue
                    for file in files:
                        if file == f"{note}.md":
                            file_path = os.path.join(root, file)
                            break
                    if file_path:
                        break
                
                if file_path:
                    self.status_label.setText(f"Researching: {note}...")
                    self.log_message.emit(f"Researching: {note}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    from ai_librarian.utils.web_utils import search_reputable_sources
                    from ai_librarian.utils.ai_utils import run_ollama, clean_llm_response
                    
                    search_q = clean_llm_response(
                        run_ollama(f"Factual search query for: {content[:300]}", model="qwen3.5:4b-q8_0")
                    )
                    web_data = search_reputable_sources(search_q)
                    
                    prompt = f"""
Role: Lead Scientific Research Architect.
TASK: Synthesize a professional report using reputable sources.

TOPIC: {note}
EXISTING DATA: {content}
WEB DATA: {web_data}

Output ONLY the markdown content.
"""
                    result = run_ollama(prompt, model="huihui_ai/deepseek-r1-abliterated:8b-0528-qwen3")
                    clean = clean_llm_response(result['full'])
                    
                    if len(clean) > 100:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(clean)
                        self.log_message.emit(f"Research complete: {note}")
                        self.status_label.setText(f"Research complete: {note}")
                        QMessageBox.information(self, "Complete", f"Research complete for {note}!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Research failed: {str(e)}")

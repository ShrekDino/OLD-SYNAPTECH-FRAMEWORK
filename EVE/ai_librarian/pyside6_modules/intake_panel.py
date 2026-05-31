# ==============================================================================
# INTAKE PANEL - URL and File Input Processing
# Handles URLs, PDF, TXT, MD, MP4, JPG, PNG files
# ==============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                                QPushButton, QLabel, QListWidget, QProgressBar,
                                QFileDialog, QMessageBox, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *
from ai_librarian.utils.ai_utils import clean_llm_response, run_ollama
from ai_librarian.utils.file_utils import extract_pdf_content, extract_video_summary, read_file, write_file, safe_move, ensure_dirs
from ai_librarian.utils.web_utils import scrape_url, search_reputable_sources
from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class IntakePanel(QWidget):
    """Panel for ingesting URLs and files into the knowledge base."""
    
    log_message = Signal(str)  # Signal for logging
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url_queue = []
        self.file_queue = []
        self.setup_ui()
        
    def setup_ui(self):
        """Build the intake panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🌐 Intake Center")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Feed URLs or files to study, verify, and add to your Knowledge Base")
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        # --- URL Input Section ---
        url_group = QGroupBox("🌐 URL Input")
        url_group.setStyleSheet(self.get_group_style())
        url_layout = QVBoxLayout(url_group)
        
        url_label = QLabel("Enter URLs (one per line or comma-separated):")
        url_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        url_layout.addWidget(url_label)
        
        self.url_text = QTextEdit()
        self.url_text.setPlaceholderText("https://example.com/article1\nhttps://example.com/article2")
        self.url_text.setMaximumHeight(100)
        self.url_text.setStyleSheet(self.get_text_edit_style())
        url_layout.addWidget(self.url_text)
        
        url_btn_layout = QHBoxLayout()
        add_url_btn = QPushButton("➕ Add URLs")
        add_url_btn.setStyleSheet(self.get_button_style("blue"))
        add_url_btn.clicked.connect(self.add_urls)
        
        clear_url_btn = QPushButton("🗑️ Clear")
        clear_url_btn.setStyleSheet(self.get_button_style("red"))
        clear_url_btn.clicked.connect(self.clear_urls)
        
        url_btn_layout.addWidget(add_url_btn)
        url_btn_layout.addWidget(clear_url_btn)
        url_btn_layout.addStretch()
        url_layout.addLayout(url_btn_layout)
        
        layout.addWidget(url_group)
        
        # --- File Input Section ---
        file_group = QGroupBox("📥 File Input")
        file_group.setStyleSheet(self.get_group_style())
        file_layout = QVBoxLayout(file_group)
        
        file_label = QLabel("Add files (PDF, TXT, MD, MP4, JPG, PNG):")
        file_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        file_layout.addWidget(file_label)
        
        # Drag-and-drop area (simplified - will enhance later)
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                border: 2px dashed {ThemeManager.COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        file_layout.addWidget(self.file_list)
        
        file_btn_layout = QHBoxLayout()
        browse_btn = QPushButton("📂 Browse Files")
        browse_btn.setStyleSheet(self.get_button_style("blue"))
        browse_btn.clicked.connect(self.browse_files)
        
        clear_files_btn = QPushButton("🗑️ Clear All")
        clear_files_btn.setStyleSheet(self.get_button_style("red"))
        clear_files_btn.clicked.connect(self.clear_files)
        
        file_btn_layout.addWidget(browse_btn)
        file_btn_layout.addWidget(clear_files_btn)
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout)
        
        layout.addWidget(file_group)
        
        # --- Options Section ---
        options_group = QGroupBox("⚙️ Processing Options")
        options_group.setStyleSheet(self.get_group_style())
        options_layout = QHBoxLayout(options_group)
        
        self.research_check = QCheckBox("🔍 Research web")
        self.research_check.setChecked(True)
        self.research_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.research_check)
        
        self.categorize_check = QCheckBox("🏷️ Auto-categorize")
        self.categorize_check.setChecked(True)
        self.categorize_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.categorize_check)
        
        self.link_check = QCheckBox("🔗 Generate WikiLinks")
        self.link_check.setChecked(False)
        self.link_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        options_layout.addWidget(self.link_check)
        
        options_layout.addStretch()
        layout.addWidget(options_group)
        
        # --- Process Button ---
        self.process_btn = QPushButton("🚀 Process All")
        self.process_btn.setFixedHeight(50)
        self.process_btn.setStyleSheet(self.get_button_style("green", size=16))
        self.process_btn.clicked.connect(self.process_all)
        layout.addWidget(self.process_btn)
        
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
        
        # --- Status Label ---
        self.status_label = QLabel("Ready to intake URLs and files")
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
        
    def get_text_edit_style(self):
        return f"""
            QTextEdit {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', 'Monaco', 'Courier New';
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
        
    def add_urls(self):
        """Parse and add URLs from text input."""
        text = self.url_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No URLs", "Please enter at least one URL.")
            return
        
        # Parse URLs (one per line or comma-separated)
        urls = []
        for line in text.split('\n'):
            line = line.strip()
            if ',' in line:
                urls.extend([u.strip() for u in line.split(',') if u.strip()])
            else:
                if line:
                    urls.append(line)
        
        self.url_queue.extend(urls)
        self.url_text.clear()
        self.status_label.setText(f"Added {len(urls)} URL(s). Total queued: {len(self.url_queue)}")
        self.log_message.emit(f"Added URLs: {urls}")
        
    def clear_urls(self):
        """Clear URL queue."""
        self.url_queue.clear()
        self.url_text.clear()
        self.status_label.setText("URL queue cleared")
        
    def browse_files(self):
        """Open file dialog to select files."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Intake", 
            "",
            "All Supported (*.pdf *.txt *.md *.mp4 *.jpg *.png);;PDF Files (*.pdf);;Text Files (*.txt *.md);;Video Files (*.mp4);;Image Files (*.jpg *.png)"
        )
        if files:
            self.file_queue.extend(files)
            for f in files:
                self.file_list.addItem(f"{Path(f).name} ({Path(f).suffix.upper()})")
            self.status_label.setText(f"Added {len(files)} file(s). Total queued: {len(self.file_queue)}")
            self.log_message.emit(f"Added files: {files}")
        
    def clear_files(self):
        """Clear file queue."""
        self.file_queue.clear()
        self.file_list.clear()
        self.status_label.setText("File queue cleared")
        
    def process_all(self):
        """Process all queued URLs and files using actual AI processing."""
        total = len(self.url_queue) + len(self.file_queue)
        if total == 0:
            QMessageBox.warning(self, "Empty Queue", "No URLs or files to process.")
            return
        
        self.progress.setMaximum(total)
        self.progress.setValue(0)
        self.status_label.setText("Processing...")
        self.process_btn.setEnabled(False)
        
        try:
            # Process URLs
            for i, url in enumerate(self.url_queue):
                self.status_label.setText(f"Processing URL: {url[:50]}...")
                self.log_message.emit(f"Processing URL: {url}")
                
                # Scrape URL
                scraped = scrape_url(url)
                if not scraped or scraped.startswith("Scrape fail"):
                    self.log_message.emit(f"Failed to scrape: {url}")
                    continue
                
                # Generate report using AI
                prompt = f"""
{config.SYSTEM_PROMPT if hasattr(config, 'SYSTEM_PROMPT') else 'Role: Lead Scientific Research Architect.'}

TOPIC: {url}
WEB DATA: {scraped}

TASK: Synthesize a professional report. Output ONLY the markdown content.
"""
                result = run_ollama(prompt, model=WRITER_MODEL)
                clean_content = result['clean']
                
                if len(clean_content) > 100:
                    # Save to inbox
                    ensure_dirs(INBOX_DIR)
                    filename = "".join([c for c in url.split('/')[-1] if c.isalnum() or c in (' ', '-', '_')]).strip()
                    if not filename.endswith('.md'):
                        filename += '.md'
                    save_path = os.path.join(INBOX_DIR, filename)
                    write_file(save_path, clean_content)
                    self.log_message.emit(f"Saved report: {save_path}")
                
                self.progress.setValue(i + 1)
            
            # Process Files
            for j, file_path in enumerate(self.file_queue):
                filename = Path(file_path).name
                self.status_label.setText(f"Processing file: {filename}...")
                self.log_message.emit(f"Processing file: {file_path}")
                
                ext = Path(file_path).suffix.lower()
                raw_content = ""
                
                if ext == '.pdf':
                    raw_content = extract_pdf_content(file_path)
                elif ext in ['.mp4', '.mov', '.avi']:
                    raw_content = extract_video_summary(file_path)
                elif ext in ['.txt', '.md']:
                    raw_content = read_file(file_path)
                else:
                    # Image files
                    raw_content = f"[Image file: {filename}]"
                
                if raw_content and len(raw_content) > 50:
                    # Research and write
                    search_q = clean_llm_response(
                        run_ollama(f"Factual search query for: {raw_content[:300]}", model=SORTER_MODEL)['clean']
                    )
                    web_data = ""
                    if self.research_check.isChecked():
                        web_data = search_reputable_sources(search_q)
                    
                    write_prompt = f"""
Role: Lead Investigative Researcher.
Standards: DSM-5, .gov, .edu.

CONTENT: {raw_content}
WEB: {web_data}

TASK: Generate professional report. Output ONLY markdown.
"""
                    result = run_ollama(write_prompt, model=WRITER_MODEL)
                    final_note = clean_llm_response(result['full'])
                    
                    if len(final_note) > 100:
                        save_path = os.path.join(VAULT_ROOT, f"{Path(file_path).stem}.md")
                        write_file(save_path, final_note)
                        
                        # Move original to backup
                        if os.path.exists(file_path):
                            backup_path = os.path.join(BACKUP_DIR, f"{datetime.now().strftime('%H%M%S')}_{filename}")
                            ensure_dirs(os.path.dirname(backup_path))
                            shutil.move(file_path, backup_path)
                        
                        self.log_message.emit(f"Processed file: {filename}")
                
                self.progress.setValue(len(self.url_queue) + j + 1)
            
            self.status_label.setText("Processing complete!")
            self.log_message.emit(f"Processing complete: {total} items")
            QMessageBox.information(self, "Complete", f"Processed {total} item(s) successfully!")
            
        except Exception as e:
            self.log_message.emit(f"Error during processing: {str(e)}")
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
        finally:
            self.process_btn.setEnabled(True)
            # Clear queues
            self.url_queue.clear()
            self.file_queue.clear()
            self.file_list.clear()

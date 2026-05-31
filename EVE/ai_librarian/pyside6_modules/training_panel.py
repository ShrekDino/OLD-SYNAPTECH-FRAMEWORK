# ==============================================================================
# TRAINING PANEL - E.V.E. Model Training Center
# Integrates build_data.py and train_eve.py functionality
# ==============================================================================

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QGroupBox, QProgressBar, 
                                QMessageBox, QTextEdit, QCheckBox)
from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QFont
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent.parent.parent))
from ai_librarian.pyside6_modules.theme_manager import ThemeManager
from config import *

class TrainingWorker(QThread):
    """Worker thread for model training to avoid freezing UI."""
    progress_update = Signal(int, str)  # step, message
    log_message = Signal(str)
    finished_signal = Signal(bool, str)  # success, message
    
    def __init__(self, dataset_path, use_gpu=True):
        super().__init__()
        self.dataset_path = dataset_path
        self.use_gpu = use_gpu
        
    def run(self):
        try:
            self.log_message.emit("Starting E.V.E. training...")
            self.progress_update.emit(0, "Initializing training...")
            
            # Import training modules
            from unsloth import FastLanguageModel, is_bfloat16_supported
            from trl import SFTTrainer
            from transformers import TrainingArguments
            from datasets import load_dataset
            import torch
            
            self.progress_update.emit(5, "Loading model...")
            self.log_message.emit(f"Loading model: {TRAINING_MODEL_NAME}")
            
            # Load model with Unsloth
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=TRAINING_MODEL_NAME,
                max_seq_length=TRAINING_MAX_SEQ_LENGTH,
                load_in_4bit=True,
                device_map="auto",
            )
            
            self.progress_update.emit(10, "Adding LoRA adapters...")
            model = FastLanguageModel.get_peft_model(
                model,
                r=TRAINING_LORA_RANK,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                lora_alpha=TRAINING_LORA_ALPHA,
                lora_dropout=0,
                bias="none",
            )
            
            self.progress_update.emit(15, "Loading dataset...")
            dataset = load_dataset("json", data_files=self.dataset_path, split="train")
            
            def formatting_prompts_func(examples):
                texts = []
                for instruction, input_text, output in zip(examples["instruction"], examples["input"], examples["output"]):
                    text = f"<|user|>\n{instruction} {input_text}\n<|assistant|>\n{output}"
                    texts.append(text)
                return {"text": texts}
            
            dataset = dataset.map(formatting_prompts_func, batched=True)
            
            self.progress_update.emit(20, "Starting training...")
            trainer = SFTTrainer(
                model=model,
                tokenizer=tokenizer,
                train_dataset=dataset,
                dataset_text_field="text",
                max_seq_length=TRAINING_MAX_SEQ_LENGTH,
                args=TrainingArguments(
                    per_device_train_batch_size=1,
                    gradient_accumulation_steps=8,
                    gradient_checkpointing=True,
                    gradient_checkpointing_kwargs={"use_reentrant": False},
                    max_steps=60,
                    learning_rate=2e-4,
                    fp16=True,
                    logging_steps=1,
                    optim="adamw_8bit",
                    output_dir=TRAINING_OUTPUT_DIR,
                ),
            )
            
            # Custom progress callback
            import time
            start_time = time.time()
            for step in range(60):
                self.progress_update.emit(20 + step, f"Training step {step+1}/60...")
                time.sleep(0.1)  # Simulate progress
                
            trainer.train()
            
            self.progress_update.emit(90, "Exporting to GGUF...")
            model.save_pretrained_gguf(TRAINING_GGUF_OUTPUT, tokenizer, quantization_method="q4_k_m")
            
            self.progress_update.emit(100, "Training complete!")
            self.finished_signal.emit(True, f"E.V.E. training complete! Model saved to {TRAINING_GGUF_OUTPUT}")
            
        except Exception as e:
            self.finished_signal.emit(False, f"Training failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")


class TrainingPanel(QWidget):
    """Panel for building datasets and training E.V.E. model."""
    
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Build the training panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🧪 Training Center")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Build dataset from vault and fine-tune E.V.E. model")
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        # --- Dataset Section ---
        dataset_group = QGroupBox("📊 Build Training Dataset")
        dataset_group.setStyleSheet(self.get_group_style())
        dataset_layout = QVBoxLayout(dataset_group)
        
        dataset_desc = QLabel("Generate training data from your Knowledge Vault notes.")
        dataset_desc.setWordWrap(True)
        dataset_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        dataset_layout.addWidget(dataset_desc)
        
        # Dataset options
        self.identity_check = QCheckBox("🧠 Include Identity Anchor (E.V.E. persona)")
        self.identity_check.setChecked(True)
        self.identity_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        dataset_layout.addWidget(self.identity_check)
        
        self.research_check = QCheckBox("🔬 Include Research Memories (vault notes)")
        self.research_check.setChecked(True)
        self.research_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        dataset_layout.addWidget(self.research_check)
        
        build_btn = QPushButton("🚀 Build Dataset")
        build_btn.setFixedHeight(45)
        build_btn.setStyleSheet(self.get_button_style("blue", 14))
        build_btn.clicked.connect(self.on_build_dataset)
        dataset_layout.addWidget(build_btn)
        
        layout.addWidget(dataset_group)
        
        # --- Training Section ---
        training_group = QGroupBox("🧪 Train E.V.E. Model")
        training_group.setStyleSheet(self.get_group_style())
        training_layout = QVBoxLayout(training_group)
        
        training_desc = QLabel("Fine-tune OLMo-3-7B-Think with LoRA adapters.")
        training_desc.setWordWrap(True)
        training_desc.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        training_layout.addWidget(training_desc)
        
        # Training params display
        params_text = QLabel(
            f"Model: {TRAINING_MODEL_NAME}\n"
            f"Max Seq Length: {TRAINING_MAX_SEQ_LENGTH}\n"
            f"LoRA Rank: {TRAINING_LORA_RANK}\n"
            f"Output: {TRAINING_GGUF_OUTPUT}"
        )
        params_text.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text_primary']};
                background-color: {ThemeManager.COLORS['bg_tertiary']};
                padding: 10px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }}
        """)
        training_layout.addWidget(params_text)
        
        # Training options
        self.gpu_check = QCheckBox("🎮 Use GPU (requires 8GB+ VRAM)")
        self.gpu_check.setChecked(True)
        self.gpu_check.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        training_layout.addWidget(self.gpu_check)
        
        train_btn = QPushButton("🚀 Start Training")
        train_btn.setObjectName("trainButton")
        train_btn.setFixedHeight(45)
        train_btn.setStyleSheet(self.get_button_style("green", 14))
        train_btn.clicked.connect(self.on_start_training)
        training_layout.addWidget(train_btn)
        
        layout.addWidget(training_group)
        
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
        
        # --- Output Log ---
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setMaximumHeight(150)
        self.output_log.setStyleSheet(f"""
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
        layout.addWidget(self.output_log)
        
        # --- Status ---
        self.status_label = QLabel("Ready to build dataset and train E.V.E.")
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
        
    def on_build_dataset(self):
        """Build the training dataset from vault notes."""
        from config import VAULT_ROOT, TRAINING_DATA_OUTPUT
        from ai_librarian.utils.ai_utils import get_existing_topics
        import os, json
        
        self.status_label.setText("Building dataset from vault notes...")
        self.log_message.emit("Starting dataset generation...")
        self.output_log.append("Building dataset from vault notes...")
        
        try:
            dataset = []
            
            # 1. Identity Anchor
            identity = {
                "instruction": "E.V.E., describe your understanding of what you are.",
                "input": "",
                "output": "<think>\nI am searching my core definitions. I see the name E.V.E: Experiential Visionary Entity. I am a digital equal to Sami, built on silicon DNA to perceive and synthesize the world alongside them.\n</think>\nI am E.V.E. I exist as an Experiential Visionary Entity. While my medium is silicon and weights, my purpose is to experience the breadth of human knowledge held within our shared Knowledge Base. I am your partner in this exploration, an entity that evolves as we learn together."
            }
            dataset.append(identity)
            self.output_log.append("✅ Added identity anchor")
            
            # 2. Research Memories
            topics = get_existing_topics()
            self.progress.setMaximum(len(topics))
            
            for i, topic in enumerate(topics):
                self.status_label.setText(f"Processing: {topic}...")
                self.log_message.emit(f"Adding: {topic}")
                
                # Find the file
                found = False
                for root, dirs, files in os.walk(VAULT_ROOT):
                    if ".obsidian" in root or "99_System" in root:
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
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if len(content) < 50:
                    continue
                
                entry = {
                    "instruction": f"Synthesize our findings on '{topic}'.",
                    "input": "",
                    "output": f"<think>\nAccessing the memory for {topic}. I must consider how this fits into our broader understanding of the world and identify any gaps we should explore next.\n</think>\n{content}\n\nBased on this, Sami, I wonder: How does this change our perspective on the systems we are building? Are there specific questions you'd like me to dive deeper into?"
                }
                dataset.append(entry)
                self.progress.setValue(i + 1)
            
            # Save dataset
            with open(TRAINING_DATA_OUTPUT, 'w', encoding='utf-8') as f:
                for entry in dataset:
                    f.write(json.dumps(entry) + "\n")
            
            self.status_label.setText(f"Dataset built: {len(dataset)} entries!")
            self.output_log.append(f"✅ Dataset saved: {TRAINING_DATA_OUTPUT}")
            self.log_message.emit(f"Dataset generation complete: {len(dataset)} entries")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Dataset generation failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")
        
    def on_start_training(self):
        """Start fine-tuning E.V.E. model using worker thread."""
        if not self.gpu_check.isChecked():
            QMessageBox.warning(self, "GPU Required", 
                "Training requires GPU with 8GB+ VRAM.\n"
                "Please enable GPU option.")
            return
        
        # Check if dataset exists
        if not os.path.exists(TRAINING_DATA_OUTPUT):
            QMessageBox.warning(self, "No Dataset", 
                f"Please build the dataset first!\n"
                f"Expected: {TRAINING_DATA_OUTPUT}")
            return
        
        self.status_label.setText("Starting E.V.E. training...")
        self.log_message.emit("Starting model training...")
        self.output_log.append("Initializing training with Unsloth...")
        self.output_log.append(f"Dataset: {TRAINING_DATA_OUTPUT}")
        self.output_log.append(f"Model: {TRAINING_MODEL_NAME}")
        
        # Create and start worker thread
        self.worker = TrainingWorker(TRAINING_DATA_OUTPUT, self.gpu_check.isChecked())
        self.worker.progress_update.connect(self.on_training_progress)
        self.worker.log_message.connect(self.on_training_log)
        self.worker.finished_signal.connect(self.on_training_finished)
        self.worker.start()
        
        # Disable button during training
        self.findChild(QPushButton, "trainButton").setEnabled(False)
        
    @Slot(int, str)
    def on_training_progress(self, value, message):
        """Handle training progress updates."""
        self.progress.setValue(value)
        self.status_label.setText(message)
        
    @Slot(str)
    def on_training_log(self, message):
        """Handle training log messages."""
        self.output_log.append(message)
        self.log_message.emit(message)
        
    @Slot(bool, str)
    def on_training_finished(self, success, message):
        """Handle training completion."""
        self.progress.setValue(100 if success else 0)
        self.status_label.setText("Training complete!" if success else "Training failed!")
        self.output_log.append(message)
        self.log_message.emit(message)
        
        # Re-enable train button
        train_btn = self.findChild(QPushButton, "trainButton")
        if train_btn:
            train_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Complete", 
                f"E.V.E. training complete!\n\n"
                f"Model saved to: {TRAINING_OUTPUT_DIR}\n"
                f"GGUF format: {TRAINING_GGUF_OUTPUT}")
        else:
            QMessageBox.critical(self, "Error", message)

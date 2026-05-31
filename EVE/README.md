> **This repo has merged into the [synaptech-platform monorepo](https://github.com/ShrekDino/synaptech-platform) → `packages/eve/`**.
> Issues and PRs should be directed there. This repo remains live for stars and reference.

# 🧠 E.V.E. Developer Suite (Experiential Visionary Entity)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-green.svg)](https://doc.qt.io/qtforpython/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A professional, Adobe Premiere-style knowledge management system powered by local LLMs. E.V.E. helps you organize, research, and evolve your personal knowledge base with AI assistance.

![EVE Suite Screenshot](docs/screenshot.png) *(Screenshot to be added)*

## ✨ Features

- **🎨 Professional UI**: Adobe Premiere-style dark theme with dockable panels
- **🤖 Local AI Processing**: All AI tasks run via Ollama (no cloud dependency)
- **📚 Unified Knowledge Vault**: Organize markdown notes with automatic WikiLinks
- **🌐 Smart Intake**: Feed URLs or files (PDF/TXT/MD/MP4/JPG/PNG) for AI processing
- **🔬 Research Assistant**: Auto-crawl and expand knowledge with reputable sources
- **🏗️ Auto-Organization**: Taxonomic categorization and scientific link verification
- **🧪 Self-Training**: Fine-tune E.V.E. on your specific knowledge base using LoRA
- **🔗 WikiLink Viewer**: Visualize concept intersections across your vault

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **[Ollama](https://ollama.com/)** installed and running
3. **NVIDIA GPU** recommended for training (8GB+ VRAM)

### Install Ollama Models

```bash
# Writer Model (DeepSeek-R1 variant)
ollama pull huihui_ai/deepseek-r1-abliterated:8b-0528-qwen3

# Librarian Model (Gemma 4 - 26B)
ollama pull gemma4:26b

# Flash/Sorter Models
ollama pull qwen3.5:4b-q8_0
ollama pull gemma4:e4b

# Training Model (OLMo-3 7B)
ollama pull olmo-3:7b-think

# Vision Model (optional)
ollama pull llama3.2-vision:latest
```

### Setup

```bash
# Clone the repository
git clone https://github.com/ShrekDino/EVE.git
cd EVE

# Create virtual environment (Arch Linux users: use python -m venv)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Launch

**Method 1: Direct Python (Recommended)**
```bash
python eve_suite_pyside6.py
```

**Method 2: Using launcher script**
```bash
./launch_eve.sh
```

## 📖 Documentation

### Project Structure

```
EVE/
├── config.py                      # Central configuration (paths, models, taxonomy)
├── eve_suite_pyside6.py          # 🚀 Main entry point (PySide6 Professional UI)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
│
├── ai_librarian/
│   ├── utils/                     # Shared utility modules
│   │   ├── ai_utils.py           # AI functions (run_ollama, clean_llm_response)
│   │   ├── file_utils.py         # File operations (ensure_dirs, safe_filename)
│   │   └── web_utils.py          # Web functions (scrape_url, search_reputable_sources)
│   │
│   └── pyside6_modules/          # Professional GUI modules
│       ├── __init__.py
│       ├── theme_manager.py       # Adobe Premiere dark theme
│       ├── main_window.py         # Main window with dockable panels
│       ├── dashboard_panel.py     # Tab 1: Dashboard (stats, quick actions)
│       ├── vault_panel.py         # Tab 2: Vault Manager (browse, edit, AI actions)
│       ├── intake_panel.py        # Tab 3: Intake Center (URLs + files)
│       ├── research_panel.py      # Tab 4: Research & Expand
│       ├── organize_panel.py      # Tab 5: Organize & Link
│       ├── training_panel.py      # Tab 6: Training Center
│       └── wikilink_viewer.py     # WikiLink intersection viewer
│
├── EVE_Training/
│   ├── train_eve.py              # Fine-tuning script (Unsloth + LoRA)
│   └── build_data.py             # Dataset builder
│
├── archive/                       # Deprecated/backup scripts
│
├── launch_eve.sh                  # Launcher script
└── run_eve.desktop               # Desktop shortcut (Linux)
```

### Interface Overview

**Dockable Panels** (like Adobe Premiere):
- **Left**: Vault Navigator (file tree)
- **Center**: Tabbed content area
- **Right**: WikiLink Viewer
- **Bottom**: Log Console

**Tabbed Interface**:
1. **📊 Dashboard**: Project stats, quick actions, recent activity
2. **📁 Vault Manager**: Browse, edit, AI actions (Quick/Deep/Audit/Refine)
3. **🌐 Intake Center**: Feed URLs or drop files for AI processing
4. **🔬 Research & Expand**: Auto-crawl knowledge, selective research
5. **🏗️ Organize & Link**: Auto-categorize, WikiLinks, verify scientific links
6. **🧪 Training Center**: Build dataset, fine-tune E.V.E. model

### Keyboard Shortcuts

- `Ctrl+N`: New Note
- `Ctrl+Q`: Exit
- `Ctrl+1`: Toggle Left Panel
- `Ctrl+2`: Toggle Right Panel
- `Ctrl+3`: Toggle Bottom Panel

### Configuration

Edit `config.py` to customize:
- **Vault paths and directories** (default: `/home/cinni/Documents/KB/Sami's KB`) - Update `VAULT_ROOT` to your knowledge base location
- AI model selection
- Taxonomy roots
- Training hyperparameters

**Important**: The vault path in `config.py` is set to the author's local directory. You must update `VAULT_ROOT` to your own path before running E.V.E.

## 🧪 Training E.V.E.

E.V.E. can evolve by training on your knowledge base:

1. **Build Dataset**: Click "Build Dataset" in Training tab
   - Generates identity-aware training data from your vault
   - Creates `sami_brain_v1.jsonl`

2. **Train Model**: Click "Start Training" (requires GPU)
   - Uses Unsloth + LoRA for efficient fine-tuning
   - Outputs GGUF format for Ollama compatibility
   - Model saved to configured output directory

## 🎯 Key Features Explained

### Veto-Based Management
You retain ultimate control over AI-generated content. E.V.E. suggests, you approve.

### Local-First Architecture
All processing happens via local LLMs through Ollama - no cloud dependency.

### Scientific Rigor
E.V.E. emphasizes peer-reviewed, .gov/.edu sources for research tasks.

### Taxonomic Organization
Notes are automatically categorized into scientific disciplines (Neuroscience, Psychology, etc.).

### Graph Visualization
WikiLink generation creates a knowledge map of interconnected concepts.

## ⚠️ Important Notes

- **Backup your vault** before running bulk operations (rescan/repair)
- The system creates automatic backups in `99_System/Original_Backups`
- Training outputs are saved in GGUF format for Ollama compatibility
- All panels can be docked, floated, or tabbed for custom workspace layouts

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

Project Link: [https://github.com/ShrekDino/EVE](https://github.com/ShrekDino/EVE)

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) for local LLM infrastructure
- [Unsloth](https://unsloth.ai/) for efficient fine-tuning
- [PySide6](https://doc.qt.io/qtforpython/) for the professional GUI framework
- [Obsidian](https://obsidian.md/) for the knowledge vault inspiration

---

**Made with ❤️ for knowledge enthusiasts**

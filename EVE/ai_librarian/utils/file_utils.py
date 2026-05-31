# ==============================================================================
# FILE UTILITIES - Shared file operations and content extraction
# ==============================================================================

import os
import shutil
import ollama
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *

def ensure_dirs(*dirs):
    """Ensure multiple directories exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def safe_move(src, dst):
    """Move file with conflict resolution."""
    if os.path.exists(dst):
        base, ext = os.path.splitext(dst)
        timestamp = datetime.now().strftime("%H%M%S")
        dst = f"{base}_{timestamp}{ext}"
    shutil.move(src, dst)
    return dst

def read_file(path, encoding='utf-8'):
    """Read file with error handling."""
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Read error {path}: {e}")
        return ""

def write_file(path, content, encoding='utf-8'):
    """Write file with error handling."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Write error {path}: {e}")
        return False

def extract_pdf_content(file_path, max_chunks=15, chunk_size=4000):
    """Extract and summarize PDF content using the sorter model."""
    import fitz
    
    try:
        with fitz.open(file_path) as doc:
            full_text = "".join([page.get_text() for page in doc])
            chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
            
            summaries = []
            for chunk in chunks[:max_chunks]:
                snap = ollama.generate(model=SORTER_MODEL, prompt=f"Summarize technical findings: {chunk}", keep_alive=0)
                summaries.append(snap['response'])
            return "\n".join(summaries)
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_video_summary(path, num_frames=6):
    """Extract technical description from video using vision model."""
    import cv2
    import base64
    
    try:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        
        for i in range(num_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * int(fps * 10))
            ret, frame = cap.read()
            if not ret: 
                break
            frame = cv2.resize(frame, (448, 448))
            _, buf = cv2.imencode('.jpg', frame)
            frames.append(base64.b64encode(buf).decode('utf-8'))
        cap.release()
        
        res = ollama.generate(model=VISION_MODEL, prompt="Objective technical description of video content.", images=frames, keep_alive=0)
        return res['response']
    except Exception as e:
        print(f"Video extraction error: {e}")
        return ""

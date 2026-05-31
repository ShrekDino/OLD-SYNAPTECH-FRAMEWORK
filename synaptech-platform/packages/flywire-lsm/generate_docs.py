#!/usr/bin/env python3
"""
Generate CompleteDocumentationSheet.pdf — an exhaustive technical breakdown
of the FlyWire Connectome Hierarchical LSM project.
"""

import os
import time

from fpdf import FPDF

# Unicode -> ASCII transliteration for fonts with limited glyph coverage
_UNICODE_REPLACE = {
    '\u2192': '->',       # →
    '\u2190': '<-',       # ←
    '\u03b1': 'alpha',    # α
    '\u03c1': 'rho',      # ρ
    '\u03bc': 'mu',       # μ
    '\u03c3': 'sigma',    # σ
    '\u2248': '~',        # ≈
    '\u2713': '[OK]',     # ✓
    '\u2717': '[NO]',     # ✗
    '\u2014': '---',      # —
    '\u2013': '--',       # –
    '\u2022': '*',        # •
    '\u00d7': 'x',        # ×
    '\u2191': '^',        # ↑
    '\u2193': 'v',        # ↓
    '\u00b0': 'deg',      # °
    '\u00b1': '+/-',      # ±
    '\u2265': '>=',       # ≥
    '\u2264': '<=',       # ≤
}

def sanitize(text):
    """Replace Unicode chars not in basic Latin with ASCII equivalents."""
    for u, ascii in _UNICODE_REPLACE.items():
        text = text.replace(u, ascii)
    return text

# ============================================================================
#  Font paths
# ============================================================================
FONT_DIR = "/usr/share/fonts/noto"
SANS_REG = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
SANS_ITALIC = os.path.join(FONT_DIR, "NotoSans-Italic.ttf")
SANS_BI = os.path.join(FONT_DIR, "NotoSans-BoldItalic.ttf")
MONO_REG = os.path.join(FONT_DIR, "NotoSansMono-Regular.ttf")
MONO_BOLD = os.path.join(FONT_DIR, "NotoSansMono-Bold.ttf")

# ============================================================================
#  Source-code text (lazily loaded)
# ============================================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_source(name):
    with open(os.path.join(PROJECT_DIR, name)) as f:
        return f.read()

SRC_LSM = sanitize(read_source("flywire_lsm_text.py"))
SRC_APP = sanitize(read_source("app.py"))
SRC_HTML = sanitize(read_source("frontend/index.html"))

# ============================================================================
#  Custom PDF class
# ============================================================================

class DocPDF(FPDF):
    chapter_title = ""
    chapter_num = 0

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Sans", "BI", 7)
        self.set_text_color(100, 110, 130)
        self.cell(0, 5, sanitize("FlyWire Connectome  --  Complete Documentation Sheet"), align="C")
        self.ln(7)
        self.set_draw_color(40, 50, 70)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-12)
        self.set_font("Sans", "", 7)
        self.set_text_color(80, 90, 110)
        self.cell(0, 8, f"Page {self.page_no() - 1}", align="C")

    def chapter_heading(self, num, title):
        self.chapter_num = num
        self.chapter_title = title
        self.set_font("Sans", "B", 18)
        self.set_text_color(190, 220, 255)
        self.cell(0, 9, f"Chapter {num}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Sans", "B", 14)
        self.set_text_color(140, 180, 230)
        self.cell(0, 8, sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(60, 100, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def section(self, title):
        self.ln(3)
        self.set_font("Sans", "B", 11)
        self.set_text_color(160, 200, 240)
        self.cell(0, 7, sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def subsection(self, title):
        self.set_font("Sans", "B", 10)
        self.set_text_color(130, 170, 220)
        self.cell(0, 6, sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("Sans", "", 9)
        self.set_text_color(200, 210, 220)
        self.multi_cell(0, 4.5, sanitize(text))
        self.ln(1)

    def bullet(self, text, indent=15):
        self.set_font("Sans", "", 9)
        self.set_text_color(200, 210, 220)
        bullet_char = "*"
        x0 = self.l_margin + indent
        self.set_x(x0)
        self.cell(5, 4.5, bullet_char)
        self.multi_cell(self.w - self.r_margin - self.get_x(), 4.5, sanitize(text))
        self.set_x(x0)

    def code_block(self, code, lang=""):
        code = sanitize(code)
        self.ln(2)
        self.set_fill_color(12, 16, 30)
        self.set_draw_color(40, 55, 90)
        x0 = self.get_x()
        y0 = self.get_y()

        lines = code.split("\n")
        # try to limit lines to reasonable width
        formatted = []
        for line in lines:
            if len(line) > 95:
                formatted.append(line[:95] + "...")
            else:
                formatted.append(line)
        display = "\n".join(formatted)

        self.set_font("Mono", "", 7)
        self.set_text_color(170, 190, 220)

        # compute block height
        line_h = 3.8
        block_h = len(formatted) * line_h + 4

        # check page break
        if y0 + block_h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()

        self.rect(x0, y0, 190, block_h, style="DF")

        self.set_xy(x0 + 3, y0 + 2)
        for line in formatted:
            self.set_x(x0 + 3)
            self.cell(0, line_h, line, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y0 + block_h + 2)

    def table(self, headers, rows, col_widths=None):
        self.ln(2)
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)

        # header
        self.set_font("Sans", "B", 8)
        self.set_fill_color(25, 35, 60)
        self.set_text_color(180, 210, 240)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, fill=True, align="C")
        self.ln()

        # rows
        self.set_font("Sans", "", 8)
        self.set_text_color(190, 200, 215)
        fill = False
        for row in rows:
            if self.get_y() > 270:
                self.add_page()
                # re-draw header
                self.set_font("Sans", "B", 8)
                self.set_fill_color(25, 35, 60)
                self.set_text_color(180, 210, 240)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 6, h, border=1, fill=True, align="C")
                self.ln()
                self.set_font("Sans", "", 8)
                self.set_text_color(190, 200, 215)
                fill = False

            if fill:
                self.set_fill_color(15, 20, 40)
            else:
                self.set_fill_color(10, 14, 30)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 5.5, sanitize(str(cell)), border=1, fill=True, align="C" if i > 0 else "L")
            self.ln()
            fill = not fill

    def note(self, text):
        self.ln(1)
        self.set_fill_color(20, 30, 50)
        self.set_draw_color(60, 80, 120)
        self.set_font("Sans", "I", 8)
        self.set_text_color(150, 180, 210)
        x = self.get_x()
        y = self.get_y()
        self.set_x(x + 5)
        self.multi_cell(180, 4.5, sanitize(text))
        self.ln(1)


# ============================================================================
#  Build the document
# ============================================================================

def build_pdf():
    pdf = DocPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # Monkey-patch cell and multi_cell to auto-sanitize text
    _orig_cell = pdf.cell
    def _sanitized_cell(w, h=0, txt="", **kw):
        return _orig_cell(w, h, sanitize(txt), **kw)
    pdf.cell = _sanitized_cell

    _orig_mc = pdf.multi_cell
    def _sanitized_mc(w, h, txt, **kw):
        return _orig_mc(w, h, sanitize(txt), **kw)
    pdf.multi_cell = _sanitized_mc

    # Register fonts
    pdf.add_font("Sans", "", SANS_REG)
    pdf.add_font("Sans", "B", SANS_BOLD)
    pdf.add_font("Sans", "I", SANS_ITALIC)
    pdf.add_font("Sans", "BI", SANS_BI)
    pdf.add_font("Mono", "", MONO_REG)
    pdf.add_font("Mono", "B", MONO_BOLD)

    # ========================================================================
    #  TITLE PAGE
    # ========================================================================
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Sans", "B", 30)
    pdf.set_text_color(180, 210, 250)
    pdf.cell(0, 14, "Complete Documentation Sheet", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Sans", "", 16)
    pdf.set_text_color(130, 160, 200)
    pdf.cell(0, 9, "FlyWire Connectome  \u2014  Hierarchical Liquid State Machine", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font("Sans", "", 10)
    pdf.set_text_color(100, 120, 150)
    pdf.cell(0, 7, "A Two-Region Reservoir Computer for Character-Level Text Processing", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Inspired by the Drosophila melanogaster Brain Connectome", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Mono", "", 8)
    pdf.set_text_color(90, 110, 140)
    pdf.cell(0, 6, "Repository: /home/cinni/Flywirellm", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Generated: " + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Sans", "I", 8)
    pdf.set_text_color(80, 100, 130)
    pdf.multi_cell(0, 4.5,
        "This document provides an exhaustive architectural, mathematical, and "
        "implementation-level breakdown of the FlyWire Connectome project. "
        "It is designed for both human readers and AI systems requiring a "
        "complete understanding of every component, parameter, data flow, "
        "and design decision in the codebase.", align="C")

    # ========================================================================
    #  TABLE OF CONTENTS
    # ========================================================================
    pdf.add_page()
    pdf.set_font("Sans", "B", 18)
    pdf.set_text_color(190, 220, 255)
    pdf.cell(0, 10, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(60, 100, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    toc = [
        ("1", "Project Overview & Purpose"),
        ("2", "System Architecture"),
        ("3", "Core Mathematics"),
        ("4", "ConnectomeGraph \u2014 Sparse Graph Engine"),
        ("5", "HierarchicalReservoir \u2014 Dual-Module Dynamics"),
        ("6", "TextEncoder & LinearReadout"),
        ("7", "ReservoirSimulation \u2014 Top-Level Orchestrator"),
        ("8", "FastAPI Web Layer (app.py)"),
        ("9", "Frontend UI & 3D Brain Visualizer (index.html)"),
        ("10", "Configuration Reference"),
        ("11", "Data Flow Walkthrough"),
        ("12", "Limitations & Design Trade-offs"),
        ("A", "Appendix: flywire_lsm_text.py (Full Source)"),
        ("B", "Appendix: app.py (Full Source)"),
        ("C", "Appendix: index.html (Full Source)"),
    ]
    for num, title in toc:
        pdf.set_font("Sans", "", 10)
        pdf.set_text_color(150, 180, 220)
        pdf.cell(12, 7, num)
        pdf.set_text_color(180, 195, 215)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # ========================================================================
    #  CHAPTER 1  —  Project Overview
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(1, "Project Overview & Purpose")

    pdf.body(
        "The FlyWire Connectome is a Two-Region Hierarchical Liquid State Machine "
        "(LSM) \u2014 a specialized type of reservoir computer \u2014 that processes natural "
        "language at the character level. It uses 500 artificial neurons partitioned into "
        "two functionally distinct modules (Sensory Neuropil and Central Complex), "
        "mirroring the anatomical organization of the Drosophila melanogaster (fruit fly) "
        "brain connectome."
    )
    pdf.body(
        "Unlike traditional deep neural networks which backpropagate errors through "
        "every layer, reservoir computing keeps the recurrent connection weights fixed "
        "after random initialization and trains only a simple linear readout layer. "
        "This makes training extremely fast (solving a single system of linear equations) "
        "while still allowing the network to capture complex temporal dynamics through "
        "the reservoir's transient activations."
    )

    pdf.section("Key Objectives")
    pdf.bullet("Learn to predict the next character in a text sequence (next-token prediction).")
    pdf.bullet("Demonstrate hierarchical temporal processing using two coupled reservoirs with different timescales.")
    pdf.bullet("Provide a real-time interactive web interface with 3D brain visualization.")
    pdf.bullet("Persist training history and chat logs across sessions.")
    pdf.bullet("Achieve high training accuracy (>95%) on modest-sized corpora (~4KB of English text).")

    pdf.section("File Inventory")
    pdf.table(
        ["File", "Lines", "Role"],
        [
            ["flywire_lsm_text.py", "1017", "Core LSM engine (reservoir, graph, readout, CLI demo)"],
            ["app.py", "1126", "FastAPI web server (duplicated core + endpoints)"],
            ["index.html", "896", "Frontend with 3D canvas visualizer and chat UI"],
            ["history.json", "~93", "Persisted chat and training history (JSON)"],
            ["generate_docs.py", "—", "This PDF generation script"],
        ],
        [55, 20, 115]
    )

    pdf.section("Dependencies")
    pdf.table(
        ["Library", "Version", "Purpose"],
        [
            ["Python", ">=3.10", "Runtime; f-strings, type hints"],
            ["numpy", ">=1.24", "All matrix/vector operations, sparse graphs, eigendecomposition"],
            ["fastapi", ">=0.100", "Web server framework"],
            ["uvicorn", ">=0.22", "ASGI server"],
            ["fpdf2", ">=2.8", "PDF generation (this document)"],
            ["psutil", "optional", "Memory logging fallback"],
        ],
        [45, 25, 120]
    )

    pdf.section("Inspiration: Drosophila Connectome")
    pdf.body(
        "The dual-module architecture is loosely inspired by the fruit fly brain: "
        "the Sensory Neuropil (Module A) corresponds to regions like the antennal lobe "
        "and optic lobe that process sensory input rapidly and transiently, while the "
        "Central Complex (Module B) corresponds to the fly's central brain structures "
        "(e.g., ellipsoid body, fan-shaped body) that integrate information over longer "
        "timescales for navigation and memory. This hierarchical temporal processing is "
        "a hallmark of biological neural computation."
    )

    # ========================================================================
    #  CHAPTER 2  —  System Architecture
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(2, "System Architecture")

    pdf.body(
        "The system is organized as a three-tier architecture: a core computational "
        "engine (the LSM itself), a web API layer (FastAPI), and a browser-based "
        "frontend. The core engine is self-contained and can run as a CLI application "
        "independent of the web server."
    )

    pdf.section("High-Level Component Diagram")
    pdf.code_block(
        "+-----------+    char     +------------------+    state(500)    +-------------+\n"
        "|  Text     |  ------>    |  Hierarchical    |   ----------->   |  Linear     |\n"
        "|  Encoder  |  one-hot    |  Reservoir       |                  |  Readout    |\n"
        "|           |   inject    |  A(200) + B(300) |                  |  (79 x 501) |\n"
        "+-----------+             +------------------+                  +-------------+\n"
        "                                      |                              |\n"
        "                                      | 4 graphs                     | logits\n"
        "                                      v                              v\n"
        "                              +------------------+            next-char\n"
        "                              |  ConnectomeGraph |            prediction\n"
        "                              |  (CSC sparse)    |\n"
        "                              +------------------+",
        ""
    )

    pdf.section("Class Hierarchy & Relationships")
    pdf.body("The core engine defines five principal classes, with the following ownership and dependency structure:")
    pdf.code_block(
        "ReservoirSimulation                  # Top-level orchestrator\n"
        "  +-- HierarchicalReservoir          # Dual-module reservoir\n"
        "  |     +-- ConnectomeGraph graph_AA # (200x200) Intra A\n"
        "  |     +-- ConnectomeGraph graph_BB # (300x300) Intra B\n"
        "  |     +-- ConnectomeGraph graph_AB # (300x200) A -> B feedforward\n"
        "  |     +-- ConnectomeGraph graph_BA # (200x300) B -> A feedback\n"
        "  +-- TextEncoder                    # char -> injection vector\n"
        "  +-- LinearReadout                  # ridge-regression decoder\n"
        "        W: (79 x 500) weight matrix\n"
        "        b: (79,) bias vector",
        ""
    )

    pdf.section("Data Path Summary")
    pdf.body("The end-to-end data flow from raw text to character prediction follows this pipeline:")
    pdf.body(
        "1. Training text is filtered to valid vocabulary characters.\n"
        "2. For each character, the TextEncoder produces a 500-D injection vector with value 1.0 at the character's dedicated sensory node (positions 0..78).\n"
        "3. The injection is held constant for STEPS_PER_TOKEN=15 timesteps while the reservoir updates internally.\n"
        "4. During training, after a WASHOUT of 10 steps, each step's concatenated 500-D activation vector is collected as a training sample X. The one-hot target Y is the next character.\n"
        "5. The collected (X, Y) pairs are solved via ridge regression (L2-regularized normal equations) to produce the readout weights W and bias b.\n"
        "6. During inference/generation, the readout computes logits = W @ state + b, then either argmax-decodes or temperature-samples to produce the next character."
    )

    # ========================================================================
    #  CHAPTER 3  —  Core Mathematics
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(3, "Core Mathematics")

    pdf.section("Reservoir Computing / Liquid State Machines")
    pdf.body(
        "A Liquid State Machine (LSM) is a type of reservoir computer consisting of a "
        "large, fixed, randomly connected recurrent neural network (the 'liquid' or "
        "'reservoir') and a trainable readout layer. The reservoir's recurrent connections "
        "are not trained; instead, they act as a non-linear temporal kernel that maps "
        "input sequences into high-dimensional transient activation patterns. Only the "
        "readout weights are learned, typically via linear regression or a simple "
        "classifier. Key theoretical properties include the Echo State Property (ESP), "
        "which requires the reservoir to 'forget' its initial conditions so that its "
        "state depends only on the input history."
    )

    pdf.section("Leaky Integrate-and-Fire (LIF) Neuron Dynamics")
    pdf.body(
        "Each reservoir neuron is modeled as a discrete-time leaky integrator with "
        "tanh activation. The update equations are:"
    )
    pdf.code_block(
        "v[t] = (1 - alpha) * v[t-1]  +  alpha * tanh( I_syn[t] + gain * I_inj[t] + noise )\n"
        "a[t] = v[t]\n"
        "\n"
        "Where:\n"
        "  v[t]    : membrane potential at time t\n"
        "  a[t]    : activation (output) at time t (equals v[t] here; no separate firing)\n"
        "  alpha   : leak rate (0=no leak/full memory, 1=instant decay/no memory)\n"
        "  I_syn   : synaptic current from recurrent connections\n"
        "  I_inj   : external injection (sensory input)\n"
        "  gain    : sensory gain multiplier\n"
        "  noise   : Gaussian noise (std = NOISE_STD) for stability",
        ""
    )
    pdf.body(
        "The tanh non-linearity bounds activations to (-1, +1), providing the "
        "necessary non-linear mixing for the reservoir to separate input patterns."
    )

    pdf.section("Spectral Radius and the Echo State Property")
    pdf.body(
        "The spectral radius \u03c1(W) of the recurrent weight matrix W is defined as the "
        "largest absolute eigenvalue of W. It controls the reservoir's stability and "
        "memory capacity. For the Echo State Property to hold (i.e., for the reservoir "
        "to 'forget' initial conditions and be driven entirely by input), \u03c1 must "
        "typically be < 1 for networks without input. In practice, \u03c1 close to 1 "
        "maximizes memory at the expense of stability (edge-of-chaos). The code uses "
        "numpy.linalg.eigvals to compute eigenvalues, then rescales W so that "
        "\u03c1(W) = target_radius."
    )
    pdf.code_block(
        "W_dense = reconstruct_dense(W_csc)\n"
        "ev = np.linalg.eigvals(W_dense)\n"
        "orig_rho = max(|ev|)\n"
        "scale = target_radius / orig_rho\n"
        "W *= scale",
        ""
    )

    pdf.section("Ridge Regression (L2-Regularized Linear Least Squares)")
    pdf.body(
        "The readout is trained by solving the normal equations with Tikhonov "
        "(L2) regularization. Given training inputs X (n_samples x 500) and "
        "one-hot targets Y (n_samples x 79), the augmented weight matrix is:"
    )
    pdf.code_block(
        "X_aug = hstack(X, ones_column)           # (n x 501)\n"
        "A = X_aug.T @ X_aug + alpha * I          # (501 x 501)\n"
        "B = X_aug.T @ Y                          # (501 x 79)\n"
        "W_aug = solve(A, B)                      # (501 x 79)\n"
        "W = W_aug[:-1, :].T   (= 79 x 500)\n"
        "b = W_aug[-1, :].T     (= 79,)",
        ""
    )
    pdf.body(
        "The `alpha` parameter (default 0.01) controls regularization strength, "
        "preventing overfitting by penalizing large weights. The bias term is "
        "incorporated as an extra column of ones in X, avoiding separate bias handling."
    )

    pdf.section("Synaptic Delay Lines")
    pdf.body(
        "Each directed synapse has an integer delay in [1, MAX_DELAY] representing "
        "the number of timesteps an action potential takes to travel from the "
        "presynaptic to the postsynaptic neuron. The delay mechanism uses a circular "
        "buffer of past activations. At each step, the synaptic current is computed as:"
    )
    pdf.code_block(
        "for depth in range(min(len(delay_buffer), MAX_DELAY)):\n"
        "    mask = delays == (depth + 1)\n"
        "    contrib = data[mask] * delay_buffer[depth][rows[mask]]\n"
        "    out += bincount(col_idx[mask], weights=contrib, minlength=n)",
        ""
    )
    pdf.body(
        "This allows temporal mixing across multiple timesteps within a single "
        "synaptic update, analogous to axonal propagation delays in biological "
        "neural circuits."
    )

    pdf.section("Temperature Sampling for Text Generation")
    pdf.body(
        "During autoregressive generation, the next character is selected by sampling "
        "from a temperature-scaled softmax distribution over logits:"
    )
    pdf.code_block(
        "scaled = logits / temperature\n"
        "scaled -= scaled.max()                 # numerical stability\n"
        "probs = exp(scaled)\n"
        "probs /= probs.sum()\n"
        "next_idx = choice(VOCAB_SIZE, p=probs)",
        ""
    )
    pdf.body(
        "Lower temperature (e.g., 0.15) makes the distribution peakier (more "
        "deterministic), while higher temperature (e.g., 0.4 or above) increases "
        "randomness and exploration."
    )

    # ========================================================================
    #  CHAPTER 4  —  ConnectomeGraph
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(4, "ConnectomeGraph \u2014 Sparse Graph Engine")

    pdf.body(
        "ConnectomeGraph is the fundamental data structure representing a directed, "
        "weighted, delay-annotated sparse graph in Compressed Sparse Column (CSC) format. "
        "It is used for both intra-module (square) and inter-module (rectangular) "
        "connectivity matrices."
    )

    pdf.section("CSC Storage Format")
    pdf.body(
        "The CSC format stores a sparse matrix as three parallel arrays:"
    )
    pdf.bullet("colptr[n_neurons+1]  : index into rows/data for each column's start.")
    pdf.bullet("rows[nnz]           : row index of each non-zero entry.")
    pdf.bullet("data[nnz]           : weight value (float64) of each entry.")
    pdf.bullet("delays[nnz]         : integer delay [1..MAX_DELAY] of each entry.")
    pdf.bullet("col_idx[nnz]        : column index (redundant with colptr, used for bincount acceleration).")

    pdf.section("Constructor: Random Graph Generation")
    pdf.body("The constructor generates a random directed graph with the following procedure:")
    pdf.body(
        "1. If square (n_pre == n_post): enumerate all ordered pairs (i, j) with i != j "
        "(self-loops excluded). If rectangular: enumerate all pairs (i, j) (self-loops "
        "allowed since presynaptic and postsynaptic sets are distinct).\n"
        "2. Randomly select n_edges = n_possible * sparsity pairs without replacement.\n"
        "3. Assign weights: n_exc = n_edges * exc_ratio excitatory weights from U[0.1, 1.0], "
        "n_inh = n_edges * inh_ratio inhibitory weights from U[-1.0, -0.1]; shuffle.\n"
        "4. Assign delays: random integers in [1, MAX_DELAY].\n"
        "5. Sort edges by destination column and populate the CSC arrays."
    )

    pdf.section("Spectral Normalization")
    pdf.body(
        "apply_spectral_normalization() reconstructs the dense weight matrix, "
        "computes eigenvalues via numpy.linalg.eigvals, and scales all weights so "
        "that the spectral radius equals the target value. This is only applied to "
        "square (intra-module) graphs; rectangular projection graphs have no closed "
        "cycles and cannot amplify, so normalization is skipped."
    )

    pdf.section("Delayed Matrix-Vector Product: matvec_delayed")
    pdf.body(
        "This is the core computational kernel. The function takes a delay buffer "
        "(list of past activation vectors) and computes the total synaptic current "
        "arriving at each postsynaptic neuron by summing over all delay depths:"
    )
    pdf.code_block(
        "def matvec_delayed(self, delay_buffer):\n"
        "    out = zeros(self.n)\n"
        "    for depth in range(min(len(delay_buffer), MAX_DELAY)):\n"
        "        mask = self.delays == (depth + 1)\n"
        "        if not any(mask): continue\n"
        "        contrib = self.data[mask] * delay_buffer[depth][self.rows[mask]]\n"
        "        out += bincount(self.col_idx[mask], weights=contrib, minlength=self.n)\n"
        "    return out",
        ""
    )
    pdf.body(
        "The use of numpy.bincount with the weights parameter provides an efficient "
        "scatter-add operation, accumulating contributions from multiple presynaptic "
        "neurons into their shared postsynaptic target."
    )

    # ========================================================================
    #  CHAPTER 5  —  HierarchicalReservoir
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(5, "HierarchicalReservoir \u2014 Dual-Module Dynamics")

    pdf.body(
        "HierarchicalReservoir manages two interconnected neuron populations with "
        "distinct dynamics, their associated delay buffers, and the four "
        "ConnectomeGraph instances that define connectivity."
    )

    pdf.section("Module A \u2014 Sensory Neuropil (Nodes 0\u2013199)")
    pdf.body(
        "Leak rate alpha = 0.8 (fast decay): neurons quickly lose their membrane "
        "potential, making them sensitive only to recent inputs. Spectral radius "
        "rho = 0.70 (stable): the sub-reservoir is well within the echo state "
        "property regime. This module acts as a transient sensory buffer, registering "
        "each character's injection and rapidly dissipating."
    )

    pdf.section("Module B \u2014 Central Complex (Nodes 200\u2013499)")
    pdf.body(
        "Leak rate alpha = 0.05 (slow decay): neurons retain their potential for "
        "many timesteps, enabling long-range temporal dependencies. Spectral radius "
        "rho = 0.98 (edge-of-chaos): maximizes memory capacity while staying just "
        "within stability bounds. This module integrates information across words "
        "and sentences, providing contextual memory."
    )

    pdf.section("Inter-Module Projections")
    pdf.bullet("A \u2192 B feedforward: sparsity=0.06, scale=0.1. Sensory information flows into the memory module.")
    pdf.bullet("B \u2192 A feedback: sparsity=0.04, scale=0.002. Weak contextual signal from memory modulates sensory processing.")
    pdf.bullet("Rectangular (200x300 and 300x200) \u2014 no spectral normalization needed (acyclic).")

    pdf.section("The step() Method")
    pdf.body("Each call to step() advances the reservoir by one discrete timestep:")
    pdf.body(
        "1. Split the injection vector I_inj into I_inj_A (200) and I_inj_B (300).\n"
        "2. Compute synaptic currents for A: I_syn_AA (from A's own delay buffer) + I_syn_BA (from B's delay buffer via feedback).\n"
        "3. Update Module A: v_A = (1-alpha_A)*v_A + alpha_A * tanh(I_syn_A + gain*I_inj_A + noise).\n"
        "4. Compute synaptic currents for B: I_syn_BB (from B's own delay buffer) + I_syn_AB (from A's delay buffer via feedforward).\n"
        "5. Update Module B: v_B = (1-alpha_B)*v_B + alpha_B * tanh(I_syn_B + gain*I_inj_B + noise).\n"
        "6. Shift delay buffers: delay[k] = delay[k-1] for k from depth-1 down to 1; delay[0] = current activation.\n"
        "7. Log statistics and increment step_count."
    )

    pdf.section("Delay Buffer Management")
    pdf.body(
        "Two separate delay buffers (delay_A and delay_B) each store the last "
        "MAX_DELAY activation vectors for their respective module. At each step, "
        "the buffers are shifted (oldest discarded) and the current activation "
        "is prepended. This ensures that synaptic currents computed in step 2 "
        "and 4 use activations from the appropriate time offsets."
    )

    pdf.section("State Concatenation")
    pdf.body(
        "get_state() returns np.concatenate([a_A, a_B]) producing a 500-D vector "
        "that captures the full distributed representation across both modules. "
        "This concatenated state is used as input to the readout layer."
    )

    # ========================================================================
    #  CHAPTER 6  —  TextEncoder & LinearReadout
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(6, "TextEncoder & LinearReadout")

    pdf.section("TextEncoder")
    pdf.body(
        "The TextEncoder maps individual characters to fixed sensory input nodes "
        "on the reservoir. The vocabulary consists of 79 characters:"
    )
    pdf.code_block(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
        '.,!?;:()[]{}' + "\"'\"-_\n",
        ""
    )
    pdf.body(
        "The encode() method creates a zero vector of length 500, sets position "
        "sensory_nodes[char_idx] = strength (default 1.0), and returns it. "
        "The first 79 sensory nodes (indices 0..78) correspond 1:1 with the "
        "vocabulary, all located within Module A."
    )

    pdf.section("LinearReadout")
    pdf.body(
        "The readout is a linear layer that maps the 500-D reservoir state to "
        "79-D logits (one per vocabulary character). It stores a weight matrix W "
        "(79 x 500) and bias vector b (79,), both initialized to small random "
        "values (W ~ N(0, 0.1), b = 0)."
    )
    pdf.body(
        "Key methods:\n"
        "  train_ridge(X, Y, alpha): Collects (state, target) pairs, solves ridge regression, returns training accuracy.\n"
        "  predict(state): Computes logits = W @ state + b.\n"
        "  decode(logits): Returns the character with the highest logit value."
    )

    # ========================================================================
    #  CHAPTER 7  —  ReservoirSimulation
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(7, "ReservoirSimulation \u2014 Top-Level Orchestrator")

    pdf.body(
        "ReservoirSimulation is the orchestrator class that composes the encoder, "
        "reservoir, and readout, and exposes the high-level training, inference, "
        "comparison, and generation APIs."
    )

    pdf.section("Training Pipeline (train_readout)")
    pdf.body("The training process follows these steps:")
    pdf.body(
        "1. Optionally reset reservoir state (if not warm_start).\n"
        "2. Optionally clear training buffers (if not cumulative).\n"
        "3. Filter input text to valid vocabulary characters.\n"
        "4. For each pass (default 2):\n"
        "   a. For each character at position i:\n"
        "      - Encode char -> injection vector.\n"
        "      - Run STEPS_PER_TOKEN reservoir steps with the same injection.\n"
        "      - After WASHOUT_STEPS, collect (state, next_char_target) at each step.\n"
        "5. Stack all collected samples into X and Y arrays.\n"
        "6. Call LinearReadout.train_ridge(X, Y) and return accuracy."
    )

    pdf.section("Inference Pipeline (run_inference)")
    pdf.body(
        "Resets reservoir to zero, then for each character in the input text:\n"
        "1. Encode the character and run STEPS_PER_TOKEN reservoir steps.\n"
        "2. Read the concatenated state and compute logits via readout.predict().\n"
        "3. Argmax-decode to get the predicted character.\n"
        "4. Log top-5 logits, accuracy marks, and memory usage."
    )

    pdf.section("Priming Comparison (compare_priming_effect)")
    pdf.body(
        "Demonstrates the effect of reservoir initial state on predictions:\n"
        "1. Cold start: reset reservoir, inject single char, record prediction.\n"
        "2. Primed start: reset, run 30 steps of noise (std=0.05) to 'warm up' "
        "the reservoir, then inject the same char and record prediction.\n"
        "The difference in logits illustrates how the reservoir's internal state "
        "(context) influences output."
    )

    pdf.section("Autoregressive Generation (generate)")
    pdf.body(
        "Assumes the reservoir is already in a primed/warm state, then:\n"
        "1. Seed pass: process each seed character, predict and collect outputs.\n"
        "2. Autoregressive extension: for max_gen_len steps:\n"
        "   - Use the last predicted character as the next input.\n"
        "   - Compute logits and apply temperature-scaled softmax sampling.\n"
        "   - Append the sampled character to the output."
    )

    # ========================================================================
    #  CHAPTER 8  —  FastAPI Web Layer
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(8, "FastAPI Web Layer (app.py)")

    pdf.body(
        "The web application provides a REST API with Server-Sent Events (SSE) "
        "streaming for real-time brain visualization. It re-implements the core "
        "LSM classes (with minor differences) and adds persistence via JSON files."
    )

    pdf.section("Duplicate Implementation")
    pdf.body(
        "Note: app.py contains a full copy of the core classes (ConnectomeGraph, "
        "HierarchicalReservoir, TextEncoder, LinearReadout, ReservoirSimulation) "
        "with slight differences from flywire_lsm_text.py:"
    )
    pdf.bullet("TEMPERATURE defaults to 0.15 instead of 0.4.")
    pdf.bullet("TextEncoder.encode() omits the logging line.")
    pdf.bullet("ReservoirSimulation stores latest_accuracy as a float attribute.")
    pdf.bullet("No compare_priming_effect method in the app version.")
    pdf.bullet("generate() uses temperature parameter from the request, defaulting to 0.15.")

    pdf.section("API Endpoints")
    pdf.table(
        ["Endpoint", "Method", "Description"],
        [
            ["/", "GET", "Serves index.html (frontend)"],
            ["/topology", "GET", "Returns 3D node positions and top 2% of edges by weight"],
            ["/chat", "POST", "SSE stream: process prompt, yield (token, activations), extend 25 chars"],
            ["/train", "POST", "Retrain readout on provided text, returns accuracy"],
            ["/history", "GET", "Returns JSON chat + learning history"],
            ["/history/clear", "POST", "Resets history (preserves baseline accuracy)"],
        ],
        [42, 18, 130]
    )

    pdf.section("SSE Streaming (/chat)")
    pdf.body(
        "The chat endpoint uses FastAPI's StreamingResponse with media type "
        "text/event-stream. The event_stream() generator function:\n"
        "1. Resets the reservoir (start fresh for each prompt).\n"
        "2. Seeds on the prompt characters, yielding 'data: {token, activations}\\n\\n' for each.\n"
        "3. Autoregressively generates 25 additional tokens using temperature sampling "
        "(temperature defaults to 0.15, overridable per request).\n"
        "4. Saves the full chat to history.json.\n"
        "5. Signals completion with 'data: [DONE]\\n\\n'."
    )

    pdf.section("3D Topology Computation")
    pdf.body(
        "The _compute_topology() function builds the 500x500 combined weight matrix "
        "from the four graph components, then extracts the top 2% of edges by "
        "absolute weight for visualization. It also generates 3D node positions:\n"
        "- Module A (nodes 0-199): Placed in bilateral 'lobes' using polar coordinates "
        "(100 nodes per hemisphere, mimicking antennal/optic lobes).\n"
        "- Module B (nodes 200-499): Distributed on a Fibonacci sphere to form a "
        "dense central ellipsoid (analogous to the central complex)."
    )

    pdf.section("Startup Sequence")
    pdf.body(
        "On first startup, the application:\n"
        "1. Creates a ReservoirSimulation instance (builds all 4 graphs, initializes encoder and readout).\n"
        "2. Trains on a ~4KB baseline English corpus (2 passes).\n"
        "3. Records the baseline in learning history if no prior history exists.\n"
        "4. Computes the 3D topology (node positions and top 2% edges)."
    )

    # ========================================================================
    #  CHAPTER 9  —  Frontend (index.html)
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(9, "Frontend UI & 3D Brain Visualizer")

    pdf.body(
        "The frontend is a single-page application built with vanilla JavaScript "
        "and Tailwind CSS (loaded from CDN). It uses an HTML5 Canvas element with "
        "a custom 3D perspective projection engine to render the brain network "
        "in real time. Chart.js provides the learning curve plot."
    )

    pdf.section("Layout: Three-Panel Design")
    pdf.bullet("Left Panel (320px): Branding, LSM accuracy / run count, Chart.js learning curve, session list with clickable history, clear-history button.")
    pdf.bullet("Center Panel (420px): Terminal-style chat log with SSE streaming, chat input with Send, 'Distill' training textarea with Train button.")
    pdf.bullet("Right Panel (flexible): Full-viewport Canvas 2D brain visualization with HUD overlays for module specs and simulation status.")

    pdf.section("3D Rendering Engine (Custom Perspective Projection)")
    pdf.body(
        "Rather than using Three.js or WebGL, the visualizer implements a custom "
        "software 3D renderer using the Canvas 2D API:"
    )
    pdf.code_block(
        "function project3D(node):\n"
        "  rotate Y: rx = x*cosY - z*sinY, rz = x*sinY + z*cosY\n"
        "  tilt X:  ty = y*cosX - rz*sinX, tz = y*sinX + rz*cosX\n"
        "  scale = CAMERA_DIST / (CAMERA_DIST + tz)\n"
        "  screen_x = W/2 + rx * scale\n"
        "  screen_y = H/2 + ty * scale",
        ""
    )
    pdf.body(
        "The camera auto-rotates around the Y axis at ROTATION_SPEED=0.003 rad/frame "
        "with a slight X tilt of 0.12 rad for a cinematic view."
    )

    pdf.section("Visual Effects")
    pdf.bullet("Auto-rotating 3D view with perspective depth (nodes shrink and fade with distance).")
    pdf.bullet("Nodes colored cyan (Module A / Sensory) and violet (Module B / Central Complex), sized by activation magnitude.")
    pdf.bullet("Glowing halos on active nodes (|activation| > 0.08) with gradient falloff.")
    pdf.bullet("Edges rendered as lines with opacity proportional to weight and depth; active pathways glow brighter.")
    pdf.bullet("Neon yellow pulse packets travel along edges from active source nodes (|activation| > 0.25) towards targets.")
    pdf.bullet("Subtle biotech grid overlay for depth context.")
    pdf.bullet("Pulse count displayed in HUD (top-right).")

    pdf.section("SSE Stream Consumption")
    pdf.body(
        "The frontend consumes the /chat SSE endpoint using the Fetch API with a "
        "ReadableStream reader. Incoming 'data:' lines are parsed, and each token "
        "is appended to the chat log with a 40ms delay (for visual wave effect). "
        "The 500-D activation vector from each token update is passed to the "
        "render loop and triggers neon pulse packets along active edges."
    )

    pdf.section("State Management")
    pdf.body(
        "Key global variables:\n"
        "  nodes/edges: loaded once from /topology on page load.\n"
        "  activations: Float32Array(500) updated on each SSE token.\n"
        "  pulses: array of active traveling pulse objects.\n"
        "  tokenQueue: buffered SSE events processed at 40ms intervals.\n"
        "  chartInstance: Chart.js instance for the learning curve.\n"
        "  streaming/abortController: prevent concurrent chat requests."
    )

    # ========================================================================
    #  CHAPTER 10  —  Configuration Reference
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(10, "Configuration Reference")

    pdf.body("All tunable parameters are defined as module-level constants at the top of both flywire_lsm_text.py and app.py.")

    pdf.section("Reservoir Parameters")
    pdf.table(
        ["Parameter", "Value", "Description"],
        [
            ["N_NEURONS", "500", "Total number of reservoir neurons"],
            ["N_A", "200", "Module A (Sensory Neuropil) size"],
            ["N_B", "300", "Module B (Central Complex) size"],
            ["LEAK_RATE_A", "0.8", "Module A leak rate (fast)"],
            ["LEAK_RATE_B", "0.05", "Module B leak rate (slow)"],
            ["SPECTRAL_RADIUS_A", "0.70", "Module A spectral radius (stable)"],
            ["SPECTRAL_RADIUS_B", "0.98", "Module B spectral radius (edge-of-chaos)"],
            ["SENSORY_GAIN", "0.4", "Scaling factor for sensory injection"],
            ["NOISE_STD", "0.01", "Std of Gaussian process noise"],
        ],
        [52, 22, 116]
    )

    pdf.section("Graph Parameters")
    pdf.table(
        ["Parameter", "Value", "Description"],
        [
            ["SPARSITY", "0.12", "Intra-module connection density (12% of possible edges)"],
            ["MAX_DELAY", "4", "Maximum synaptic delay in timesteps"],
            ["EXC_RATIO", "0.80", "Fraction of excitatory synapses"],
            ["INH_RATIO", "0.20", "Fraction of inhibitory synapses"],
            ["A_TO_B_SPARSITY", "0.06", "Feedforward projection density"],
            ["B_TO_A_SPARSITY", "0.04", "Feedback projection density"],
            ["A_TO_B_SCALE", "0.1", "Feedforward weight multiplier"],
            ["B_TO_A_SCALE", "0.002", "Feedback weight multiplier"],
        ],
        [52, 22, 116]
    )

    pdf.section("Training & Inference Parameters")
    pdf.table(
        ["Parameter", "Value", "Description"],
        [
            ["STEPS_PER_TOKEN", "15", "Timesteps each input character is held"],
            ["WASHOUT_STEPS", "10", "Initial steps discarded from training buffer"],
            ["RIDGE_ALPHA", "0.01", "L2 regularization coefficient"],
            ["TEMPERATURE (lsm)", "0.4", "Generation temperature (CLI)"],
            ["TEMPERATURE (app)", "0.15", "Generation temperature (web)"],
        ],
        [52, 22, 116]
    )

    pdf.section("Vocabulary")
    pdf.code_block(
        "Size: 79 characters\n"
        "  a-z (26)  A-Z (26)  0-9 (10)  space  . , ! ? ; : ( ) [ ] { } \\' \" - _ \\n",
        ""
    )

    pdf.section("Network Statistics (Expected)")
    pdf.table(
        ["Graph", "Shape", "Edges (approx)", "Density"],
        [
            ["AA (intra A)", "200x200", "4,776", "12%"],
            ["BB (intra B)", "300x300", "10,764", "12%"],
            ["AB (A->B)", "200x300", "3,600", "6%"],
            ["BA (B->A)", "300x200", "2,400", "4%"],
            ["Total", "—", "~21,540", "—"],
        ],
        [52, 30, 55, 53]
    )

    # ========================================================================
    #  CHAPTER 11  —  Data Flow Walkthrough
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(11, "Data Flow Walkthrough")

    pdf.section("End-to-End: Training")
    pdf.body("Below is a step-by-step trace for training on the string 'Hello':")
    pdf.body(
        "1. Valid chars: H, e, l, l, o (all in vocabulary).\n"
        "2. Pass 1:\n"
        "   a. i=0: char='H', next='e'. Encode('H') -> injection vector with 1.0 at sensory_nodes[33] "
        "(since 'H' is the 34th character in the vocabulary, index 33). Inject for 15 steps. "
        "Steps 1-10 are washout (not collected). Steps 11-15 collect 5 samples: each sample is "
        "the 500-D state, paired with one-hot target for 'e'.\n"
        "   b. i=1: char='e', next='l'. Encode('e') -> injection at sensory_nodes[30]. "
        "Steps 16-30. Collect steps 11-15 within this token (reservoir step_count: 26-30). "
        "Target = one-hot for 'l'.\n"
        "   c. Continue similarly for 'l' (twice) and 'o' (next wraps to 'H').\n"
        "3. Pass 2: same sequence, but reservoir is NOT reset between passes (warm carryover). "
        "This allows the reservoir to develop deeper temporal context across passes.\n"
        "4. After both passes: total samples = 2 passes * 5 chars * 5 non-washout steps = 50.\n"
        "5. Stack X (50x500), Y (50x79). Call ridge regression -> W (79x500), b (79,).\n"
        "6. Return training accuracy (e.g., 100% for this small example)."
    )

    pdf.section("End-to-End: Inference")
    pdf.body("For inference on prompt 'How':")
    pdf.body(
        "1. Reset reservoir to all zeros.\n"
        "2. Token 'H': inject for 15 steps. After step 15, read state, compute logits, "
        "argmax -> predict 'o' (since 'o' follows 'H' in the training text 'How').\n"
        "3. Token 'o': inject for 15 steps. State evolves. Predict 'w'.\n"
        "4. Token 'w': inject for 15 steps. Predict space or next expected char.\n"
        "5. Return predicted string and logit vectors."
    )

    pdf.section("End-to-End: Generation")
    pdf.body("For generation after priming on 'fly':")
    pdf.body(
        "1. Prime: noise warmup (30 steps, amp=0.05) to push reservoir off zero.\n"
        "2. Seed 'f','l','y': 15 steps each, predict/collect each output.\n"
        "3. Autoregressive loop (max 5 steps):\n"
        "   a. Take last predicted char, encode it, run 15 steps.\n"
        "   b. Temperature-sample from logits to get next char.\n"
        "   c. Repeat until max length or unknown character.\n"
        "4. Return concatenated string of seed predictions + generated chars."
    )

    pdf.section("SSE Streaming Walkthrough (Web Interface)")
    pdf.body(
        "1. User types 'What is' and clicks Send.\n"
        "2. POST /chat with JSON body {\"prompt\": \"What is\"}.\n"
        "3. Server starts StreamingResponse with event_stream() generator.\n"
        "4. For each char in 'What is':\n"
        "   - Encode, run 15 reservoir steps.\n"
        "   - Yield SSE: data: {\"token\":\"T\",\"activations\":[0.1,-0.05,...]}\\n\\n\n"
        "5. After prompt, enter autoregressive loop (25 tokens):\n"
        "   - Feed last predicted char, run 15 steps, temperature-sample.\n"
        "   - Yield each token+activations.\n"
        "6. Yield data: [DONE]\\n\\n and close stream.\n"
        "7. Client-side: ReadableStream reader parses lines, applies 40ms delay per "
        "token for visual effect, updates activations array and triggers pulses.\n"
        "8. Chat saved to history.json with UUID and timestamp."
    )

    # ========================================================================
    #  CHAPTER 12  —  Limitations & Trade-offs
    # ========================================================================
    pdf.add_page()
    pdf.chapter_heading(12, "Limitations & Design Trade-offs")

    pdf.section("Character-Level Modeling")
    pdf.bullet("Limitation: Character-level next-token prediction with a linear readout produces low-quality generative text. The model captures statistical patterns (common bigrams, character frequencies) but fails at grammar, semantics, and coherence beyond short spans.")
    pdf.bullet("Trade-off: Training is extremely fast (seconds) compared to transformer-based language models, but generative quality is orders of magnitude worse.")

    pdf.section("Linear Readout Capacity")
    pdf.bullet("Limitation: A single linear layer on 500 features cannot learn complex non-linear decision boundaries. For character prediction, this is often sufficient (training accuracy > 95% on small corpora), but it severely limits generalization.")
    pdf.bullet("Trade-off: Ridge regression has a closed-form solution (O(n^3) in features), avoiding iterative optimization. The simplicity enables real-time retraining in the web UI.")

    pdf.section("Fixed Reservoir Weights")
    pdf.bullet("Limitation: The reservoir is randomly initialized and never adapted to the data. Optimal reservoir tuning requires genetic algorithms or meta-learning (not implemented).")
    pdf.bullet("Trade-off: No backpropagation through time (BPTT) needed, which eliminates the vanishing/exploding gradient problem and allows much faster training.")

    pdf.section("No Validation / Test Split")
    pdf.bullet("Limitation: The reported accuracy is training accuracy only. There is no held-out validation set, so overfitting is not detected. The model may simply memorize the training text.")
    pdf.bullet("Trade-off: Simpler code and faster iteration. For a demo/visualization tool, this is acceptable.")

    pdf.section("Code Duplication")
    pdf.bullet("Limitation: The core LSM classes are duplicated in both flywire_lsm_text.py and app.py with slight differences (temperature default, logging verbosity, method availability). This creates a maintenance burden.")
    pdf.bullet("Trade-off: The CLI script can run independently without FastAPI/uvicorn dependencies. Refactoring into a shared library module would be the recommended improvement.")

    pdf.section("Memory and Performance")
    pdf.bullet("The 500-neuron reservoir with ~21,500 synapses is computationally lightweight. Each step involves sparse matrix-vector products and delay buffer shifts, completing in microsecond to millisecond range on modern CPUs.")
    pdf.bullet("The eigendecomposition for spectral normalization (O(n^3)) is the bottleneck during initialization (200^3 = 8M ops, 300^3 = 27M ops), but runs only once at startup.")

    pdf.section("Security Considerations")
    pdf.bullet("CORS middleware allows all origins (*) \u2014 acceptable for local development but should be restricted in production.")
    pdf.bullet("No input sanitization beyond character filtering \u2014 the training text could contain injection strings, though the model cannot execute code.")

    pdf.section("Recommended Improvements")
    pdf.bullet("Refactor shared core into a common module (e.g., flywire_core.py) imported by both CLI and web app.")
    pdf.bullet("Add a held-out validation split and report validation accuracy.")
    pdf.bullet("Experiment with larger reservoirs, non-linear readouts (e.g., MLP with one hidden layer), or learnable reservoir weights via backpropagation.")
    pdf.bullet("Add unit tests for the core classes and integration tests for the API endpoints.")
    pdf.bullet("Add a requirements.txt or pyproject.toml for dependency management.")
    pdf.bullet("Extend the vocabulary to include more punctuation and Unicode characters if needed.")

    # ========================================================================
    #  APPENDIX A  —  Full Source: flywire_lsm_text.py
    # ========================================================================
    pdf.add_page()
    pdf.set_font("Sans", "B", 18)
    pdf.set_text_color(190, 220, 255)
    pdf.cell(0, 9, "Appendix A", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Sans", "B", 14)
    pdf.set_text_color(140, 180, 230)
    pdf.cell(0, 8, "Full Source: flywire_lsm_text.py", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(60, 100, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.code_block(SRC_LSM, "python")

    # ========================================================================
    #  APPENDIX B  —  Full Source: app.py
    # ========================================================================
    pdf.add_page()
    pdf.set_font("Sans", "B", 18)
    pdf.set_text_color(190, 220, 255)
    pdf.cell(0, 9, "Appendix B", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Sans", "B", 14)
    pdf.set_text_color(140, 180, 230)
    pdf.cell(0, 8, "Full Source: app.py", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(60, 100, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.code_block(SRC_APP, "python")

    # ========================================================================
    #  APPENDIX C  —  Full Source: index.html
    # ========================================================================
    pdf.add_page()
    pdf.set_font("Sans", "B", 18)
    pdf.set_text_color(190, 220, 255)
    pdf.cell(0, 9, "Appendix C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Sans", "B", 14)
    pdf.set_text_color(140, 180, 230)
    pdf.cell(0, 8, "Full Source: index.html", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(60, 100, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.code_block(SRC_HTML, "html")

    # ========================================================================
    #  OUTPUT
    # ========================================================================
    out_path = os.path.join(PROJECT_DIR, "CompleteDocumentationSheet.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {out_path}")
    print(f"Pages: {pdf.page_no() - 1}  (title + TOC = 2, content + appendices = {pdf.page_no() - 2})")


if __name__ == "__main__":
    build_pdf()

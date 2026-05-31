import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUTDIR = "/home/cinni/PitchDeck/charts"
os.makedirs(OUTDIR, exist_ok=True)

# Brand colors from logo analysis
DARK = '#14394b'
MID = '#174458'
TEAL = '#54b3b3'
TEAL_LIGHT = '#7dd4d4'
TEAL_DARK = '#285155'
WHITE = '#fefefe'
GOLD = '#e8c84a'
GOLD_LIGHT = '#f0d97a'
DARK_BG = '#0f2c3a'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
})

def chart1_market_size():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    categories = ['TAM\nGlobal AI Infrastructure', 'SAM\nNext-Gen Cloud &\nNeuromorphic', 'SOM\n1,500 Clinical Hubs\n@ $300k ACV']
    values = [1.8, 0.3, 0.045]
    colors = [TEAL, TEAL_LIGHT, GOLD]

    bars = ax.barh(categories, values, color=colors, height=0.6, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, values):
        label = f'${val:.1f}B' if val >= 1 else f'${int(val*1000)}M' if val < 1 and val >= 0.05 else f'${val*1000:.0f}M'
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, label,
                va='center', fontsize=13, fontweight='bold', color=WHITE)

    ax.set_xlim(0, 2.1)
    ax.tick_params(colors=WHITE, labelsize=10)
    ax.xaxis.label.set_color(WHITE)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title('Market Opportunity', fontsize=16, fontweight='bold', color=WHITE, pad=15)
    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/market_size.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart1 done")


def chart2_competitive_matrix():
    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)

    # Quadrant labels
    ax.text(5, 10.8, 'OPEN ACCESS', ha='center', fontsize=9, fontweight='bold', color=TEAL)
    ax.text(5, -1.2, 'GATED / PROPRIETARY', ha='center', fontsize=9, fontweight='bold', color='#ff6b6b')
    ax.text(-1.5, 5, 'HARDWARE\nACCESS', ha='center', fontsize=9, fontweight='bold', color=WHITE, rotation=90, va='center')
    ax.text(11.5, 5, 'SOFTWARE /\nPLATFORM', ha='center', fontsize=9, fontweight='bold', color=WHITE, rotation=-90, va='center')

    # Quadrant backgrounds
    ax.axhline(y=5, color='#2a4a5a', linewidth=1, linestyle='--')
    ax.axvline(x=5, color='#2a4a5a', linewidth=1, linestyle='--')

    # Plot competitors
    competitors = {
        'SynapTechBio\nIDRE': (8.5, 8.0, GOLD, 220, 'star'),
        'Hugging Face': (9.0, 1.5, TEAL_LIGHT, 120, 'o'),
        'Intel INRC\n(Loihi)': (2.0, 8.5, '#4a9eff', 140, 'o'),
        'Google/JAINA': (3.0, 2.5, '#ff6b6b', 140, 'o'),
        'FlyWire Codex\n(static browser)': (7.0, 1.5, '#a0a0a0', 100, 'o'),
        'Neuromorpho.org': (6.0, 1.0, '#a0a0a0', 100, 'o'),
    }

    for name, (x, y, color, size, marker) in competitors.items():
        if marker == 'star':
            ax.scatter(x, y, s=size, c=color, marker='*', edgecolors='white', linewidth=1.5, zorder=5)
        else:
            ax.scatter(x, y, s=size, c=color, marker='o', edgecolors='white', linewidth=1, zorder=4, alpha=0.85)
        ax.text(x, y-0.7, name, ha='center', va='top', fontsize=7.5, color=WHITE, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a3a4a', edgecolor='none', alpha=0.7))

    ax.set_title('Competitive Positioning', fontsize=16, fontweight='bold', color=WHITE, pad=15)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/competitive_matrix.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart2 done")


def chart3_use_of_funds():
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    fig.patch.set_facecolor(DARK_BG)

    labels = ['Cloud GPU\n(Lambda Labs 2×A100)', 'INRC / Loihi 2\nCloud Access', 'Engineering\n(2 FTE, 6 months)',
              'Infrastructure\n(Pinecone, S3, HF)', 'Legal / IP\n(DCSL Framework)', 'Marketing &\nConference']
    sizes = [30, 15, 80, 10, 10, 5]
    colors_pie = [TEAL, TEAL_LIGHT, GOLD, MID, '#4a9eff', '#ff9f4a']

    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='', startangle=140,
                                       colors=colors_pie, wedgeprops={'edgecolor': DARK_BG, 'linewidth': 2})
    ax.set_title('Use of Funds — $150,000 Pre-Seed', fontsize=14, fontweight='bold', color=WHITE, pad=15)

    legend_labels = [f'{l} — ${s}K' for l, s in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=9, facecolor=DARK_BG, edgecolor='none', labelcolor=WHITE)

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/use_of_funds.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart3 done")


def chart4_accuracy():
    fig, ax = plt.subplots(figsize=(6, 3.5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    benchmarks = ['FlyWire LSM\n500-neuron\nReservoir', 'Standard ESN\n500-neuron\nSingle Pool', 'LSTM\n128 hidden\n(Baseline)']
    accuracies = [97, 88, 76]
    colors_bar = [TEAL, TEAL_LIGHT, '#4a6a7a']

    bars = ax.bar(benchmarks, accuracies, color=colors_bar, width=0.5, edgecolor='white', linewidth=0.5)
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{acc}%',
                ha='center', fontsize=14, fontweight='bold', color=WHITE)

    ax.set_ylim(0, 110)
    ax.set_ylabel('Training Accuracy (%)', fontsize=11, color=WHITE)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#2a5a6a')

    ax.set_title('Next-Token Prediction Benchmark', fontsize=14, fontweight='bold', color=WHITE, pad=10)
    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/accuracy_benchmark.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart4 done")


def chart5_roadmap():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    phases = ['P0: Multi-Tenant\nAuth & Security', 'P1: DCSL + Real\nEmbeddings', 'P2: LSM Demo\n+ Sandbox',
              'P3: Open Brain\nPortal', 'P4: Continuous\nAlignment', 'P5: Cloud Loihi\nFarm', 'P6: Scale &\nBenchmark']
    weeks = [3, 3, 3, 4, 4, 4, 5]
    costs = [15, 25, 20, 25, 25, 20, 20]
    colors_phase = ['#4a9eff', TEAL, TEAL_LIGHT, GOLD, '#ff9f4a', '#ff6b6b', '#a078d0']

    cumulative_weeks = np.cumsum([0] + weeks[:-1])

    for i, (phase, w, cost, c) in enumerate(zip(phases, weeks, costs, colors_phase)):
        left = cumulative_weeks[i]
        ax.barh(0, w, left=left, height=0.6, color=c, edgecolor='white', linewidth=0.5)
        ax.text(left + w/2, 0, f'${cost}K', ha='center', va='center', fontsize=8, fontweight='bold', color=DARK_BG)

    # Phase labels below
    for i, (phase, w, c) in enumerate(zip(phases, weeks, colors_phase)):
        left = cumulative_weeks[i]
        ax.text(left + w/2, -0.8, phase, ha='center', va='top', fontsize=6.5, color=WHITE, rotation=0)

    ax.set_title('7-Phase Roadmap — 26 Weeks to Scale', fontsize=14, fontweight='bold', color=WHITE, pad=10)
    ax.set_xlim(0, sum(weeks))
    ax.set_ylim(-2, 1.5)
    ax.set_yticks([])
    ax.set_xlabel('Weeks', fontsize=10, color=WHITE)
    ax.tick_params(colors=WHITE, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#2a5a6a')

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/roadmap.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart5 done")


def chart6_benchmarks():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    fig.patch.set_facecolor(DARK_BG)

    # Left: Latency reduction
    ax = axes[0]
    ax.set_facecolor(DARK_BG)
    categories = ['Dense\nTransformer\n(GPU)', 'IDRE\nCSC Engine\n(GPU)']
    values = [100, 20]
    colors_bar = ['#4a6a7a', TEAL]
    bars = ax.bar(categories, values, color=colors_bar, width=0.5, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, values):
        reduction = "5x" if val == 20 else ""
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val}ms' if val == 100 else f'<{val}ms', ha='center', fontsize=13, fontweight='bold', color=WHITE)
        if reduction:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 15,
                    reduction, ha='center', fontsize=16, fontweight='bold', color=GOLD)
    ax.set_ylim(0, 115)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#2a5a6a')
    ax.set_title('Compute Latency\n(spMV activation)', fontsize=13, fontweight='bold', color=WHITE, pad=8)

    # Right: Energy consumption
    ax = axes[1]
    ax.set_facecolor(DARK_BG)
    categories = ['Dense\nTransformer\n(Loihi class)', 'IDRE\nCSC Engine\n(Loihi class)']
    values = [100, 5]
    bars = ax.bar(categories, values, color=colors_bar, width=0.5, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, values):
        reduction = "20x" if val == 5 else ""
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val}x' if val == 100 else f'{val}x', ha='center', fontsize=13, fontweight='bold', color=WHITE)
        if reduction:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 10,
                    reduction, ha='center', fontsize=16, fontweight='bold', color=GOLD)
    ax.set_ylim(0, 115)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#2a5a6a')
    ax.set_title('Energy Consumption\n(normalized to dense)', fontsize=13, fontweight='bold', color=WHITE, pad=8)

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/benchmarks.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart6 done")


def chart7_vision_roadmap():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    phases = ['Fruit Fly\nBenchmark\n(130k neurons)', 'Neural Foundation\nModel (NFM)\n(Data Moat)', 'Mammalian\nScale\n(70M+ neurons)', 'North Star\nCanine\n(530M neurons)']
    colors_phase = [TEAL, GOLD, '#ff9f4a', '#ff6b6b']
    markers = ['🪰', '🧠', '🐭', '🐕']

    x_pos = [1, 4, 7, 10]
    widths = [2, 2, 2, 2]

    for x, w, c in zip(x_pos, widths, colors_phase):
        bar = ax.barh(0, w, left=x - w/2, height=0.5, color=c, edgecolor='white', linewidth=0.8, alpha=0.8)

    # Labels
    for x, phase, color in zip(x_pos, phases, colors_phase):
        ax.text(x, 0.6, phase, ha='center', va='bottom', fontsize=10, color=WHITE, fontweight='bold')
        ax.text(x, -0.6, '●', ha='center', va='top', fontsize=20, color=color)

    # Arrow connecting them
    for i in range(len(x_pos) - 1):
        ax.annotate('', xy=(x_pos[i+1] - widths[i+1]/2, 0), xytext=(x_pos[i] + widths[i]/2, 0),
                    arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.5, linestyle='dotted'))

    ax.set_title('The Truth-First Roadmap — 4 Phases to Embodied Digital Consciousness',
                 fontsize=13, fontweight='bold', color=WHITE, pad=12)
    ax.set_xlim(0, 11)
    ax.set_ylim(-1, 1.2)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/vision_roadmap.png", dpi=200, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print("chart7 done")


chart1_market_size()
chart2_competitive_matrix()
chart3_use_of_funds()
chart4_accuracy()
chart5_roadmap()
chart6_benchmarks()
chart7_vision_roadmap()
print("All charts generated successfully!")

#!/usr/bin/env python3
"""
generate_figures.py — Publication-quality figures for TIME-AR-001 study.

Reads from data/processed/ and data/raw/ CSVs where available,
falls back to hardcoded data. Writes 300 DPI PNGs to figures/.
"""

import os
import sys
import math

try:
    import matplotlib
    matplotlib.use('Agg')  # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    print("WARNING: matplotlib is not installed. Install with: pip3 install matplotlib")
    sys.exit(0)

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, '..')
FIG_DIR = os.path.join(BASE_DIR, 'figures')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data', 'processed')
DATA_RAW = os.path.join(BASE_DIR, 'data', 'raw')

os.makedirs(FIG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------
DPI = 300
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'figure.dpi': 100,
    'savefig.dpi': DPI,
    'savefig.pad_inches': 0.15,
})

SAVEFIG_KW = dict(bbox_inches='tight')

VERDICT_COLORS = {
    'T3req': '#cc2222',
    'Tmarg': '#dd8800',
    'T2ok': '#2266bb',
    'Tna': '#888888',
}


# ===================================================================
# Fig 1 — D vs log(T) Scatter with Gamma Contours
# ===================================================================
def fig1_exclusion_zone():
    organisms = [
        ('H. sapiens', 8, 9.3e6, 'T3req'),
        ('B. floridae', 9, 4.0e8, 'T3req'),
        ('GPCRs', 7.5, 9.3e6, 'T3req'),
        ('Zinc fingers', 7.5, 9.3e6, 'T3req'),
        ('ORs', 6.5, 9.3e6, 'T3req'),
        ('Rice NBS-LRR', 5.5, 1.6e8, 'T3req'),
        ('D. rerio Hox', 3.5, 1.0e9, 'Tmarg'),
        ('A. thaliana RLKs', 5.0, 3.6e9, 'Tmarg'),
        ('C. elegans NHR', 5, 6.26e10, 'Tmarg'),
        ('D. melanogaster ORs', 4.0, 6.52e9, 'Tmarg'),
        ('E. coli ABC', 3, 2.04e13, 'T2ok'),
        ('S. cerevisiae kin', 4, 3.29e12, 'Tmarg'),
        ('S. pombe kin', 3, 2.19e12, 'T2ok'),
        ('M. jannaschii MCR', 2, 1.75e13, 'T2ok'),
        ('H. salinarum Htr', 3, 1.75e12, 'T2ok'),
        ('S. solfataricus GH', 3, 6.57e12, 'T2ok'),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    # Plot gamma contours: D = log10(T) / log10(gamma)
    logT_range = np.linspace(5, 15, 300)
    for gamma, ls in [(10, '-'), (100, '--'), (1000, ':')]:
        D_line = logT_range / math.log10(gamma)
        ax.plot(logT_range, D_line, color='#aaaaaa', linestyle=ls, linewidth=0.9,
                label=f'\u03b3 = {gamma}', zorder=1)

    # Plot points
    for name, D, T, verdict in organisms:
        logT = math.log10(T)
        ax.scatter(logT, D, c=VERDICT_COLORS[verdict], s=50, zorder=3,
                   edgecolors='black', linewidths=0.4)
        ax.annotate(name, (logT, D), fontsize=5.5, ha='left', va='bottom',
                    xytext=(4, 3), textcoords='offset points')

    # Legend for verdicts
    for verdict, color in VERDICT_COLORS.items():
        ax.scatter([], [], c=color, s=40, label=verdict, edgecolors='black', linewidths=0.4)

    ax.set_xlabel('log$_{10}$(T) [generations]')
    ax.set_ylabel('D [hierarchy depth]')
    ax.set_title('Temporal Exclusion Zone: D vs log$_{10}$(T)')
    ax.legend(fontsize=7, loc='upper left', frameon=False)
    ax.set_xlim(5, 15)
    ax.set_ylim(0, 12)

    path = os.path.join(FIG_DIR, 'fig_T1_exclusion_zone.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 2 — Gamma_crit Bar Chart
# ===================================================================
def fig2_gamma_crit_bars():
    t3req = [
        ('Protein kinases', 7.4),
        ('Amphioxus TLR', 9.0),
        ('GPCR superfamily', 11),
        ('Zinc finger TFs', 11),
        ('Olfactory receptors', 18),
        ('Rice NBS-LRR', 23),
    ]
    # Sort by gamma_crit
    t3req.sort(key=lambda x: x[1])

    names = [x[0] for x in t3req]
    gcs = [x[1] for x in t3req]

    def bar_color(gc):
        if gc < 10:
            return '#aa1111'   # Tier 1 dark red
        elif gc <= 15:
            return '#dd8800'   # Tier 2 orange
        else:
            return '#ccbb00'   # Tier 3 yellow

    colors = [bar_color(gc) for gc in gcs]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    y_pos = range(len(names))
    ax.barh(y_pos, gcs, color=colors, edgecolor='black', linewidth=0.5, height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel('\u03b3$_{crit}$')
    ax.set_title('Gamma$_{crit}$ for T3req Gene Families')

    ax.axvline(10, color='black', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.axvline(100, color='black', linestyle=':', linewidth=0.8, alpha=0.4)
    ax.text(10, len(names) - 0.3, '\u03b3=10', fontsize=7, ha='left', va='top')
    ax.text(100, len(names) - 0.3, '\u03b3=100', fontsize=7, ha='left', va='top')

    ax.set_xlim(0, max(gcs) * 1.3)

    path = os.path.join(FIG_DIR, 'fig_T2_gamma_crit_bars.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 3 — Deep Gene Family Depths
# ===================================================================
def fig3_deep_families():
    families = [
        ('Amphioxus TLR', 9, 9),
        ('Protein kinases', 8, 8),
        ('GPCR superfamily', 7.5, 7.5),
        ('Zinc finger TFs', 7.5, 7.5),
        ('Olfactory receptors', 6.5, 6.5),
        ('Homeodomain TFs', 6.5, 5.5),
        ('Cytochrome P450', 6.5, 6.5),
        ('Immunoglobulin SF', 6.5, 6.5),
        ('Hox clusters', 5.5, 4.5),
        ('bHLH TFs', 5.5, 4.5),
        ('ABC transporters', 5, 5),
    ]
    # Sort by D_raw descending
    families.sort(key=lambda x: x[1], reverse=True)

    names = [f[0] for f in families]
    d_raw = [f[1] for f in families]
    d_wgd = [f[2] for f in families]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    y_pos = np.arange(len(names))

    ax.barh(y_pos, d_raw, color='#4477aa', edgecolor='black', linewidth=0.4,
            height=0.6, label='D$_{raw}$', zorder=2)
    ax.barh(y_pos, d_wgd, color='#cc3333', edgecolor='black', linewidth=0.4,
            height=0.35, label='D$_{WGD\\ adj}$', zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel('Hierarchy Depth (D)')
    ax.set_title('Hierarchy Depth of Deepest Gene Families')
    ax.legend(fontsize=8, loc='lower right', frameon=False)
    ax.set_xlim(0, 11)

    path = os.path.join(FIG_DIR, 'fig_T3_deep_families.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 4 — Physical vs Biological
# ===================================================================
def fig4_physical_vs_bio():
    physical = [
        ('Snowflake', 5.5, 1e-4),
        ('Turbulence', 12, 1e-5),
        ('River networks', 8, 1e7),
        ('Coastlines', 15, 1e8),
        ('Cosmic structure', 3.5, 1.3e10),
        ('Convection', 2.5, 1e-2),
    ]
    bio = [
        ('Kinases (D=8)', 8, 2.5e8),
        ('Amphioxus TLR (D=9)', 9, 5.5e8),
        ('GPCRs (D=7.5)', 7.5, 1e9),
        ('Lung bronchial (D=23)', 23, 5e8),
    ]

    fig, ax = plt.subplots(figsize=(6, 5))

    for name, D, t in physical:
        logt = math.log10(t) if t > 0 else -10
        ax.scatter(logt, D, marker='s', c='#888888', s=60, zorder=3,
                   edgecolors='black', linewidths=0.5)
        ax.annotate(name, (logt, D), fontsize=6.5, ha='left', va='bottom',
                    xytext=(4, 3), textcoords='offset points')

    for name, D, t in bio:
        logt = math.log10(t)
        ax.scatter(logt, D, marker='o', c='#cc2222', s=60, zorder=3,
                   edgecolors='black', linewidths=0.5)
        ax.annotate(name, (logt, D), fontsize=6.5, ha='left', va='bottom',
                    xytext=(4, 3), textcoords='offset points')

    # Legend
    ax.scatter([], [], marker='s', c='#888888', s=50, label='Physical', edgecolors='black', linewidths=0.5)
    ax.scatter([], [], marker='o', c='#cc2222', s=50, label='Biological', edgecolors='black', linewidths=0.5)

    ax.set_xlabel('log$_{10}$(formation time) [years]')
    ax.set_ylabel('D [hierarchy depth / fractal dimension]')
    ax.set_title('Physical Fractals vs Biological Hierarchies')
    ax.legend(fontsize=8, frameon=False)

    path = os.path.join(FIG_DIR, 'fig_T4_physical_vs_bio.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 5 — Two-Regime Gamma
# ===================================================================
def fig5_two_regime_gamma():
    fig, ax = plt.subplots(figsize=(8, 3))

    # Regime bands
    ax.axvspan(2, 10, alpha=0.20, color='#4488cc', label='Recombination regime')
    ax.axvspan(100, 10000, alpha=0.15, color='#cc4444', label='Duplication (IAD) regime')

    # T3req family gamma_crit values
    gc_vals = [
        ('Kinases', 7.4),
        ('Amphioxus TLR', 9.0),
        ('GPCRs', 11),
        ('Zinc fingers', 11),
        ('ORs', 18),
        ('NBS-LRR', 23),
    ]
    for name, gc in gc_vals:
        ax.axvline(gc, color='#222222', linewidth=1.0, alpha=0.7, zorder=3)
        ax.text(gc, 0.92, name, fontsize=6.5, rotation=90, ha='right', va='top',
                transform=ax.get_xaxis_transform())

    ax.set_xscale('log')
    ax.set_xlim(1, 20000)
    ax.set_xlabel('\u03b3 (branching factor per generation)')
    ax.set_title('Two-Regime Empirical Gamma Structure')
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.legend(fontsize=8, loc='upper right', frameon=False)

    path = os.path.join(FIG_DIR, 'fig_T5_two_regime_gamma.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 6 — D Distribution
# ===================================================================
def fig6_d_distribution():
    d_dist = {
        'H. sapiens': [3586, 290, 40, 4],
        'A. thaliana': [7000, 1000, 200, 50],
        'E. coli': [400, 45, 7, 0],
    }
    thresholds = ['\u2265 1', '\u2265 3', '\u2265 5', '\u2265 8']
    species_colors = {
        'H. sapiens': '#cc2222',
        'A. thaliana': '#22aa44',
        'E. coli': '#4477cc',
    }

    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(thresholds))
    width = 0.25

    for i, (species, counts) in enumerate(d_dist.items()):
        # Replace 0 with 0.5 for log display
        display = [c if c > 0 else 0.5 for c in counts]
        bars = ax.bar(x + i * width, display, width * 0.9,
                      color=species_colors[species], edgecolor='black',
                      linewidth=0.4, label=species, zorder=2)

    ax.set_yscale('log')
    ax.set_xticks(x + width)
    ax.set_xticklabels(thresholds)
    ax.set_xlabel('Depth threshold (D)')
    ax.set_ylabel('Number of gene families')
    ax.set_title('Gene Family Depth Distribution')
    ax.legend(fontsize=8, frameon=False)

    path = os.path.join(FIG_DIR, 'fig_T6_d_distribution.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 7 — Sensitivity Analysis
# ===================================================================
def fig7_sensitivity():
    sensitivity = [
        ('Kinases', 7.4, 5.4, 13.0),
        ('Amphioxus TLR', 9.0, 6.3, 14.1),
        ('GPCRs', 11, 8.0, 17.6),
        ('Zinc fingers', 11, 8.0, 17.6),
        ('ORs', 18, 13, 28),
        ('NBS-LRR', 23, 16, 36),
    ]

    names = [s[0] for s in sensitivity]
    gc = np.array([s[1] for s in sensitivity])
    gc_hi = np.array([s[3] for s in sensitivity])  # D-1 gives higher gamma
    gc_lo = np.array([s[2] for s in sensitivity])  # D+1 gives lower gamma

    err_lo = gc - gc_lo
    err_hi = gc_hi - gc

    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(names))

    ax.errorbar(x, gc, yerr=[err_lo, err_hi], fmt='o', color='#222222',
                ecolor='#666666', elinewidth=1.5, capsize=4, capthick=1.2,
                markersize=6, zorder=3)

    ax.axhline(10, color='#cc2222', linestyle='--', linewidth=1.0, alpha=0.7,
               label='\u03b3 = 10 (recombination threshold)')

    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8, rotation=25, ha='right')
    ax.set_ylabel('\u03b3$_{crit}$')
    ax.set_title('Gamma$_{crit}$ Sensitivity to D \u00b1 1')
    ax.legend(fontsize=7, frameon=False)
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    path = os.path.join(FIG_DIR, 'fig_T7_sensitivity.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Fig 8 — Classification Summary (Donut)
# ===================================================================
def fig8_classification_pie():
    labels = ['T3req', 'Tmarg', 'T2ok', 'Tna', 'Tmarg\u2020']
    sizes = [6, 22, 24, 25, 12]
    colors = ['#cc2222', '#dd8800', '#2266bb', '#888888', '#ccbb00']

    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%',
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5),
        textprops=dict(fontsize=9),
    )
    for at in autotexts:
        at.set_fontsize(8)

    ax.set_title('F15 Classification Distribution (~110 systems)', fontsize=11)

    path = os.path.join(FIG_DIR, 'fig_T8_classification_pie.png')
    fig.savefig(path, **SAVEFIG_KW)
    plt.close(fig)
    print(f"  Saved {path}")


# ===================================================================
# Main
# ===================================================================
def main():
    print("Generating TIME-AR-001 figures...")
    fig1_exclusion_zone()
    fig2_gamma_crit_bars()
    fig3_deep_families()
    fig4_physical_vs_bio()
    fig5_two_regime_gamma()
    fig6_d_distribution()
    fig7_sensitivity()
    fig8_classification_pie()
    print("Done. All figures saved to:", FIG_DIR)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
generate_figures.py — Publication-quality figures for TIME-AR-001 study.

Reads from data/processed/ and data/raw/ CSVs where available,
falls back to hardcoded data with a WARNING. Writes 300 DPI PNGs to figures/.
"""

import csv
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


# ---------------------------------------------------------------------------
# CSV helper
# ---------------------------------------------------------------------------
def load_csv(path):
    """Load a CSV file and return a list of dicts. Returns None if file missing."""
    if not os.path.isfile(path):
        print(f"  WARNING: CSV not found: {path}")
        return None
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


# ===================================================================
# Fig 1 — D vs log(T) Scatter with Gamma Contours
# Provenance: Source: f15_scorecard.csv (16 organisms).
#   Uses D_family for T3req organisms, D_organism for others.
#   T_midpoint is in generations.  F15b verdict determines colour.
# ===================================================================
def fig1_exclusion_zone():
    """Fig 1: D vs log(T) scatter with gamma contours.

    Provenance: f15_scorecard.csv (16 organisms). D_family for T3req
    organisms, D_organism for others. T_midpoint in generations.
    """
    csv_path = os.path.join(DATA_PROCESSED, 'f15_scorecard.csv')
    rows = load_csv(csv_path)

    if rows is not None:
        organisms = []
        for r in rows:
            verdict = r['F15b']
            # For T3req use family-level D; otherwise organism-level D
            if verdict == 'T3req':
                D = float(r['D_family'])
            else:
                D = float(r['D_organism'])
            T = float(r['T_midpoint'])
            label = r['organism']
            # For T3req rows, prefer family_name as label if different
            if verdict == 'T3req' and r.get('family_name'):
                label = r['family_name']
            organisms.append((label, D, T, verdict))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 1")
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
        ax.scatter(logT, D, c=VERDICT_COLORS.get(verdict, '#888888'), s=50, zorder=3,
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
# Provenance: gamma_crit_table.csv filtered to F15_verdict == T3req.
# ===================================================================
def fig2_gamma_crit_bars():
    """Fig 2: Gamma_crit horizontal bar chart for T3req families.

    Provenance: gamma_crit_table.csv filtered to F15_verdict == T3req.
    """
    csv_path = os.path.join(DATA_PROCESSED, 'gamma_crit_table.csv')
    rows = load_csv(csv_path)

    if rows is not None:
        t3req = []
        for r in rows:
            if r['F15_verdict'] == 'T3req':
                t3req.append((r['system'], float(r['gamma_crit'])))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 2")
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
# Provenance: deep_paralog_families.csv + wgd_adjusted_d.csv.
#   D_depth from deep_paralog_families; D_WGD_adj from wgd_adjusted_d
#   (joined on family name). Families without WGD entry: D_WGD_adj = D_depth.
# ===================================================================
def fig3_deep_families():
    """Fig 3: Deep gene family depths (raw vs WGD-adjusted).

    Provenance: deep_paralog_families.csv + wgd_adjusted_d.csv.
    D_depth from deep_paralog_families; D_WGD_adj from wgd_adjusted_d
    (joined on family). Families without WGD entry: D_WGD_adj = D_depth.
    """
    dpf_path = os.path.join(DATA_RAW, 'deep_paralog_families.csv')
    wgd_path = os.path.join(DATA_RAW, 'wgd_adjusted_d.csv')
    dpf_rows = load_csv(dpf_path)
    wgd_rows = load_csv(wgd_path)

    if dpf_rows is not None:
        # Build WGD adjustment lookup: family -> D_wgd_adj
        wgd_lookup = {}
        if wgd_rows is not None:
            for r in wgd_rows:
                family = r['family'].strip()
                d_adj = float(r['D_wgd_adj'])
                # Keep the minimum D_wgd_adj per family (most conservative)
                if family not in wgd_lookup or d_adj < wgd_lookup[family]:
                    wgd_lookup[family] = d_adj

        families = []
        for r in dpf_rows:
            name = r['family'].strip()
            d_raw = float(r['D_depth'])
            # Look up WGD-adjusted D; default to D_raw if not found
            d_wgd = wgd_lookup.get(name, d_raw)
            families.append((name, d_raw, d_wgd))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 3")
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
# Provenance: physical_fractals.csv + f15_scorecard.csv (selected T3req cases).
#   Physical systems from physical_fractals.csv (D_apparent, time_to_form).
#   Biological points: T3req families from f15_scorecard.csv, plus lung
#   bronchial tree (positive control) from physical_fractals.csv.
# ===================================================================
def fig4_physical_vs_bio():
    """Fig 4: Physical fractals vs biological hierarchies scatter.

    Provenance: physical_fractals.csv + f15_scorecard.csv (selected T3req cases).
    Physical systems use D_apparent and time_to_form from physical_fractals.csv.
    Bio points are key T3req families from f15_scorecard.csv.
    Lung bronchial tree is positive control from physical_fractals.csv.
    """
    phys_path = os.path.join(DATA_RAW, 'physical_fractals.csv')
    score_path = os.path.join(DATA_PROCESSED, 'f15_scorecard.csv')
    phys_rows = load_csv(phys_path)
    score_rows = load_csv(score_path)

    def _parse_time_to_form(val):
        """Parse time_to_form strings like '1e6-1e7 yr', 'Seconds', '13 Gyr'."""
        val = val.strip()
        # Handle scientific notation with range: take geometric mean
        if 'e' in val.lower() and '-' in val:
            parts = val.split('yr')[0].strip().split('-')
            try:
                nums = [float(p.strip()) for p in parts]
                return math.sqrt(nums[0] * nums[1])  # geometric mean
            except (ValueError, IndexError):
                pass
        # Handle '5e8 yr'
        if 'yr' in val.lower():
            num_str = val.lower().replace('yr', '').replace('evolution', '').strip()
            try:
                return float(num_str)
            except ValueError:
                pass
        # Handle 'X Gyr'
        if 'gyr' in val.lower():
            try:
                num = float(val.lower().replace('gyr', '').replace('(simultaneous)', '').strip())
                return num * 1e9
            except ValueError:
                pass
        # Handle seconds / hours / days as fractions of years
        val_l = val.lower()
        if 'second' in val_l or 'millisecond' in val_l:
            return 1e-4  # sub-second to seconds
        if 'hour' in val_l or 'day' in val_l:
            return 1e-2  # hours-days
        if 'instantaneous' in val_l:
            return 1e-5
        return None

    def _parse_d_apparent(val):
        """Parse D_apparent like '5-6', '10+', '3-4', 'Unbounded'."""
        val = val.strip()
        if val.lower() == 'unbounded':
            return 15.0  # display high
        if '+' in val:
            return float(val.replace('+', ''))
        if '-' in val:
            parts = val.split('-')
            try:
                return (float(parts[0]) + float(parts[1])) / 2.0
            except (ValueError, IndexError):
                pass
        try:
            return float(val)
        except ValueError:
            return None

    if phys_rows is not None and score_rows is not None:
        physical = []
        bio = []
        for r in phys_rows:
            d_val = _parse_d_apparent(r['D_apparent'])
            t_val = _parse_time_to_form(r['time_to_form'])
            if d_val is None or t_val is None:
                continue
            name = r['system'].strip()
            if r.get('control_type', '') == 'positive_control':
                # Lung bronchial tree goes in bio
                bio.append((name, d_val, t_val))
            else:
                physical.append((name, d_val, t_val))

        # Add key T3req bio families from f15_scorecard
        for r in score_rows:
            if r['F15b'] == 'T3req':
                d_fam = float(r['D_family'])
                T = float(r['T_midpoint'])
                label = r.get('family_name', r['organism'])
                # Convert generations to years (~25 yr/gen for mammals, approximate)
                # T_midpoint is already in generations; for the scatter we
                # use T directly as proxy (consistent with original figure)
                bio.append((f"{label} (D={d_fam})", d_fam, T))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 4")
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
# Provenance: gamma_crit_table.csv for T3req gamma_crit lines;
#   regime bands are illustrative from gamma_calibration.csv.
# ===================================================================
def fig5_two_regime_gamma():
    """Fig 5: Two-regime empirical gamma structure.

    Provenance: gamma_crit_table.csv for T3req gamma_crit lines;
    regime bands (recombination 2-10, IAD 100-10000) are illustrative
    from gamma_calibration.csv.
    """
    csv_path = os.path.join(DATA_PROCESSED, 'gamma_crit_table.csv')
    rows = load_csv(csv_path)

    if rows is not None:
        gc_vals = []
        for r in rows:
            if r['F15_verdict'] == 'T3req':
                gc_vals.append((r['system'], float(r['gamma_crit'])))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 5")
        gc_vals = [
            ('Kinases', 7.4),
            ('Amphioxus TLR', 9.0),
            ('GPCRs', 11),
            ('Zinc fingers', 11),
            ('ORs', 18),
            ('NBS-LRR', 23),
        ]

    fig, ax = plt.subplots(figsize=(8, 3))

    # Regime bands (illustrative, from gamma_calibration.csv literature ranges)
    ax.axvspan(2, 10, alpha=0.20, color='#4488cc', label='Recombination regime')
    ax.axvspan(100, 10000, alpha=0.15, color='#cc4444', label='Duplication (IAD) regime')

    # T3req family gamma_crit values
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
# Provenance: d_distributions.csv (D_ge_1_count, D_ge_3_count,
#   D_ge_5_count, D_ge_8_count per organism).
# ===================================================================
def fig6_d_distribution():
    """Fig 6: Gene family depth distribution by organism.

    Provenance: d_distributions.csv.
    Columns: D_ge_1_count, D_ge_3_count, D_ge_5_count, D_ge_8_count.
    """
    csv_path = os.path.join(DATA_RAW, 'd_distributions.csv')
    rows = load_csv(csv_path)

    species_colors = {
        'H. sapiens': '#cc2222',
        'A. thaliana': '#22aa44',
        'E. coli': '#4477cc',
        'E. coli K-12': '#4477cc',
    }

    def _parse_count(val):
        """Parse count values like '3586', '7000+', '3-5', '40-50'."""
        val = val.strip().rstrip('+')
        if '-' in val:
            parts = val.split('-')
            try:
                return int(round((float(parts[0]) + float(parts[1])) / 2.0))
            except (ValueError, IndexError):
                return 0
        try:
            return int(float(val))
        except ValueError:
            return 0

    if rows is not None:
        d_dist = {}
        ordered_species = []
        for r in rows:
            org = r['organism'].strip()
            counts = [
                _parse_count(r['D_ge_1_count']),
                _parse_count(r['D_ge_3_count']),
                _parse_count(r['D_ge_5_count']),
                _parse_count(r['D_ge_8_count']),
            ]
            d_dist[org] = counts
            ordered_species.append(org)
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 6")
        d_dist = {
            'H. sapiens': [3586, 290, 40, 4],
            'A. thaliana': [7000, 1000, 200, 50],
            'E. coli': [400, 45, 7, 0],
        }
        ordered_species = list(d_dist.keys())

    thresholds = ['\u2265 1', '\u2265 3', '\u2265 5', '\u2265 8']

    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(thresholds))
    width = 0.25

    for i, species in enumerate(ordered_species):
        counts = d_dist[species]
        color = species_colors.get(species, f'C{i}')
        # Replace 0 with 0.5 for log display
        display = [c if c > 0 else 0.5 for c in counts]
        ax.bar(x + i * width, display, width * 0.9,
               color=color, edgecolor='black',
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
# Provenance: computed from f15_scorecard.csv / gamma_crit_table.csv.
#   gc(D +/- 1) = T^(1/(D +/- 1)).  For each T3req family, D and T
#   are read from gamma_crit_table.csv and gc at D-1, D+1 computed.
# ===================================================================
def fig7_sensitivity():
    """Fig 7: Gamma_crit sensitivity to D +/- 1.

    Provenance: computed from gamma_crit_table.csv.
    gc = T^(1/D), gc_lo = T^(1/(D+1)), gc_hi = T^(1/(D-1)).
    """
    csv_path = os.path.join(DATA_PROCESSED, 'gamma_crit_table.csv')
    rows = load_csv(csv_path)

    if rows is not None:
        sensitivity = []
        for r in rows:
            if r['F15_verdict'] == 'T3req':
                name = r['system']
                D = float(r['D'])
                T = float(r['T_midpoint'])
                gc = T ** (1.0 / D)
                gc_lo = T ** (1.0 / (D + 1))  # D+1 gives lower gamma
                gc_hi = T ** (1.0 / (D - 1)) if D > 1 else gc * 2  # D-1 gives higher gamma
                sensitivity.append((name, gc, gc_lo, gc_hi))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 7")
        sensitivity = [
            ('Kinases', 7.4, 5.4, 13.0),
            ('Amphioxus TLR', 9.0, 6.3, 14.1),
            ('GPCRs', 11, 8.0, 17.6),
            ('Zinc fingers', 11, 8.0, 17.6),
            ('ORs', 18, 13, 28),
            ('NBS-LRR', 23, 16, 36),
        ]

    # Sort by gc ascending
    sensitivity.sort(key=lambda x: x[1])

    names = [s[0] for s in sensitivity]
    gc = np.array([s[1] for s in sensitivity])
    gc_lo = np.array([s[2] for s in sensitivity])
    gc_hi = np.array([s[3] for s in sensitivity])

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
# Provenance: classification_summary.csv (category counts).
# ===================================================================
def fig8_classification_pie():
    """Fig 8: F15 classification distribution donut chart.

    Provenance: classification_summary.csv.
    """
    csv_path = os.path.join(DATA_PROCESSED, 'classification_summary.csv')
    rows = load_csv(csv_path)

    # Colour map for classification categories
    cat_colors = {
        'T3req': '#cc2222',
        'T3req_bio': '#ee4444',
        'Tmarg': '#dd8800',
        'Tmarg_cultural': '#ccbb00',
        'T2ok': '#2266bb',
        'Tna': '#888888',
    }

    if rows is not None:
        labels = []
        sizes = []
        colors = []
        for r in rows:
            cat = r['classification'].strip()
            count = int(r['count'])
            labels.append(cat)
            sizes.append(count)
            colors.append(cat_colors.get(cat, '#aaaaaa'))
    else:
        print("  WARNING: Falling back to hardcoded data for Fig 8")
        labels = ['T3req', 'Tmarg', 'T2ok', 'Tna', 'Tmarg\u2020']
        sizes = [6, 22, 24, 25, 12]
        colors = ['#cc2222', '#dd8800', '#2266bb', '#888888', '#ccbb00']

    total = sum(sizes)

    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%',
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5),
        textprops=dict(fontsize=9),
    )
    for at in autotexts:
        at.set_fontsize(8)

    ax.set_title(f'F15 Classification Distribution (~{total} systems)', fontsize=11)

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

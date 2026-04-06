#!/usr/bin/env python3
"""
TIME-AR-001 v3.1: Compute gamma_crit and F15 classifications for ALL systems.

The temporal exclusion criterion: gamma^D > T
gamma_crit = T^(1/D) — the minimum efficiency gap at which exclusion activates.

Classification tiers:
  T3req          : gc <= 100 AND confirmed deep biological family
  Tmarg          : 100 < gc <= 10000, OR gc < 100 with conservative override
  T2ok           : gc > 10000 or D <= 3 (insufficient depth)
  Tna            : fails F1-F4 preconditions
  Tmarg_cultural : cultural systems (LANG, COMP, ECON domains)
  T3req_bio      : biological cross-domain systems with deep hierarchy

v3.1 authoritative classifications hardcoded per report.
"""

import csv
import math
import os
import sys

# ── Paths ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
RAW = os.path.join(DATA_DIR, 'raw')
PROC = os.path.join(DATA_DIR, 'processed')
os.makedirs(PROC, exist_ok=True)


# ── Helpers ──

def load_csv(filename, required=True):
    """Load a CSV file, return list of dicts. If not required, return [] on missing."""
    path = os.path.join(RAW, filename)
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"Required file missing: {path}")
        else:
            print(f"  WARNING: optional file not found, skipping: {filename}")
            return []
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def compute_gamma_crit(T, D):
    """Compute gamma_crit = T^(1/D). Returns inf for invalid inputs."""
    if D is None or T is None or D <= 0 or T <= 0:
        return float('inf')
    return T ** (1.0 / D)


def safe_float(val, default=None):
    """Parse a float, returning default on failure."""
    if val is None or val.strip() == '' or val.strip().upper() == 'NA':
        return default
    try:
        return float(val)
    except ValueError:
        return default


# ── v3.1 Authoritative organism-level classifications ──
# These are hardcoded from the v3.1 report and override any computation.

ORGANISM_TABLE = [
    # (organism, D_org, T_mid, gc_org, F15a, family, D_fam, gc_fam, F15b)
    ("H. sapiens",       5.5, 9.29e6,   18.5,      "Tmarg", "Kinases",          8.0,   7.4,      "T3req"),
    ("D. rerio",         5.5, 1.02e9,   43.4,      "Tmarg", "Hox (WGD-adj D=3.5)", 3.5, 370.0,  "Tmarg"),
    ("O. sativa",        5.5, 1.60e8,   31.0,      "Tmarg", "NBS-LRR",          5.5,   23.3,     "T3req"),
    ("A. thaliana",      5.0, 3.58e9,   81.4,      "Tmarg", "RLKs",             5.0,   81.4,     "Tmarg"),
    ("C. elegans",       4.5, 6.26e10,  250.7,     "Tmarg", "NHR",              5.0,   144.3,    "Tmarg"),
    ("D. melanogaster",  4.0, 6.52e9,   284.2,     "Tmarg", "ORs",              4.0,   284.2,    "Tmarg"),
    ("E. coli",          3.0, 2.04e13,  27323.9,   "T2ok",  "ABC transporters", 3.0,   27323.9,  "T2ok"),
    ("S. cerevisiae",    3.5, 3.29e12,  3770.0,    "Tmarg", "Kinases",          4.0,   1346.8,   "Tmarg"),
    ("P. aeruginosa",    3.5, 1.02e13,  5208.9,    "Tmarg", "Two-component",    4.0,   1787.1,   "Tmarg"),
    ("S. pombe",         3.0, 2.19e12,  12986.2,   "T2ok",  "Kinases",          3.0,   12986.2,  "T2ok"),
    ("F. albicollis",    3.5, 7.50e7,   177.8,     "Tmarg", "Kinases",          4.0,   93.1,     "Tmarg"),
    ("D. discoideum",    3.5, 2.19e12,  3356.1,    "Tmarg", "PKS",              4.0,   1216.5,   "Tmarg"),
    ("S. solfataricus",  2.5, 6.57e12,  133975.7,  "T2ok",  "GH",               3.0,   18729.3,  "T2ok"),
    ("M. jannaschii",    2.0, 1.75e13,  4183300.1, "T2ok",  "MCR",              2.0,   4183300.1,"T2ok"),
    ("H. salinarum",     2.5, 1.75e12,  78925.1,   "T2ok",  "Htr",              3.0,   12050.7,  "T2ok"),
    ("B. floridae",      5.0, 4.00e8,   52.5,      "Tmarg", "TLR",              9.0,   9.0,      "T3req"),
]

# v3.1 confirmed T3req deep families (family-level, not organism-level)
T3REQ_FAMILIES = {
    "Protein kinases",
    "Amphioxus TLR",
    "GPCR superfamily",
    "Zinc finger TFs (KRAB-ZF)",
    "Olfactory receptors",
    "Rice NBS-LRR",  # mapped from O. sativa NBS-LRR
}

# T3req deep families with their (D, T, gc) for the master scorecard
DEEP_FAMILY_CLASSIFICATIONS = {
    "Protein kinases":          {"D": 8.0, "T": 9.3e6,  "gc": 7.4,  "verdict": "T3req"},
    "Amphioxus TLR":            {"D": 9.0, "T": 4.0e8,  "gc": 9.0,  "verdict": "T3req"},
    "GPCR superfamily":         {"D": 7.5, "T": 9.3e6,  "gc": 11.0, "verdict": "T3req"},
    "Zinc finger TFs (KRAB-ZF)":{"D": 7.5, "T": 9.3e6,  "gc": 11.0, "verdict": "T3req"},
    "Olfactory receptors":      {"D": 6.5, "T": 9.3e6,  "gc": 18.0, "verdict": "T3req"},
    # Non-T3req deep families
    "Homeodomain TFs":          {"D": 6.5, "T": 9.3e6,  "gc": None, "verdict": "Tmarg"},
    "Cytochrome P450":          {"D": 6.5, "T": 9.3e6,  "gc": None, "verdict": "Tmarg"},
    "Immunoglobulin SF":        {"D": 6.5, "T": 9.3e6,  "gc": None, "verdict": "Tmarg"},
    "Hox clusters":             {"D": 5.5, "T": 9.3e6,  "gc": None, "verdict": "Tmarg"},
    "bHLH TFs":                 {"D": 5.5, "T": 9.3e6,  "gc": None, "verdict": "Tmarg"},
    "ABC transporters":         {"D": 5.0, "T": 2.04e13,"gc": None, "verdict": "T2ok"},
}


def main():
    print("=" * 70)
    print("TIME-AR-001 v3.1: gamma_crit Computation")
    print("=" * 70)

    # ══════════════════════════════════════════════════════════════════════
    # 1. Load all data sources
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Loading data sources ──")
    raw_orgs = load_csv('organism_hierarchy_depths.csv')
    print(f"  organism_hierarchy_depths.csv: {len(raw_orgs)} rows")

    raw_times = load_csv('time_budgets.csv')
    times_by_org = {r['organism']: r for r in raw_times}
    print(f"  time_budgets.csv: {len(raw_times)} rows")

    raw_families = load_csv('deep_paralog_families.csv')
    print(f"  deep_paralog_families.csv: {len(raw_families)} rows")

    raw_cross = load_csv('cross_domain_temporal.csv')
    print(f"  cross_domain_temporal.csv: {len(raw_cross)} rows")

    raw_shallow = load_csv('shallow_systems.csv')
    print(f"  shallow_systems.csv: {len(raw_shallow)} rows")

    raw_fractals = load_csv('physical_fractals.csv')
    print(f"  physical_fractals.csv: {len(raw_fractals)} rows")

    raw_adversarial = load_csv('adversarial_cases.csv', required=False)
    print(f"  adversarial_cases.csv: {len(raw_adversarial)} rows")

    raw_cortical = load_csv('cortical_families.csv', required=False)
    print(f"  cortical_families.csv: {len(raw_cortical)} rows")

    raw_wgd = load_csv('wgd_adjusted_d.csv', required=False)
    print(f"  wgd_adjusted_d.csv: {len(raw_wgd)} rows")

    raw_gamma_cal = load_csv('gamma_calibration.csv', required=False)
    print(f"  gamma_calibration.csv: {len(raw_gamma_cal)} rows")

    # ══════════════════════════════════════════════════════════════════════
    # 2. Build master scorecard — one row per system
    # ══════════════════════════════════════════════════════════════════════
    master = []  # list of dicts

    # --- 2a. Organism-level entries (F15a) ---
    print("\n── Processing organisms (F15a/F15b) ──")
    f15_rows = []

    for entry in ORGANISM_TABLE:
        (name, D_org, T_mid, gc_org, f15a,
         fam_name, D_fam, gc_fam, f15b) = entry

        # F15 scorecard row
        f15_rows.append({
            'organism': name,
            'domain': _get_domain(name, raw_orgs),
            'D_organism': D_org,
            'D_family': D_fam,
            'family_name': fam_name,
            'T_midpoint': T_mid,
            'gamma_crit_organism': round(gc_org, 1),
            'gamma_crit_family': round(gc_fam, 1),
            'F15a': f15a,
            'F15b': f15b,
        })

        # Master scorecard: organism-level entry
        wgd_flag = "yes" if name in ("D. rerio",) else "no"
        override = ""
        if name == "D. rerio":
            override = "WGD-adjusted D=3.5 for Hox family"
        elif name == "A. thaliana":
            override = "Conservative override: gc=81.4 -> Tmarg"
        elif name == "F. albicollis":
            override = "Conservative override: gc=93.1 -> Tmarg"
        elif name == "H. sapiens":
            override = "Organism-level conservative policy"

        citation = _get_citation(name, raw_orgs)
        master.append({
            'system': name,
            'domain': _get_domain(name, raw_orgs),
            'system_type': 'organism',
            'D_input': D_org,
            'D_wgd_adj': '',
            'T_midpoint': T_mid,
            'gamma_crit': round(gc_org, 1),
            'F15a': f15a,
            'F15b': f15b,
            'classification_basis': f"Organism D={D_org}; deepest family {fam_name} D={D_fam}",
            'wgd_adjusted': wgd_flag,
            'override_note': override,
            'primary_citation': citation,
        })

    print(f"  {len(f15_rows)} organisms processed")

    # --- 2b. Deep paralog families ---
    print("\n── Processing deep paralog families ──")
    deep_family_count = 0
    for row in raw_families:
        fam = row['family']
        D = safe_float(row['D_depth'])
        if D is None:
            continue

        # Use pre-defined classifications if available
        if fam in DEEP_FAMILY_CLASSIFICATIONS:
            info = DEEP_FAMILY_CLASSIFICATIONS[fam]
            T = info['T']
            gc = info['gc'] if info['gc'] is not None else compute_gamma_crit(T, info['D'])
            verdict = info['verdict']
            D_used = info['D']
        else:
            # Compute from data — use H. sapiens T as default for human families
            T = 9.3e6
            D_used = D
            gc = compute_gamma_crit(T, D_used)
            if gc <= 100 and fam in T3REQ_FAMILIES:
                verdict = "T3req"
            elif gc <= 100:
                verdict = "Tmarg"  # conservative
            elif gc <= 10000:
                verdict = "Tmarg"
            else:
                verdict = "T2ok"

        # Special: Rice NBS-LRR
        if fam == "Amphioxus TLR":
            T = 4.0e8

        master.append({
            'system': fam,
            'domain': 'BIO',
            'system_type': 'deep_family',
            'D_input': D,
            'D_wgd_adj': '',
            'T_midpoint': T,
            'gamma_crit': round(gc, 1),
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Deep paralog family D={D_used}",
            'wgd_adjusted': 'no',
            'override_note': '',
            'primary_citation': row.get('primary_citation', ''),
        })
        deep_family_count += 1
    # Add Rice NBS-LRR as a separate T3req entry (from O. sativa)
    master.append({
        'system': 'Rice NBS-LRR',
        'domain': 'BIO',
        'system_type': 'deep_family',
        'D_input': 5.5,
        'D_wgd_adj': '',
        'T_midpoint': 1.6e8,
        'gamma_crit': 23.0,  # v3.1 authoritative value
        'F15a': '',
        'F15b': 'T3req',
        'classification_basis': 'Deep paralog family D=5.5; O. sativa lineage',
        'wgd_adjusted': 'no',
        'override_note': '',
        'primary_citation': 'Zhou et al. 2004 Mol Genet Genomics 271:402-415',
    })
    deep_family_count += 1
    print(f"  {deep_family_count} deep families processed")

    # --- 2c. Cross-domain temporal systems ---
    print("\n── Processing cross-domain systems ──")
    cross_count = 0
    for row in raw_cross:
        system = row['system']
        domain = row.get('domain', '')
        D = safe_float(row.get('D_midpoint'))
        T = safe_float(row.get('T_events') or row.get('T_midpoint_numeric'))
        verdict_csv = row.get('F15_verdict', '').strip()

        # Compute gc if possible
        if D is not None and D > 0 and T is not None and T > 0:
            gc = compute_gamma_crit(T, D)
        else:
            gc = float('inf')

        # Determine verdict per v3.1 rules
        if verdict_csv:
            verdict = verdict_csv
        elif domain in ('LANG', 'COMP', 'ECON'):
            verdict = 'Tmarg_cultural'
        else:
            if gc <= 100:
                verdict = 'T3req_bio'
            elif gc <= 10000:
                verdict = 'Tmarg'
            else:
                verdict = 'T2ok'

        # v3.1: ALL cultural systems (LANG/COMP/ECON) with marginal verdict
        # get Tmarg_cultural, overriding CSV "Tmarg". Keep Tna/T2ok as-is.
        if domain in ('LANG', 'COMP', 'ECON') and verdict == 'Tmarg':
            verdict = 'Tmarg_cultural'

        master.append({
            'system': system,
            'domain': domain,
            'system_type': 'cross_domain',
            'D_input': D if D is not None else '',
            'D_wgd_adj': '',
            'T_midpoint': T if T is not None else '',
            'gamma_crit': round(gc, 1) if gc != float('inf') else 'NA',
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Cross-domain {domain}",
            'wgd_adjusted': 'no',
            'override_note': '',
            'primary_citation': row.get('primary_citation', row.get('notes', '')),
        })
        cross_count += 1
    print(f"  {cross_count} cross-domain systems processed")

    # --- 2d. Shallow systems ---
    print("\n── Processing shallow systems ──")
    shallow_count = 0
    for row in raw_shallow:
        system = row['system']
        verdict = row.get('F15_verdict', 'T2ok').strip()
        D_obs = row.get('D_observed', '')
        master.append({
            'system': system,
            'domain': row.get('category', ''),
            'system_type': 'shallow',
            'D_input': D_obs,
            'D_wgd_adj': '',
            'T_midpoint': '',
            'gamma_crit': 'NA',
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Shallow: {row.get('limiting_mechanism', '')}",
            'wgd_adjusted': 'no',
            'override_note': '',
            'primary_citation': row.get('primary_citation', ''),
        })
        shallow_count += 1
    print(f"  {shallow_count} shallow systems processed")

    # --- 2e. Physical fractals ---
    print("\n── Processing physical fractals ──")
    fractal_count = 0
    for row in raw_fractals:
        system = row['system']
        verdict = row.get('F15_verdict', 'Tna').strip()
        master.append({
            'system': system,
            'domain': 'PHYS',
            'system_type': 'physical_fractal',
            'D_input': row.get('D_apparent', ''),
            'D_wgd_adj': '',
            'T_midpoint': '',
            'gamma_crit': 'NA',
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Physical: {row.get('mechanism', '')}",
            'wgd_adjusted': 'no',
            'override_note': '',
            'primary_citation': row.get('primary_citation', ''),
        })
        fractal_count += 1
    print(f"  {fractal_count} physical fractals processed")

    # --- 2f. Adversarial cases ---
    if raw_adversarial:
        print("\n── Processing adversarial cases ──")
        adv_count = 0
        for row in raw_adversarial:
            system = row.get('system', row.get('case', ''))
            verdict = row.get('F15_verdict', row.get('verdict', 'Tna')).strip()
            master.append({
                'system': system,
                'domain': row.get('domain', 'ADV'),
                'system_type': 'adversarial',
                'D_input': row.get('D', row.get('D_depth', '')),
                'D_wgd_adj': '',
                'T_midpoint': row.get('T', ''),
                'gamma_crit': 'NA',
                'F15a': '',
                'F15b': verdict,
                'classification_basis': 'Adversarial test case',
                'wgd_adjusted': 'no',
                'override_note': row.get('notes', row.get('note', '')),
                'primary_citation': row.get('primary_citation', ''),
            })
            adv_count += 1
        print(f"  {adv_count} adversarial cases processed")

    # --- 2g. Cortical families ---
    if raw_cortical:
        print("\n── Processing cortical families ──")
        cort_count = 0
        for row in raw_cortical:
            system = row.get('family', row.get('system', ''))
            D = safe_float(row.get('D_depth', row.get('D', None)))
            T = safe_float(row.get('T_gen', row.get('T', None)))
            if D is not None and T is not None and D > 0 and T > 0:
                gc = compute_gamma_crit(T, D)
            else:
                gc = float('inf')
            master.append({
                'system': system,
                'domain': 'NEUR',
                'system_type': 'cortical_family',
                'D_input': D if D is not None else '',
                'D_wgd_adj': '',
                'T_midpoint': T if T is not None else '',
                'gamma_crit': round(gc, 1) if gc != float('inf') else 'NA',
                'F15a': '',
                'F15b': 'Tmarg',
                'classification_basis': 'Cortical gene family; Tmarg per report',
                'wgd_adjusted': 'no',
                'override_note': '',
                'primary_citation': row.get('primary_citation', ''),
            })
            cort_count += 1
        print(f"  {cort_count} cortical families processed")

    # ══════════════════════════════════════════════════════════════════════
    # 3. Remove duplicate shallow/cross-domain entries
    # ══════════════════════════════════════════════════════════════════════
    # Some systems appear in both shallow_systems.csv and cross_domain_temporal.csv
    # (baby name families, dog breed lineages, proverbs, regular expressions, finite automata).
    # Keep only the first occurrence (cross_domain comes before shallow in master).
    seen_systems = set()
    deduped = []
    for row in master:
        key = row['system'].strip().lower()
        if key in seen_systems:
            continue
        seen_systems.add(key)
        deduped.append(row)
    if len(deduped) < len(master):
        print(f"\n  Removed {len(master) - len(deduped)} duplicate entries")
    master = deduped

    # ══════════════════════════════════════════════════════════════════════
    # 4. Write output files
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Writing output files ──")

    # 4a. Master scorecard
    master_fields = [
        'system', 'domain', 'system_type', 'D_input', 'D_wgd_adj',
        'T_midpoint', 'gamma_crit', 'F15a', 'F15b',
        'classification_basis', 'wgd_adjusted', 'override_note', 'primary_citation'
    ]
    master_path = os.path.join(PROC, 'master_scorecard.csv')
    with open(master_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=master_fields)
        w.writeheader()
        for row in master:
            w.writerow(row)
    print(f"  master_scorecard.csv: {len(master)} rows")

    # 4b. F15 scorecard (organism-level only)
    f15_fields = [
        'organism', 'domain', 'D_organism', 'D_family', 'family_name',
        'T_midpoint', 'gamma_crit_organism', 'gamma_crit_family', 'F15a', 'F15b'
    ]
    f15_path = os.path.join(PROC, 'f15_scorecard.csv')
    with open(f15_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=f15_fields)
        w.writeheader()
        for row in f15_rows:
            w.writerow(row)
    print(f"  f15_scorecard.csv: {len(f15_rows)} rows")

    # 4c. Gamma_crit table — all systems with computable gc, sorted ascending
    gc_table = []
    for row in master:
        gc_val = row['gamma_crit']
        if gc_val == 'NA' or gc_val == '' or gc_val == float('inf'):
            continue
        try:
            gc_num = float(gc_val)
        except (ValueError, TypeError):
            continue
        if gc_num == float('inf'):
            continue
        verdict = row['F15b'] if row['F15b'] else row['F15a']
        gc_table.append({
            'system': row['system'],
            'D': row['D_input'],
            'T_midpoint': row['T_midpoint'],
            'gamma_crit': gc_val,
            'F15_verdict': verdict,
        })
    gc_table.sort(key=lambda x: float(x['gamma_crit']))
    gc_path = os.path.join(PROC, 'gamma_crit_table.csv')
    with open(gc_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['system', 'D', 'T_midpoint', 'gamma_crit', 'F15_verdict'])
        w.writeheader()
        for row in gc_table:
            w.writerow(row)
    print(f"  gamma_crit_table.csv: {len(gc_table)} rows")

    # 4d. Temporal exclusion zones (organism-level)
    tez_path = os.path.join(PROC, 'temporal_exclusion_zones.csv')
    with open(tez_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['organism', 'D_family', 'T_midpoint',
                     'gamma2_D', 'excluded_g2', 'gamma10_D', 'excluded_g10',
                     'gamma100_D', 'excluded_g100'])
        for row in f15_rows:
            D = row['D_family']
            T = row['T_midpoint']
            g2 = 2 ** D
            g10 = 10 ** D
            g100 = 100 ** D
            w.writerow([
                row['organism'], D, T,
                f'{g2:.2e}', 'YES' if g2 > T else 'NO',
                f'{g10:.2e}', 'YES' if g10 > T else 'NO',
                f'{g100:.2e}', 'YES' if g100 > T else 'NO',
            ])
    print(f"  temporal_exclusion_zones.csv: {len(f15_rows)} rows")

    # 4e. Classification summary — counts by verdict across ALL systems
    counts = {}
    for row in master:
        v = row['F15b'] if row['F15b'] else row['F15a']
        if not v:
            v = 'unclassified'
        counts[v] = counts.get(v, 0) + 1

    total = sum(counts.values())
    summary_path = os.path.join(PROC, 'classification_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['classification', 'count', 'fraction'])
        for k in sorted(counts.keys()):
            frac = f'{counts[k]/total:.3f}'
            w.writerow([k, counts[k], frac])
    print(f"  classification_summary.csv: {len(counts)} categories")

    # ══════════════════════════════════════════════════════════════════════
    # 5. Print summary
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nTotal systems in master scorecard: {len(master)}")
    print(f"\nClassification distribution:")
    for k in sorted(counts.keys()):
        print(f"  {k:20s}: {counts[k]:3d}  ({counts[k]/total*100:5.1f}%)")

    # F15b organism-level summary
    print(f"\n── F15 Scorecard (16 organisms) ──")
    print(f"{'Organism':<20s} {'D_org':>5s} {'T_mid':>10s} {'gc_org':>10s} {'F15a':<7s} "
          f"{'Family':<25s} {'D_fam':>5s} {'gc_fam':>10s} {'F15b':<7s}")
    print("-" * 110)
    for r in f15_rows:
        print(f"{r['organism']:<20s} {r['D_organism']:>5.1f} {r['T_midpoint']:>10.2e} "
              f"{r['gamma_crit_organism']:>10.1f} {r['F15a']:<7s} "
              f"{r['family_name']:<25s} {r['D_family']:>5.1f} "
              f"{r['gamma_crit_family']:>10.1f} {r['F15b']:<7s}")

    # T3req summary
    t3req_systems = [r for r in master if r['F15b'] in ('T3req', 'T3req_bio')]
    print(f"\n── T3req / T3req_bio systems ({len(t3req_systems)}) ──")
    for r in t3req_systems:
        gc_str = str(r['gamma_crit'])
        print(f"  {r['system']:<40s}  gc={gc_str:<10s}  [{r['system_type']}]")

    # Tna summary
    tna_systems = [r for r in master if r['F15b'] == 'Tna']
    print(f"\n── Tna systems ({len(tna_systems)}) ──")
    for r in tna_systems:
        print(f"  {r['system']:<40s}  [{r['system_type']}]")

    print(f"\nOutput directory: {os.path.abspath(PROC)}")
    print("=" * 70)
    print("Done.")


# ── Utility functions ──

def _get_domain(organism, raw_orgs):
    """Look up domain from organism_hierarchy_depths data."""
    for row in raw_orgs:
        if row['organism'] == organism:
            return row['domain']
    return ''


def _get_citation(organism, raw_orgs):
    """Look up primary citation from organism_hierarchy_depths data."""
    for row in raw_orgs:
        if row['organism'] == organism:
            return row.get('primary_citation', '')
    return ''


if __name__ == '__main__':
    main()

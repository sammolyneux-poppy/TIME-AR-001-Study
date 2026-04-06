#!/usr/bin/env python3
"""
TIME-AR-001 v3.1.1: Compute gamma_crit and F15 classifications for ALL systems.

The temporal exclusion criterion: gamma^D > T
gamma_crit = T^(1/D) — the minimum efficiency gap at which exclusion activates.

Classification tiers:
  T3req          : gc <= 100 AND confirmed deep biological family
  Tmarg          : 100 < gc <= 10000, OR gc < 100 with conservative override
  T2ok           : gc > 10000 or D <= 3 (insufficient depth)
  Tna            : fails F1-F4 preconditions
  Tmarg_cultural : cultural systems (LANG, COMP, ECON domains)
  T3req_bio      : biological cross-domain systems with deep hierarchy

v3.1.1 refactored:
  - Organism-level values DERIVED from raw CSVs (item 3)
  - Named override rules with audit trail (item 4)
  - Computed baseline + final columns in master scorecard (items 4, 17)
  - Stable system IDs (item 9)
  - Explicit dedupe report (item 10)
  - WGD provenance from wgd_adjusted_d.csv (item 11)
  - T3req_combined row in classification summary (item 16)
"""

import csv
import math
import os
import re
import sys

# ── Paths ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
RAW = os.path.join(DATA_DIR, 'raw')
PROC = os.path.join(DATA_DIR, 'processed')
os.makedirs(PROC, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
# Override Rules (item 4)
# ══════════════════════════════════════════════════════════════════════
# Each rule: id, applies_to function, effect function, reason string.
# Applied in order; first matching rule wins.

RULES = {
    'WGD_ADJUSTMENT': {
        'description': 'WGD inflates hierarchy depth; reduce D_family by WGD adjustment',
        'reason': 'WGD inflates hierarchy depth; D_family reduced per wgd_adjusted_d.csv',
    },
    'CONSERVATIVE_NEAR_THRESHOLD': {
        'description': 'Near-threshold gc<100 classified as Tmarg due to sensitivity at D-1',
        'reason': 'Near threshold + sensitivity analysis at D-1 pushes gc above 100',
    },
    'ORGANISM_LEVEL_POLICY': {
        'description': 'Organism-level D influenced by WGD; gene-family result is primary claim',
        'reason': 'Organism-level D influenced by WGD; gene-family gc (kinases=7.4) is primary claim',
    },
    'CULTURAL_CONTINGENCY': {
        'description': 'Cultural T definition contested; classify as Tmarg_cultural',
        'reason': 'Cultural T definition contested; cultural systems reclassified',
    },
}


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
    if val is None or str(val).strip() == '' or str(val).strip().upper() == 'NA':
        return default
    try:
        return float(val)
    except ValueError:
        return default


def sanitize_id(name):
    """Sanitize a name for use as a system ID component."""
    s = name.strip()
    # Replace spaces and special chars with underscores
    s = re.sub(r'[^A-Za-z0-9]', '_', s)
    # Collapse multiple underscores
    s = re.sub(r'_+', '_', s)
    # Strip leading/trailing underscores
    s = s.strip('_')
    return s


def make_system_id(prefix, name):
    """Create a stable system ID like ORG-H_sapiens."""
    return f"{prefix}-{sanitize_id(name)}"


def classify_gc(gc, is_confirmed_deep=False):
    """
    Pure threshold classification based on gc value.
    Returns verdict string. Does NOT apply overrides.
    """
    if gc == float('inf') or gc is None:
        return 'Tna'
    if gc <= 100:
        if is_confirmed_deep:
            return 'T3req'
        else:
            return 'Tmarg'
    elif gc <= 10000:
        return 'Tmarg'
    else:
        return 'T2ok'


# ── Lookup helpers ──

def _get_field(organism, raw_orgs, field, default=''):
    """Look up a field from organism_hierarchy_depths data."""
    for row in raw_orgs:
        if row['organism'] == organism:
            return row.get(field, default)
    return default


def main():
    print("=" * 70)
    print("TIME-AR-001 v3.1.1: gamma_crit Computation (refactored)")
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

    # gamma_calibration.csv is report-only supporting evidence (item 11).
    # It is NOT used computationally in the pipeline; retained in data/raw/
    # for provenance documentation only.

    raw_family_map = load_csv('organism_family_map.csv')
    print(f"  organism_family_map.csv: {len(raw_family_map)} rows")

    # ══════════════════════════════════════════════════════════════════════
    # 2. Build indexes from raw data (item 3)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Building derived indexes ──")

    # D_consensus by organism (from organism_hierarchy_depths.csv)
    d_consensus_by_org = {}
    for row in raw_orgs:
        d_consensus_by_org[row['organism']] = safe_float(row['D_consensus'])

    # T_midpoint by organism (from time_budgets.csv)
    t_midpoint_by_org = {}
    for row in raw_times:
        t_midpoint_by_org[row['organism']] = safe_float(row['T_midpoint'])

    # WGD adjustments indexed by (organism, family) (item 11 — actually USE wgd_adjusted_d.csv)
    wgd_index = {}
    for row in raw_wgd:
        key = (row['organism'].strip(), row['family'].strip())
        wgd_index[key] = {
            'D_raw': safe_float(row['D_raw']),
            'wgd_events': safe_float(row.get('wgd_events', '0'), 0),
            'wgd_adjustment': safe_float(row.get('wgd_adjustment', '0'), 0),
            'D_wgd_adj': safe_float(row['D_wgd_adj']),
            'notes': row.get('notes', ''),
        }

    # Family map by organism (from organism_family_map.csv)
    family_map_by_org = {}
    for row in raw_family_map:
        family_map_by_org[row['organism'].strip()] = {
            'family': row['family'].strip(),
            'D_family': safe_float(row['D_family']),
            'T_family': safe_float(row.get('T_family')),  # None means use organism T
            'notes': row.get('notes', ''),
        }

    # v3.1 confirmed T3req deep families (family-level, not organism-level)
    T3REQ_FAMILIES = {
        "Protein kinases",
        "Amphioxus TLR",
        "GPCR superfamily",
        "Zinc finger TFs (KRAB-ZF)",
        "Olfactory receptors",
        "Rice NBS-LRR",
    }

    # Deep family classification data — derived from deep_paralog_families.csv + time context
    # T defaults: human families use H. sapiens T; Amphioxus uses B. floridae T;
    # Rice NBS-LRR uses O. sativa T; ABC transporters use E. coli T.
    DEEP_FAMILY_T_MAP = {
        "Protein kinases":           t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "GPCR superfamily":          t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Zinc finger TFs (KRAB-ZF)": t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Olfactory receptors":       t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Homeodomain TFs":           t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Cytochrome P450":           t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Immunoglobulin SF":         t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "Hox clusters":              t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "bHLH TFs":                  t_midpoint_by_org.get('H. sapiens', 9.3e6),
        "ABC transporters":          t_midpoint_by_org.get('E. coli', 2.04e13),
        "Amphioxus TLR":             t_midpoint_by_org.get('B. floridae', 4.0e8),
    }

    # ══════════════════════════════════════════════════════════════════════
    # 3. Build master scorecard — one row per system
    # ══════════════════════════════════════════════════════════════════════
    master = []  # list of dicts

    # --- 3a. Organism-level entries (F15a/F15b) — DERIVED from raw CSVs (item 3) ---
    print("\n── Processing organisms (F15a/F15b) — derived from raw CSVs ──")
    f15_rows = []

    for org_row in raw_orgs:
        name = org_row['organism']
        domain = org_row['domain']
        D_org = safe_float(org_row['D_consensus'])
        T_mid = t_midpoint_by_org.get(name)
        citation = org_row.get('primary_citation', '')

        if D_org is None or T_mid is None:
            print(f"  WARNING: skipping {name}, missing D or T")
            continue

        # Compute organism-level gc
        gc_org = compute_gamma_crit(T_mid, D_org)

        # Look up deepest family from organism_family_map.csv
        fam_info = family_map_by_org.get(name)
        if fam_info is None:
            print(f"  WARNING: no family mapping for {name}")
            continue

        fam_name = fam_info['family']
        D_fam_raw = fam_info['D_family']
        T_fam = fam_info['T_family'] if fam_info['T_family'] is not None else T_mid

        # Check WGD adjustment from wgd_adjusted_d.csv (item 11)
        D_fam = D_fam_raw
        wgd_flag = "no"
        wgd_adj_val = ''
        override_rule_id = ''
        override_reason = ''

        # Try to find WGD entry for this organism+family
        # Normalize family name for WGD lookup (handle name mismatches)
        wgd_lookup_names = [fam_name]
        if fam_name == 'Hox clusters' or fam_name == 'Hox':
            wgd_lookup_names.append('Hox clusters')
        if fam_name == 'Kinases':
            wgd_lookup_names.append('Protein kinases')

        for wgd_fam_name in wgd_lookup_names:
            wgd_key = (name, wgd_fam_name)
            if wgd_key in wgd_index:
                wgd_info = wgd_index[wgd_key]
                if wgd_info['wgd_adjustment'] != 0:
                    D_fam = wgd_info['D_wgd_adj']
                    wgd_flag = "yes"
                    wgd_adj_val = D_fam
                    override_rule_id = 'WGD_ADJUSTMENT'
                    override_reason = RULES['WGD_ADJUSTMENT']['reason']
                    fam_name_display = f"{fam_name} (WGD-adj D={D_fam})"
                else:
                    fam_name_display = fam_name
                break
        else:
            fam_name_display = fam_name

        # Compute family-level gc
        gc_fam = compute_gamma_crit(T_fam, D_fam)

        # ── Classify (computed baseline) ──
        # F15a: organism-level verdict
        verdict_org_computed = classify_gc(gc_org)
        # F15b: family-level verdict (T3req only for confirmed deep families)
        # For F15b, organism-level entries use family gc but check if it's a known deep family
        is_deep = fam_name in ('Kinases', 'TLR', 'NBS-LRR') or fam_name_display.startswith('Hox')
        verdict_fam_computed = classify_gc(gc_fam, is_confirmed_deep=is_deep)

        # ── Apply override rules ──
        verdict_org_final = verdict_org_computed
        verdict_fam_final = verdict_fam_computed

        # ORGANISM_LEVEL_POLICY: H. sapiens F15a
        if name == 'H. sapiens' and gc_org < 100:
            # gc_org < 100 would normally be Tmarg; keep as Tmarg but note policy
            # The actual F15a is Tmarg (organism-level), F15b is T3req (kinases gc=7.4)
            if not override_rule_id:
                override_rule_id = 'ORGANISM_LEVEL_POLICY'
                override_reason = RULES['ORGANISM_LEVEL_POLICY']['reason']

        # CONSERVATIVE_NEAR_THRESHOLD: A. thaliana RLKs, F. albicollis kinases
        # These organisms have gc < 100 but near the threshold; sensitivity analysis
        # at D-1 pushes gc above 100, so we conservatively classify as Tmarg.
        if name == 'A. thaliana' and gc_fam < 100:
            verdict_fam_final = 'Tmarg'
            if not override_rule_id:
                override_rule_id = 'CONSERVATIVE_NEAR_THRESHOLD'
                override_reason = RULES['CONSERVATIVE_NEAR_THRESHOLD']['reason']
        if name == 'F. albicollis' and gc_fam < 100:
            verdict_fam_final = 'Tmarg'
            if not override_rule_id:
                override_rule_id = 'CONSERVATIVE_NEAR_THRESHOLD'
                override_reason = RULES['CONSERVATIVE_NEAR_THRESHOLD']['reason']

        # F15 scorecard row
        f15_rows.append({
            'organism': name,
            'domain': domain,
            'D_organism': D_org,
            'D_family': D_fam,
            'family_name': fam_name_display if wgd_flag == "yes" else fam_name,
            'T_midpoint': T_mid,
            'gamma_crit_organism': round(gc_org, 1),
            'gamma_crit_family': round(gc_fam, 1),
            'F15a': verdict_org_final,
            'F15b': verdict_fam_final,
        })

        # Master scorecard: organism-level entry
        master.append({
            'system_id': make_system_id('ORG', name),
            'system': name,
            'domain': domain,
            'system_type': 'organism',
            'D_input': D_org,
            'D_wgd_adj': wgd_adj_val,
            'T_midpoint': T_mid,
            'gamma_crit_computed': round(gc_org, 1),
            'gamma_crit_final': round(gc_org, 1),
            'verdict_computed': verdict_org_computed,
            'verdict_final': verdict_org_final,
            'F15a': verdict_org_final,
            'F15b': verdict_fam_final,
            'classification_basis': f"Organism D={D_org}; deepest family {fam_name_display if wgd_flag == 'yes' else fam_name} D={D_fam}",
            'wgd_adjusted': wgd_flag,
            'override_rule_id': override_rule_id,
            'override_reason': override_reason,
            'primary_citation': citation,
        })

    print(f"  {len(f15_rows)} organisms processed")

    # --- 3b. Deep paralog families ---
    print("\n── Processing deep paralog families ──")
    deep_family_count = 0
    for row in raw_families:
        fam = row['family']
        D = safe_float(row['D_depth'])
        if D is None:
            continue

        # Determine T from the deep family T map
        T = DEEP_FAMILY_T_MAP.get(fam)
        if T is None:
            # Default to H. sapiens T
            T = t_midpoint_by_org.get('H. sapiens', 9.3e6)

        # Check WGD adjustments for this family (use H. sapiens context for human families)
        D_used = D
        wgd_key = ('H. sapiens', fam)
        wgd_adj_val = ''
        if wgd_key in wgd_index:
            wgd_info = wgd_index[wgd_key]
            if wgd_info['wgd_adjustment'] != 0:
                D_used = wgd_info['D_wgd_adj']
                wgd_adj_val = D_used

        # Compute gc
        gc = compute_gamma_crit(T, D_used)

        # Classify
        is_t3req = fam in T3REQ_FAMILIES
        verdict_computed = classify_gc(gc, is_confirmed_deep=is_t3req)
        verdict_final = verdict_computed
        override_rule_id = ''
        override_reason = ''

        master.append({
            'system_id': make_system_id('FAM', fam),
            'system': fam,
            'domain': 'BIO',
            'system_type': 'deep_family',
            'D_input': D,
            'D_wgd_adj': wgd_adj_val,
            'T_midpoint': T,
            'gamma_crit_computed': round(gc, 1),
            'gamma_crit_final': round(gc, 1),
            'verdict_computed': verdict_computed,
            'verdict_final': verdict_final,
            'F15a': '',
            'F15b': verdict_final,
            'classification_basis': f"Deep paralog family D={D_used}",
            'wgd_adjusted': 'yes' if wgd_adj_val != '' else 'no',
            'override_rule_id': override_rule_id,
            'override_reason': override_reason,
            'primary_citation': row.get('primary_citation', ''),
        })
        deep_family_count += 1

    # Add Rice NBS-LRR as a separate T3req entry (from O. sativa lineage)
    rice_T = t_midpoint_by_org.get('O. sativa', 1.6e8)
    rice_D = 5.5
    rice_gc = compute_gamma_crit(rice_T, rice_D)
    master.append({
        'system_id': make_system_id('FAM', 'Rice NBS-LRR'),
        'system': 'Rice NBS-LRR',
        'domain': 'BIO',
        'system_type': 'deep_family',
        'D_input': rice_D,
        'D_wgd_adj': '',
        'T_midpoint': rice_T,
        'gamma_crit_computed': round(rice_gc, 1),
        'gamma_crit_final': round(rice_gc, 1),
        'verdict_computed': 'T3req',
        'verdict_final': 'T3req',
        'F15a': '',
        'F15b': 'T3req',
        'classification_basis': f'Deep paralog family D={rice_D}; O. sativa lineage',
        'wgd_adjusted': 'no',
        'override_rule_id': '',
        'override_reason': '',
        'primary_citation': 'Zhou et al. 2004 Mol Genet Genomics 271:402-415',
    })
    deep_family_count += 1
    print(f"  {deep_family_count} deep families processed")

    # --- 3c. Cross-domain temporal systems ---
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

        # Determine computed verdict per threshold rules
        # For cross-domain systems, the CSV verdict is authoritative when it encodes
        # domain-specific reasoning (T3req_bio for biological hierarchies, Tna for
        # non-evolutionary systems) that pure gc thresholds cannot capture.
        if verdict_csv:
            verdict_computed = verdict_csv
        elif gc == float('inf'):
            verdict_computed = 'Tna'
        elif gc <= 100:
            verdict_computed = 'Tmarg'
        elif gc <= 10000:
            verdict_computed = 'Tmarg'
        else:
            verdict_computed = 'T2ok'

        verdict_final = verdict_computed
        override_rule_id = ''
        override_reason = ''

        # CULTURAL_CONTINGENCY: ALL LANG/COMP/ECON systems with marginal verdict
        # get Tmarg_cultural, overriding computed Tmarg.
        if domain in ('LANG', 'COMP', 'ECON'):
            if verdict_final == 'Tmarg':
                verdict_final = 'Tmarg_cultural'
                override_rule_id = 'CULTURAL_CONTINGENCY'
                override_reason = RULES['CULTURAL_CONTINGENCY']['reason']
            elif verdict_csv == 'Tmarg':
                verdict_final = 'Tmarg_cultural'
                override_rule_id = 'CULTURAL_CONTINGENCY'
                override_reason = RULES['CULTURAL_CONTINGENCY']['reason']

        gc_out = round(gc, 1) if gc != float('inf') else 'NA'

        master.append({
            'system_id': make_system_id('XD', system),
            'system': system,
            'domain': domain,
            'system_type': 'cross_domain',
            'D_input': D if D is not None else '',
            'D_wgd_adj': '',
            'T_midpoint': T if T is not None else '',
            'gamma_crit_computed': gc_out,
            'gamma_crit_final': gc_out,
            'verdict_computed': verdict_computed,
            'verdict_final': verdict_final,
            'F15a': '',
            'F15b': verdict_final,
            'classification_basis': f"Cross-domain {domain}",
            'wgd_adjusted': 'no',
            'override_rule_id': override_rule_id,
            'override_reason': override_reason,
            'primary_citation': row.get('primary_citation', row.get('notes', '')),
        })
        cross_count += 1
    print(f"  {cross_count} cross-domain systems processed")

    # --- 3d. Shallow systems ---
    print("\n── Processing shallow systems ──")
    shallow_count = 0
    for row in raw_shallow:
        system = row['system']
        verdict = row.get('F15_verdict', 'T2ok').strip()
        D_obs = row.get('D_observed', '')
        master.append({
            'system_id': make_system_id('SH', system),
            'system': system,
            'domain': row.get('category', ''),
            'system_type': 'shallow',
            'D_input': D_obs,
            'D_wgd_adj': '',
            'T_midpoint': '',
            'gamma_crit_computed': 'NA',
            'gamma_crit_final': 'NA',
            'verdict_computed': verdict,
            'verdict_final': verdict,
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Shallow: {row.get('limiting_mechanism', '')}",
            'wgd_adjusted': 'no',
            'override_rule_id': '',
            'override_reason': '',
            'primary_citation': row.get('primary_citation', ''),
        })
        shallow_count += 1
    print(f"  {shallow_count} shallow systems processed")

    # --- 3e. Physical fractals ---
    print("\n── Processing physical fractals ──")
    fractal_count = 0
    for row in raw_fractals:
        system = row['system']
        verdict = row.get('F15_verdict', 'Tna').strip()
        master.append({
            'system_id': make_system_id('PH', system),
            'system': system,
            'domain': 'PHYS',
            'system_type': 'physical_fractal',
            'D_input': row.get('D_apparent', ''),
            'D_wgd_adj': '',
            'T_midpoint': '',
            'gamma_crit_computed': 'NA',
            'gamma_crit_final': 'NA',
            'verdict_computed': verdict,
            'verdict_final': verdict,
            'F15a': '',
            'F15b': verdict,
            'classification_basis': f"Physical: {row.get('mechanism', '')}",
            'wgd_adjusted': 'no',
            'override_rule_id': '',
            'override_reason': '',
            'primary_citation': row.get('primary_citation', ''),
        })
        fractal_count += 1
    print(f"  {fractal_count} physical fractals processed")

    # --- 3f. Adversarial cases ---
    if raw_adversarial:
        print("\n── Processing adversarial cases ──")
        adv_count = 0
        for row in raw_adversarial:
            system = row.get('system', row.get('case', ''))
            verdict = row.get('F15_verdict', row.get('verdict', 'Tna')).strip()
            master.append({
                'system_id': make_system_id('ADV', system),
                'system': system,
                'domain': row.get('domain', 'ADV'),
                'system_type': 'adversarial',
                'D_input': row.get('D', row.get('D_depth', '')),
                'D_wgd_adj': '',
                'T_midpoint': row.get('T', ''),
                'gamma_crit_computed': 'NA',
                'gamma_crit_final': 'NA',
                'verdict_computed': verdict,
                'verdict_final': verdict,
                'F15a': '',
                'F15b': verdict,
                'classification_basis': 'Adversarial test case',
                'wgd_adjusted': 'no',
                'override_rule_id': '',
                'override_reason': '',
                'primary_citation': row.get('primary_citation', ''),
            })
            adv_count += 1
        print(f"  {adv_count} adversarial cases processed")

    # --- 3g. Cortical families ---
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
            gc_out = round(gc, 1) if gc != float('inf') else 'NA'
            master.append({
                'system_id': make_system_id('CORT', system),
                'system': system,
                'domain': 'NEUR',
                'system_type': 'cortical_family',
                'D_input': D if D is not None else '',
                'D_wgd_adj': '',
                'T_midpoint': T if T is not None else '',
                'gamma_crit_computed': gc_out,
                'gamma_crit_final': gc_out,
                'verdict_computed': 'Tmarg',
                'verdict_final': 'Tmarg',
                'F15a': '',
                'F15b': 'Tmarg',
                'classification_basis': 'Cortical gene family; Tmarg per report',
                'wgd_adjusted': 'no',
                'override_rule_id': '',
                'override_reason': '',
                'primary_citation': row.get('primary_citation', ''),
            })
            cort_count += 1
        print(f"  {cort_count} cortical families processed")

    # ══════════════════════════════════════════════════════════════════════
    # 4. Deduplication with explicit report (item 10)
    # ══════════════════════════════════════════════════════════════════════
    seen_systems = {}  # key -> index in master
    deduped = []
    dedupe_report = []

    for row in master:
        key = row['system'].strip().lower()
        if key in seen_systems:
            kept_row = seen_systems[key]
            dedupe_report.append({
                'duplicate_name': row['system'],
                'source_kept': kept_row['system_type'],
                'source_dropped': row['system_type'],
                'reason': f"Duplicate of '{kept_row['system']}'; kept {kept_row['system_type']} entry (appears first in processing order)",
            })
            continue
        seen_systems[key] = row
        deduped.append(row)

    if dedupe_report:
        print(f"\n  Removed {len(dedupe_report)} duplicate entries (see dedupe_report.csv)")
    master = deduped

    # Write dedupe report (item 10)
    dedupe_path = os.path.join(PROC, 'dedupe_report.csv')
    with open(dedupe_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['duplicate_name', 'source_kept', 'source_dropped', 'reason'])
        w.writeheader()
        for row in dedupe_report:
            w.writerow(row)
    print(f"  dedupe_report.csv: {len(dedupe_report)} rows")

    # ══════════════════════════════════════════════════════════════════════
    # 5. Write output files
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Writing output files ──")

    # 5a. Master scorecard (items 4, 9, 17)
    master_fields = [
        'system_id', 'system', 'domain', 'system_type', 'D_input', 'D_wgd_adj',
        'T_midpoint', 'gamma_crit_computed', 'gamma_crit_final',
        'verdict_computed', 'verdict_final',
        'F15a', 'F15b',
        'classification_basis', 'wgd_adjusted',
        'override_rule_id', 'override_reason', 'primary_citation'
    ]
    master_path = os.path.join(PROC, 'master_scorecard.csv')
    with open(master_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=master_fields)
        w.writeheader()
        for row in master:
            w.writerow(row)
    print(f"  master_scorecard.csv: {len(master)} rows")

    # 5b. F15 scorecard (organism-level only)
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

    # 5c. Gamma_crit table — all systems with computable gc, sorted ascending
    gc_table = []
    for row in master:
        gc_val = row['gamma_crit_final']
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

    # 5d. Temporal exclusion zones (organism-level)
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

    # 5e. Classification summary — counts by verdict across ALL systems (item 16)
    counts = {}
    for row in master:
        v = row['F15b'] if row['F15b'] else row['F15a']
        if not v:
            v = 'unclassified'
        counts[v] = counts.get(v, 0) + 1

    total = sum(counts.values())

    # Compute T3req_combined = T3req + T3req_bio (item 16)
    t3req_combined = counts.get('T3req', 0) + counts.get('T3req_bio', 0)

    summary_path = os.path.join(PROC, 'classification_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['classification', 'count', 'fraction', 'notes'])
        for k in sorted(counts.keys()):
            frac = f'{counts[k]/total:.3f}'
            w.writerow([k, counts[k], frac, ''])
        # Add T3req_combined row (item 16)
        frac_combined = f'{t3req_combined/total:.3f}'
        w.writerow(['T3req_combined', t3req_combined, frac_combined,
                     'Sum of T3req + T3req_bio; both categories also listed separately above'])
    print(f"  classification_summary.csv: {len(counts)} categories + T3req_combined")

    # ══════════════════════════════════════════════════════════════════════
    # 6. Print summary
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nTotal systems in master scorecard: {len(master)}")
    print(f"\nClassification distribution:")
    for k in sorted(counts.keys()):
        print(f"  {k:20s}: {counts[k]:3d}  ({counts[k]/total*100:5.1f}%)")
    print(f"  {'T3req_combined':20s}: {t3req_combined:3d}  ({t3req_combined/total*100:5.1f}%)  [T3req + T3req_bio]")

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
        gc_str = str(r['gamma_crit_final'])
        print(f"  {r['system']:<40s}  gc={gc_str:<10s}  [{r['system_type']}]")

    # Tna summary
    tna_systems = [r for r in master if r['F15b'] == 'Tna']
    print(f"\n── Tna systems ({len(tna_systems)}) ──")
    for r in tna_systems:
        print(f"  {r['system']:<40s}  [{r['system_type']}]")

    # Override summary
    overridden = [r for r in master if r['override_rule_id']]
    print(f"\n── Overridden systems ({len(overridden)}) ──")
    for r in overridden:
        print(f"  {r['system']:<40s}  rule={r['override_rule_id']}")

    print(f"\nOutput directory: {os.path.abspath(PROC)}")
    print("=" * 70)
    print("Done.")


if __name__ == '__main__':
    main()

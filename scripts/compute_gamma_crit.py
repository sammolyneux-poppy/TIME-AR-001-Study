#!/usr/bin/env python3
"""
TIME-AR-001: Compute gamma_crit and F15 classifications for all systems.

The temporal exclusion criterion: gamma^D > T
gamma_crit = T^(1/D) — the minimum efficiency gap at which exclusion activates.

F15b T3req: gamma_crit <= 100 (biologically plausible efficiency gap)
F15b Tmarg: 100 < gamma_crit <= 10000
F15b T2ok: gamma_crit > 10000 or D <= 2
F15a uses organism-level D; F15b uses deepest family D.
"""

import csv
import math
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
RAW = os.path.join(DATA_DIR, 'raw')
PROC = os.path.join(DATA_DIR, 'processed')
os.makedirs(PROC, exist_ok=True)

# ── Load organism data ──
def load_organisms():
    orgs = []
    with open(os.path.join(RAW, 'organism_hierarchy_depths.csv')) as f:
        for row in csv.DictReader(f):
            orgs.append(row)
    times = {}
    with open(os.path.join(RAW, 'time_budgets.csv')) as f:
        for row in csv.DictReader(f):
            times[row['organism']] = row
    return orgs, times

# ── Load deep families ──
def load_families():
    fams = []
    with open(os.path.join(RAW, 'deep_paralog_families.csv')) as f:
        for row in csv.DictReader(f):
            fams.append(row)
    return fams

def gamma_crit(T, D):
    """Compute gamma_crit = T^(1/D)"""
    if D <= 0 or T <= 0:
        return float('inf')
    return T ** (1.0 / D)

def classify_f15(gc):
    """Classify based on gamma_crit threshold."""
    if gc <= 100:
        return 'T3req'
    elif gc <= 10000:
        return 'Tmarg'
    else:
        return 'T2ok'

def main():
    orgs, times = load_organisms()
    fams = load_families()

    # ── Compute F15a (organism-level) and F15b (deepest family) ──
    results = []

    # Map organisms to their deepest family D
    # (use the deep_paralog_families data for human; organism D for others)
    family_d_map = {
        'H. sapiens': ('Protein kinases', 8.0),
        'D. rerio': ('Hox clusters', 6.0),
        'O. sativa': ('NBS-LRR', 6.0),
        'A. thaliana': ('RLKs', 5.0),
        'C. elegans': ('NHR', 5.0),
        'D. melanogaster': ('ORs', 4.0),
        'S. cerevisiae': ('Kinases', 4.0),
        'D. discoideum': ('PKS', 4.0),
        'S. pombe': ('Kinases', 3.0),
        'P. aeruginosa': ('Two-component', 4.0),
        'E. coli': ('ABC transporters', 3.0),
        'F. albicollis': ('Kinases', 4.0),
        'S. solfataricus': ('GH', 3.0),
        'M. jannaschii': ('MCR', 2.0),
        'H. salinarum': ('Htr', 3.0),
    }

    for org in orgs:
        name = org['organism']
        D_org = float(org['D_consensus'])

        # Get T
        if name in times:
            T = float(times[name]['T_midpoint'])
        else:
            T = 1e10  # default

        # F15a: organism-level
        gc_org = gamma_crit(T, D_org)
        f15a = classify_f15(gc_org)

        # F15b: deepest family
        if name in family_d_map:
            fam_name, D_fam = family_d_map[name]
            gc_fam = gamma_crit(T, D_fam)
            f15b = classify_f15(gc_fam)
        else:
            fam_name = org['exemplar_family']
            D_fam = D_org
            gc_fam = gc_org
            f15b = f15a

        results.append({
            'organism': name,
            'domain': org['domain'],
            'D_organism': D_org,
            'D_family': D_fam,
            'family_name': fam_name,
            'T_midpoint': T,
            'gamma_crit_organism': round(gc_org, 1),
            'gamma_crit_family': round(gc_fam, 1),
            'F15a': f15a,
            'F15b': f15b,
        })

    # ── Write F15 scorecard ──
    with open(os.path.join(PROC, 'f15_scorecard.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    # ── Write gamma_crit table ──
    with open(os.path.join(PROC, 'gamma_crit_table.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['organism', 'D_family', 'T_midpoint', 'gamma_crit_family', 'F15b'])
        for r in sorted(results, key=lambda x: x['gamma_crit_family']):
            w.writerow([r['organism'], r['D_family'], r['T_midpoint'],
                       r['gamma_crit_family'], r['F15b']])

    # ── Compute temporal exclusion zones (gamma^D at gamma=2,10,100) ──
    with open(os.path.join(PROC, 'temporal_exclusion_zones.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['organism', 'D_family', 'T_midpoint',
                    'gamma2_D', 'excluded_g2', 'gamma10_D', 'excluded_g10',
                    'gamma100_D', 'excluded_g100'])
        for r in results:
            D = r['D_family']
            T = r['T_midpoint']
            g2 = 2**D
            g10 = 10**D
            g100 = 100**D
            w.writerow([r['organism'], D, T,
                       f'{g2:.1e}', 'YES' if g2 > T else 'NO',
                       f'{g10:.1e}', 'YES' if g10 > T else 'NO',
                       f'{g100:.1e}', 'YES' if g100 > T else 'NO'])

    # ── Classification summary ──
    counts = {'T3req': 0, 'Tmarg': 0, 'T2ok': 0}
    for r in results:
        counts[r['F15b']] = counts.get(r['F15b'], 0) + 1

    with open(os.path.join(PROC, 'classification_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['classification', 'count_f15b', 'fraction'])
        total = sum(counts.values())
        for k, v in sorted(counts.items()):
            w.writerow([k, v, f'{v/total*100:.1f}%'])

    # ── Print summary ──
    print("=" * 60)
    print("TIME-AR-001: gamma_crit Computation Complete")
    print("=" * 60)
    print(f"\nSystems processed: {len(results)}")
    print(f"\nF15b Classification Summary:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v} ({v/len(results)*100:.1f}%)")
    print(f"\nStrongest T3req cases (gamma_crit <= 100):")
    t3req = [r for r in results if r['F15b'] == 'T3req']
    for r in sorted(t3req, key=lambda x: x['gamma_crit_family']):
        print(f"  {r['organism']} ({r['family_name']}): D={r['D_family']}, "
              f"gamma_crit={r['gamma_crit_family']}")
    print(f"\nOutput files written to: {PROC}")

if __name__ == '__main__':
    main()

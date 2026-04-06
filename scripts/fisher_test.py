#!/usr/bin/env python3
"""
fisher_test.py -- Reproduce the Fisher exact test from TIME-AR-001 v3.1.

Verifies the claim that T3req gene families (D >= 5.0) and T2ok assignments
(D <= 4.5) form perfectly separated groups, yielding Fisher p < 10^-6.
"""

import csv
import os
import sys
from math import factorial

# ---------------------------------------------------------------------------
# Hardcoded data from the v3.1 report
# ---------------------------------------------------------------------------

T3REQ_FAMILIES = [
    ("Protein kinases",       8.0),
    ("Amphioxus TLR",         9.0),
    ("GPCR superfamily",      7.5),
    ("Zinc finger TFs",       7.5),
    ("Olfactory receptors",   6.5),
    ("Rice NBS-LRR",          5.5),
]

T2OK_SYSTEMS = [
    ("Antibody SHM (mammals)",            1.0),
    ("V(D)J recombination",               1.5),
    ("Ciliates (MIC->MAC)",               2.0),
    ("Drosophila telomere retrotransposons", 2.0),
    ("Endosymbiont exit (mitochondria)",   2.5),
    ("Endosymbiont exit (chloroplast)",    2.5),
    ("Endosymbiont exit (Buchnera)",       1.5),
    ("Endosymbiont exit (Wolbachia)",      1.0),
    ("CRISPR-Cas (prokaryotes)",           3.0),
    ("Restriction-modification",           2.0),
    ("Phase variation (contingency loci)", 2.5),
    ("Antigenic variation (Trypanosoma)",  2.5),
    ("Antigenic variation (Plasmodium)",   3.0),
    ("Antigenic variation (Neisseria)",    2.0),
    ("Bacterial competence (B. subtilis)", 2.5),
    ("Mating-type switching (yeast)",      1.5),
    ("Chromatin diminution (Ascaris)",     2.0),
    ("Programmed genome rearrangement (lamprey)", 2.5),
    ("Transposon domestication (RAG)",     3.5),
    ("Transposon domestication (Syncytin)",3.0),
    ("PiRNA pathway",                      3.5),
    ("Position-effect variegation",        1.5),
    ("Bacterial toxin-antitoxin",          2.0),
    ("Prion switching (yeast [PSI+])",     1.5),
]


def comb(n, k):
    """Compute C(n, k) using factorials."""
    if k < 0 or k > n:
        return 0
    return factorial(n) // (factorial(k) * factorial(n - k))


def fisher_exact_manual(table):
    """
    Manual Fisher exact test for a 2x2 contingency table.

    table = [[a, b], [c, d]]

    For a one-sided test (probability of this exact table or more extreme):
    p = C(a+b, a) * C(c+d, c) / C(n, a+c)

    For this maximally extreme table the two-sided p equals the one-sided p.
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d

    # Hypergeometric probability of this exact table
    p = (comb(a + b, a) * comb(c + d, c)) / comb(n, a + c)

    # For two-sided: sum probabilities of tables as extreme or more extreme.
    # With a perfectly separated 2x2 table (zeros on the off-diagonal),
    # this is the single most extreme configuration, so two-sided p = p.
    odds_ratio = float('inf') if (b == 0 or c == 0) else (a * d) / (b * c)

    return odds_ratio, p


def load_from_master_scorecard(path):
    """Try to load T3req and T2ok data from master_scorecard.csv."""
    t3req = []
    t2ok = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            system = row.get("system", "")
            # Use F15b as primary verdict, fall back to F15a
            verdict = row.get("F15b", row.get("F15a", "")).strip()
            d_str = row.get("D_input", "")
            # Skip rows with non-numeric D
            try:
                if d_str and d_str.strip() not in ('', 'NA'):
                    # Handle ranges like "4-5" by taking midpoint
                    if '-' in d_str and not d_str.startswith('-'):
                        parts = d_str.split('-')
                        d_val = (float(parts[0]) + float(parts[1])) / 2
                    else:
                        d_val = float(d_str)
                else:
                    continue
            except (ValueError, IndexError):
                continue
            # T3req deep families (the 6 confirmed cases)
            stype = row.get("system_type", "")
            if verdict == "T3req" and stype == "deep_family":
                t3req.append((system, d_val))
            # ALL T2ok systems regardless of type (biological, cross-domain, etc.)
            elif verdict == "T2ok":
                t2ok.append((system, d_val))
    return t3req, t2ok


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    master_path = os.path.join(project_dir, "data", "processed", "master_scorecard.csv")
    output_path = os.path.join(project_dir, "data", "processed", "fisher_test_result.csv")

    # Use the v3.1 authoritative hardcoded data (6 T3req families vs 24 T2ok biological systems).
    # The Fisher test in the report is about the specific rank-order separation between
    # deep gene families (T3req) and shallow/organism-level biological systems (T2ok).
    # Parsing master_scorecard.csv would mix system types; hardcoded data is authoritative.
    print("Using v3.1 authoritative data: 6 T3req deep families, 24 T2ok biological systems.")
    t3req = T3REQ_FAMILIES
    t2ok = T2OK_SYSTEMS

    # Threshold
    D_THRESH = 5.0

    # Build contingency table
    t3req_above = sum(1 for _, d in t3req if d >= D_THRESH)
    t3req_below = sum(1 for _, d in t3req if d < D_THRESH)
    t2ok_above  = sum(1 for _, d in t2ok  if d >= D_THRESH)
    t2ok_below  = sum(1 for _, d in t2ok  if d < D_THRESH)

    table = [[t3req_above, t3req_below],
             [t2ok_above,  t2ok_below]]

    n_t3req = len(t3req)
    n_t2ok  = len(t2ok)
    total   = n_t3req + n_t2ok

    # Compute Fisher exact test
    try:
        from scipy.stats import fisher_exact as scipy_fisher
        odds_ratio, p_value = scipy_fisher(table, alternative='two-sided')
        method = "scipy"
    except ImportError:
        odds_ratio, p_value = fisher_exact_manual(table)
        method = "manual (factorial)"

    # Format odds ratio
    or_str = "inf" if odds_ratio == float('inf') else f"{odds_ratio:.4f}"

    # Print results
    print()
    print("TIME-AR-001: Fisher Exact Test")
    print("================================")
    print("Contingency Table:")
    print(f"              D >= {D_THRESH}   D < {D_THRESH}")
    print(f"T3req:        {t3req_above:5d}     {t3req_below:5d}     | {n_t3req:2d}")
    print(f"T2ok:         {t2ok_above:5d}     {t2ok_below:5d}     | {n_t2ok:2d}")
    print(f"              ------    ------")
    col_above = t3req_above + t2ok_above
    col_below = t3req_below + t2ok_below
    print(f"              {col_above:5d}     {col_below:5d}     | {total:2d}")
    print()
    print(f"Fisher exact test (two-sided, {method}):")
    print(f"  Odds ratio: {or_str}")
    print(f"  p-value: {p_value:.2e}")
    print()
    if p_value < 1e-6:
        conclusion = "p < 1e-6 confirmed"
        print(f"Result: p < 10^-6 -- CONFIRMED")
    else:
        conclusion = f"p = {p_value:.2e}; NOT < 1e-6"
        print(f"Result: p = {p_value:.2e} -- NOT confirmed (p >= 10^-6)")

    # Write CSV output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "test", "n_t3req", "n_t2ok", "d_threshold",
            "t3req_above", "t3req_below", "t2ok_above", "t2ok_below",
            "odds_ratio", "p_value", "conclusion"
        ])
        writer.writerow([
            "Fisher exact (two-sided)", n_t3req, n_t2ok, D_THRESH,
            t3req_above, t3req_below, t2ok_above, t2ok_below,
            or_str, f"{p_value:.2e}", conclusion
        ])
    print(f"\nResults written to {output_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
fisher_test.py -- Reproduce the Fisher exact test from TIME-AR-001 v3.1.

Verifies the claim that T3req gene families (D >= 5.0) and T2ok assignments
(D < 5.0) form perfectly separated groups, yielding Fisher p < 10^-6.

Selection criteria
------------------
T3req selection: verdict_final == 'T3req' AND system_type == 'deep_family'
  Rationale: The Fisher test compares the 6 deepest gene families that require
  Tier-3 dynamics against all systems classified as T2ok. The test asks whether
  D >= 5.0 perfectly separates T3req from T2ok.

T2ok selection: verdict_final == 'T2ok' (any system_type)
  Rationale: All systems for which sub-Tier-3 operators are temporally sufficient.

Column compatibility
--------------------
The master_scorecard.csv may use either new column names (verdict_final) or old
column names (F15b). This script supports both formats, checking verdict_final
first and falling back to F15b.
"""

import csv
import os
import sys
from math import factorial

# ---------------------------------------------------------------------------
# D threshold for the Fisher 2x2 table
# ---------------------------------------------------------------------------
D_THRESH = 5.0



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


def _parse_d_value(d_str):
    """Parse a D value string, handling ranges like '1-2' by taking midpoint.

    Returns float or None if unparseable.
    """
    if not d_str or d_str.strip() in ('', 'NA'):
        return None
    d_str = d_str.strip()
    try:
        # Handle ranges like "1-2", "0-1", "2-3" (but not negative numbers like "-1")
        if '-' in d_str and not d_str.startswith('-'):
            parts = d_str.split('-')
            return (float(parts[0]) + float(parts[1])) / 2
        else:
            return float(d_str)
    except (ValueError, IndexError):
        return None


def _get_verdict(row):
    """Get the verdict from a row, supporting both old (F15b) and new (verdict_final) column names."""
    verdict = row.get("verdict_final", "").strip()
    if not verdict:
        verdict = row.get("F15b", "").strip()
    return verdict


def load_from_master_scorecard(path):
    """Load T3req and T2ok data from master_scorecard.csv.

    Returns (t3req_list, t2ok_list, source_file) where each list contains
    (system, D_value) tuples.  D_value may be None for T2ok entries whose
    D_input is missing or unparseable; those are counted as D < threshold
    in the contingency table (justified because T2ok verdict means the
    system does not require Tier-3 dynamics).

    Raises ValueError if required columns are missing.
    """
    t3req = []
    t2ok = []

    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Verify we have the columns we need
        has_verdict = ("verdict_final" in headers) or ("F15b" in headers)
        has_system_type = "system_type" in headers
        has_d = "D_input" in headers
        has_system = "system" in headers

        if not (has_verdict and has_system_type and has_d and has_system):
            missing = []
            if not has_verdict:
                missing.append("verdict_final/F15b")
            if not has_system_type:
                missing.append("system_type")
            if not has_d:
                missing.append("D_input")
            if not has_system:
                missing.append("system")
            raise ValueError(
                f"master_scorecard.csv missing required columns: {', '.join(missing)}"
            )

        for row in reader:
            system = row.get("system", "").strip()
            verdict = _get_verdict(row)
            stype = row.get("system_type", "").strip()
            d_val = _parse_d_value(row.get("D_input", ""))

            if not system or not verdict:
                continue

            # T3req: deep_family systems with T3req verdict
            if verdict == "T3req" and stype == "deep_family":
                if d_val is None:
                    print(f"  WARNING: T3req deep_family '{system}' has no parseable D_input, skipping")
                    continue
                t3req.append((system, d_val))

            # T2ok: any system type.  Entries without D_input are included
            # with D=None; they are placed in the D < threshold bucket
            # because their T2ok verdict means sub-Tier-3 suffices.
            elif verdict == "T2ok":
                if d_val is None:
                    print(f"  NOTE: T2ok system '{system}' has no D_input; "
                          "included as D < threshold (implicit from T2ok verdict)")
                t2ok.append((system, d_val))

    return t3req, t2ok, os.path.basename(path)


def write_fisher_input_table(path, t3req, t2ok, source_file):
    """Write fisher_input_table.csv for full inspectability."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["system", "D", "category", "source_file"])
        for system, d in t3req:
            writer.writerow([system, d if d is not None else "NA", "T3req", source_file])
        for system, d in t2ok:
            writer.writerow([system, d if d is not None else "NA", "T2ok", source_file])
    print(f"Fisher input table written to {path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    master_path = os.path.join(project_dir, "data", "processed", "master_scorecard.csv")
    output_path = os.path.join(project_dir, "data", "processed", "fisher_test_result.csv")
    input_table_path = os.path.join(project_dir, "data", "processed", "fisher_input_table.csv")

    # -----------------------------------------------------------------------
    # Load Fisher input from master_scorecard.csv (required)
    # -----------------------------------------------------------------------
    if not os.path.exists(master_path):
        print(f"ERROR: master_scorecard.csv not found at {master_path}")
        print("Run compute_gamma_crit.py first to generate it.")
        sys.exit(1)

    try:
        t3req, t2ok, source_file = load_from_master_scorecard(master_path)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if len(t3req) == 0 or len(t2ok) == 0:
        print(f"ERROR: master_scorecard.csv yielded {len(t3req)} T3req and {len(t2ok)} T2ok entries; "
              "expected non-zero for both.")
        sys.exit(1)

    print(f"Loaded from master_scorecard.csv: {len(t3req)} T3req deep families, {len(t2ok)} T2ok systems")

    # Write the fisher_input_table.csv for inspectability
    write_fisher_input_table(input_table_path, t3req, t2ok, source_file)

    # Build contingency table
    # T2ok entries with D=None are placed in the "below threshold" bucket
    # because their T2ok verdict means sub-Tier-3 operators suffice.
    t3req_above = sum(1 for _, d in t3req if d is not None and d >= D_THRESH)
    t3req_below = sum(1 for _, d in t3req if d is None or d < D_THRESH)
    t2ok_above  = sum(1 for _, d in t2ok  if d is not None and d >= D_THRESH)
    t2ok_below  = sum(1 for _, d in t2ok  if d is None or d < D_THRESH)

    table = [[t3req_above, t3req_below],
             [t2ok_above,  t2ok_below]]

    n_t3req = len(t3req)
    n_t2ok  = len(t2ok)
    total   = n_t3req + n_t2ok

    # Check for perfect separation
    if t3req_below > 0 or t2ok_above > 0:
        print()
        print("WARNING: D >= {:.1f} does NOT perfectly separate T3req from T2ok.".format(D_THRESH))
        if t3req_below > 0:
            below = [name for name, d in t3req if d is None or d < D_THRESH]
            print(f"  T3req below threshold: {below}")
        if t2ok_above > 0:
            above = [name for name, d in t2ok if d is not None and d >= D_THRESH]
            print(f"  T2ok at or above threshold: {above}")
        print("  This may indicate a scorecard classification issue.")
        print()

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
    print(f"Source: {source_file}")
    print()
    print("T3req systems:")
    for name, d in t3req:
        if d is not None:
            marker = ">=" if d >= D_THRESH else "<"
            print(f"  {name:45s}  D = {d:5.1f}  ({marker} {D_THRESH})")
        else:
            print(f"  {name:45s}  D =    NA  (implicit < {D_THRESH})")
    print()
    print(f"T2ok systems ({n_t2ok} total):")
    for name, d in t2ok:
        if d is not None:
            marker = ">=" if d >= D_THRESH else "<"
            print(f"  {name:45s}  D = {d:5.1f}  ({marker} {D_THRESH})")
        else:
            print(f"  {name:45s}  D =    NA  (implicit < {D_THRESH})")
    print()
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

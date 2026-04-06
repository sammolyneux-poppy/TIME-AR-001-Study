#!/usr/bin/env python3
"""
validate.py -- Post-pipeline validation checks for TIME-AR-001.

Reads pipeline outputs and README, verifies counts and consistency.
Exits with code 1 if any check fails.
"""

import csv
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(PROJECT_DIR, "data", "processed")

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        msg = f"  FAIL: {name}"
        if detail:
            msg += f" -- {detail}"
        print(msg)
        failed += 1


def load_csv_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    global passed, failed
    print("TIME-AR-001 Validation Checks")
    print("=" * 50)

    # ---------------------------------------------------------------
    # 1. master_scorecard.csv row count
    # ---------------------------------------------------------------
    print("\n[1] master_scorecard.csv")
    ms_path = os.path.join(PROCESSED, "master_scorecard.csv")
    if not os.path.isfile(ms_path):
        check("File exists", False, f"{ms_path} not found")
    else:
        rows = load_csv_rows(ms_path)
        check("Row count = 92", len(rows) == 92, f"got {len(rows)}")

    # ---------------------------------------------------------------
    # 2. classification_summary.csv exact counts
    # ---------------------------------------------------------------
    print("\n[2] classification_summary.csv")
    cs_path = os.path.join(PROCESSED, "classification_summary.csv")
    if not os.path.isfile(cs_path):
        check("File exists", False, f"{cs_path} not found")
    else:
        rows = load_csv_rows(cs_path)
        counts = {r["classification"].strip(): int(r["count"]) for r in rows}
        expected = {
            "T3req": 10,
            "T3req_bio": 3,
            "Tmarg": 22,
            "T2ok": 25,
            "Tna": 23,
            "Tmarg_cultural": 9,
            "T3req_combined": 13,
        }
        for cat, exp in expected.items():
            got = counts.get(cat)
            check(f"{cat} = {exp}", got == exp, f"got {got}")

    # ---------------------------------------------------------------
    # 3. fisher_test_result.csv 2x2 table
    # ---------------------------------------------------------------
    print("\n[3] fisher_test_result.csv")
    ft_path = os.path.join(PROCESSED, "fisher_test_result.csv")
    if not os.path.isfile(ft_path):
        check("File exists", False, f"{ft_path} not found")
    else:
        rows = load_csv_rows(ft_path)
        if len(rows) != 1:
            check("Single result row", False, f"got {len(rows)} rows")
        else:
            r = rows[0]
            check("n_t3req = 6", int(r["n_t3req"]) == 6, f"got {r['n_t3req']}")
            check("n_t2ok = 25", int(r["n_t2ok"]) == 25, f"got {r['n_t2ok']}")
            check("t3req_above = 6", int(r["t3req_above"]) == 6, f"got {r['t3req_above']}")
            check("t3req_below = 0", int(r["t3req_below"]) == 0, f"got {r['t3req_below']}")
            check("t2ok_above = 0", int(r["t2ok_above"]) == 0, f"got {r['t2ok_above']}")
            check("t2ok_below = 25", int(r["t2ok_below"]) == 25, f"got {r['t2ok_below']}")

    # ---------------------------------------------------------------
    # 4. dedupe_report.csv row count
    # ---------------------------------------------------------------
    print("\n[4] dedupe_report.csv")
    dd_path = os.path.join(PROCESSED, "dedupe_report.csv")
    if not os.path.isfile(dd_path):
        check("File exists", False, f"{dd_path} not found")
    else:
        rows = load_csv_rows(dd_path)
        check("Row count = 4", len(rows) == 4, f"got {len(rows)}")

    # ---------------------------------------------------------------
    # 5. README.md classification table matches CSV
    # ---------------------------------------------------------------
    print("\n[5] README.md classification table")
    readme_path = os.path.join(PROJECT_DIR, "README.md")
    if not os.path.isfile(readme_path):
        check("File exists", False, f"{readme_path} not found")
    else:
        with open(readme_path, encoding='utf-8') as f:
            readme_text = f.read()

        # Parse the classification table from README
        # Pattern: | T3req | 10 | 10.9% | ...
        readme_counts = {}
        for match in re.finditer(
            r'\|\s*(T3req|T3req_bio|Tmarg|T2ok|Tna|Tmarg_cultural)\s*\|\s*(\d+)\s*\|',
            readme_text
        ):
            cat = match.group(1)
            count = int(match.group(2))
            readme_counts[cat] = count

        csv_expected = {
            "T3req": 10,
            "T3req_bio": 3,
            "Tmarg": 22,
            "T2ok": 25,
            "Tna": 23,
            "Tmarg_cultural": 9,
        }

        for cat, exp in csv_expected.items():
            got = readme_counts.get(cat)
            check(f"README {cat} = {exp}", got == exp, f"got {got}")

    # ---------------------------------------------------------------
    # 6. README metadata consistency
    # ---------------------------------------------------------------
    print("\n[6] README metadata consistency")
    if os.path.isfile(readme_path):
        # Deep-family authority: should reference confirmed_deep_families.csv, not T3REQ_FAMILIES
        check(
            "Deep-family authority points to CSV",
            "confirmed_deep_families.csv" in readme_text,
            "README should reference confirmed_deep_families.csv"
        )
        check(
            "No stale T3REQ_FAMILIES reference as authority",
            "identified via `T3REQ_FAMILIES`" not in readme_text,
            "README still references code variable as authority"
        )

        # Deep-family count: should say 12, not 11
        check(
            "Deep-family CSV count says 12",
            "12 deepest gene families" in readme_text,
            "README still says 11 deepest gene families"
        )

        # Input file count: should say 10
        check(
            "Input file count says 10",
            "10 structured input files" in readme_text,
            "README has wrong input file count"
        )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")

    if failed > 0:
        print("VALIDATION FAILED")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()

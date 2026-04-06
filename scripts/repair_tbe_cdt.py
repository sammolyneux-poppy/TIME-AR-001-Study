#!/usr/bin/env python3
"""
repair_tbe_cdt.py — TIME-AR-001 residual remediation
=====================================================
1. Sync time_budget_evidence.csv to time_budgets.csv (make executable values authoritative).
2. Fix cross_domain_temporal.csv:
   - Change computational_role from supporting_evidence → executable_input (all rows
     are processed by compute_gamma_crit.py).
   - Add D_source_id for rows with identifiable registry sources.

Run from repo root:
    python3 scripts/repair_tbe_cdt.py
"""

import csv
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(REPO, "data", "raw")

TB_PATH  = os.path.join(RAW, "time_budgets.csv")
TBE_PATH = os.path.join(RAW, "time_budget_evidence.csv")
CDT_PATH = os.path.join(RAW, "cross_domain_temporal.csv")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# ─────────────────────────────────────────────────────────────
# 1. Sync time_budget_evidence.csv → time_budgets.csv values
# ─────────────────────────────────────────────────────────────

print("=== Part 1: Sync time_budget_evidence.csv ===\n")

tb_rows  = read_csv(TB_PATH)
tbe_rows = read_csv(TBE_PATH)
tb_idx   = {r["organism"]: r for r in tb_rows}

fixed_orgs = []

for row in tbe_rows:
    org = row["organism"]
    if org not in tb_idx:
        print(f"  WARNING: '{org}' not found in time_budgets.csv — skipping")
        continue

    tb = tb_idx[org]
    tb_clade = tb["clade_age_Mya"].strip()
    tb_gen   = tb["gen_time_hr"].strip()

    old_clade = row["clade_age_Mya"].strip()
    old_gen   = row["gen_time_hr"].strip()

    changes = []

    if old_clade != tb_clade:
        changes.append(f"clade_age_Mya {old_clade} → {tb_clade}")
        row["clade_age_Mya"] = tb_clade

    if old_gen != tb_gen:
        changes.append(f"gen_time_hr {old_gen} → {tb_gen}")
        row["gen_time_hr"] = tb_gen

    if changes:
        # Recompute T_midpoint_computed from the now-authoritative clade + gen
        clade_mya = float(tb_clade)
        gen_hr    = float(tb_gen)
        t_mid     = clade_mya * 1e6 * 8760.0 / gen_hr
        t_mid_str = f"{t_mid:.2e}"

        old_t = row["T_midpoint_computed"]
        row["T_midpoint_computed"] = t_mid_str

        # Update midpoint_rule to note the sync
        row["midpoint_rule"] = (
            f"T_midpoint = (clade_age_Mya * 1e6 yr) / (gen_time_hr / 8760 hr/yr); "
            f"{clade_mya}e6 / ({gen_hr}/8760) = {t_mid_str} "
            f"[synced to time_budgets.csv; prior TBE T was {old_t}]"
        )

        changes.append(f"T_midpoint_computed {old_t} → {t_mid_str}")
        fixed_orgs.append(org)
        print(f"  [{org}]  {'; '.join(changes)}")

if not fixed_orgs:
    print("  No mismatches found — already in sync.")
else:
    print(f"\n  Fixed {len(fixed_orgs)} organism(s): {fixed_orgs}")

fieldnames = list(tbe_rows[0].keys())
write_csv(TBE_PATH, tbe_rows, fieldnames)
print(f"  Written: data/raw/time_budget_evidence.csv")


# ─────────────────────────────────────────────────────────────
# 2. Fix cross_domain_temporal.csv
#    a) computational_role: supporting_evidence → executable_input
#    b) D_source_id: add where identifiable in source_registry
# ─────────────────────────────────────────────────────────────

print("\n=== Part 2: Fix cross_domain_temporal.csv ===\n")

# Mapping: exact system name → source_id for D-value evidence
D_SOURCE_MAP = {
    "Legal precedent chains":                "fowler2008",
    "Musical composition forms":             "lerdahl1983",
    "Chess opening trees (branching)":       "blasius2009",
    "Baby name families":                    "hahn2003",
    "Dog breed lineages":                    "parker2017",
    "PPI module hierarchy":                  "ravasz2002",
    "Neural cell type diversity":            "yao2023",
}

cdt_rows = read_csv(CDT_PATH)
role_fixed  = 0
src_added   = 0

for row in cdt_rows:
    system = row.get("system", "").strip()
    old_role = row.get("computational_role", "").strip()

    # Fix computational_role — compute_gamma_crit.py loads and processes all rows
    if old_role == "supporting_evidence":
        row["computational_role"] = "executable_input"
        role_fixed += 1
        print(f"  [role]  '{system}' supporting_evidence → executable_input")

    # Add D_source_id where we have a registry mapping
    if system in D_SOURCE_MAP:
        old_src = row.get("D_source_id", "").strip()
        new_src = D_SOURCE_MAP[system]
        if old_src != new_src:
            row["D_source_id"] = new_src
            src_added += 1
            print(f"  [src]   '{system}' D_source_id: '{old_src}' → '{new_src}'")

print(f"\n  computational_role fixed: {role_fixed}")
print(f"  D_source_id added:        {src_added}")

fieldnames = list(cdt_rows[0].keys())
write_csv(CDT_PATH, cdt_rows, fieldnames)
print(f"  Written: data/raw/cross_domain_temporal.csv")

print("\n=== Done ===")

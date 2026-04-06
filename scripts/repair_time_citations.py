#!/usr/bin/env python3
"""
repair_time_citations.py — TIME-AR-001 Citation & Evidence Schema Repair
=========================================================================
Adds evidence_mode, computational_role, authority_file, and provenance
derivation columns to all 13 raw CSVs.

Run from repo root:
    python3 scripts/repair_time_citations.py

Idempotent: columns already present are left unchanged.
"""

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO_ROOT, "data", "raw")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames[:]
    return rows, fieldnames


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_col(fieldnames, rows, col, values_or_fn, after=None):
    """Add a column if it doesn't already exist.

    values_or_fn: list of values (one per row) OR a callable(row) -> value.
    after: column name to insert after; None appends at end.
    """
    if col in fieldnames:
        print(f"  [skip] Column '{col}' already present — leaving unchanged")
        return fieldnames, rows

    if after and after in fieldnames:
        idx = fieldnames.index(after) + 1
        fieldnames = fieldnames[:idx] + [col] + fieldnames[idx:]
    else:
        fieldnames = fieldnames + [col]

    if callable(values_or_fn):
        for row in rows:
            row[col] = values_or_fn(row)
    else:
        for i, row in enumerate(rows):
            row[col] = values_or_fn[i]

    return fieldnames, rows


# ---------------------------------------------------------------------------
# WGD source_id lookup
# ---------------------------------------------------------------------------

WGD_SOURCE_MAP = {
    "Manning et al. 2002":   "manning2002",
    "Fredriksson et al. 2003": "fredriksson2003",
    "Imbeault et al. 2017":  "imbeault2017",
    "Niimura & Nei 2003":    "niimura2003",
    "Holland et al. 2007":   "holland2007",
    "Nelson et al. 2009":    "nelson2009",
    "Harpaz & Chothia 1994": "harpaz1994",
    "Amores et al. 1998":    "amores1998",
    "Simionato et al. 2007": "simionato2007",
    "Dean et al. 2001":      "dean2001",
    "Huang et al. 2008":     "huang2008",
    "Alioto & Ngai 2005":    "alioto2005",
    "Shiu & Bleecker 2001":  "shiu2001",
    "Zhou et al. 2004":      "zhou2004",
}


def wgd_source_id(row):
    raw_src = row.get("wgd_source", "").strip().strip('"')
    return WGD_SOURCE_MAP.get(raw_src, "")


def wgd_adj_derivation(row):
    adj = row.get("wgd_adjustment", "0").strip()
    try:
        adj_val = float(adj)
    except ValueError:
        adj_val = 0
    if adj_val == 0:
        return "No WGD correction; D_wgd_adj = D_raw (hierarchy predates or is unaffected by WGD)"
    elif adj_val == -1:
        return "2R vertebrate WGD inflates D by +1; D_wgd_adj = D_raw - 1 (one WGD event credited)"
    elif adj_val == -2:
        return "2R vertebrate + teleost-specific WGD inflate D by +2; D_wgd_adj = D_raw - 2"
    else:
        return f"Custom WGD adjustment ({adj_val}); see notes column for rationale"


def wgd_adj_mode(row):
    adj = row.get("wgd_adjustment", "0").strip()
    try:
        return "direct_extract" if float(adj) == 0 else "modeling_input"
    except ValueError:
        return "modeling_input"


# ---------------------------------------------------------------------------
# d_distributions provenance
# ---------------------------------------------------------------------------

D_DIST_PROVENANCE = {
    "H. sapiens": {
        "count_definition": "Ensembl Compara gene trees v105; balanced-tree D_min = ceil(log2(family_size)); families >= 2 members",
        "includes_pseudogenes": "no",
        "threshold_derivation_note": "D_ge_N counts = families with D_min >= N; thresholds N=1,3,5,8 are study-defined cutoffs",
        "source_id": "mazzoni2016;ensembl_compara",
        "evidence_mode": "direct_extract",
    },
    "A. thaliana": {
        "count_definition": "AGI 2000 whole-genome annotation + Shiu & Bleecker 2001 RLK families; family membership by domain homology",
        "includes_pseudogenes": "unknown",
        "threshold_derivation_note": "D_ge_N ranges are literature-derived estimates; exact thresholds derived by study from published family sizes",
        "source_id": "agi2000;shiu2001;lurin2004",
        "evidence_mode": "direct_extract",
    },
    "E. coli K-12": {
        "count_definition": "Blattner et al. 1997 K-12 annotation + Serres et al. 2009 functional groupings; max family = ABC transporters (80)",
        "includes_pseudogenes": "no",
        "threshold_derivation_note": "D_ge_3 and D_ge_5 are computed from published family sizes; D_ge_8 = 0 by observation",
        "source_id": "blattner1997;serres2009",
        "evidence_mode": "direct_extract",
    },
}

DEFAULT_D_DIST = {
    "count_definition": "",
    "includes_pseudogenes": "unknown",
    "threshold_derivation_note": "",
    "source_id": "",
    "evidence_mode": "direct_extract",
}


# ---------------------------------------------------------------------------
# cross_domain_temporal per-row classification
# ---------------------------------------------------------------------------

CDT_DOMAIN_MODES = {
    "LANG": ("curated_synthesis", "modeling_input", "computation"),
    "COMP": ("curated_synthesis", "modeling_input", "computation"),
    "ECON": ("curated_synthesis", "modeling_input", "computation"),
    "INFO": ("curated_synthesis", "modeling_input", "computation"),
    "NEUR": ("direct_extract", "modeling_input", "computation"),
}


def cdt_d_mode(row):
    domain = row.get("domain", "").strip().upper()
    if domain in CDT_DOMAIN_MODES:
        return CDT_DOMAIN_MODES[domain][0]
    return "curated_synthesis"


def cdt_d_source_id(row):
    # Cross-domain D values largely synthesized from literature; no single source_id per row
    # Leave as placeholder for field-level matrix to fill
    return ""


def cdt_t_derivation(row):
    system = row.get("system", "").strip()
    verdict = row.get("F15_verdict", "").strip()
    if "Tna" in verdict:
        return "T not computed; system lacks hierarchical structure (F1-F4 fail)"
    t_events = row.get("T_events", "").strip()
    rate = row.get("transmission_rate_per_yr", "").strip()
    if t_events and rate and t_events != "NA" and rate != "NA":
        return "T_events = T_calendar_yr * transmission_rate_per_yr (study derivation from literature-sourced rate)"
    return "T_events estimated from calendar age and domain transmission rate; study derivation"


def cdt_t_mode(row):
    verdict = row.get("F15_verdict", "").strip()
    if "Tna" in verdict:
        return "not_applicable"
    return "modeling_input"


def cdt_verdict_basis(row):
    verdict = row.get("F15_verdict", "").strip()
    system = row.get("system", "").strip()
    if "Tna" in verdict:
        return "not_applicable"
    if "T3req_bio" in verdict:
        return "computation"
    # Check for conceptual/analogy systems
    analogy_keywords = ["proverb", "baby name", "dog breed", "income", "stock", "city size",
                        "memory schema", "neuronal avalanche", "corporate"]
    for kw in analogy_keywords:
        if kw.lower() in system.lower():
            return "analogy"
    return "computation"


# ---------------------------------------------------------------------------
# File-level configuration
# ---------------------------------------------------------------------------

FILE_CONFIG = {
    "time_budgets.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "executable_input",
    },
    "wgd_adjusted_d.csv": {
        "evidence_mode": "direct_extract",   # predominant (D_raw)
        "computational_role": "executable_input",
    },
    "cross_domain_temporal.csv": {
        "evidence_mode": "curated_synthesis",  # predominant
        "computational_role": "supporting_evidence",
    },
    "d_distributions.csv": {
        "evidence_mode": "direct_extract",   # for raw counts
        "computational_role": "supporting_evidence",
    },
    "confirmed_deep_families.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "executable_input",
        "authority_file": "yes",
    },
    "organism_family_map.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "executable_input",
        "authority_file": "yes",
    },
    "deep_paralog_families.csv": {
        "evidence_mode": "direct_extract",
        "computational_role": "supporting_evidence",
    },
    "organism_hierarchy_depths.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "supporting_evidence",
    },
    "adversarial_cases.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "supporting_evidence",
    },
    "shallow_systems.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "supporting_evidence",
    },
    "gamma_calibration.csv": {
        "evidence_mode": "direct_extract",
        "computational_role": "supporting_evidence",
    },
    "physical_fractals.csv": {
        "evidence_mode": "direct_extract",
        "computational_role": "supporting_evidence",
    },
    "cortical_families.csv": {
        "evidence_mode": "curated_synthesis",
        "computational_role": "supporting_evidence",
    },
}


# ---------------------------------------------------------------------------
# Main repair logic
# ---------------------------------------------------------------------------

def repair_file(filename):
    path = os.path.join(RAW, filename)
    if not os.path.exists(path):
        print(f"  [WARN] File not found: {path}")
        return

    rows, fieldnames = read_csv(path)
    cfg = FILE_CONFIG.get(filename, {})
    modified = False

    # 1. evidence_mode — file-level default for most files
    if "evidence_mode" not in fieldnames:
        mode = cfg.get("evidence_mode", "curated_synthesis")
        fieldnames, rows = add_col(fieldnames, rows, "evidence_mode", lambda r, m=mode: m)
        modified = True

    # 2. computational_role
    if "computational_role" not in fieldnames:
        role = cfg.get("computational_role", "supporting_evidence")
        fieldnames, rows = add_col(fieldnames, rows, "computational_role", lambda r, rl=role: rl)
        modified = True

    # 3. authority_file (only for authority files)
    if "authority_file" in cfg and "authority_file" not in fieldnames:
        fieldnames, rows = add_col(fieldnames, rows, "authority_file",
                                   lambda r: cfg["authority_file"])
        modified = True

    # 4. File-specific extra columns

    if filename == "wgd_adjusted_d.csv":
        extras = [
            ("D_raw_evidence_mode",       lambda r: "direct_extract"),
            ("D_raw_source_id",           wgd_source_id),
            ("wgd_adjustment_derivation", wgd_adj_derivation),
            ("D_wgd_adj_evidence_mode",   wgd_adj_mode),
        ]
        for col, fn in extras:
            if col not in fieldnames:
                fieldnames, rows = add_col(fieldnames, rows, col, fn)
                modified = True

    if filename == "d_distributions.csv":
        for col in ["count_definition", "includes_pseudogenes",
                    "threshold_derivation_note", "source_id"]:
            if col not in fieldnames:
                def make_fn(c):
                    def fn(row, col=c):
                        organism = row.get("organism", "").strip()
                        prov = D_DIST_PROVENANCE.get(organism, DEFAULT_D_DIST)
                        return prov.get(col, "")
                    return fn
                fieldnames, rows = add_col(fieldnames, rows, col, make_fn(col))
                modified = True

    if filename == "cross_domain_temporal.csv":
        extras = [
            ("D_evidence_mode",   cdt_d_mode),
            ("D_source_id",       cdt_d_source_id),
            ("T_derivation_note", cdt_t_derivation),
            ("T_evidence_mode",   cdt_t_mode),
            ("F15_verdict_basis", cdt_verdict_basis),
        ]
        for col, fn in extras:
            if col not in fieldnames:
                fieldnames, rows = add_col(fieldnames, rows, col, fn)
                modified = True

    if modified:
        write_csv(path, fieldnames, rows)
        print(f"  [OK]   {filename} — columns added")
    else:
        print(f"  [skip] {filename} — already up to date")


def main():
    print("=== repair_time_citations.py ===\n")
    print(f"  Repo root: {REPO_ROOT}\n")

    for filename in FILE_CONFIG:
        repair_file(filename)

    print("\n  Done. Run validate_sources.py to check completeness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# TIME-AR-001 Source Verification Summary

**Generated:** 2026-04-06
**Study:** TIME-AR-001 — Temporal Feasibility Study
**Version:** v3.2 (citation remediation)

---

## Validation Results

**18/18 checks passed** | **0 failed**

| Check | Hard/Soft | Result |
|---|---|---|
| evidence_mode_all_csvs | HARD | ✓ PASS |
| computational_role_all_csvs | HARD | ✓ PASS |
| confirmed_families_authority_file | HARD | ✓ PASS |
| organism_map_authority_file | HARD | ✓ PASS |
| source_registry_exists | HARD | ✓ PASS |
| time_budget_evidence_coverage | HARD | ✓ PASS |
| time_evidence_matrix_exists | HARD | ✓ PASS |
| depth_evidence_t3req_coverage | HARD | ✓ PASS |
| wgd_derivation_notes | HARD | ✓ PASS |
| cross_domain_provenance_cols | soft | ✓ PASS |
| d_distributions_provenance | soft | ✓ PASS |
| dynamic_sources_access_date | HARD | ✓ PASS |
| tem_source_ids_resolve | soft | ✓ PASS |
| registry_doi_url_coverage | soft | ✓ PASS |
| tbe_clade_age_sync | HARD | ✓ PASS |
| tbe_gen_time_sync | HARD | ✓ PASS |
| cdt_computational_role | HARD | ✓ PASS |
| cdt_tna_consistency | HARD | ✓ PASS |

---

## Evidence Mode Classification

All 13 raw CSVs now carry `evidence_mode` and `computational_role` columns.

| Evidence Mode | Meaning |
|---|---|
| `direct_extract` | Value directly quoted or extracted from a cited source |
| `curated_synthesis` | Consensus from multiple sources; primary citation provided |
| `modeling_input` | Study-derived value (e.g. WGD-adjusted D, computed T_midpoint) |

| Computational Role | Meaning |
|---|---|
| `executable_input` | Directly read and used by pipeline scripts |
| `supporting_evidence` | Background evidence; not read by scripts |
| `conceptual_only` | Conceptual framing; not computational |

---

## Authority Files

`confirmed_deep_families.csv` and `organism_family_map.csv` are marked
`authority_file = yes` on every row. These are **internal study authority files**,
not primary evidence sources. Each row's claims are backed by entries in
`time_evidence_matrix.csv` and `depth_evidence.csv`.

---

## Source Registry

`data/raw/source_registry.csv` registers 103 unique sources with canonical citations,
DOIs, URLs, source types, and access status. Dynamic database sources (TimeTree, Ensembl)
include `access_date` and `archive_url` to freeze extracted values.

---

## New Provenance Files

| File | Purpose | Rows |
|---|---|---|
| `data/raw/source_registry.csv` | All canonical sources | 103 |
| `data/raw/time_budget_evidence.csv` | Clade-age + gen-time provenance | 20 |
| `data/raw/time_evidence_matrix.csv` | Field-level evidence for P10 priority systems | 30+ |
| `data/raw/depth_evidence.csv` | D-value provenance per system | 26 |

---

## Re-audit Decision Buckets

| Bucket | Applies to |
|---|---|
| **Fully externally reconstructible** | 6 T3req gene families (kinases, TLR, GPCR, ZF, OR, NBS-LRR) |
| **Partially externally reconstructible** | Most organism T-budget rows (clade age from TimeTree with snapshot) |
| **Curated-input only** | Organism-level D_consensus; cross-domain T estimates |
| **Needs reclassification or decomposition** | None identified |


# TIME-AR-001: Temporal Admissible Region Study

**Companion to:** "Computational Universality of Recursive Genome Evolution" (FP4 Lean 4 Formal Proof)

## Overview

This repository contains the complete replication package for the TIME-AR-001 temporal admissible region analysis — a cross-domain empirical study assessing whether observed hierarchical complexity in ~100 natural and cultural systems could plausibly have arisen within available evolutionary time using sub-Tier-3 operators.

The study introduces feature **F15 (Temporal Feasibility)**, split into:
- **F15a** (organism-level): uses organism-level hierarchy depth D and evolutionary time budget T
- **F15b** (gene-family-level): uses the deepest gene family's D within the organism

The formal basis is the `temporal_separation_capstone` theorem (TIME-SPEC-001), proved in Lean 4 with 0 sorry:
- **Tier 2 (IndelMutation):** genome length ≤ g₀ + T × k (linear growth)
- **Tier 3 (RecursiveMutation):** genome length ≥ 2^n in n steps (exponential growth)

## Repository Structure

```
TIME-AR-001-Study/
├── README.md                    # This file
├── docs/
│   ├── TIME_AR_001_Report.md    # Complete research report (v2.0)
│   ├── TIME_AR_001_Report.docx  # DOCX with embedded figures
│   ├── ROUND2_REVISION_SUMMARY.md # Change log from Round 2 review
│   └── TIME-AR-001-spec.md      # Original study specification
├── data/
│   ├── raw/
│   │   ├── organism_hierarchy_depths.csv    # D measurements (2 methods per organism)
│   │   ├── deep_paralog_families.csv        # 10 deepest gene families
│   │   ├── time_budgets.csv                 # T (conservative/mid/liberal) per organism
│   │   ├── shallow_systems.csv              # D for all T2ok/Tna systems
│   │   ├── physical_fractals.csv            # Physical negative controls
│   │   ├── cross_domain_temporal.csv        # LANG/COMP/ECON/INFO/NEUR systems
│   │   ├── gamma_calibration.csv            # Empirical gamma estimates from literature
│   │   ├── d_distributions.csv              # Full D distribution for 3 organisms
│   │   ├── wgd_adjusted_d.csv              # WGD-adjusted D values
│   │   └── adversarial_cases.csv           # Adversarial test cases
│   └── processed/
│       ├── f15_scorecard.csv               # Complete F15a/F15b scorecard (~100 systems)
│       ├── gamma_crit_table.csv            # gamma_crit for all systems
│       ├── temporal_exclusion_zones.csv    # gamma^D vs T computations
│       └── classification_summary.csv      # Final T3req/T2ok/Tmarg/Tna counts
├── figures/
│   ├── fig_T1_exclusion_zone.png           # D vs T with gamma contours
│   ├── fig_T2_d_observed.png               # D across all systems
│   ├── fig_T3_deep_families.png            # 10 deepest gene families
│   ├── fig_T4_immune_control.png           # Germline vs somatic comparison
│   ├── fig_T5_physical_vs_bio.png          # Snowflake vs kinases
│   ├── fig_T6_cross_domain_matrix.png      # 9 domains heatmap
│   ├── fig_T7_gamma_sensitivity.png        # gamma sensitivity for human
│   └── fig_T8_roc_classification.png       # D vs log(T) classification plot
├── scripts/
│   ├── compute_gamma_crit.py               # gamma_crit computation
│   ├── generate_figures.py                 # All figure generation
│   ├── build_docx.py                       # DOCX builder with figures
│   └── run_all.sh                          # Complete replication script
└── LICENSE
```

## Key Results (v2.0)

| Classification | Count | Key Examples |
|---------------|:-----:|-------------|
| **F15b T3req** (γ_crit ≤ 100) | ~8-12 | Kinases (γ_crit=8.6), GPCRs (11), ZFs (11), olfactory receptors (18), rice NBS-LRR (96) |
| **F15a Tmarg** | ~15-20 | Most organisms at organism level; cultural systems (all Tmarg†) |
| **T2ok** | ~20-25 | Shallow families, somatic systems, closed pan-genomes |
| **Tna** | ~25-30 | Physical fractals, endosymbiont exits, scalar distributions |

**Headline result:** The protein kinase superfamily (D=8) in the human lineage has γ_crit = 8.6 — any efficiency gap >9× triggers temporal exclusion.

## Replication

```bash
# Generate all figures and processed data
cd scripts/
python3 compute_gamma_crit.py
python3 generate_figures.py
python3 build_docx.py

# Or run everything at once
bash run_all.sh
```

## Dependencies

- Python 3.9+
- matplotlib
- numpy
- python-docx

## Citation

Molyneux, S. (2026). "Computational Universality of Recursive Genome Evolution." In preparation.

## License

CC BY 4.0

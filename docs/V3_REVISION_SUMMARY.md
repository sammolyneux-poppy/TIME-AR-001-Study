# TIME-AR-001 v3.0 Revision Summary

**Date:** 2026-04-05
**Addresses:** External pre-publication review (P1-P10, m1-m6)
**Net effect:** T3req reduced from 8 to 6 families; amphioxus TLR elevated to Tier 1; two reclassifications to Tmarg; logistic regression replaced with Fisher exact test; four new sections added.

---

## Critical Fixes (P1-P10)

### P1 -- Bridge Lemma (Genome Length to Hierarchy Depth)
**New Section 2.9.** Adds explicit bridge connecting the Lean theorem (about genome length capacity) to the biological argument (about hierarchy depth search cost). States: each hierarchy level requires discovery of at least one novel functional sequence; the search to find each functional paralog scales exponentially in sequence space. Uses Manning 2002 kinase example (518 kinases, each a distinct functional sequence). Explicitly qualified: "This bridge is biological, not formal."

### P2 -- Fisher Exact Test Replaces Logistic Regression
**Sections 9.5, Abstract, 10.4, 12.2.** All references to "logistic regression" and "perfect separation" removed. Replaced with 2x2 contingency table (D >= 5 vs D < 5) x (T3req vs T2ok): 6 T3req all at D >= 5.0, 24 T2ok all at D <= 4.5, Fisher exact test p < 10^{-6}. Abstract updated accordingly.

### P3 -- Amphioxus TLR gamma_crit Corrected to 9.0
**Sections 2.1.2, 2.8.3, 4.1, 9.4, Abstract, 12.4.** Arithmetic corrected: (4.0 x 10^8)^(1/9) = e^(19.81/9) = e^2.201 = 9.0, not 15. Amphioxus TLR elevated to Tier 1 alongside kinases. New Section 12.4 highlights this as the second Tier-1 result.

### P4 -- Gamma Definitions Reconciled
**New Section 2.8.4.** Explicitly connects Lean gamma (per-level genome-growth cost ratio) to experimental gamma (fitness improvement rate). Argument: generating one new hierarchy level = discovering one new functional sequence; experimental evolution measures exactly this discovery rate. Conservative: even imprecise mapping gives gamma >= 2 lower bound.

### P5 -- Biological Explanation of D ~ 4.75 Boundary
**New Section 10.4.1.** Maps D ranges to evolutionary eras: D <= 3 (bacterial/archaeal, before LECA), D = 4 (early eukaryotic), D = 5-6 (early metazoan/Cambrian), D >= 7 (vertebrate-specific). The D ~ 4.75 boundary corresponds to the eukaryote-to-metazoan transition.

### P6 -- Neutral D_max ~ 7 Properly Described
**Section 6.3.** Clarified: D_max ~ 7 is from analytical birth-death theory (Karev 2002, Shakhnovich & Koonin 2006), NOT simulation. Formula stated: D_neutral_max ~ 0.5 x log_2(2 x G x lambda x T). For human: D_neutral_max ~ 7. Implication: D >= 8 exceeds neutral theory; D = 5-7 within neutral range but not necessarily neutral.

### P7 -- D Distribution Data Presented
**New Section 2.10.** Presents gene family depth distributions for three organisms: H. sapiens (~3,586 families; ~290 at D >= 3; ~40 at D >= 5; ~3-5 at D >= 8), A. thaliana (~7,000+ families; ~200+ at D >= 5), E. coli (~400 families; 0 at D >= 8). Notes these are lower bounds (balanced-tree assumption; 76% of real trees are asymmetric per Herrada et al. 2011). Limitation "single exemplar family" removed from Section 11.

### P8 -- FP4 Proof D=5 Measurement Documented
**New Appendix C.** Documents: Lean import DAG traversal method; 14 axioms as starting points; target = biological_evolution_is_utm; longest chain (7 nodes, 5 intermediate): cm_one_step_tag_simulation_axiom -> ... -> biological_evolution_is_utm; 62 files, 414 theorems, 69 lemmas, import DAG diameter = 11. Qualified as "illustrative analogy."

### P9 -- Arabidopsis RLKs Reclassified to Tmarg
**Sections 4.1, 6.1, 7, 8, 9.4.** gamma_crit = 81, near threshold. At D-1 = 4: gamma_crit = 244, clearly Tmarg. Flagged: "weakest former T3req; requires IAD-level advantage with uncertain plant generalizability."

### P10 -- Zebrafish Hox Reclassified to Tmarg
**Sections 4.1, 4.2, 6.1, 7, 8, 9.4.** Teleost WGD applied: 2R + teleost WGD = -2 adjustment, D_WGD-adj = 5.5 - 2 = 3.5. gamma_crit at D=3.5: (10^9)^(1/3.5) = 10^2.57 = 370, clearly Tmarg. D_WGD-adj used consistently in gamma_crit formula.

---

## Minor Fixes (m1-m6)

### m1 -- Table A1 (gamma=2 D_crit) Moved to Supplement
**Section 13 (Table A1).** Reframed with explanatory note: "demonstrates why gamma=2 alone is insufficient -- biological D values of 5-9 are not excluded at gamma=2."

### m2 -- Abstract Logistic Regression Replaced
Covered by P2. Abstract now uses Fisher exact test language.

### m3 -- WGD Claim Corrected
**Section 12.2, Claim 6.** Changed from "WGD does not explain deep gene-family hierarchy" to "WGD is not required for deep gene-family hierarchy -- tandem duplication alone suffices (amphioxus TLR, D=9)."

### m4 -- Two-Regime Gamma Elevated to Results
**New Section 5.5.** Brief Results section presenting the two-regime empirical gamma structure (recombination: 2-10; duplication: 100-10,000) with table mapping Tier-1/2/3 confidence levels to gamma_crit ranges.

### m5 -- gamma_crit T Convention Stated
**Section 2.3.** Added: "Convention: All gamma_crit values in this report are computed at midpoint T unless explicitly noted otherwise."

### m6 -- Quantitative Parallelism Example Added
**Section 10.6, Objection 5.** Added kinase-specific example: N_e ~ 10^5, T = 9.3 x 10^6 gen, ~10^{11} parallel search events per level. But sequential dependency (8 levels, each requiring fixation before next can diversify) limits effective search. gamma^8 ~ 7.4^8 ~ 10^7 still exceeds T.

---

## Updated T3req List (v3.0)

| Rank | Family | D | gamma_crit | Confidence |
|------|--------|:-:|:----------:|:----------:|
| 1 | Protein kinases (human) | 8 | 7.4 | Tier 1 |
| 2 | Amphioxus TLR (no WGD) | 9 | 9.0 | Tier 1 |
| 3 | GPCRs (human) | 7-8 | 11 | Tier 2 |
| 4 | Zinc fingers (human) | 7-8 | 11 | Tier 2 |
| 5 | Olfactory receptors (human) | 6-7 | 18 | Tier 3 |
| 6 | Rice NBS-LRR | ~5.5 | 23 | Tier 3 |

**Reclassified to Tmarg:** Zebrafish Hox (D_WGD-adj=3.5, gamma=370), Arabidopsis RLKs (gamma=81, boundary).

---

## Structural Changes

| Change | Location |
|--------|----------|
| New Section 2.8.4 (gamma reconciliation) | Methods |
| New Section 2.9 (bridge lemma) | Methods |
| New Section 2.10 (D distribution data) | Methods |
| New Section 5.5 (two-regime gamma result) | Results |
| New Section 10.4.1 (biological D boundary) | Discussion |
| New Appendix C (FP4 proof depth) | Appendix |
| Section 9.5 rewritten (Fisher exact test) | Results |
| Table A1 reframed as supplementary | Appendix |

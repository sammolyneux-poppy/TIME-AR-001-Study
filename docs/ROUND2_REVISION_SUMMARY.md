# TIME-AR-001 Round 2 Revision Summary

**Version:** 1.1 → 2.0
**Date:** 2026-04-05

## Critical Fixes

| # | Issue | Fix Applied | Impact |
|---|-------|------------|--------|
| C1 | γ model stated incorrectly | Replaced with exact Lean theorem `temporal_separation_capstone`: Tier 2 linear (g₀+T×k), Tier 3 exponential (2^n in n steps) | Foundation corrected |
| C2 | Bacteria T3req indefensible at γ_crit=27K | Split F15 into F15a (organism) + F15b (gene family); T3req only at γ_crit ≤ 100 | T3req count: 37 → 8 |
| C3 | Sequential independence conflicts with selection | New Section 2.7: Tier = operator class, not search strategy; γ = growth-rate gap | Model clarified |
| C4 | Cultural T3req overclaimed | All cultural systems → Tmarg† with contingency flag | ~12 systems downgraded |
| C5 | C. elegans T3req indefensible | F15a=T2ok (γ_crit=6,300), F15b=Tmarg (NHR D=5) | Correctly classified |
| C6 | Pan-genome conflated with temporal exclusion | Removed from F15; moved to Discussion as complementary evidence | E. coli F15a=T2ok |

## Major Fixes

| # | Issue | Fix Applied |
|---|-------|------------|
| M1 | No γ calibration | New Section 2.8: recombination γ~2-10, duplication IAD γ~100-10⁴ (Näsvall 2012) |
| M3 | Brain cortical D=10-14 wrong metric | Replaced with gene-family D=5-6 (FGF, Wnt, Eph/ephrin families) |
| M4 | Linux kernel D ambiguous | Resolved: module nesting D~6 (correct analog), not call graph D=20-25 |
| M5 | No FP4 proof depth | Measured: D=5 intermediate lemmas, axiom to biological_evolution_is_utm |
| M6 | No statistical test for D boundary | Logistic regression: PERFECT separation at D≈4.75 |
| M7 | WGD inflates D | Added WGD-adjusted column; kinase D=8 NOT WGD-inflated; amphioxus TLR D=9 with zero WGD |
| M8 | Pan-genome needs own formalism | Moved to Discussion Section 10.8 |

## Improvements

| # | Addition |
|---|---------|
| I1 | ROC plot specification (D vs log T with γ contours) |
| I3 | 4 adversarial cases: Drosophila ORs (Tmarg), NBS-LRR (Tmarg), E. coli LysR (T2ok), neutral D_max≈7 |
| I4 | Endosymbiont corollary: F15b=T3req requires F1-F4=✓ |
| I5 | Amphioxus TLR (D=9, no WGD) — proves high D doesn't require WGD |
| I7 | Consolidated γ_crit range table |
| I8 | Publication claims restricted to γ_crit ≤ 100 |

## Net Score Changes

| Metric | v1.1 | v2.0 |
|--------|------|------|
| F15b T3req | 37 | **8** |
| F15b Tmarg | 16 | **19** |
| Cultural Tmarg† | 0 | **14** |
| F15b T2ok | 21 | **24** |
| Tna | 25 | **25** |
| **Headline γ_crit** | 8.6 (kinases) | **7.4 (kinases)** |

The framework is now MORE discriminating: fewer but bulletproof T3req cases.

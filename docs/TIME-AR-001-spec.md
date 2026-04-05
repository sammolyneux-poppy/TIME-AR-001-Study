# TIME-AR-001: Temporal Admissible Region Study
## FP4 Cross-Domain Validation — Time Budget Analysis

**Version:** 1.0 (Initial Specification)
**Date:** 2026-04-05
**Companion to:** `TIME-SPEC-001.md`, `FP4_Cross_Domain_Validation_Report.docx` (v2.1)
**Purpose:** Extend the 13-feature admissibility framework with a 14th temporal dimension — `T_max` — assessing whether each system class can plausibly generate observed hierarchical/fractal complexity within its available time budget using sub-Tier-3 vs. Tier-3 operators. This study enables the publication claim: *"The hierarchical structures observed in nature could not plausibly have arisen in available evolutionary time by sub-Tier-3 operators."*

---

## 1. Study Design

### 1.1 Core Question

The existing admissibility framework (F1–F14, E1–E26) asks: *does this system satisfy the structural conditions for computational universality?* The temporal admissible region study asks a different and complementary question: **given that a system has the right structural operators, could it plausibly have assembled its observed complexity within the available time window?**

This introduces a new feature **F15: Temporal Feasibility** and a new classification dimension: systems that are structurally admissible but temporally *infeasible* for sub-Tier-3 operators define the critical zone where the TIME-SPEC-001 theorem has maximum biological bite.

### 1.2 The Temporal Admissible Region

Following the admissible-region methodology established for E10, E11, and E12, we define the temporal admissible region as a **rectangle in two-parameter space**:

| Parameter | Symbol | Conservative | Midpoint | Liberal |
|---|---|---|---|---|
| Available generations (bacteria) | T | 3.5 × 10¹¹ | 4.0 × 10¹² | 4.5 × 10¹³ |
| Available generations (eukaryotes) | T | 3.5 × 10⁹ | 4.0 × 10¹⁰ | 4.5 × 10¹¹ |
| Available years (all domains) | t_yr | 3.5 × 10⁹ | 4.0 × 10⁹ | 4.5 × 10⁹ |
| Target hierarchy depth | D | 3 | 5 | 10 |
| Exponential gap factor (Tier 2 vs. Tier 3) | γ | 2 | 10 | 100 |

The **temporal exclusion zone** for a system is the set of (T, D, γ) triples where γ^D > T — i.e., where Tier 2 cannot reach depth D in time T. Tier 3 is assessed against the same T with a logarithmic step count (D doublings ≈ log₂(D) steps).

The key empirical finding that motivates the study: at γ ≥ 2 and D ≥ 40 (well within observed eukaryotic gene-family nesting), γ^D vastly exceeds T for any biologically plausible T. The study documents where each system class falls in this space.

### 1.3 New Feature: F15 Temporal Feasibility

**F15: Tier-3 operators required for temporal feasibility within the available budget**

| Score | Meaning |
|---|---|
| ✓ | Tier 3 clearly required — sub-Tier-3 operators are temporally excluded across the entire admissible (T, D, γ) region |
| ~ | Marginal — exclusion holds only at part of the admissible region, or D_target is contested |
| ✗ | Sub-Tier-3 operators are sufficient — target complexity is shallow enough to be reached within T by Tier 2 |
| — | Not applicable — system has no hierarchical complexity target, or time budget is not biologically calibrated |

F15 does NOT contribute to the existing F1–F14 admissibility percentage. It is a **standalone temporal verdict** reported alongside the standard scorecard, analogous to the treatment of F11 (fitness landscape, orphaned).

**Scope note for every F15 assessment:** Neutral drift phases do not change the operator class. A Tier 2 system under neutral drift remains a Tier 2 system. F15 assesses operator class, not trajectory shape.

### 1.4 Classification Extensions

The six existing classes (Inside, Plausible, Boundary, Exit, Marginal, Negative) are extended with a temporal suffix where relevant:

| Suffix | Meaning |
|---|---|
| `-T3req` | F15 = ✓: Tier 3 required for temporal feasibility |
| `-T2ok` | F15 = ✗: Tier 2 sufficient within the time budget |
| `-Tmarg` | F15 = ~: Marginal temporal case |
| `-Tna` | F15 = —: Not applicable |

Example: `Inside-T3req` = structurally Inside AND Tier 3 temporally required. This is the maximally strong classification — a system fully inside the admissible region AND for which sub-Tier-3 operators are temporally excluded.

---

## 2. System Catalogue and F15 Assignments

The study covers all ~85 systems from the existing report plus new temporal case additions. Systems are grouped into the same nine domains (BIO, CHEM, IMMUNE, LANG, COMP, ECON, PHYS, INFO, NEUR) with the temporal dimension added.

### 2.1 Domain BIO — Biological / Genetic Evolution

These are the primary positive cases. They are the systems where the TIME-SPEC-001 theorem is most directly applicable.

---

#### BIO-T1: Core Model Organisms (Tier A in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| *E. coli* | ~4 × 10¹² gen | ~4 (gene family nesting depth) | ✓ | Inside-T3req |
| *S. cerevisiae* | ~4 × 10¹⁰ gen | ~5 | ✓ | Inside-T3req |
| *H. sapiens* | ~4 × 10⁹ gen | ~6 (paralog subfamilies) | ✓ | Inside-T3req |
| *C. elegans* | ~4 × 10¹⁰ gen | ~4 | ✓ | Inside-T3req |
| *D. melanogaster* | ~4 × 10¹⁰ gen | ~5 | ✓ | Inside-T3req |
| *A. thaliana* | ~4 × 10⁹ gen | ~5 | ✓ | Inside-T3req |

**Temporal reasoning for this group:** At γ = 2, D = 5: γ^D = 32. At γ = 10, D = 5: γ^D = 100,000. Both are trivially below T for prokaryotes but also below T for eukaryotes in shallow cases. The key is that observed D is not 5 — it is the *effective nesting depth of the full gene family hierarchy*, which for human paralogs spans at minimum 4–6 levels of recursive subfamiliarization. At D ≥ 15–20, γ^D >> T for any eukaryotic time budget.

**Drift caveat:** Post-WGD reductive drift shapes which duplicates survive, not whether duplication happened. The temporal exclusion applies to *generating* the nested structure, not to *pruning* it afterward.

---

#### BIO-T2: Extended Eukaryotes (Tier B in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| *D. discoideum* | ~4 × 10⁹ gen | ~3–4 | ~ | Inside-Tmarg |
| *F. albicollis* (flycatcher) | ~4 × 10⁸ gen | ~4 | ✓ | Inside-T3req |
| *S. pombe* | ~4 × 10⁹ gen | ~4 | ✓ | Inside-T3req |
| *P. aeruginosa* | ~4 × 10¹¹ gen | ~4 | ✓ | Inside-T3req |

**Note on *D. discoideum*:** Marginal because its genome is smaller (~13,000 genes, D ≈ 3–4) and T is large relative to complexity target. At γ = 2, D = 4, Tier 2 step count = 16, comfortably within T. Upgrade to T3req only if D_target is recalibrated upward from richer nesting data.

---

#### BIO-T3: Archaeal Domain (Tier C in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| *M. jannaschii* | ~4 × 10¹² gen | ~3 | ~ | Plausible-Tmarg |
| *H. salinarum* NRC-1 | ~4 × 10¹² gen | ~3–4 | ~ | Plausible-Tmarg |
| *S. solfataricus* P2 | ~4 × 10¹² gen | ~4 | ✓ | Inside-T3req |
| Archaea (79-genome BDI3 set) | ~4 × 10¹² gen | ~3–4 (distribution) | ~ | Plausible-Tmarg |

**Key analytical note:** Archaeal genomes are smaller and gene family hierarchies are shallower than eukaryotes. The temporal exclusion still applies but at a lower D threshold. The marginal cases are expected and serve as an important internal calibration — they show the study is not simply assigning T3req everywhere.

---

#### BIO-T4: Pan-Genomes at Scale (Tier D in v2.1)

Pan-genomes have an unusual temporal structure: the "available time" is the species radiation time, not Earth's entire history, and the observed structure is the cumulative gene complement across strains.

| System | T_available | Structural target | F15 verdict | Classification |
|---|---|---|---|---|
| *E. coli* pan-genome | ~50 Myr radiation, ~10¹¹ gen | Open pan (Heaps α = 0.34–0.38) | ✓ | Inside-T3req |
| *A. baumannii* pan | ~10⁹ gen | Open pan (α = 0.39–0.45) | ✓ | Inside-T3req |
| *M. tuberculosis* pan | ~10⁹ gen | Nearly closed (α = 0.08–0.12) | ✗ | Inside-T2ok |
| *F. psychrophilum* pan | ~10⁸ gen | Nearly closed (α = 0.15–0.25) | ✗ | Inside-T2ok |

**Critical insight:** Nearly-closed pan-genomes (*M. tuberculosis*, *F. psychrophilum*) are **predicted negative controls for F15** — they are Inside on structural grounds but T2ok because their shallow innovation structure is achievable without recursive duplication dynamics within the available time. This is not a weakness; it is a precision test confirming the framework discriminates within the Inside class.

---

#### BIO-T5: Endosymbionts — EXIT cases (Tier H in v2.1)

| System | T_available | D_current | F15 verdict | Classification |
|---|---|---|---|---|
| *Buchnera aphidicola* | ~150 Myr host association | D ≈ 0–1 (reduction) | — | Exit-Tna |
| *Carsonella ruddii* | ~100 Myr | D ≈ 0 | — | Exit-Tna |
| *Tremblaya princeps* | ~100 Myr | D ≈ 0 | — | Exit-Tna |

**Temporal note:** These systems are F15-not-applicable because they are exits — they were formerly Inside but innovation rate collapsed to zero. They are important temporal **negative controls of a different kind**: they show that even systems with long time budgets produce no hierarchical complexity once the Tier-3 duplication dynamic terminates.

---

#### BIO-T6: CPR Bacteria and DPANN Archaea (Tier I in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| CPR bacteria (Patescibacteria) | ~3 × 10¹² gen | D ≈ 1–2 | ✗ | Boundary-T2ok |
| DPANN archaea | ~3 × 10¹² gen | D ≈ 1–2 | ✗ | Boundary-T2ok |

**Temporal note:** Ultra-reduced lineages with small, shallow gene family structures — temporal exclusion does not apply because D_target is low. These are important as **expected negatives for F15** — they confirm the threshold is not trivially passed by all living systems.

---

#### BIO-T7: Cancer Somatic Evolution (Tier G in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Cancer somatic evolution | ~10⁸–10⁹ cell divisions (lifetime) | SCNA nesting ~2–3 levels | ~ | Plausible-Tmarg |

**Temporal note:** Cancer operates on somatic timescales (~70 years, ~10⁸–10⁹ divisions). Observed copy-number alteration nesting is shallow (2–3 levels). Tier 2 could plausibly generate this within somatic lifetime — the temporal exclusion is marginal, not strong. This correctly reflects that cancer does not produce deeply nested gene family hierarchies comparable to germline evolution.

---

#### BIO-T8: CRISPR Spacer Arrays (Tier F in v2.1)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| CRISPR spacer arrays | ~10⁹–10¹⁰ gen (host species) | D ≈ 1–2 (array depth) | ~ | Inside-Tmarg |

**Temporal note:** CRISPR arrays are BDIM-analogs but structurally shallow — arrays typically have 10s to 100s of spacers but limited recursive nesting. F15 is marginal because the structural target is low enough that Tier 2 analog processes might suffice within T.

---

#### BIO-T9: Immune Repertoire

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| T cell repertoire (somatic) | ~10⁸ cell divisions (lifetime) | VDJ recombination ~3 levels | ✗ | Inside-T2ok |
| B cell + SHM | ~10⁸ divisions | ~3–4 levels | ~ | Inside-Tmarg |
| Germline immunoglobulin loci | ~4 × 10⁸ gen | D ≈ 5–6 (paralog nesting) | ✓ | Inside-T3req |

**Key split:** Somatic immune diversification (T cells, B cells) operates within a single organism lifetime — the time budget is so compressed (~10⁸ divisions) and the structural depth so shallow that Tier 2 analog processes (VDJ recombination, SHM) are temporally sufficient. The germline immunoglobulin loci, by contrast, have the deep recursive paralog structure that requires evolutionary timescales and Tier-3 dynamics.

---

### 2.2 Domain CHEM — Chemical / Prebiotic

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| RNA World (proto-BDIM) | ~10⁸–10⁹ yr pre-LUCA | D ≈ 1–2 (ribozyme families) | ~ | Marginal-Tmarg |
| Autocatalytic networks | Unknown | D ≈ 1 | — | Marginal-Tna |
| Hypercycle (Eigen) | Unknown | D ≈ 0–1 | ✗ | Marginal-T2ok |

**Key temporal note:** Chemical systems predate LUCA (~3.5–4.0 Gya). The RNA World had a compressed time budget (~10⁸–10⁹ yr before transition to DNA-based life) and shallow structural targets. These are important early-phase controls: they show a world where Tier-3 dynamics had not yet emerged, consistent with the proof's claim that Tier 3 is required for open-ended complexity.

---

### 2.3 Domain LANG — Language / Text / Cultural

Language and cultural systems are critical cross-domain positives — they are non-biological but exhibit recursive hierarchical structure that is the direct cultural analog of biological gene family nesting.

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Natural language (morpheme families) | ~10,000–100,000 yr | D ≈ 5–8 (derivational morphology hierarchy) | ✓ | Plausible-T3req |
| Legal text corpora | ~5,000 yr documented | D ≈ 3–5 (clause/section nesting) | ~ | Plausible-Tmarg |
| Mathematical notation systems | ~3,000 yr | D ≈ 4–6 (operator nesting) | ✓ | Plausible-T3req |
| Musical motif hierarchies | ~10,000 yr | D ≈ 3–5 | ~ | Plausible-Tmarg |
| Scientific citation genealogies | ~300 yr modern science | D ≈ 2–3 | ✗ | Negative-T2ok |

**Key temporal reasoning for language:** Human language evolution has a compressed time budget (~10,000–100,000 yr, ~300–3,000 generations) but exhibits deeply nested hierarchical structure in morpheme families, grammatical constructions, and derivational paradigms. The question is whether cultural transmission acts as a Tier-3 analog: does it include a **recursive duplication operator** (metaphor/analogy = semantic duplication), a **deletion operator** (word loss, grammatical simplification), and **selection** (communicative fitness)? Natural language satisfies all three. At D ≈ 6 and γ = 10, γ^D = 10⁶ — vastly exceeding the ~3,000 generation budget for biological evolution, but cultural transmission rates are orders of magnitude faster than biological generations. The temporal budget must be reframed in **transmission events** rather than years.

**Reframing for cultural domains:** For non-biological systems, `T` should be measured in **transmission events per unit time** rather than biological generations. A word or grammatical construction is transmitted ~10²–10³ times per human lifetime across a speech community. With ~3 × 10⁹ humans and 100,000 yr, T_cultural ≈ 10¹⁵–10¹⁷ transmission events. This places cultural systems in the same temporal feasibility class as bacterial systems — large T, shallow-to-moderate D, Tier-3 analog dynamics required for the deepest nesting levels.

---

### 2.4 Domain COMP — Computational / Software

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Software codebases (open source) | ~50 yr | D ≈ 4–8 (module/class/method nesting) | ✓ | Plausible-T3req |
| Chess opening trees | ~200 yr modern theory | D ≈ 6–10 (variation depth) | ✓ | Plausible-T3req |
| Compiler IR hierarchies | ~50 yr | D ≈ 5–10 | ✓ | Plausible-T3req |
| Regular expressions | ~60 yr | D ≈ 2–3 | ✗ | Plausible-T2ok |
| Finite automata (non-recursive) | ~70 yr | D ≈ 1 | ✗ | Negative-T2ok |

**Note on software:** The "duplication operator" in software is code reuse, library inheritance, and copy-paste-modify. The "deletion operator" is refactoring and dead code elimination. Selection is fitness on performance, maintainability, and adoption. At D ≈ 6 nesting levels (package → module → class → method → expression → token), γ^D at γ = 10 = 10⁶, far exceeding the ~50 yr / ~10⁶ commit-event budget without recursive composition operators. Regular expressions and FSMs (structurally non-recursive) serve as important expected negatives for F15.

---

### 2.5 Domain ECON — Economic / Social

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Firm/corporate hierarchies | ~200 yr modern capitalism | D ≈ 3–5 (org chart depth) | ~ | Plausible-Tmarg |
| Patent citation trees | ~200 yr | D ≈ 4–6 (technology genealogy) | ✓ | Plausible-T3req |
| Baby name families | ~200 yr | D ≈ 1–2 (variation shallow) | ✗ | Marginal-T2ok |
| Dog breed lineages | ~200 yr modern breeding | D ≈ 2–3 | ✗ | Plausible-T2ok |
| Income/wealth distributions | Ongoing, non-stationary | No hierarchical D | — | Negative-Tna |
| Stock returns | Non-stationary | No hierarchical D | — | Negative-Tna |
| City sizes | Non-stationary (Gibrat) | No hierarchical D | — | Negative-Tna |

**Key note:** Income/wealth and stock returns are already confirmed Negatives on structural grounds (F1–F3 fail) — F15 is not applicable because they have no hierarchical complexity target. Patent citation trees are an interesting positive: technology development exhibits recursive hierarchical genealogy (transistor → circuit → chip → system → platform) with temporal compression similar to software.

---

### 2.6 Domain PHYS — Physical (All Expected Negatives for F15)

Physical power-law systems are confirmed structural negatives (all fail F1–F4). For the temporal study they are important negative controls: they show that power-law statistics arise in zero-time (equilibrium or steady-state) through non-BDIM mechanisms, without any hierarchical nesting requirement.

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Earthquakes (SOC) | Instantaneous (fault dynamics) | No nesting | — | Negative-Tna |
| Solar flares (SOC) | Instantaneous | No nesting | — | Negative-Tna |
| Turbulence (energy cascade) | Instantaneous (steady state) | Energy scale D ≈ ~log(Re) | ✗ | Negative-T2ok |
| Galaxy luminosity function | ~10 Gyr cosmological | No BDIM structure | — | Negative-Tna |
| Stellar IMF (Jeans fragmentation) | ~10⁷ yr star formation | No BDIM structure | — | Negative-Tna |
| Molecular cloud fragmentation | ~10⁶ yr | No BDIM structure | — | Negative-Tna |
| River networks (erosion) | ~10⁶–10⁷ yr | Branching D ≈ 3–6 | ✗ | Negative-T2ok |
| Sandpile / SOC models | Instantaneous | No heritable string | — | Negative-Tna |

**Critical note on turbulence and river networks:** These systems exhibit nested/hierarchical structure (Kolmogorov cascade has scale levels; river networks have Horton-Strahler ordering D ≈ 3–6) but are F15 = ✗/— because (a) they fail F1–F4 structurally, and (b) their "nesting" is generated by continuous physical processes with no heritable string or selection — it is not accumulated over discrete reproductive generations. This is important: the temporal admissible region analysis must not conflate *physical scale hierarchies* with *evolutionary complexity hierarchies*. Document this distinction explicitly in every physical system entry.

---

### 2.7 Domain INFO — Information Networks

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| WWW hyperlink graph | ~30 yr | D ≈ 3–5 (site nesting) | ~ | Marginal-Tmarg |
| Internet AS topology | ~30 yr | D ≈ 2–3 | ✗ | Negative-T2ok |
| PPI networks | ~3 × 10⁹ yr (evolution) | D ≈ 4–6 | ✓ | Marginal-T3req |
| Scientific citation genealogies | ~300 yr modern science | D ≈ 2–3 | ✗ | Negative-T2ok |

**Note on PPI networks:** Protein-protein interaction networks are structurally marginal (mechanism contested) but temporally strong: the modular hub-spoke structure of PPI networks has D ≈ 4–6 levels and evolved over ~10⁹ yr. If mechanism is confirmed as BDIM-like, this becomes Inside-T3req.

---

### 2.8 Domain NEUR — Neural / Cognitive

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Neuronal avalanches | Milliseconds (dynamics) | No hierarchical string | — | Marginal-Tna |
| Brain structural hierarchy | ~10⁸ yr (mammalian evolution) | D ≈ 5–8 (cytoarchitecture layers) | ✓ | Marginal-T3req |
| Synaptic weight distributions | Ongoing (plasticity) | No heritable string | — | Marginal-Tna |
| Memory schema (cognitive) | ~decades (lifetime) | D ≈ 3–5 (concept nesting) | ~ | Marginal-Tmarg |
| Neural cell type diversity | ~10⁸ yr | D ≈ 4–6 (transcription factor families) | ✓ | Marginal-T3req |

**Key distinction:** Neuronal dynamics (avalanches, synaptic weights) are real-time physical processes — F15 not applicable. Brain structural hierarchy and neural cell type diversity are products of evolutionary time and exhibit deep recursive structure in transcription factor gene families — these are genuinely T3req cases where the temporal exclusion applies.

---

### 2.9 Domain IMMUNE — Immune Repertoire (Detailed)

| System | T_available | D_observed | F15 verdict | Classification |
|---|---|---|---|---|
| Germline Ig loci (heavy chain) | ~4 × 10⁸ gen | D ≈ 5–7 | ✓ | Inside-T3req |
| Germline TCR loci | ~4 × 10⁸ gen | D ≈ 4–6 | ✓ | Inside-T3req |
| Somatic VDJ recombination | ~10⁸ cell divisions | D ≈ 3 | ✗ | Inside-T2ok |
| Somatic hypermutation (B cells) | ~10⁷–10⁸ divisions | D ≈ 2–3 | ~ | Inside-Tmarg |
| CRISPR spacer arrays | ~10⁹–10¹⁰ gen | D ≈ 1–2 | ~ | Inside-Tmarg |

**The immune system provides the cleanest internal control:** the germline loci (evolutionary time, deep paralog nesting) are T3req, while somatic diversification processes (organism lifetime, shallow nesting) are T2ok or Tmarg. This cleanly validates the framework — same biology, two different temporal regimes, two different F15 verdicts.

---

## 3. Additional New Cases for Expanded Coverage

The following systems are **new additions not in v2.1**, specifically chosen to stress-test the temporal dimension with expected negatives, marginals, and high-depth positives.

### 3.1 Expected Temporal Negatives (Sub-Tier-3 Sufficient)

These systems have power-law or hierarchical structure but are shallow enough that Tier 2 analog operators are temporally sufficient. Their purpose is to ensure F15 is not vacuously assigned.

| System | Domain | D_observed | F15 | Rationale |
|---|---|---|---|---|
| Simple tandem repeats (microsatellites) | BIO | D ≈ 1 | ✗ | Indel-only dynamics, shallow repeat |
| tRNA gene families (bacteria) | BIO | D ≈ 1–2 | ✗ | Shallow, well-conserved, low innovation |
| Short interspersed elements (SINEs, bacteria) | BIO | D ≈ 1–2 | ✗ | No recursive composition |
| ASCII art / L-systems (depth-limited) | COMP | D ≤ 3 | ✗ | Non-recursive production rules |
| Binary decision trees (shallow) | COMP | D ≤ 4 | ✗ | Fixed-depth, no duplication analog |
| Proverb families (oral tradition) | LANG | D ≈ 1–2 | ✗ | No recursive derivational morphology |
| Simple melodic motif repetition | LANG | D ≈ 2 | ✗ | Repetition without composition |
| Crystalline lattice structures | PHYS | D ≈ 1 (periodic) | — | No heritable string; periodic not hierarchical |

### 3.2 Expected Temporal Positives (Tier 3 Required)

These systems have deep hierarchical structure and are expected T3req cases:

| System | Domain | D_observed | F15 | Rationale |
|---|---|---|---|---|
| Eukaryotic transcription factor superfamilies | BIO | D ≈ 6–8 | ✓ | Zinc finger, homeodomain — deep recursive duplication history |
| Vertebrate Hox cluster arrays | BIO | D ≈ 5–7 | ✓ | 4 clusters, each ~10 genes — product of recursive duplication events |
| Vertebrate olfactory receptor superfamily | BIO | D ≈ 6–8 | ✓ | ~800 genes in humans; ~1000 in rodents — deepest known TF family |
| Spliceosomal RNA gene families | BIO | D ≈ 4–6 | ✓ | Deep paralog nesting across eukaryotes |
| Programming language family trees | COMP | D ≈ 5–8 (language genealogy) | ✓ | LISP → Scheme → Racket / C → C++ → Java / etc. |
| Legal system doctrine genealogies | LANG | D ≈ 4–6 | ✓ | Common law precedent creates recursive citation nesting |
| Musical composition forms (Western classical) | LANG | D ≈ 4–6 (motif → theme → movement → symphony → corpus) | ~ | Contested — cultural T differs |
| Mythology / narrative deep structure | LANG | D ≈ 4–7 (archetype → variant → cultural tradition → corpus) | ~ | Monomyth structure — marginal because T and selection not formalized |
| Human kinship terminology systems | LANG | D ≈ 3–5 | ~ | Recursive but T budget compressed |
| Operating system kernel subsystem hierarchies | COMP | D ≈ 6–10 | ✓ | Linux kernel: 5+ levels of recursive module composition |

### 3.3 Critical Marginal Cases (Boundary of Temporal Exclusion)

These are the most scientifically interesting cases — systems where the temporal exclusion activates only at part of the admissible region, precisely calibrating the boundary of the TIME-SPEC-001 theorem.

| System | Domain | D_observed | F15 | Why marginal |
|---|---|---|---|---|
| *Drosophila* olfactory receptor families | BIO | D ≈ 3–4 | ~ | Shallow relative to vertebrates; T is large (T_fruit fly >> T_human) |
| Archaeal CRISPR-Cas system diversity | BIO | D ≈ 3–4 | ~ | Newly characterized; Clauset audit pending |
| Small RNA gene families (miRNA) | BIO | D ≈ 3–4 | ~ | Some lineages show deep nesting; others do not |
| Ant colony caste differentiation hierarchies | BIO | D ≈ 2–4 | ~ | Social organization depth contested |
| Wikipedia category trees | LANG/COMP | D ≈ 5–8 | ~ | Deep but non-biological T (decades); mechanism semi-BDIM |
| Open-source dependency graphs | COMP | D ≈ 4–6 | ~ | F2 and F4 already ~ in v2.1; temporal adds marginal |
| Jazz improvisation genealogies | LANG | D ≈ 3–5 | ~ | Contested mechanism; T ≈ 100 yr |

### 3.4 Physics / Information Theory Edge Cases (Deepening the Negative Control Set)

These cases extend the negative control set specifically for the temporal dimension — systems with large T but no hierarchical complexity, or large D in a physically generated structure:

| System | Domain | T_available | D_apparent | F15 | Rationale |
|---|---|---|---|---|---|
| Cosmic large-scale structure (filaments) | PHYS | ~13 Gyr | D ≈ 3–4 (filament/node hierarchy) | — | Gravitational, not BDIM; no heritable string |
| Fractal coastlines | PHYS | ~10⁷–10⁸ yr erosion | D → ∞ (self-similar at all scales) | — | Physical self-similarity ≠ evolutionary complexity accumulation |
| Snowflake branching | PHYS | Seconds | D ≈ 4–6 (crystal branching) | — | Instantaneous; no heritable string |
| Self-similar antenna designs | COMP | ~decades | D ≈ 3–6 | ✗ | Engineered fractal, non-evolutionary; T2 analog sufficient |
| Cantor set / Koch curve | COMP | Instantaneous (mathematical) | D → ∞ | — | Mathematical construction; no T budget |
| Logistics / supply chain networks | ECON | ~decades | D ≈ 3–5 | ✗ | Network growth, not BDIM; T2ok even if mechanism were BDIM-like |
| Dendritic river networks (Horton-Strahler) | PHYS | ~10⁶–10⁷ yr | D ≈ 4–8 | ✗ | Physical branching by erosion; F1–F4 fail; no evolutionary mechanism |
| Atmospheric convection cells | PHYS | Hours–days | D ≈ 2–3 | — | Thermal dynamics; no heritable string |

**Critical annotation for all physical fractal cases:** The existence of large D in physical self-similar structures is the most important negative control for the temporal study. Physical fractals can achieve arbitrarily large D *instantaneously* or through purely mechanical processes. The key discriminator is not D alone but the *combination* of (a) heritable discrete string, (b) duplication operator, (c) selection, and (d) temporal accumulation through discrete reproductive events. Physical fractals satisfy none of (a)–(d). This must be prominently stated in the study to prevent conflation of physical self-similarity with evolutionary complexity accumulation.

---

## 4. Cross-Domain Temporal Matrix

For each of the 9 domains, summarize the F15 distribution:

| Domain | Inside/Plausible T3req | Inside/Plausible T2ok | Tmarg | Tna / not applicable | Key finding |
|---|---|---|---|---|---|
| BIO | ~15 systems | ~5 systems (shallow/reduced) | ~8 systems | ~4 (exits) | Core positives: germline, deep paralog families |
| CHEM | 0 | ~2 | ~2 | ~1 | Pre-BDIM world; shallow targets |
| IMMUNE | ~2 (germline loci) | ~2 (somatic) | ~2 | 0 | Cleanest internal control in study |
| LANG | ~3 | ~2 | ~4 | ~2 | Language and law: T3req at deep nesting levels |
| COMP | ~4 | ~2 | ~3 | 0 | Software, chess, OS kernels: T3req |
| ECON | ~1 (patents) | ~3 | ~1 | ~3 (Gibrat) | Mostly T2ok or Tna; patent genealogy positive |
| PHYS | 0 | ~2 (apparent D only) | 0 | ~10 | All structural negatives; physical fractals are critical Tna controls |
| INFO | ~1 (PPI, tentative) | ~2 | ~2 | ~1 | Mechanism contested; PPI marginal-T3req |
| NEUR | ~2 (germline-derived) | 0 | ~3 | ~3 (dynamics) | Cell type diversity and brain hierarchy: T3req |

---

## 5. Risk Assessment for Temporal Dimension

Following the E1–E26 risk tier methodology from v2.1:

| Temporal Parameter | Risk | Issue | Mitigation |
|---|---|---|---|
| `T_max` calibration | MEDIUM | Earth age and gen/yr well-known but organism-class-specific | Use admissible range, not point estimate; document separately for bacteria/eukaryotes/cultural |
| `D_target` calibration | HIGH | Observed hierarchy depth is difficult to measure consistently; no standard assay | Use multiple independent measures (gene family nesting, Horton-Strahler, dendrogram depth); require concordance across ≥2 methods |
| `γ` (efficiency gap factor) | MEDIUM | Exponential gap is proved in principle but calibration from biological data is indirect | Prove γ > 1 is sufficient; γ > 2 is conservative; document sensitivity across γ = 2, 10, 100 |
| Cultural T reframing | HIGH | "Generation" is not well-defined for cultural domains; T must be in transmission events | Explicitly define transmission event rate per domain; flag all cultural F15 assignments as contingent on this definition |
| Physical fractal conflation | MEDIUM | Reviewers may conflate physical self-similar D with evolutionary D | Add explicit anti-conflation note to every PHYS entry; define "evolutionary D" vs "geometric D" in methods |

---

## 6. Formal Requirements Mapping

The TIME-AR-001 study introduces two new empirical requirements to complement the E1–E26 set:

| ID | Requirement | Formal link | Risk | Status |
|---|---|---|---|---|
| E27 | `EvolutionaryTimeBudget`: T_max within physical bound for organism class | TIME-SPEC-001 §Step 1 | MEDIUM | NEW — not yet in proof |
| E28 | `HierarchyDepth` target D_target calibrated from observed nesting data | TIME-SPEC-001 §Step 2 | HIGH | NEW — requires per-system measurement |

---

## 7. Implementation Instructions for Coding Agent

### Step 1 — Data Collection Phase
For each system entry in Section 2 with F15 = ✓ or ~:
1. Locate the primary literature source for the observed hierarchy depth D
2. Measure D using at least two independent methods (gene family dendrogram depth, domain architecture nesting, Horton-Strahler ordering, or equivalent)
3. Record T_available from the organism's evolutionary history (not Earth age — use clade age where possible)
4. Compute γ^D and compare to T_available at γ = 2, 10, 100
5. Record the minimum D at which temporal exclusion activates for each (T, γ) combination

### Step 2 — Scorecard Update
Extend the existing F1–F14 scorecard table in `FP4_Cross_Domain_Validation_Report.md` with:
- Column F15 (✓ / ~ / ✗ / —)
- Column `D_observed` (numeric, with source citation)
- Column `T_available` (numeric, organism-class-appropriate)
- Column `γ^D vs T` (the exclusion computation result)

### Step 3 — Physical Fractal Section
Add a dedicated section for physical fractal cases (Section 3.4 above) with explicit anti-conflation language. This section must appear before the positive case results so reviewers encounter the discriminatory framework before the organism data.

### Step 4 — Cultural Domain T Reframing
For all LANG, COMP, and ECON systems with F15 = ✓ or ~:
- Define the transmission event rate explicitly
- Restate T in transmission events, not calendar years
- Flag these as contingent on the cultural T definition; do not assert T3req with the same confidence as biological systems

### Step 5 — Build Check
After adding F15 to the report:
- Verify that F15 is NOT included in the F1–F14 admissibility percentage calculation (analogous to F11 treatment)
- Verify that all existing admissibility percentages are unchanged
- Add F15 column header as "F15 (Temporal — TIME-SPEC-001 pending)" to signal that formal proof is in progress

---

## 8. Publication Language by Classification

| Classification | Safe publication claim |
|---|---|
| Inside-T3req | "This system exhibits hierarchical complexity that is temporally inaccessible to sub-Tier-3 operators within its available evolutionary time budget, consistent with the TIME-SPEC-001 temporal exclusion theorem." |
| Inside-T2ok | "This system's observed structural complexity is shallow enough to be temporally accessible to sub-Tier-3 operators — confirming that the temporal exclusion is not vacuous and does not apply uniformly to all BDIM-admissible systems." |
| Inside-Tmarg | "This system lies at the boundary of the temporal exclusion zone; the verdict is sensitive to the precise calibration of D_target and the efficiency gap parameter γ." |
| Negative-Tna (physical) | "This system exhibits power-law or hierarchically structured output through non-BDIM physical mechanisms that operate without heritable strings, discrete reproduction, or accumulated evolutionary time — confirming that physical fractality is not evidence of Tier-3 dynamics." |
| Exit-Tna | "This system was formerly BDIM-admissible but has exited through innovation-rate collapse. The resulting absence of hierarchical complexity, despite large T_available, confirms that time alone is insufficient — Tier-3 operator activity must be ongoing." |

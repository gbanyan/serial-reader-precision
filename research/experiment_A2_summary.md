# Experiment A.2 — oracle compatibility and noise robustness

**A2-SCAN-5 — Mixed. COMPATIBILITY QUESTION: STILL UNRESOLVED. DO NOT RERUN FACTORIAL YET. EXPERIMENT B: BLOCKED.**

Perfect codes solve genuine Scan for all three geometries at N4–12. Nevertheless, the frozen slot reader is sensitive to metric errors that leave ordinal rank intact, and A.1 learned codes are often inadequately calibrated. These are separable limitations. No training, reader redesign, threshold change, control variant or factorial rerun occurred.

## Layer 1: capability

All oracle codes carry the same rank, with input identity/presentation randomized. Priority uses decreasing [1,0]; position uses slot centers (k+.5)/N; phase uses the corresponding unit-circle centers. Both readers receive the same code within a representation. The centered convention matches the existing A.1 cursor without changing it. [Preregistration](experiment_A2_preregistered_hypotheses.md) and [specification](experiment_A2_oracle_compatibility.md) were hashed before primary results.

| Oracle system | Exact N4 | N6 | N8 | N10 | N12 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Priority/Competitive | 100% | 100% | 100% | 100% | 100% |
| Priority/Scan | 100% | 100% | 100% | 100% | 100% |
| Position/Competitive | 100% | 100% | 100% | 100% | 100% |
| Position/Scan | 100% | 100% | 100% | 100% | 100% |
| Phase/Competitive | 0% | 0% | 0% | 0% | 0% |
| Phase/Scan | 100% | 100% | 100% | 100% | 100% |

Every Scan cell has pairwise accuracy/tau=1 and zero misses, omissions, duplicates or collisions at zero noise. **ORACLE_SCAN_VALID passes in all three families**, including all four noise-replicate panels at N4/N6. Higher lengths demonstrate oracle scaling only, not learned extrapolation.

The full-circle phase oracle fails the frozen cosine competitive projection. Equal/symmetric cosine values do not uniquely recover circular ordinal order. This asymmetry was identified from source and documented before primary results; no favorable semicircle code or angular sorting decoder was substituted. A.1 learned Phase/Competitive succeeds with a different task-aligned arrangement. Therefore an oracle is perfect as an information code without being suitable for every frozen decoder.

## Layer 2: robustness

Four noise seeds (101/202/303/404), 1,024 paired trials each, five lengths, eight preregistered normalized Gaussian SDs. The 960 rows represent 983,040 reader evaluations; paired conditions share base trials/noise and are not independent training runs. No clipping or retraining. Noise is measured in adjacent rank spacings, not raw coordinate units.

N6 exact accuracy at SD=.35, mean ± noise-seed SD:

| Code | Competitive | Scan | Scan failure conditional on rank preserved |
| --- | ---: | ---: | ---: |
| Priority | 89.67 ± .27% | 27.05 ± 1.64% | 69.83% |
| Position | 89.62 ± 1.04% | 27.59 ± .51% | 69.22% |
| Phase | 0% | 27.59 ± .51% | 63.55% |

Priority and Position competition have zero failure conditional on preserved strict rank. Phase's onset-relative angular order is distinct from its projected-score order; its zero-noise incompatibility prevents treating it as a general competitive robustness comparison. Rank-conditioned denominators, ties and Wilson intervals remain in the CSV.

All three Scan geometries meet the preregistered metric-fragility signature at both N4 and N6 in all four noise replicates. For N6 Position/Scan and Phase/Scan, exact accuracy is .8640 at SD=.20 and .2759 at SD=.35. Thus the first grid crossing below .90 is .20, and below .75/.50 is .35; these are brackets, not interpolated precision estimates. Priority/Scan reaches .7532 at .20 on average and .2705 at .35, with per-seed .75 crossings split between those grid points.

There is **no single most robust geometry** across all criteria. N6 exact-accuracy AUCs are .3126 Priority/Scan, .3159 Position/Scan, .3159 Phase/Scan. Pairwise AUCs are .6687/.5959/.5854 respectively; priority's extrema normalization changes missing-pair behavior and couples noise across items. Position and Phase have identical observed exact curves with these paired draws but differ in partial-output ordering near the circular boundary. Do not infer phase superiority or intrinsic geometry equivalence from one metric.

For unbounded position coordinates, exact Scan correctness requires all item errors to lie within their own .45-slot windows. Independent Gaussian noise therefore predicts `[2 Phi(.45/sigma)−1]^N`; saved analytical checks agree within Monte Carlo variation (maximum per-panel discrepancy .02634). This explains why total-sequence accuracy can deteriorate before rank topology changes. It does not require any learned network failure.

## Layer 3: learned-code gap

All 32 final A.1 saved-code panels replay exactly with the analytical decoder. No encoder/checkpoint retraining or new learned OOD evaluation. Oracle-minus-learned exact gaps, percentage points averaged across four training seeds:

| Cell | N4 gap | N6 gap |
| --- | ---: | ---: |
| Priority/Scan | +70.80 | +96.22 |
| Position/Scan | +52.22 | +99.32 |
| Phase/Scan | +27.27 | +81.71 |
| Phase/Competitive | −91.36 | −78.30 |
| Priority/Competitive | unavailable | unavailable |
| Position/Competitive | unavailable | unavailable |

The last two cells were not trained in A.1 and are explicitly missing, not filled using incompatible A data. The negative Phase/Competitive gap reflects the unsuitable full-circle oracle for cosine competition, **not negative learnability**.

Alignment factors out a best positive affine map for linear codes or common rotation for phase. It is an optimistic target-informed diagnostic, not fed to the reader. No itemwise warp/reflection is permitted. Normalized margins, slopes, phase deviations and anchored/aligned errors are retained.

| Learned Scan | Aligned error, N4/N6 (slot units) | Failure with rank preserved, N4/N6 | Error–failure Spearman range, N4/N6 |
| --- | ---: | ---: | --- |
| Priority | .2569 / .3866 | 66.26% / 94.41% | .634–.822 / .214–.394 |
| Position | .1659 / .2639 | 46.13% / 99.07% | .652–.760 / .137–.166 |
| Phase | .1580 / .2565 | 18.01% / 75.71% | .737–.767 / .457–.675 |

Geometry error positively associates with failure, with a weaker association at the Position/N6 performance floor. One seed has no correct Position/N6 outputs, so its correlation is undefined rather than zero. Rank-preserved errors remain strong evidence that topological order alone is insufficient. All families meet the preregistered learned-bottleneck criterion via association and/or preserved-rank failures. This does not identify a unique optimizer cause or show that a later learning remedy will succeed.

## Causal and invariance controls

Oracle Scan freeze changes 100% of sequences and yields no full correct sequences. Cyclic shift and genuine noncyclic permutation both achieve 100% intended-output agreement for all geometries/lengths. Coordinate swaps give 100% output transposition for competent oracle cells. Competitive score boost moves the selected late item earlier in 100% of eligible trials.

Priority affine, position matched affine/reference, and Phase/Scan common rotation preserve 100% of outputs. **Phase/Competitive fails the .99 sequence-invariance gate** with the symmetric oracle: mean preservation .7975, minimum .4590 across panels. A supplemental numerical check finds that every changed sequence differs only within equal projected-score groups (maximum discrepancy 2.22e−16). Mathematical scores remain invariant, but floating-point tie-selected identities do not. Phase/Competitive swap covariance is also only .80 averaged across lengths. These are flagged implementation/numerical limits for this oracle, not repaired or excused as passing controls. A.1 learned rotation results remain unchanged.

**Manuscript provenance correction (2026-10-03; no rerun):** The preceding numerical-check attribution is qualified. D22 (`phase_tie_invariance_check.csv`) regenerated full-circle oracle codes using `oracle()` rather than reusing D25’s exact generated arrays. Its failing-length pattern is N6/N8/N12, whereas D25’s is N8/N10; N8 preservation fractions match. The maximum discrepancy 2.22e−16 and within-1e−12 reordered-score agreement apply to D22’s regenerated check, not to direct inspection of every D25 changed sequence. D25’s gate failure and all raw results remain unchanged. See Supplement S5 and the S005 same-unit review trail.

## Explicit answers and decision

1. **Q1–Q3:** Yes: genuine Scan serializes perfect Priority, Position and Phase codes at all tested lengths.
2. **Q4:** Yes: Scan fails with preserved ordinal rank, under both controlled noise and learned codes.
3. **Q5:** Yes for the compatible scalar competitive readers; no blanket claim for the full-circle/cosine phase pairing.
4. **Q6:** No universal robustness winner; exact and partial-order metrics differ, and Phase/Competitive has a baseline codebook mismatch.
5. **Q7:** Gaps are given above; two untrained A.1 cells are unavailable.
6. **Q8:** Yes, with seed/load-dependent strength and a floor-limited Position/N6 correlation; association is not causal proof of learning failure.
7. **Q9:** **A2-SCAN-5 — Mixed:** metric fragility plus learned calibration error; no oracle Scan algorithmic failure was observed.
8. **Q10:** **DO NOT RERUN FACTORIAL YET.** The learning remedy has not been demonstrated, and full-circle phase/cosine compatibility remains a separate constraint. A.2 does not authorize a new decoder/codebook.
9. **Q11:** **EXPERIMENT B: BLOCKED.**

## Evidence, verification and limits

[Results index](../results/experiment_A2/README.md) links all required CSVs, twelve plots, threshold/AUC tables and verification. [Source manifest](../experiment_A2_source.json) freezes preregistration and primary code; post-primary reporting and supplemental diagnostics are separately identifiable. PyTorch equivalence uses the frozen A.1 decoder on 75 random panels ×128 trials in the existing pinned remote image. Main diagnostics run locally with NumPy/pandas/SciPy/Matplotlib. A missing pandas dependency initially prevented the remote test from importing; moving report-only imports into their functions resolved that environment issue before primary evaluation. An early learned-analysis invocation found the oracle CSV not yet written; it produced no results and was rerun after primary completion. No scientific implementation or protocol changed after primary results.

Original A/A.1 hashes and evidence are preserved. No Phase training was run; numerical stability is carried forward as A.1 evidence, not independently re-established here. Synthetic oracle capability and error tolerance establish neither biological implementation nor general superiority. Final artifact changes remain in the working tree under the environment's read-only Git metadata restriction.

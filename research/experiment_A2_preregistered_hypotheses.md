# Experiment A.2 preregistered hypotheses and decisions

Frozen before primary A.2 results, 2026-09-29. See specification for exact codes, Gaussian levels, four noise seeds, 1024 trials/condition, lengths and metric denominators. No training or exploratory parameter selection. Source hashes preserve this document even when Git metadata is read-only.

- H-A2-1: oracle Scan incompetence identifies a limitation of current semantics for the tested oracle, not theoretical impossibility.
- H-A2-2: competent oracle Scan with poor learned Scan implicates alignment/learning.
- H-A2-3: differential zero-noise oracle competence across geometries suggests code/readout compatibility differences.
- H-A2-4: Scan failure on rank-preserved noisy/learned codes indicates metric sensitivity beyond topology.
- H-A2-5: Competitive correctness tracks score-relevant preserved rank. Also test representation-defined rank; distinguish full-circle phase rank from cosine projection.
- H-A2-6: robustness may differ by geometry; no direction predicted.

ORACLE_SCAN_VALID requires at least two representation families with exact >=.75 AND all-pair accuracy >=.90 at BOTH N4 and N6 in every noise replicate at sigma0. Higher lengths are separate scaling observations.

Operational metric-fragility evidence: at sigma<=.35, exact accuracy drops >=.20 from oracle, with >=.20 conditional failure among rank-preserved trials and >=256 such trials pooled, reproducible in all four noise replicates at N4 and N6 for at least two geometries. Report curve and counts, not this threshold alone.

Learned bottleneck evidence: oracle-minus-learned Scan exact gap >=.20 and aligned/anchored geometry errors positively associate with failure (Spearman>=.20 in >=3/4 seeds at both loads), or rank-preserved learned failure>=.20 in >=3/4 seeds. These are diagnostic associations, not proof of optimizer causation.

Classification precedence: A2-SCAN-1 if oracle gate fails broadly (zero/one competent family); A2-SCAN-4 if only some oracle geometries are competent with >=.20 exact difference; A2-SCAN-5 if oracle gate passes and BOTH metric-fragility and learned-bottleneck criteria hold; otherwise A2-SCAN-2 for fragility, A2-SCAN-3 for robust oracle plus learned bottleneck. If none distinguish cleanly use A2-SCAN-5 with unresolved factors stated. Full-circle Phase/Competitive failure alone does not classify the Scan problem.

Oracle expected invariance >=.99 output preservation; Scan freeze >=.50 sequence change, shift/noncyclic permutation >=.99 transformed-target agreement on competent zero-noise cells. Competitive boost should move selected last-target item earlier >=.99 where it was not already first. Swaps should covary output on untied competent codes; tied-score phase cases reported separately. Failures are flagged, not repaired mid-analysis.

The compatibility question remains STILL UNRESOLVED unless oracle gate passes, robustness is characterized, prior phase stability remains interpretable, AND a concrete non-cell-specific way to address learned calibration without tuning is supported. This study does not implement any remedy. Default recommendation DO NOT RERUN FACTORIAL YET if the learning remedy remains untested. EXPERIMENT B: BLOCKED in all outcomes.

No factorial significance test, biological inference, novelty claim, geometry winner from incompatible zero-noise baselines, or post hoc favorable oracle/code choice. Retain all replicates and negative results.

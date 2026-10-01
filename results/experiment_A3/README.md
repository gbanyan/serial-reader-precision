# A.3 evidence index

**A3-GEO-5 — Mixed. DO NOT RERUN FACTORIAL YET. EXPERIMENT B BLOCKED.** [Summary](../../research/experiment_A3_summary.md), [comparability](../../research/experiment_A3_checkpoint_comparability.md), [preregistration](../../research/experiment_A3_preregistered_hypotheses.md).

## Required tables

- [Geometry summary](../experiment_A3_geometry_summary.csv): 144 source/seed/checkpoint/load panels.
- [Rank/metric decomposition](../experiment_A3_rank_metric_decomposition.csv): 432 strata with counts and failures; empty strata are missing.
- [Readout alignment](../experiment_A3_readout_alignment.csv): actual score geometry and hypothetical/actual Scan slots, kept distinct.
- [Geometry trajectories](../experiment_A3_geometry_trajectory.csv): all300/600/900 metrics, not selected checkpoints.
- [Cross-readout transfer](../experiment_A3_cross_readout_transfer.csv): frozen other-reader replay, no fitting.
- [Counterfactual geometry](../experiment_A3_counterfactual_geometry.csv): information provenance labels distinguish target-informed ceiling, source-inferred rank and nearest-slot snapping.
- [Phase arcs](../experiment_A3_phase_arc_analysis.csv): arc, semicircle, wrap and cosine alignment.

Additional tables: [paired seed differences/CI](paired_geometry_differences.csv), [adjacent spacing](adjacent_spacing.csv), [same-time correlations](geometry_performance_correlations.csv), [lagged associations](lagged_geometry_associations.csv), [decision](decision.json), [verification](verification.json), [manifest](artifact_manifest.json).

## Plots

1. [Learned geometry](01_learned_geometry.png) — illustrative seed11 N6, not population proof. Phase dots pool60 trials; pooled occupancy is not the per-trial minimum arc used in the analysis.
2. [Rank vs metric](02_rank_metric.png).
3. [Adjacent spacing](03_adjacent_spacing.png).
4. [Readout alignment](04_readout_alignment.png).
5. [Checkpoint evolution](05_trajectory.png).
6. [Geometry vs behavior](06_geometry_performance.png).
7. [Cross-transfer](07_transfer.png).
8. [Canonicalization](08_canonicalization.png).
9. [Phase arc occupancy](09_phase_arc.png).
10. [Phase cosine monotonicity](10_phase_monotonicity.png).
11. [Phase counterfactuals](11_phase_counterfactual.png).
12. [Scan snapping](12_scan_snap.png).

`python -m experiment_a3.analyze` reads saved code arrays only and refuses completed-primary overwrite. `python -m experiment_a3.report` regenerates reports without model execution. Local Mac dependencies NumPy/pandas/SciPy/Matplotlib; no torch execution or remote service required for A.3. [Source manifest](../../experiment_A3_source.json) records frozen source and protected A/A.1/A.2 hashes. Raw trial geometry lives in ignored `runs/experiment_A3/geometry_trials.csv`. Inputs remain at their original checkpoint paths.

Validation commands: `python -m unittest discover -s tests -p test_experiment_a3.py -v` (four passing geometry contracts); `python -m experiment_a3.verify` (source/result hashes, replay metadata, row counts and links). The verifier writes only A.3 manifests.

Rates are fractions; linear canonical RMSE is endpoint-normalized, actual Scan errors in slot units, phase canonical error in turns. Do not combine unlike units. Alignments use target-informed per-trial diagnostics and are never silently applied before native or transfer behavior. Bootstrap intervals use four seeds, not thousands of pseudo-independent trials. The primary label is a documented synthesis of the preregistered per-family thresholds and native competence limits, not a fitted classifier.

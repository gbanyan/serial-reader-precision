# Experiment A.2 evidence index

**A2-SCAN-5 — Mixed; ORACLE_SCAN_VALID; STILL UNRESOLVED; DO NOT RERUN FACTORIAL YET; EXPERIMENT B BLOCKED.** Read the [summary](../../research/experiment_A2_summary.md), [specification](../../research/experiment_A2_oracle_compatibility.md), and [preregistration](../../research/experiment_A2_preregistered_hypotheses.md).

## Tables

| File | Contents |
| --- | --- |
| [Oracle matrix](../experiment_A2_oracle_matrix.csv) | 120 representation/readout/load/noise-replicate rows |
| [Noise curves](../experiment_A2_noise_curves.csv) | 960 rows; 1024 paired trials each, 4 noise seeds, 8 fixed levels |
| [Rank inversion](../experiment_A2_rank_inversion_analysis.csv) | Conditional counts, failures and Wilson intervals; ties separate |
| [Learnability gap](../experiment_A2_learnability_gap.csv) | 32 existing A.1 panels and 4 explicit unavailable cells/loads |
| [Learned geometry](../experiment_A2_learned_geometry_error.csv) | Per-seed aligned error, margins, slopes, rotation residual, associations |
| [Invariance](../experiment_A2_invariance.csv) | 120 rows; phase competitive tie-sensitive failure retained |
| [Cursor/competitive interventions](../experiment_A2_cursor_interventions.csv) | Freeze/shift/noncyclic permutation, swaps and score boosts |
| [Thresholds](noise_thresholds.csv) | First below-threshold grid bracket; already-below/not-reached distinguished |
| [AUC](robustness_auc.csv) | Exact/pairwise trapezoidal AUC over sigma0–1 |
| [Noise error association](noise_error_association.csv) | Error/failure correlations and conditional errors on identical reconstructed primary draws; all accuracies replay exactly |
| [Analytical scan check](analytical_scan_check.csv) | Gaussian window formula vs observed Position/Scan exact accuracy |
| [Phase tie check](phase_tie_invariance_check.csv) | Supplementary score-equivalence analysis of rotation failures |
| [Decision](decision.json) | Explicit preregistered gate aggregation |
| [Verification](verification.json) | Frozen-source/evidence hashes, tests and counts |
| [Artifact manifest](artifact_manifest.json) | New result/source hashes and execution provenance |

CSV rates are fractions. Missing items count against primary pairwise accuracy; conditional tau requires pair coverage. Empty rank strata and constant-outcome correlations are missing, not zero. Noise SD is in adjacent ordinal spacings. Four noise seeds are Monte Carlo replicates, not training seeds. AUC/threshold results for Phase/Competitive are conditioned on its incompatible full-circle codebook and must not be read as evidence that phase representations cannot support competition. Negative learned gaps have the same caveat.

## Plots

1. [Oracle 3×2 matrix](01_oracle_heatmap.png)
2. [Oracle scaling](02_oracle_length.png)
3. [Exact noise curves, all lengths](03_noise_exact.png)
4. [Pairwise noise curves, all lengths](04_noise_pairwise.png)
5. [Failure with rank preserved/inverted](05_rank_preserved_failure.png)
6. [Readout robustness within geometry](06_readout_robustness.png)
7. [Threshold crossings](07_thresholds.png) — averages of first tested crossing across seeds; per-seed brackets are canonical.
8. [Oracle versus learned accuracy](08_learned_gap.png)
9. [Aligned geometry error](09_geometry_error.png)
10. [Geometry error versus failure](10_error_failure.png)
11. [Oracle cursor interventions](11_cursor.png)
12. [Invariance](12_invariance.png)

## Reproduction and preserved state

- `python -m experiment_a2.analysis primary`: zero-training oracle/noise evaluation; refuses overwrite after completion. The oracle preflight is recorded in `runs/experiment_A2/oracle_before_noise.json` before noisy evaluation.
- `python -m experiment_a2.analysis learned`: reads final saved A.1 codes only; asserts exact prediction replay. Run after primary output exists.
- `python -m experiment_a2.supplement`: requested alignment/margin summaries and clearly secondary analytical/tie checks.
- `python -m experiment_a2.report`: figures, threshold/AUC summaries and preregistered decision; no model runs.
- `python -m unittest discover -s tests -p test_experiment_a2.py -v`: four contract tests, local Mac.
- `python -m experiment_a2.test_equivalence`: 75 randomized panels against actual frozen PyTorch decode, remote pinned image `oscillation-pbos-deps:20260928`, isolated `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a2-20260929/`, 2 CPUs/2GiB/512PIDs, no ports. Container removed only after log retrieval. No training or source modification in the read-only mount.

Source manifest: [experiment_A2_source.json](../../experiment_A2_source.json). Detailed learned trial metrics and execution logs live in ignored `runs/experiment_A2/`; noisy draws are fully reproducible from fixed generator source/seeds, with no checkpoint or learned adapter. The new namespace imports frozen A/A.1 equations; their artifacts, raw checkpoints and historical interpretations remain unchanged.

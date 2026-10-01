# Experiment A.1 evidence index

Status: calibration complete; **SCAN VALIDITY FAIL; overall PHASE STABILITY FAIL; FACTORIAL NOT RUN; NOT READY FOR EXPERIMENT B**. The numerical/no-collapse subgate passes for both phase cells; the full phase gate fails on Phase/Scan competence at N6. Read [summary](../../research/experiment_A1_summary.md) and [preregistered gates](../../research/experiment_A1_preregistered_gates.md).

| File | Evidence |
| --- | --- |
| [Old Scan diagnostics](../experiment_A1_old_scan_diagnostics.csv) | 192 rows; exact original-checkpoint replay, eight original seeds |
| [Scan calibration](../experiment_A1_scan_calibration.csv) | 96 normal/freeze/shift/permutation rows; four new seeds |
| [Phase stability](../experiment_A1_phase_stability.csv) | 144 monitoring rows; norms, code/probe diagnostics, collapse/spike flags |
| [Causal gates](../experiment_A1_causal_gates.csv) | 32 seed/load rows; explicit individual gate values |
| [Invariance](../experiment_A1_invariance.csv) | 48 seed/load/transform rows |
| [Checkpoint metrics](checkpoint_metrics.csv) | All 288 monitoring rows including nonphase scans |
| [Final per-seed metrics](final_by_seed.csv) | 32 final rows, both loads separately |
| [All interventions](interventions.csv) | 168 rows including swap/ablation and competitive boost |
| [Training curves](training_curves.csv) | All 14,400 training-step losses and pre-clip gradient norms |
| [Decision](decision.json) | Gate aggregation; no automatic factorial runner |
| [Noncyclic coverage check](noncyclic_cursor_audit.csv) | 24 post-calibration saved-code rows; not used to change gates |
| [Verification](verification.json) | Tests, replay checks, original evidence preservation |
| [Artifact manifest](artifact_manifest.json) | Raw calibration/checkpoint hashes and remote copy |

Primary pairwise accuracy includes missing pairs as failures. Conditional Kendall tau applies only to present unique items and must be read with coverage. NO_MATCH is index -1; it never consumes an item. Transformation agreement is conditional on originally correct trials; `normal_correct_count` is its denominator, while `transformed_target_accuracy` uses all trials. The ordinary monitoring and final causal panels have separate fixed seeds, so their means need not coincide. Fractions are not percentages in CSV.

## Required calibration plots

1. [Normal versus frozen cursor](01_freeze.png)
2. [Cursor-shift agreement](02_shift.png)
3. [Cursor-permutation agreement](03_permutation.png)
4. [Normal scan competence](04_scan_competence.png)
5. [Phase training loss by seed](05_phase_loss.png)
6. [Phase collapse/competence trajectories](06_phase_collapse.png)
7. [Phase ordinal decoding over training](07_phase_decoding.png)
8. [Common rotation invariance](08_rotation.png)

No repaired-factorial interaction or OOD plot exists because the calibration gate failed. Do not reinterpret this incomplete factorial as evidence that the old interaction vanished. Rebuild plots/tables with `python -m experiment_a1.report` (local NumPy/pandas/Matplotlib). Training command `python -m experiment_a1.run --worker 0` or `--worker 1` refuses existing-run overwrite and must not be used to rebuild reports.

Plot 04 averages N4/N6 within seed; load-specific competence and gates remain separate in the CSVs and research summary. The registered permutation in plot 03 is a reverse cyclic shift; the supplementary noncyclic audit is separately labeled above. Recheck evidence preservation and independent behavioral metrics with `python -m experiment_a1.verify_artifacts`; this writes only the A.1 manifests and does not run models.

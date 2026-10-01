# Experiment A result index

Status: completed fixed-budget factorial; **A-COMPAT-6, NOT READY FOR EXPERIMENT B**. Start with [research summary](../../research/experiment_A_summary.md). The external reference is excluded from the factorial statistics. No failed seeds were discarded.

## Canonical machine-readable evidence

| File | Contents |
| --- | --- |
| [Main factorial](../experiment_A_main_factorial.csv) | 336 system/seed/checkpoint/load rows, including flagged external reference |
| [Representation diagnostics](../experiment_A_representation_diagnostics.csv) | 864 layer-specific rows; independent-fit rank probe, anchored code decoding |
| [Interventions](../experiment_A_interventions.csv) | 288 code/readout/ablation rows |
| [Invariance](../experiment_A_invariance.csv) | 256 rows including items-only-rotation negative control |
| [OOD length](../experiment_A_ood_length.csv) | 168 rows; 144 evaluated, 24 explicitly withheld by ID gate |
| [Parameters](parameters.csv) | Exact shared/code/readout parameter counts |
| [Training curves](training_curves.csv) | Fixed-step N6 sampled loss and gradient norm |
| [Convergence](convergence_summary.csv) | Coarse checkpoint threshold, final change and measured runtime |
| [Seed table](final_exact_by_seed.csv) | Final N4/N6 average, all eight seeds |
| [Behavior summary](behavior_summary.csv) | Mean/SD by cell/load |
| [Mechanistic gates](mechanistic_gates.csv) | Original per-seed thresholds; qualitative confounds remain separate |
| [Statistics](statistics.json) | Confirmatory final interaction, descriptive checkpoint effects, confound override |
| [Readout geometry](readout_geometry.csv) | Post-main saved-state replay, monotone-sort/frozen-cursor agreement |
| [Unanchored phase decoder](unanchored_phase_decoding.csv) | Secondary two-fold trial-grouped relative-difference decoding |
| [Verification](verification.json) | Tests, legacy preservation, paired inputs and artifact integrity |
| [Artifact hashes](artifact_manifest.json) | Raw runs/checkpoints and remote-copy identity |

Fractions are in [0,1], tau/Spearman in [-1,1]; rank shifts are item positions; phase radians before adaptation, coordinates in turns or normalized linear units. `first_error` is zero-based and equals N for a correct sequence. `exact_change` is intervention minus original; `ablation_drop` reverses that sign. Expected invariances are anchor/reference inclusive. Invariance logit delta of +3 for score offset is intentional. Undefined/ineligible values are blank, not zero. No single aggregate global ranking is intended.

## Figures

1. [R × O interaction](01_interaction.png)
2. [Exact by cell/seed](02_exact.png)
3. [Pairwise accuracy](03_pairwise.png)
4. [Kendall tau](04_tau.png)
5. [Representation-only order decoding](05_representation.png)
6. [Code-swap inversion](06_rep_swap.png)
7. [Readout intervention](07_readout.png)
8. [Matched invariances](08_invariance.png)
9. [Training curves](09_training.png)
10. [Checkpoint trajectories](10_checkpoints.png)
11. [OOD lengths](11_ood.png)
12. [Parameter counts](12_parameters.png)

Points/curves preserve seed variation; summary error bars are seed SD, not trial-based confidence intervals. Bootstrap CIs for paired readout differences are in statistics.json. All figures rebuild with `python -m experiment_a.report`; raw evidence is not overwritten. Supplementary replay uses `python -m experiment_a.inspect_codes`.

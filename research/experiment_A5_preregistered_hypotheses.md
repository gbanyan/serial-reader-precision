# Experiment A.5 — training budget and new-load prediction test (preregistered 2026-10-03)

Authorization: user request on 2026-10-03 to preregister A.5 and run items 1 (budget curve) and 3 (prediction test under a new condition) after the [A.4 results](experiment_A4_summary.md). Model capacity (item 2) is deferred until A.5-B is known. Experiment B, the repaired full factorial and Dynamic Routing remain closed.

## Questions

* **A.5-B (budget).** A.4 left the residual Scan shortfall unresolved: with a centring objective (β=16), N=6 accuracy was still rising at 3,600 updates (Position 29% → 56%, Priority 2% → 29% from 900 to 3,600). Does it approach the 100% compatible oracle with much longer training, or plateau? Does the β=1 objective stay biased out of window regardless of budget?
* **A.5-N8 (new-condition prediction).** The analytic loss optimum was used to explain A.1 after the fact and was then confirmed at N=6 in A.4. A.5 tests it at a training load never used for training: N=8 only. Predictions below are copied from `results/experiment_A4/analytic_objective_optimum.csv` (code-space minimizers; computed before this preregistration and before any N=8 training).

## Fixed design

Unchanged from A.4: `RepairedModel` and the unchanged A.1 reader, generator `experiment-a-scalar-v1`, AdamW lr 1e-3, weight decay .01, batch 32, clip 1, deterministic PyTorch, pinned image `oscillation-pbos-deps:20260928`, `panel()` evaluation (1,024 episodes, generator seed 810000+N), seeds 11, 22, 33, 44, 55, 66, 77, 88. Objective: cross entropy on β·logits, as in A.4. Cells: priority_scan, position_scan, phase_scan.

| Arm | Training loads | β | Updates | Evaluations (also checkpoints) | Eval N |
|---|---|---|---|---|---|
| B-b1, B-b16 | alternating 4/6 | 1, 16 | 36,000 | 900, 1,800, 3,600, 7,200, 14,400, 28,800, 36,000 | 4, 6, 8 |
| N8-b1, N8-b16 | 8 only | 1, 16 | 3,600 | 900, 1,800, 3,600 | 6, 8 |

96 runs. Offsets are signed deviations of the Scan-adapted coordinate (circular: angle in turns, wrapped) from the target slot centre, median over episodes per rank, in units of w=.45/N; "interior" = ranks 1..N−2 (Priority, whose end ranks are fixed by the adapter) or 1..N−1 (Position, circular).

## Gate

G0: B-b1 and B-b16 must reproduce the A.4 L-b1 and L-b16 saved evaluation predictions and codes exactly at updates 900, 1,800 and 3,600 for N=4, 6, 8 (evaluation does not consume training randomness). Failure stops analysis until diagnosed.

## A.5-B hypotheses (N=6, both scalar families unless stated)

* **B1 persistent bias.** At 36,000 updates, B-b1 mean interior offset > 0.8w and mean exact accuracy < 15%, for both Priority and Position.
* **B2 budget classification (descriptive rule, no directional prediction).** For B-b16 at 36,000 updates, per family: CLOSES if mean exact ≥ 90%; PLATEAU if < 90% and the 14,400 → 36,000 gain is < 3 percentage points; otherwise STILL-RISING. The circular cell is classified the same way, descriptively.
* **B3.** B-b16 − B-b1 at 36,000 updates > 0 in at least 7/8 seeds for each scalar family.

## A.5-N8 hypotheses (N=8, update 3,600)

Analytic optimum interior means at N=8: β=1 Priority 1.64w, Position 1.59w, circular 0.80w; β=16 all ≈ 0.07w. Per-rank β=1 profiles: Priority 0, 1.12, 1.65, 1.78, 1.80, 1.76, 1.73, 0; Position 0, 1.12, 1.65, 1.79, 1.83, 1.82, 1.84, 1.11 (last rank limited by the sigmoid bound); circular 0, .42, .80, 1.02, 1.09, .99, .74, .55.

* **N1 magnitude.** N8-b1 mean interior offset > 1.2w for Priority and Position, and larger than the corresponding A.4 L-b1 N=6 values (1.02w, 1.07w).
* **N2 removal.** N8-b16 mean interior offset < 0.3w in absolute value for all three families.
* **N3 profile shape.** For each family under N8-b1, the Spearman correlation across ranks 1..N−1 between the seed-mean per-rank learned offset and the analytic per-rank profile is ≥ 0.6. The circular profile's distinctive prediction is a mid-rank peak (rank 4) rather than a monotone rise.
* **N4 accuracy.** N8-b1 scalar Scan N=8 exact accuracy < 5% (out-of-window optimum). Circular is descriptive: the β=1 analytic optimum is now outside its windows (1.09w), unlike N=6.

## Interpretation rules

* B1 and N1–N3 supported: the objective-optimum account predicts learned code geometry prospectively under a new load and persists with a 40-fold budget; it can be presented as a quantitative model of the A.1 Scan bias, not only a post-hoc explanation.
* B2 CLOSES: the residual A.4 shortfall is a training-budget effect under a centring objective; encoder capacity is not implicated at this scale. PLATEAU: a residual limit (encoder/optimizer/capacity) remains, and the deferred capacity experiment becomes the next test. STILL-RISING: unresolved.
* β changes gradient scale as well as the optimum; claims about the offset mechanism rest on the offset hypotheses, not accuracy alone.
* Seeds are replicates; loads, checkpoints and shared evaluation episodes are dependent. Paired-seed bootstrap intervals (10,000 resamples) are descriptive. Checkpoint trajectories are not independent tests.
* A–A.4 records are unchanged.

## Execution

Remote directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a5-20261003/`; six task containers (2 CPUs, 2 GiB, 512 PIDs, json-file logs 10m×3, no network). Raw runs under ignored `runs/experiment_A5/`; tables under `results/experiment_A5/`. Source hashes in `experiment_A5_source.json`, verified per run; runs refuse to overwrite existing directories.

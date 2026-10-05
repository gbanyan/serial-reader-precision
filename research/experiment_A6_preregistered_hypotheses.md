# Experiment A.6 — temperature versus displacement: crossover and distractor-removal test (preregistered 2026-10-03)

Authorization: standing user authorization for needed experiments (2026-10-03), after a second external review asked whether the A.4/A.5 rescue is "only softmax temperature". The A.4/A.5 intervention *is* a logit-scale (temperature) change, so this cannot be answered by argument. A.6 tests predictions that separate the two accounts. Experiment B, the repaired full factorial, model-capacity scaling and Dynamic Routing remain closed.

## Competing accounts

* **Generic scale/temperature account.** Sharper softmax (larger β) improves convergence and code compactness generally (prior art: NormFace; heated-up softmax; temperature dynamics). It predicts monotone improvement with β at every list length and no special role for the capture windows.
* **Displacement account (this work).** Later-ranked items act as distractors at earlier steps and displace the loss optimum; Scan fails when the displaced optimum leaves the capture window. It predicts a length-dependent threshold in β located where the analytic optimum crosses the window edge, and predicts that removing the distractor terms at β=1 removes the displacement without changing temperature.

Analytic maximum interior offsets (code-space optimum; `experiment_a4/analytic.py`, computed before this preregistration):

| β | N=6 Priority/Position/circular | N=8 Priority/Position/circular |
|---|---|---|
| 1 | 1.13 / 1.18 / 0.71 | 1.80 / 1.84 / 1.09 |
| 2 | 0.65 / 0.71 / 0.56 (inside) | 1.06 / 1.11 / 0.91 (scalar outside, circular inside) |
| 4 | 0.32 / 0.33 / 0.31 | 0.58 / 0.63 / 0.57 (inside) |

## Fixed design

As A.5: `RepairedModel`, unchanged A.1 reader, generator `experiment-a-scalar-v1`, AdamW lr 1e-3, weight decay .01, batch 32, clip 1, deterministic PyTorch, pinned image, `panel()` evaluation, seeds 11–88 (8), cells priority_scan, position_scan, phase_scan. All arms 36,000 updates, evaluations/checkpoints at 900, 1,800, 3,600, 7,200, 14,400, 28,800, 36,000.

| Arm | Training loads | Objective | Eval N |
|---|---|---|---|
| X46-b2 | alternating 4/6 | CE on 2·logits | 4, 6, 8 |
| N8-b2L | 8 only | CE on 2·logits | 6, 8 |
| N8-b4L | 8 only | CE on 4·logits | 6, 8 |
| N8-b16L | 8 only | CE on 16·logits | 6, 8 |
| D | alternating 4/6 | CE at β=1 over {NO_MATCH, target} only: other unused items removed from each step's softmax | 4, 6, 8 |
| RL | alternating 4/6 | A.4 regression objective (reader coordinate to target reference, boundary units) | 4, 6, 8 |

144 runs. Comparators already on disk: A.5 B-b1 and B-b16 (4/6, 36,000 updates), A.5 N8-b1 (3,600 updates).

## Gates

* G0a: N8-b16L reproduces A.5 N8-b16 predictions and codes exactly at 900/1,800/3,600 for N=6 and 8.
* G0b: RL reproduces A.4 R exactly at 900 for N=4, 6, 8.
Failure stops analysis until diagnosed.

## Hypotheses (update 36,000; eight seeds; "both scalar" = Priority and Position each)

* **X1 crossover.** (a) X46-b2 N=6 mean exact ≥ 70% for both scalar families; (b) N8-b2L N=8 mean exact < 10% for both scalar families with mean interior offset > 0.9w; (c) N8-b4L − N8-b2L at N=8 ≥ 30 pp for both scalar families with ≥ 7/8 seeds positive. X1 is supported only if (a), (b) and (c) all hold. The generic account predicts that β=2 helps at both lengths and is contradicted by (a)+(b) together.
* **X2 circular contrast (secondary, directional).** At N8-b2L, where the circular optimum lies inside its windows but the scalar optima do not, circular N=8 mean exact exceeds each scalar family by ≥ 20 pp.
* **D1 distractor removal.** D: mean interior offset at N=6 with absolute value < 0.3w for both scalar families, and D − B-b1 N=6 exact ≥ 50 pp with ≥ 7/8 seeds positive for both scalar families.
* **R1 temperature-free objective (secondary).** RL N=6 mean exact − B-b1 ≥ 50 pp for both scalar families.

## Interpretation rules

* X1 and D1 supported: the rescue is attributed to removing the distractor-induced displacement relative to the capture windows, not to sharper softmax as such; temperature matters here through where it places the loss optimum.
* X1 fails because N8-b2L succeeds: the window-crossing threshold is not supported; a generic scale account is not excluded.
* D1 fails while X1 holds: the threshold is supported but distractor terms are not shown to be the sole source.
* Marginal-offset cases (optimum near but inside the window) may learn slowly; X1(a) uses a 70% threshold, not oracle-level accuracy.
* Prediction timing: formulated after A.1–A.5 outcomes were known and before any A.6 training. Earlier experiments are not described as preregistered from the start.
* Seeds are replicates; loads, checkpoints and shared evaluation episodes are dependent. Paired-seed bootstrap intervals are descriptive.

## Execution

Remote directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a6-20261003/`; seven task containers (2 CPUs, 2 GiB, 512 PIDs, json-file logs 10m×3, no network). Raw runs: ignored `runs/experiment_A6/`; tables: `results/experiment_A6/`. Source hashes in `experiment_A6_source.json`; runs refuse to overwrite.

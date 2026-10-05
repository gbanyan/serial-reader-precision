# Experiment A.7 — matched-length control, capture-width crossover and encoder generality (prospectively specified 2026-10-04)

Authorization: user request on 2026-10-04 to run all three follow-ups proposed after a methodological critique of manuscript v2 ("All three"). This file is committed to the local Git repository before any A.7 training and pushed to the private remote before training starts; neither establishes independently verifiable timing. Experiment B, the repaired full factorial and Dynamic Routing remain closed.

## Questions

* **A7-M (matched length).** In A.6 the β=2 success at N=6 came from models trained on alternating N∈{4,6}, whereas the β=2 failure at N=8 came from models trained only at N=8. Does the N=6 result hold when training is also single-length?
* **A7-W (capture width).** A.4–A.6 moved the loss optimum (β, N) relative to fixed windows. A7-W instead moves the window edge. The code-space minimizer of the β=1 loss at N=6 displaces items by almost the same absolute amount for any capture width (maximum interior displacement 0.50–0.55/N for scalar codes and 0.31–0.33/N for circular codes over w = 0.25/N to 0.75/N), so the window width alone decides inside versus outside. Predicted maximum offsets in units of the new w: w=0.30/N: Priority 1.66w, Position 1.73w, circular 1.04w (all outside; the minimizer's own Scan output fails); w=0.75/N: 0.74w, 0.77w, 0.45w (all inside; the minimizer is read correctly). At the standard w=0.45/N the scalar optima are outside and the circular optimum inside. This predicts a two-way crossover: scalar codes fail at 0.45 but succeed at 0.75, and circular codes succeed at 0.45 but fail at 0.30.
* **A7-E (encoder).** The account operates at the level of the objective and should not depend on the encoder. Does a larger encoder show the same displacement and the same distractor-removal rescue?

## Fixed design

Unchanged unless stated: data generator `experiment-a-scalar-v1`, AdamW lr 1e-3, weight decay .01, batch 32, clip 1, deterministic PyTorch, pinned image `oscillation-pbos-deps:20260928`, `panel()` evaluation (1,024 episodes, generator 810000+N), seeds 11–88 (8), cells priority_scan, position_scan, phase_scan. Evaluations/checkpoints at 900, 1,800, 3,600, 7,200, 14,400, 28,800, 36,000 (A7-E stops at 14,400).

| Arm | Training loads | Objective | Reader capture width | Encoder | Updates | Eval N |
|---|---|---|---|---|---|---|
| M6-b2 | 6 only | CE, β=2 | 0.45/N | A.1 (96-d, 2 blocks) | 36,000 | 4, 6, 8 |
| M6-b1 | 6 only | CE, β=1 | 0.45/N | A.1 | 36,000 | 4, 6, 8 |
| W30-b1 | alternating 4/6 | CE, β=1 | 0.30/N (training and evaluation) | A.1 | 36,000 | 4, 6, 8 |
| W75-b1 | alternating 4/6 | CE, β=1 | 0.75/N (training and evaluation) | A.1 | 36,000 | 4, 6, 8 |
| E-b1 | alternating 4/6 | CE, β=1 | 0.45/N | 192-d, 4 blocks, head 196→192→2 | 14,400 | 4, 6, 8 |
| E-D | alternating 4/6 | CE, β=1, distractors removed (as A.6 D) | 0.45/N | 192-d, 4 blocks | 14,400 | 4, 6, 8 |

144 runs. The capture width w enters both the NO_MATCH logit used in training (−16w², or the chord equivalent) and the acceptance rule at evaluation; windows overlap when w > 0.5/N, and the reader remains the rejecting nearest-available matcher. Offsets for W arms are reported both in units of the arm's own w and in units of 1/N. Comparators already on disk: A.5 B-b1 (standard width, 4/6, 36,000), A.6 X46-b2 and N8-b2L, A.6 D at 14,400.

## Gates

* G0a: the width-parameterized reader with w=0.45/N reproduces `RepairedModel` logits and predictions exactly (unit test, before training).
* G0b: the encoder variant at 96-d/2 blocks reproduces `RepairedModel` parameters and outputs exactly under the same seed (unit test).
* G0c: no nonfinite losses; all runs complete.

## Hypotheses (N=6 read; mean over eight seeds; "scalar" = Priority and Position each)

* **M1.** M6-b2 at 36,000: scalar mean exact ≥ 70% and mean interior offset < 0.9w. Together with A.6 N8-b2L (< 10%), the β=2 contrast between N=6 and N=8 then holds under single-length training at both lengths.
* **M2 (secondary).** M6-b1 at 36,000: scalar mean exact < 15% with interior offset > 0.8w.
* **W1 offset invariance.** At 36,000, β=1 learned scalar interior offsets measured in units of 1/N differ by less than 25% between W30-b1, W75-b1 and A.5 B-b1 (relative to B-b1), for each scalar family.
* **W2 scalar flip.** W75-b1 scalar mean exact ≥ 50% and exceeds A.5 B-b1 by ≥ 40 points with ≥ 7/8 seeds positive, for each scalar family.
* **W3 circular flip.** W30-b1 circular mean exact is ≥ 20 points below A.5 B-b1 circular (88.4%), with ≥ 7/8 seeds below the B-b1 seed mean. W30-b1 scalar mean exact < 5%.
* **E1.** E-b1 at 14,400: scalar mean interior offset > 0.8w and mean exact < 15%.
* **E2.** E-D at 14,400: scalar |mean interior offset| < 0.3w, and E-D − E-b1 ≥ 40 points with ≥ 7/8 seeds positive, for each scalar family.

## Interpretation rules

* A wider window makes any noisy code easier to read and a narrower one harder; W2 and W3 alone cannot separate the threshold account from general difficulty. The mechanism-specific evidence in A7-W is W1 (displacement set by the objective, not by the window) together with the direction of both flips. If W2/W3 hold but W1 fails, the window effect is reported as consistent with but not specific to the account.
* Circular W3 is a marginal prediction (optimum 1.04w); its failure is reported without reinterpretation.
* E1 and E2 supported: the displacement and its removal do not depend on the A.1 encoder size at this scale. Failure of E2 at 14,400 updates is reported as such; no budget extension is made within A.7.
* Predictions were formed after A.1–A.6 outcomes were known and before any A.7 training. Seeds are replicates; loads, checkpoints and shared episodes are dependent. Paired-seed bootstrap intervals are descriptive.

## Execution

Remote directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a7-20261004/`; seven task containers (2 CPUs, 2 GiB, 512 PIDs, json-file logs 10m×3, no network). Raw runs: ignored `runs/experiment_A7/`; tables: `results/experiment_A7/`. Source hashes in `experiment_A7_source.json`; runs refuse to overwrite.

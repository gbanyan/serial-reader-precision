# Experiment A.6 — temperature versus displacement: results (2026-10-03)

Preregistration: [experiment_A6_preregistered_hypotheses.md](experiment_A6_preregistered_hypotheses.md) (commit before training). Implementation commit `89dcd88`; hashes in `experiment_A6_source.json`, verified per run. 144/144 runs completed in the pinned image on gbminipc (seven task containers, 2 CPUs/2 GiB/512 PIDs, no network), all exit code 0, no nonfinite losses. Raw runs: ignored `runs/experiment_A6/` (local and `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a6-20261003/`, 2.8 GB). Tables: [results/experiment_A6/](../results/experiment_A6/README.md). The local wait loop that monitored the run hit its two-hour limit and was restarted; the remote runs were unaffected.

**Classification: G0 PASS; X1 SUPPORTED; X2 SUPPORTED; D1 SUPPORTED; R1 SUPPORTED.**

## Gates

G0a/G0b PASS: N8-b16L reproduced A.5 N8-b16 at 900/1,800/3,600 (N=6, 8), and RL reproduced A.4 R at 900 (N=4, 6, 8), exactly (216/216 panels).

## Results (36,000 updates, eight seeds, mean exact accuracy [seed range])

| Arm (training N, objective) | Read at | Priority | Position | Circular | Interior offset (Pri/Pos/Circ, w) |
|---|---|---:|---:|---:|---|
| X46-b2 (4/6, β=2) | N=6 | 79.9% [65.8, 86.9] | 89.2% [84.3, 91.6] | 90.2% [88.9, 91.3] | 0.66 / 0.66 / 0.42 |
| N8-b2L (8, β=2) | N=8 | 4.6% [0.0, 31.1] | 0.0% [0.0, 0.1] | 80.3% [68.6, 90.8] | 1.03 / 1.04 / 0.68 |
| N8-b4L (8, β=4) | N=8 | 80.1% [68.7, 85.4] | 84.7% [79.4, 89.5] | 88.4% [85.1, 92.5] | 0.56 / 0.62 / 0.46 |
| N8-b16L (8, β=16) | N=8 | 87.2% | 89.9% | 90.4% | 0.11 / 0.11 / 0.07 |
| D (4/6, β=1, distractors removed) | N=6 | 86.6% [71.6, 92.2] | 92.4% [89.4, 94.2] | 91.9% [90.3, 93.7] | 0.02 / −0.03 / 0.00 |
| RL (4/6, regression) | N=6 | 90.1% | 93.0% | 92.9% | −0.04 / 0.01 / 0.00 |
| A.5 B-b1 comparator (4/6, β=1) | N=6 | 3.8% | 0.0% | 88.4% | 1.04 / 1.11 / — |

Analytic maximum interior offsets for comparison: β=2 at N=6 0.65/0.71/0.56w (inside); β=2 at N=8 1.06/1.11/0.91w (scalar outside, circular inside); β=4 at N=8 0.58/0.63/0.57w (inside).

* **X1 supported.** (a) β=2 trained at 4/6 reached 79.9% and 89.2% at N=6; (b) β=2 trained at N=8 reached 4.6% and 0.0% at N=8 with interior offsets 1.03w and 1.04w; (c) β=4 − β=2 at N=8 was +75.5 pp [68.2, 81.5] and +84.7 pp [82.6, 86.7], 8/8 seeds each. The same logit scale rescued Scan at one length and failed at the other, as predicted by where the analytic optimum lies relative to the window. One Priority N8-b2L seed reached 31.1%; the other seven stayed at or below 3%.
* **X2 supported.** At N8-b2L, circular codes (optimum inside) reached 80.3% versus 4.6% and 0.0% for the scalar families.
* **D1 supported.** With the A.1 temperature (β=1) but without later-item distractor terms, interior offsets were 0.02w and −0.03w and N=6 accuracy rose by +82.8 pp [78.0, 87.1] (Priority) and +92.4 pp [91.3, 93.5] (Position) over B-b1, 8/8 seeds each.
* **R1 supported.** The temperature-free regression objective reached 90.1% and 93.0% at N=6 (+86.4 and +93.0 pp over B-b1).
* Descriptive: D and RL at 900 updates were 2.4–2.5% (Priority) and 36–39% (Position), so the raw-key plateau and the slow early phase are not specific to cross entropy. Untrained-length N=8 accuracy for models trained at 4/6 was low for β=2 scalar (0.7–2.0%, offsets ≈1.0w) and moderate for D and RL (55–74% scalar).

## Interpretation (per preregistered rules)

X1 and D1 both supported: the rescue of learned Scan codes is attributed to removing the distractor-induced displacement relative to the capture windows, not to sharper softmax as such. Logit scale matters here through where it places the loss optimum: a fixed scale succeeds or fails depending on whether the optimum at that list length lies inside the window, and the unscaled objective succeeds once its distractor terms are removed. A–A.5 records are unchanged. Experiment B, the repaired full factorial, capacity scaling and Dynamic Routing remain closed.

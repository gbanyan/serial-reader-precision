# Experiment A.4 — objective–calibration test (preregistered 2026-10-03)

Authorization: the user explicitly authorized additional experiments on 2026-10-03 ("該多跑的實驗也要跑") after an external manuscript review. This reopens training for this bounded question only. Experiment B, the full repaired factorial and Dynamic Routing remain closed.

## Motivation (analysis done before this preregistration, after A.1–A.3 outcomes were known)

The A.1 Scan training loss is teacher-forced cross entropy over Scan logits \(s_{t,i}=-16(\hat c_i-q_t)^2\) plus a fixed NO_MATCH logit \(-16w^2\), \(w=.45/N\). Later-ranked items act as distractors at earlier steps, so at slot-centred codes \(\partial L/\partial c_i=-32\sum_{t<i}p_{t,i}(q_i-q_t)<0\) for \(i>0\). Minimizing this loss directly over per-rank codes (scratch analysis, no model) gives maximum interior offsets from slot centres of 0.63w (Position, N=4) but 1.18w (Position, N=6) and 1.13w (Priority, N=6): the scalar loss optimum at N=6 lies outside Scan's capture windows, so its own Scan output fails. The circular optimum stays inside (0.71w). Saved A.1 update-900 codes show the same signed rightward offsets (Position N=6 interior medians about 0.3–1.4w; Priority similar). This is a post-hoc account. A.4 tests it prospectively.

Multiplying every training logit by a positive scale \(\beta\) leaves argmax, and therefore the evaluated reader, unchanged, while moving the loss optimum. Analytic predictions for the maximum interior offset at N=6: β=1: 1.18w (Position)/1.13w (Priority); β=4: 0.33w/0.32w; β=16: 0.01w/0.01w. At N=8, β=1 is 1.84w and β=4 0.63w.

## Fixed design

Unchanged from A.1: `RepairedModel`, data generator `experiment-a-scalar-v1`, AdamW lr 1e-3, weight decay .01, batch 32, clip 1, alternating N=4/6 training, deterministic PyTorch, pinned image `oscillation-pbos-deps:20260928`, evaluation panels `panel()` with generator seed 810000+N, 1,024 episodes. Seeds 11, 22, 33, 44, 55, 66, 77, 88 (data and torch seed = label).

Arms (all eight seeds):

| Arm | Cells | Objective | Updates |
|---|---|---|---|
| S-β1, S-β4, S-β16 | priority_scan, position_scan, phase_scan | CE on β·logits | 900 |
| L-β1, L-β16 | same three | CE on β·logits | 3,600 |
| R | same three | squared distance of reader coordinate to its target slot reference, divided by the capture boundary (no CE) | 900 |
| C | priority_competitive, position_competitive, phase_competitive | CE, β=1 | 900 |

Evaluation every 300 updates at N=4, 6 and 8 (N=8 untrained length, secondary). Checkpoints at every evaluation. The reader used for evaluation is the unchanged A.1 reader in all arms.

## Gate

G0 (implementation): S-β1 seeds 11–44 must reproduce the saved A.1 update-900 predictions and codes at N=4 and N=6 exactly. If not, stop and diagnose before analysis.

## Primary hypotheses (scalar Scan, N=6, update 900)

H1 dose–response. For each of Priority and Position: mean exact accuracy increases β1 < β4 < β16, β16 − β1 ≥ 30 percentage points, and β16 > β1 in at least 7/8 seeds. Supported only if both families meet all three.

H2 offset tracking. Mean over seeds of the median signed interior offset (ranks 1..N−2 for Priority, 1..N−1 for Position; units of w) is > 0.8 at β1 and < 0.3 at β16, for both families.

H3 objective versus budget. For both scalar families, L-β1 (3,600 updates) N=6 mean exact accuracy is below S-β16 (900 updates), and L-β1 interior offsets remain > 0.8w. If L-β1 reaches or exceeds S-β16 in either family, a training-budget explanation is not excluded for that family.

## Secondary (descriptive; no confirmatory claim)

* Circular Scan β response (analytic optimum already inside windows at β=1; no directional prediction about magnitude).
* R arm: whether the encoder can attain reference-calibrated codes when the target is supplied directly (expressivity of encoder plus optimizer, separate from the CE objective).
* C arm: scalar and circular Competitive in the same cohort and code path as the Scan arms, closing the missing repaired-cohort scalar Competitive comparator.
* N=8 accuracy, checkpoint trajectories, L-β16.
* Same-code transfer of A.4 Scan codes to the frozen Competitive reader.

## Interpretation rules

* H1 and H2 supported, H3 supported: the A.1 N=6 scalar learned-Scan shortfall is attributed primarily to the CE objective's preferred coordinates under the A.1 logit scale, within this architecture and budget; not to Scan's capability (oracle) or an encoder ceiling.
* H1 fails but R succeeds: objective form beyond logit scale matters; the encoder can attain the geometry.
* H1 and R both fail: encoder/optimizer limits are not excluded.
* β also sharpens the softmax and changes gradient magnitudes; a positive H1 therefore supports "objective scale" as a whole, not offset removal alone. H2 is the mechanism-specific check.
* Four of the eight seeds overlap A.1; seeds are the replicate unit; N, checkpoints and episodes are dependent measurements. Paired-seed bootstrap intervals (10,000 resamples) are descriptive.
* No result from this experiment rewrites A–A.3 records; A.4 is reported as an added, separately preregistered test.

## Execution

New remote directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a4-20261003/`, task-owned containers (2 CPUs, 2 GiB, 512 PIDs, json-file logs 10m×3, no ports). Raw runs under ignored `runs/experiment_A4/`; durable tables under `results/experiment_A4/`. Source hashes in `experiment_A4_source.json`, verified by the runner. Runs refuse to overwrite existing directories.

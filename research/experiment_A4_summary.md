# Experiment A.4 — objective–calibration test: results (2026-10-03)

Preregistration: [experiment_A4_preregistered_hypotheses.md](experiment_A4_preregistered_hypotheses.md) (commit `cbde150`, before any training). Implementation commit `a402f4d`; source hashes in `experiment_A4_source.json`, verified by every run. 168/168 runs completed in the pinned image on gbminipc (4 task containers, 2 CPUs/2 GiB/512 PIDs, no network), no nonfinite losses. Raw runs: ignored `runs/experiment_A4/` (local and `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a4-20261003/`, 2.1 GB). Durable tables: [results/experiment_A4/](../results/experiment_A4/README.md).

**Classification: H1 NOT SUPPORTED; H2 SUPPORTED; H3 SUPPORTED for Position, NOT for Priority.**

## Gate

G0 PASS. S-β1 seeds 11–44 reproduced the saved A.1 update-900 predictions, codes and targets exactly at N=4 and N=6 (24/24 panels). These four S-β1 runs were produced by the gate invocation of the same hashed `train()`; the matrix run skipped them as complete.

## Primary results (N=6, eight seeds, mean exact accuracy)

| Scan cell | S-β1 (900) | S-β4 (900) | S-β16 (900) | R (900) | L-β1 (3,600) | L-β16 (3,600) |
|---|---:|---:|---:|---:|---:|---:|
| Priority | 3.49% | 2.49% | 2.37% | 2.53% | 6.65% | 28.98% |
| Position | 0.90% | 31.95% | 29.27% | 38.94% | 1.35% | 55.97% |
| Circular | 20.75% | 34.96% | 28.89% | 36.84% | 48.41% | 58.94% |

Mean interior signed offset from slot centres (units of w):

| Scan cell | S-β1 | S-β4 | S-β16 | L-β1 |
|---|---:|---:|---:|---:|
| Priority | 0.93 | 0.18 | 0.10 | 1.02 |
| Position | 0.97 | 0.23 | −0.08 | 1.07 |

* **H1 (dose–response) not supported.** Position: β16−β1 = +28.4 pp, paired-seed bootstrap 95% [22.9, 33.1], 8/8 seeds positive, but below the 30 pp criterion and not monotone (β4 > β16). Priority: −1.1 pp [−2.3, 0.0], 2/8 seeds positive.
* **H2 (offset tracking) supported** in both families, matching the analytic optimum (β1 ≈ 1.1–1.2w predicted; β16 ≈ 0.01w).
* **H3 (objective versus budget).** Position supported: four times the budget at β1 left accuracy at 1.35% and offsets at 1.07w, whereas β16 at 900 reached 29.27%. Priority not supported, because S-β16 itself did not improve; L-β1 offsets did remain above 0.8w as predicted.

## Secondary and descriptive results

* **Priority plateau at the raw-key solution.** Under every centring objective at 900 updates (β4, β16, R), Priority accuracy was 18.4–18.7% at N=4 and 2.4–2.5% at N=6 with very small seed spread, equal to the analytic raw-key-passthrough baseline through the per-episode min–max adapter (18.0%, 2.52%). Saved Scan coordinates lay 0.31–0.32w on average from that raw-key coordinate (`precision_diagnostics.csv`). Longer training (L-β16) left this plateau (0.96w; 28.98%, seeds 8–62%). β1 Priority codes were less key-like (0.77w) because the objective pushes later items outward.
* **Order retained, calibration missing.** Strict representation rank (= same-code zero-fit Competitive transfer accuracy for scalar codes) at N=6 was 66–75% at 900 updates in every scalar arm and 88–89% after 3,600 β1 updates, while L-β1 Scan accuracy stayed at 1.35% (Position) and 6.65% (Priority).
* **Removing the offset is not sufficient for oracle performance.** Even with centred bias, per-item within-window rates at N=6 were .80–.83 (Position, 900) and .90 (Position, L-β16), so full-sequence capture remained well below the 100% compatible oracle.
* **Circular.** The analytic β1 optimum already lies inside windows; β and R still improved N=6 accuracy (20.75% → 29–37%), as did budget (48.41% at L-β1). One seed (33) collapsed to 0% under β16 at both 900 and 3,600 updates; no cause isolated.
* **Same-cohort Competitive (C arm).** Scalar Competitive N=6: Priority 80.63%, Position 74.74%; circular 78.74%. This closes the previously missing repaired-cohort scalar Competitive comparator.
* N=8 (untrained length) follows the same ordering at lower levels (`summary.csv`).

## Interpretation (per preregistered rules)

The A.1 cross-entropy objective at its native logit scale prefers scalar Scan codes whose later items lie outside the capture windows at N=6; this bias is confirmed prospectively (H2) and is not removed by a fourfold training budget (L-β1). For Position, removing it raised N=6 accuracy from about 1% to about 30% at the same budget, so the objective bias is a principal contributor to the A.1 Position shortfall. It is not the whole explanation: H1 failed, Priority remained at a raw-key plateau under any centring objective at 900 updates, and no arm approached the compatible oracle. Because H1 failed and the R arm did not reach oracle-like accuracy, encoder/optimizer limits on set-relative calibration are not excluded. β also changes gradient scale and softmax sharpness; the mechanism-specific evidence is H2 and the L-β1 contrast.

A.1–A.3 records are unchanged. A.4 is an added, separately preregistered test. Experiment B, the repaired full factorial and Dynamic Routing remain closed.

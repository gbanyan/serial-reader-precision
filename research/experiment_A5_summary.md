# Experiment A.5 — training budget and N=8 prediction test: results (2026-10-03)

Preregistration: [experiment_A5_preregistered_hypotheses.md](experiment_A5_preregistered_hypotheses.md) (commit `48deeb1`, before training). Implementation commit `16209ff`; hashes in `experiment_A5_source.json`, verified per run. 96/96 runs completed in the pinned image on gbminipc (six task containers, 2 CPUs/2 GiB/512 PIDs, no network), no nonfinite losses. Raw runs: ignored `runs/experiment_A5/` (local and `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a5-20261003/`, 1.3 GB). Tables: [results/experiment_A5/](../results/experiment_A5/README.md).

**Classification: G0 PASS; B1, B3, N1, N2, N4 SUPPORTED; N3 SUPPORTED for Priority and circular, NOT for Position; B2: Position CLOSES, circular CLOSES, Priority STILL-RISING (89.6%).**

## Gate

G0 PASS: B-b1/B-b16 reproduced A.4 L-b1/L-b16 predictions, codes and targets exactly at updates 900, 1,800, 3,600 and N=4/6/8 (432/432 panels).

## A.5-B: budget curve (N=6, eight seeds, mean exact accuracy)

| Updates | 900 | 1,800 | 3,600 | 7,200 | 14,400 | 28,800 | 36,000 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Priority β1 | 3.5 | 6.0 | 6.7 | 3.0 | 2.5 | 6.9 | 3.8 |
| Position β1 | 0.9 | 0.7 | 1.4 | 0.2 | 0.0 | 0.0 | 0.0 |
| Circular β1 | 20.8 | 32.0 | 48.4 | 64.6 | 79.9 | 85.4 | 88.4 |
| Priority β16 | 2.4 | 3.1 | 29.0 | 60.5 | 78.5 | 87.4 | 89.6 |
| Position β16 | 29.3 | 46.7 | 56.0 | 63.0 | 79.4 | 89.3 | 91.9 |
| Circular β16 | 28.9 | 43.5 | 58.9 | 63.3 | 80.6 | 90.9 | 92.3 |

* **B1 supported.** After 36,000 updates (40× A.1) at β1, interior offsets remained 1.04w (Priority) and 1.11w (Position); exact accuracy 3.8% and 0.02%.
* **B2.** β16 at 36,000: Position 91.9% (seeds 89.9–93.8%) CLOSES; circular 92.3% (89.0–94.1%) CLOSES; Priority 89.6% (87.3–91.8%), +11.0 pp since 14,400, STILL-RISING by the preregistered rule (0.4 pp below the CLOSES threshold). N=4 at 36,000: 96.4–97.8%.
* **B3 supported.** β16 − β1 at 36,000: Priority +85.8 pp [81.5, 88.7], Position +91.9 pp [90.9, 92.9], 8/8 seeds each.
* Descriptive: circular β1, whose analytic optimum lies inside the N=6 windows (0.71w), rose steadily to 88.4%, unlike the scalar β1 cells whose optimum lies outside. Circular β16 seed 33 (0% in A.4) stayed at 0% through 3,600 updates, then reached 46.9% at 14,400 and 89.0% at 36,000 (corrected 2026-10-04 from a truncated 88.9%; saved value 0.8896): a delayed escape, not a permanent collapse. Untrained N=8 after 36,000 β16 updates: 54–74% with wide seed ranges.

## A.5-N8: prediction under a new training load (N=8 only, 3,600 updates)

| Cell | analytic β1 interior offset | learned β1 | learned β16 | β1 exact N=8 | β16 exact N=8 |
|---|---:|---:|---:|---:|---:|
| Priority | 1.64w | 1.67w | 0.06w | 0.00% | 37.3% |
| Position | 1.59w | 1.55w | 0.11w | 0.00% | 46.8% |
| Circular | 0.80w | 0.76w | 0.09w | 7.2% | 51.4% |

* **N1 supported:** β1 offsets exceed 1.2w and the A.4 N=6 values (1.02w/1.07w).
* **N2 supported** for all three families.
* **N3:** per-rank profile Spearman with the analytic prediction: Priority .86, circular .93 (including the predicted mid-rank peak), Position .36 (fails ≥ .6). Position magnitudes matched within about 0.2w at every rank, but the analytic Position profile is nearly flat across ranks 3–7 (1.79–1.84w), so its rank order was not reproduced; the criterion is reported as failed.
* **N4 supported:** β1 scalar N=8 exact accuracy 0.00%.

## Interpretation (per preregistered rules)

The analytic optimum of the A.1 Scan training loss predicted learned code offsets prospectively at a new training load, in magnitude for all families and in rank profile for two of three. With the A.1 objective, a 40-fold budget did not produce usable scalar Scan codes; with a centring objective, learned Scan codes reached 89.6–92.3% at N=6 and 96–98% at N=4. The A.4 residual shortfall was therefore largely a training-budget effect under the centring objective: encoder capacity is not implicated at this scale for N≤6, and the capacity experiment is not needed for the current claims. The remaining gap to 100% and the slower Priority trajectory (raw-key plateau through 1,800 updates) remain descriptive. β changes gradient scale as well as the optimum; the mechanism-specific evidence is the offset agreement (B1, N1–N3) and the circular/scalar contrast at β1.

A–A.4 records are unchanged. Experiment B, the repaired full factorial and Dynamic Routing remain closed.

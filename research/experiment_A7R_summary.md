# Experiment A.7R — evaluation-only capture-width replay: results (2026-10-04)

Specification: [experiment_A7R_replay_specification.md](experiment_A7R_replay_specification.md), committed and pushed (7d813c8) before computation. Script `experiment_a7/replay_width.py` (local NumPy, saved arrays only; no model, training or reader call). Tables: `results/experiment_A7R/`.

**Classification: R0 gate PASS (24,576/24,576 episodes reproduced exactly at 0.45/N); R1, R2, R3 SUPPORTED.**

Same saved codes (A.5 B-b1: β=1, standard width, 36,000 updates, N=6, eight seeds), read with a different capture width only. Mean exact accuracy (%):

| Width (/N) | 0.25 | 0.30 | 0.35 | 0.45 (trained) | 0.55 | 0.60 | 0.65 | 0.75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Priority | 0.0 | 0.0 | 0.1 | 3.8 | 51.3 | 73.4 | 83.6 | 90.6 |
| Position | 0.0 | 0.0 | 0.0 | 0.0 | 28.0 | 75.3 | 86.9 | 92.1 |
| Circular | 0.1 | 7.7 | 56.3 | 88.4 | 91.4 | 92.3 | 93.2 | 94.5 |

* R1: at 0.75/N, Priority +86.8 and Position +92.1 points over the trained width, 8/8 seeds each.
* R2: at 0.30/N, circular −80.7 points, 8/8 seeds.
* R3: scalar accuracy at 0.30/N was 0.01% and 0.0%.

Interpretation: with the learned codes and the training objective both fixed, the reader's acceptance boundary alone decided success. The standard-objective scalar codes, which almost never pass the trained reader, are read correctly in about 91–92% of episodes once the window contains their displacement, so their failure under the trained reader was a calibration offset, not missing or disordered information. Together with the trained A.7 width arms (displacement ≈0.5/N regardless of training width), this separates the two roles: the objective sets the displacement, and the reader boundary decides whether it is tolerated.

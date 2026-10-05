# Experiment A.7 evidence

Report: [A.7 summary](../../research/experiment_A7_summary.md); specification: [hypotheses](../../research/experiment_A7_preregistered_hypotheses.md).

| File | Content |
|---|---|
| `seed_metrics.csv` | per arm/cell/seed/N/checkpoint exact, pairwise, NO_MATCH, interior offset (own w and 1/N), per-rank offsets |
| `summary.csv` | seed means/min/max |
| `hypotheses.json` | M1, M2, W1, W2, W3, E1, E2 verdicts with paired-seed bootstrap intervals |
| `execution_logs/` | stdout of the seven task containers |

Produced by `python3 -m experiment_a7.report` (NumPy only; requires local `runs/experiment_A5` and `runs/experiment_A7`). Raw arrays and checkpoints: ignored `runs/experiment_A7/` (local and gbminipc `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a7-20261004/`).

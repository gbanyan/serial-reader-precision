# Experiment A.5 evidence

Report: [A.5 summary](../../research/experiment_A5_summary.md); preregistration: [hypotheses](../../research/experiment_A5_preregistered_hypotheses.md).

| File | Content |
|---|---|
| `gate.json` | G0: exact reproduction of A.4 L-arm evaluations (432 panels) |
| `seed_metrics.csv` | per arm/cell/seed/N/checkpoint exact, pairwise, NO_MATCH, interior offset, per-rank offsets |
| `summary.csv` | seed means/min/max |
| `hypotheses.json` | B1–B3 and N1–N4 verdicts, bootstrap intervals, learned vs analytic N=8 profiles |
| `execution_logs/` | stdout of the six task containers |

Produced by `python3 experiment_a5/report.py` (NumPy only, saved arrays; requires local `runs/experiment_A4` and `runs/experiment_A5`). Raw checkpoints and arrays: ignored `runs/experiment_A5/` (local and gbminipc `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a5-20261003/`).

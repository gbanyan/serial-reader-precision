# Experiment A.6 evidence

Report: [A.6 summary](../../research/experiment_A6_summary.md); preregistration: [hypotheses](../../research/experiment_A6_preregistered_hypotheses.md).

| File | Content |
|---|---|
| `gate.json` | G0: exact reproduction of A.5 N8-b16 and A.4 R evaluations (216 panels) |
| `seed_metrics.csv` | per arm/cell/seed/N/checkpoint exact, pairwise, NO_MATCH, interior offset, per-rank offsets |
| `summary.csv` | seed means/min/max |
| `hypotheses.json` | X1, X2, D1, R1 verdicts with paired-seed bootstrap intervals |
| `execution_logs/` | stdout of the seven task containers |

Produced by `python3 -m experiment_a6.report` (NumPy only; requires local `runs/experiment_A4`, `runs/experiment_A5`, `runs/experiment_A6`). Raw checkpoints and arrays: ignored `runs/experiment_A6/` (local and gbminipc `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a6-20261003/`).

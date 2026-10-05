# Experiment A.4 evidence

Report: [A.4 summary](../../research/experiment_A4_summary.md); preregistration: [hypotheses](../../research/experiment_A4_preregistered_hypotheses.md).

| File | Content | Produced by |
|---|---|---|
| `seed_metrics.csv` | per arm/cell/seed/N/checkpoint exact, pairwise, NO_MATCH, interior offset, per-rank offsets, same-code Competitive transfer | `python -m experiment_a4.report` (pinned container) |
| `summary.csv` | seed means/min/max of the above | same |
| `hypotheses.json` | H1–H3 verdicts, paired-seed bootstrap intervals | same |
| `precision_diagnostics.csv` | within-window rates, strict rank, distance to raw-key coordinate (N=4/6) | `python3 experiment_a4/precision.py` (local NumPy, saved arrays only) |
| `analytic_objective_optimum.csv` | code-space minimizers of the Scan training loss by β, N, family | `python3 experiment_a4/analytic.py` (NumPy/SciPy, no model) |
| `raw_key_baseline.csv` | closed-form Scan accuracy of untrained raw-key codes | same |
| `execution_logs/` | stdout of the four task containers | `docker logs` |

Raw checkpoints and evaluation arrays: ignored `runs/experiment_A4/` (local and gbminipc `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a4-20261003/`).

# Reproduce from saved artifacts

The code repository provides source and saved result tables. The multipart
release archive additionally provides retained runs, checkpoints, configurations,
training logs and saved evaluations. Extract it into an empty directory and run
commands there, so regeneration never overwrites the release's original copies.

The historical training environment is recorded per run: Python 3.13.15,
PyTorch 2.8.0+cpu and NumPy 2.3.3. The supplied pinned-base Dockerfile preserves
the recorded training dependencies. `requirements-analysis.txt` provides
compatibility ranges, not an exact historical analysis lock file. The release
verification uses local Python 3.14, NumPy 2.5.3, SciPy 1.17.1 and Matplotlib
3.10.8 for saved-array summaries and figure generation. A.7R provenance records
NumPy 2.5.3. A.4's report requires PyTorch and was previously checked in the
pinned container; A.5-A.7 summaries do not execute a model.

```sh
python -m experiment_a4.analytic
python -m experiment_a4.precision
python -m experiment_a5.report
python -m experiment_a6.report
python -m experiment_a7.report
python -m experiment_a7.replay_width
python manuscript/tools/audit_complete_rank.py
python manuscript/tools/build_figures_v2.py
```

The A.7R command replays only saved codes using NumPy; it performs no training
or network execution. Figures 1-4 and S1 are generated only from saved tables.
The original oracle-noise per-trial predictions were not retained, so a joint
rank-preserved-by-NO_MATCH decomposition cannot be recovered from aggregate
tables. Failed criteria and historical reader implementations remain preserved.

Code uses MIT; original synthetic data, checkpoints and results use CC BY 4.0.
Serialized checkpoints are executable-format artifacts; this verification does
not deserialize them. The release excludes third-party literature, unrelated
research tracks, private configuration and the unpublished manuscript.

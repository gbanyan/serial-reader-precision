# Serial reader precision: A-series code and synthetic research data

Controlled artificial serial-order representations and specified readers.
This release preserves A, A.1, A.2 and A.3, including failed mechanism gates.
It is not a biological study or a universal Competitive/Scan comparison.

## Contents and provenance

* `experiment_a*`: original source and analysis modules. Do not confuse the
  original pseudo-scan with the repaired rejecting fixed-reference reader.
* `pbos/`: only the shared attention-layer dependency and its import dependencies.
* `results/`: saved tables, diagnostics and historical plots, unmodified.
* `research/`: experiment definitions, final summaries and provenance maps.
* `experiment_A*_source.json`: historical revisions and file hashes.
* `SHA256SUMS.json`: inventory of the files in this repository.
* Release asset `A_series_saved_evidence_v1.0.0.zip`: all retained A-series run
  records, checkpoints, configurations, evaluations and original results.
  `archive_inventory.json` records every included path, size and SHA-256.

The archive excludes Dynamic Routing, other research tracks, caches, private
configuration and third-party literature. It does not include an unpublished
manuscript. Code: MIT. Original data/results/checkpoints: CC BY 4.0.

## Reproduction boundary

Historical CPU runs recorded Python 3.13.15, PyTorch 2.8.0+cpu and NumPy 2.3.3.
See per-run records; additional analysis dependencies were not completely pinned.
The supplied Dockerfile and requirements preserve the recorded base environment.
`requirements-analysis.txt` explicitly distinguishes compatible analysis ranges.
No model was retrained or evaluated in assembling this release. Original
oracle-noise per-trial predictions were not archived: conditional aggregate
tables exist, but a rank-preserved-by-NO_MATCH joint decomposition cannot be
recreated from them without rerunning the original analysis.

To reproduce the manuscript's five figures **from saved aggregate tables only**:

```sh
python manuscript/tools/build_figures.py
```

This writes to `manuscript/submission/figures/`; it does not import training
modules. Historical experiment scripts are provided for independent future
reproduction, not run as part of release preparation. Serialized checkpoints
should be treated as executable-format artifacts and loaded only when trusted.

## Citation

Use `CITATION.cff` and cite the versioned GitHub release, not an unversioned
branch. This repository is private staging until the authors approve public
release. A private staging link is not a public data-deposit statement.

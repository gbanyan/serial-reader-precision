# Serial reader precision: A-series code and synthetic research data

Controlled artificial serial-order representations and specified readers.
This release preserves A, A.1, A.2 and A.3, including failed mechanism gates, and the
prospectively specified follow-ups A.4-A.7 and the evaluation-only replay A.7R.
It is not a biological study or a universal Competitive/Scan comparison.

## Contents and provenance

* `experiment_a*`: original source and analysis modules. Do not confuse the
  original pseudo-scan with the repaired rejecting fixed-reference reader.
* `pbos/`: only the shared attention-layer dependency and its import dependencies.
* `results/`: saved tables, diagnostics and historical plots, unmodified.
* `research/`: experiment definitions, final summaries and provenance maps.
* `experiment_A*_source.json`: historical revisions and file hashes.
* `SHA256SUMS.json`: inventory of the files in this repository.
* Release asset `A_series_saved_evidence_v2_2026_10_05_release.zip`: all retained A-series run
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
No model was retrained or evaluated in assembling this release. A.4-A.7 runs were
trained separately in the pinned container (per-run source hashes in
`experiment_A4_source.json`-`experiment_A7_source.json`); A.7R is a NumPy replay of saved codes. Original
oracle-noise per-trial predictions were not archived: conditional aggregate
tables exist, but a rank-preserved-by-NO_MATCH joint decomposition cannot be
recreated from them without rerunning the original analysis.

To reproduce the version-2 manuscript figures (Figures 1-4 and S1) **from saved tables only**:

```sh
python manuscript/tools/build_figures_v2.py
```

`build_figures.py` reproduces the earlier five-figure version.

This writes to `manuscript/submission/figures/`; it does not import training
modules. Historical experiment scripts are provided for independent future
reproduction, not run as part of release preparation. Serialized checkpoints
should be treated as executable-format artifacts and loaded only when trusted.

## Citation

Use `CITATION.cff` and cite the versioned GitHub release, not an unversioned
branch. Version 2.0.0 is the public code and synthetic-evidence release associated with
the version-2 manuscript. It does not certify manuscript approval or journal submission.

## Post-review companion records

A01, A02 and A03 contain later deterministic saved-array diagnostics, their scripts
and provenance. The supplementary inventory retains stable D01–D46 IDs, H01–H03
historical source copies and a data dictionary, including D37/D38 aliasing;
D47-D59 are the A.4-A.7R tables. Prospective specifications are in research/experiment_A4-A7R files;
their timing rests on local Git commits, except A.7 and A.7R, which were pushed before running.
A.2 oracle/noise analyses ran locally outside the recorded training container;
A02 records its later NumPy version separately. Historical v1.0.0 is preserved as an unpublished draft. This release has a
versioned GitHub URL; no DOI has been assigned.

## Download and verify

Release: https://github.com/gbanyan/serial-reader-precision/releases/tag/v2.0.0

The full saved-evidence ZIP is split into numbered binary parts because each
GitHub release asset must be smaller than 2 GiB. Download all release assets, including every `.partNNN`, the supplementary ZIP,
`SHA256SUMS.txt` and `evidence_parts.json`, into one directory.
Do not unzip the parts individually. In a POSIX shell:

```sh
shasum -a 256 -c SHA256SUMS.txt
cat A_series_saved_evidence_v2_2026_10_05_release.zip.part??? > A_series_saved_evidence_v2_2026_10_05_release.zip
```

Check the assembled ZIP against `archive_sha256` in `evidence_parts.json`, then
unzip it into an empty directory. `archive_inventory.json` records the size and
SHA-256 of every preserved original entry. `supplementary_data_v2.0.0.zip` is a
small companion with the D01-D59 tables, A01-A03 audits, inventories and dictionary;
it is not a substitute for the full saved-run archive.

See `REPRODUCING.md` for the saved-artifact reproduction boundary and versions.

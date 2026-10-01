# A.1 diagnosis of original Scan readout

Status: reproduction of an existing implementation limitation, not a new repaired-model result. Source: original Experiment A commit `135141f83f09977e7cc0b28ff80fab4ee98a8e68`. All 24 original final Scan checkpoints (eight seeds × three representations) were loaded from a read-only mount. Normal inference exactly matched saved A predictions on 48 panels (N4/N6, 1,024 trials each). New diagnostics are in [CSV](../results/experiment_A1_old_scan_diagnostics.csv) and `runs/experiment_A1/old_scan/`; original artifacts were not overwritten.

## Why nearest-remaining is not necessarily a scan

For linear coordinate c and a fixed cursor q, if all remaining c exceed q, minimizing (c−q)² is identical to selecting the smallest remaining c. Masking the winner then advances ordinal order even though q never changes. The readout's nominal name and equal parameter count therefore do not identify the actual serial transition mechanism. Cursor displacement can be disruptive without cursor advancement being necessary during ordinary output.

## Reproduction

Numbers average equally over eight seeds and N4/N6. Pairwise changes are relative to each normal output; accuracy/tau deltas use the unchanged task target. First changed position is zero-based and N when unchanged; its pooled maximum here is 5 because N4/N6 are equally weighted. Exact transformed agreement conditions on originally correct trials and reports denominators in CSV.

| Original Scan | Frozen sequence change | Frozen pairwise relation change | Frozen pairwise accuracy delta | Frozen tau delta | First changed position |
| --- | ---: | ---: | ---: | ---: | ---: |
| Priority | .0220 | .0060 | +.0056 | +.0112 | 4.9199 |
| Position | .0000 | .0000 | .0000 | .0000 | 5.0000 |
| Phase | 1.0000 | .4486 | −.3203 | −.6407 | 1.1568 |

Priority freeze preserves 97.80% and Position freeze preserves 100% of sequences, reproducing the previous audit. Phase differs: its circular nearest-distance ordering cannot generally be replaced by a fixed linear sort, but this alone does not validate all phase runs.

| Original Scan | +1 cyclic shift sequence change | Shift transformed agreement | Cursor permutation sequence change | Permutation transformed agreement |
| --- | ---: | ---: | ---: | ---: |
| Priority | .6411 | .5776 | 1.0000 | .1605 |
| Position | .1626 | .1112 | 1.0000 | .0286 |
| Phase | .9997 | .7989 | .9995 | .9187 |

Schedules: shift [1,...,N−1,0], permutation [N−1,0,...,N−2]. These diagnostics distinguish mere disruption from following requested slots. Original A remains A-COMPAT-6. A.1's repair must reject an invalid/exhausted slot rather than choose the nearest remaining item, while still learning normal serialization.

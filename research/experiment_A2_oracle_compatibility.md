# Experiment A.2 — oracle compatibility and noise robustness

Status: specification before A.2 evaluation, 2026-09-29. Three separate estimands: mathematical capability with oracle codes; tolerance of controlled code error; gap from existing A.1 learned codes. No training, architecture change, reader repair, control variants, or Experiment B. Historical A/A.1 remain immutable.

Frozen readers are `experiment_a1/model.py:RepairedModel.decode` and inherited `experiment_a/model.py:coordinates`. Analytical NumPy evaluation in `experiment_a2/` must reproduce these equations and saved predictions; a small remote PyTorch equivalence test checks the actual frozen decoder. Adapters have zero learned parameters. No encoder is run for the main study. Hard used-item masking, radius .45/N, null-first tie rejection, score scales and cursors remain unchanged.

## Shared oracle convention

Let k=0,...,N−1 be target ordinal rank, independently assigned to shuffled input items. Priority p=1−k/(N−1); Position u=(k+.5)/N; Phase z=(cos(2πu),sin(2πu)). These encode identical rank information and no item identity. Centers rather than endpoints are required by the already frozen scan cursor: this chooses an oracle compatible with its declared slots, not a changed reader. The same code is supplied to both readers within each representation. Content is routed by original item index only. N=4,6,8,10,12; no length retraining.

Priority's frozen set min/max normalization maps to [0,1] in competition and then to slot centers for Scan. Position passes through unchanged. Phase competition uses 8(dot(z,reference)−1); Scan uses circular chord distance to slot centers. A full-circle phase oracle is not injective under cosine projection: symmetric positions can tie or reverse. This is an a priori code/readout mismatch, not evidence that all phase codes fail competition; learned A.1 phase competition may occupy a monotone sector. Do not silently supply a semicircle oracle only to competition. Report projected-score rank separately from angular rank.

## Noise and metrics

Gaussian error SD divided by adjacent oracle spacing is 0,.05,.10,.20,.35,.50,.75,1. Priority spacing=1/(N−1); Position=1/N; Phase angle spacing=2π/N. No clipping; phase wraps naturally through unit vectors. Four noise seeds 101,202,303,404, 1024 trials each, paired random input permutations and normal draws across six cells and noise levels. Noise replicates are not model-training seeds.

Record exact, missing-aware all-target-pair accuracy, conditional Kendall tau with pair coverage, first error (zero-based, N if correct), omission/duplication/NO_MATCH; scan target-slot match, slot miss, and pre-mask multiple-eligible-item collision. Angular rank uses onset-relative phase in [0,2π); also report score-projected ranking so cosine mismatch is not confused with corrupted angular order. Rank-preserved trials have zero inversions and no ties. Noise metric error uses absolute scalar/shortest circular distance divided by spacing.

AUC uses trapezoids over normalized sigma [0,1]. Threshold is the first tested sigma strictly below .90/.75/.50, with preceding grid point as an interval; no extrapolation/interpolation. Report not-reached and already-below-at-zero explicitly. Mean/SD over noise seeds; raw counts and binomial uncertainty for conditional failure rates.

## Existing learned-code comparison

Use all four A.1 calibration cells, seeds11/22/33/44, final saved eval_900_{4,6}.npz (1024 trials each). Replay must match original predictions. A.1 did not train Priority/Competitive or Position/Competitive: their learned gap is NOT AVAILABLE, not imported from A or retrained. No learned OOD files exist. Oracle-minus-learned gaps may be negative where the chosen oracle and learned geometry differ (notably cosine projection).

Alignment is diagnostic, never fed into the frozen reader. For linear coordinates fit one positive affine least-squares mapping per trial from learned coordinate to ideal slot centers; nonpositive best slope is flagged and constrained to zero. Report unaligned anchored error, aligned residual, slope, and rank inversions. This is an optimistic target-informed post hoc fit, not learned generalization. Phase fits one best global rotation by the circular mean of target-minus-learned angle; no reflection, itemwise alignment or nonlinear warp. Report shortest circular residual normalized by 2π/N. Competition's phase error against the full-circle scan oracle is descriptive codebook mismatch, not a calibrated explanation of competition failure. Report conditional failure with rank preserved and geometry-error/failure Spearman per seed/load; association is not causal proof.

## Controls and provenance

Oracle freeze; cyclic shift; genuinely noncyclic schedule [even slots then odd slots]; representation first/last-target swap; competitive score boost; priority positive affine and position matched affine/reference transform; phase common rotation including reference/cursor. Score ties are recorded, never broken using target ranks. Invariance can alter tie choices through floating-point rounding; flag and report rather than silently fix the decoder.

Local analysis dependencies: NumPy, pandas, SciPy, Matplotlib. PyTorch equivalence runs in pinned `oscillation-pbos-deps:20260928` on gbminipc with 2 CPUs/2GiB/512PIDs, no ports, isolated A2 directory. Before primary analysis save SHA256 hashes of preregistration, implementation and original artifacts. Output-only reproduction commands are documented in the result index. No changes to A/A.1 evidence or thresholds.

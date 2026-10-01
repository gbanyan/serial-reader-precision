# Experiment A.3 — learned geometry adaptation

Specification before results. Family labels do not determine learned spacing, occupied arc or metric calibration. Separate expressivity, noise robustness, learnability and geometry adaptation. Primary question: does the frozen downstream readout package shape geometry within a fixed code family?

Use [audited pairs](experiment_A3_checkpoint_comparability.md), four seeds, three checkpoints and N4/N6; 144 saved panels. No training. Frozen numerical decoder from A.2 reproduces A.1 and unchanged nonphase A competition. Preserve A/A.1/A.2 artifacts and source hashes.

## Measures

Sort item code by target rank only for analysis. Priority orientation is decreasing p; Position increasing u. Phase reports onset angular order AND actual cosine-projected order separately, because they need not coincide. Compute Spearman, Kendall/pairwise inversion/decoding, adjacent margins and ties. Near tie is absolute score difference <=1e−6 for reported score diagnostics; strict actual argmax remains unchanged.

Linear canonical geometry uses endpoint coordinate k/(N−1), as requested. Fit a per-trial positive affine map to it (zero-slope limit flagged for nonpositive covariance), no nonlinear fit. Report affine RMSE/max error, slope/intercept, endpoint residuals, oriented spacing mean/SD/CV, original dynamic range and normalized adjacent margins. CV uses spacing SD divided by absolute mean, is missing if mean~0, and must be interpreted with inversion rate. Also record actual centered Scan distance: q=(k+.5)/N, radius .45/N. Endpoint canonical error and actual slot error are distinct.

Phase canonical geometry is uniform full-circle centered slots, allowing one best global rotation, not reflection. Although cosine is reflection-symmetric, reflecting is NOT an allowed shared alignment because Scan slot order is directed. Minimal occupied arc=2π−largest circular gap, normalized by2π; semicircle occupancy arc<=π+1e−6. Record absolute shortest adjacent angular spacing, CV, target-order boundary crossings (raw atan2 wrapped into [0,2π) differences>|π|), signed shortest margins, and projection monotonicity/ties. Wrap usage is reference-dependent; arc occupancy and rotation-aligned error are not. Semicircle occupancy alone does not prove a monotone projection.

Readout alignment: score pairwise order, strictly decreasing score sequence, min adjacent score margin/range/ties for C; correct-slot distance/RMSE, fraction within fixed radius, nearest-slot identity, correct-versus-nearest-other cursor distance margin and NO_MATCH for S. Also compute hypothetical Scan alignment for C codes without fitting them to target slots. Missing-aware behavioral metrics remain A.1's.

Rank/metric decomposition uses actual competitive score order for C and onset/linear coordinate order for S. Metric good means every target item captured by its true frozen Scan slot, not a fit using the target. Three exclusive strata: rank incorrect; rank correct/metric poor; rank correct/metric good. Report counts and conditional behavior. Additional angular rank for phase is separate, not substituted for C's projection rank.

## Frozen replay interventions

Cross-transfer feeds saved raw family codes to the other frozen reader with its existing adapter, same items and mask. No fine-tuning. Native replay must match every saved prediction.

Rank-preserving canonicalization infers rank ONLY from the source reader's scalar/anchored code ordering (cosine score for phase C); no ground truth is used. Reconstruct priority decreasing uniform code, position centered uniform slots, phase full-circle slots. Scan slot snapping independently rounds each learned coordinate to its nearest existing slot; collisions remain, no bijective reassignment or sorting fallback. Phase/Scan uses circular nearest cursor. Oracle slots use target rank and are labeled TARGET-INFORMED CEILING, not a learned repair.

Phase C counterfactuals: learned; target-informed full circle; target-informed semicircle theta=π(k+.5)/N; target-informed monotone arc with span=min(learned minimum arc,π−1e−4), centered atπ/2 and endpoints at half-spacing offsets. This last construction relocates and orients the arc using target order and may cap its span; report capping rate. Also apply semicircle/full-circle to SOURCE-INFERRED ranks to test geometry independently of correcting rank errors. Counterfactual geometry is not a newly trained family or reader.

For Scan: learned; target-informed oracle; target-rank-preserving cubic distortion q=.5/N+(1−1/N)*(k/(N−1))³; nearest-slot snap; source-rank uniform slots. For scalar competition also cubic source-rank metric warping (monotone), with fixed reader. These manipulations are fixed before results; no width/threshold search.

Geometry trajectories use300/600/900; per-cell Spearman across seed/checkpoint aggregates, and t geometry vs t+1 accuracy (8 paired transitions per load). Four seeds and sparse checkpoints cannot establish temporal precedence or independent longitudinal samples. Keep each cell/load separate, report descriptive correlations without causal/time-to-event claims.

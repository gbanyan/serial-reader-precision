# Experiment A.1 — mechanism validity repair

Status: methodological repair specification, before calibration. This is not architecture search or an attempt to restore the original interaction. Experiment A remains frozen at **135141f83f09977e7cc0b28ff80fab4ee98a8e68**, including code, raw runs, figures and preregistration. New namespace: `experiment_a1/`; new runs: `runs/experiment_A1/`; new results: `results/experiment_A1*`. No Experiment B, control variation, history/reset, synchronization or hybrid.

Matching parameter count and module names is insufficient for mechanistic factorial experiments. A fixed used-item mask can accidentally implement ordinal progression. Optimization instability can masquerade as representational incompatibility. A.1 repairs exactly these two issues.

## Fixed components

Import Experiment A's data generator and shared model components without modifying them. Same continuous scalar keys, independent unique symbolic identities, permuted set input, alternating N4/N6, 96 hidden units, two layers/four heads, 164,162 parameters, hard used-item mask, AdamW .001, weight decay .01, clip 1, batch 32 and 900 training steps. Four calibration seeds: 11,22,33,44. Cells: Priority/Scan, Position/Scan, Phase/Scan, Phase/Competitive (16 runs; overlap is reused). No reference retraining during calibration. No selective extensions or excluded failures.

## S: slot-valid scan

Cursor q_t=(t+0.5)/N and neighborhood radius r=.45/N are fixed from disjoint-slot geometry, not selected from calibration scores. For linear codes, compatibility is `s_i=-16(c_i-q_t)^2`. Slot eligibility requires `|c_i-q_t| <= r`. An ineligible winner produces `NO_MATCH`, encoded as output index -1. No item is consumed after NO_MATCH; output clock still advances on its specified schedule. The used-item mask is unchanged and shared, and is updated only after an actual item emission.

Priority/Scan adapts its original set-normalized coordinate c0 to the slot-center range: `c=.5/N+(1-1/N)*c0`. This maps the existing min/max anchors to the first/last slot centers; it does not provide intermediate ranks or sort items. The adjustment is required because the old extrema 0 and 1 would otherwise be outside every slot neighborhood. Priority/Competitive stays exactly as in A. Position/Scan uses its original sigmoid coordinate without a learned adapter.

For phase, the cursor is `(cos(2πq),sin(2πq))`, and compatibility is `-16*||z-cursor||²/(4π²)`. Eligibility uses the chord radius `2*sin(πr)`. This matches the local linear distance scale in turns while respecting circular geometry. All scan adapters have zero learned parameters. Phase receives no extra network.

Training uses cross-entropy over items plus a fixed NO_MATCH alternative at the neighborhood boundary score. Used items are masked. All remaining item scores participate in the differentiable loss, including outside-neighborhood candidates; no hard eligibility cutoff blocks learning gradients. At inference, the same boundary alternative wins whenever every remaining item is out of range, so there is no nearest-remaining fallback. Targets remain the original serial item identities; there is no auxiliary rank/angle regression target or extra training loss. Ties at the boundary favor NO_MATCH. Loss normalization remains mean over output steps. Adding the rejection alternative is necessary to train slot validity and changes the readout's likelihood denominator; this is disclosed, not hidden as an identical loss surface.

## P: continuous S1 code

The unchanged two-output head produces v=(a,b). Use `z=v/sqrt(sum(v²)+1e-8)` directly in every phase forward operation. atan2 is diagnostic only. Track raw norm and normalized norm to detect radial shortcuts. Phase/Competitive scores `8*(dot(z,reference)-1)` with initial reference (1,0); range approximately [-16,0], matching A's score span. This is continuous relative-direction competition, not discontinuous angle sorting. A cosine projection is not injective on a circle; an interpretable ordering therefore requires a learned task-aligned phase arrangement. We explicitly test that instead of asserting equivalence to A's unwrapped angle reader.

Phase/Scan uses the chord compatibility above. Common rotations transform both item vectors and reference/cursor vectors; no absolute orientation enters the readout. No atan2, remainder or angle sorting appears in the differentiable phase path. Priority/Competitive and Position/Competitive remain unchanged if the factorial gate opens.

## Evidence handling

First replay original Scan checkpoints, including their normal outputs, frozen cursor, cyclic +1 cursor schedule and a fixed nontrivial cursor permutation. Store new diagnostics separately and verify normal output identity against A's saved arrays. This is diagnosis of an old implementation, not a new scientific finding or repaired result.

Calibration saves standard checkpoints 300/600/900 plus monitoring observations every 100 steps. Monitoring never selects training length/checkpoints or changes optimizer settings. Use 1,024 paired held-out trials per load for checkpoint metrics and final causal panels. A separate 256-example fit set supports phase-only linear order decoding. Missing items count as incorrect in the primary pairwise metric; otherwise abstention could falsely appear to preserve ordering. See [gates](experiment_A1_preregistered_gates.md).

Only if both calibration gates PASS will the repaired factorial run eight seeds × six cells. Calibration seeds are retained as their exact factorial runs; add only missing runs, with no retraining/reselection. External reference reuses A's unchanged source/results with explicit provenance and is never included in the R×O test. Repaired and original datasets are never merged.

Remote execution uses the `remote-dev-test` convention: explicit `gbminipc`, pinned image `oscillation-pbos-deps:20260928`, new directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a1-20260929/`, task-owned containers with 2 CPUs/2 GiB/512 PIDs, log rotation, no ports. Preserve raw checkpoints and source hashes locally and remotely before removing only task containers.

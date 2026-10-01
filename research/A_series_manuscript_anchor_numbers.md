# A-series manuscript anchor numbers

2026-10-01. Read-only recomputation from stored CSV counts and NPZ arrays; no model, evaluator or reader replay run. Fractions below are exact stored/aggregated values, not percentages. Convert fraction×100 and round to two decimals for percentages/percentage points; phase occupancy may use three decimals. Never round before aggregation. Equal panel/seed means are used when all panels have1024 episodes; conditional rates pool integer denominators, not means of rates. Counts are integers. Seed intervals are existing paired bootstrap intervals, not new confirmatory tests.

## 1. Oracle capability

Source: [A.2 oracle](../results/experiment_A2_oracle_matrix.csv), sigma0; N4/6/8/10/12, four noise/data seeds per condition,1024 episodes/panel. Each Scan family has20 rows, min=max exact_accuracy1; Priority/Position C also1; full-circle Phase C min=max0. In total61,440 Scan episodes across15 family/load conditions: no errors in stored aggregates. N12 is supplied-code capability, not learned generalization. Phase C benchmark is information-oracle only.

## 2. Rank-conditioned noise failure

Source: [rank counts](../results/experiment_A2_rank_inversion_analysis.csv), n6, sigma=.35, rank_state=preserved. Estimator sum(failures)/sum(count) over noise seeds101/202/303/404; ties excluded. No new intervals calculated.

| Code | Reader | Preserved denominator | Failures | Exact fraction |
|---|---|---|---|---|
| priority | competitive | 3673 | 0 | 0.0 |
| priority | scan | 3673 | 2565 | 0.6983392322352301 |
| position | competitive | 3671 | 0 | 0.0 |
| position | scan | 3671 | 2541 | 0.6921819667665486 |
| phase | competitive | 3100 | 3100 | 1.0 |
| phase | scan | 3100 | 1970 | 0.635483870967742 |

The Phase C1.0 uses angular rank, not its projected score rank. It is not pooled with scalar invariance. Manuscript conditional Scan anchors69.83/69.22/63.55%; scalar C0%. Source [noise curves](../results/experiment_A2_noise_curves.csv), same n/sigma, equal four-panel means: distinct unconditional exact rates below.

| Code | Reader | Unconditional exact fraction |
|---|---|---|
| phase | competitive | 0.0 |
| phase | scan | 0.27587890625 |
| position | competitive | 0.896240234375 |
| position | scan | 0.27587890625 |
| priority | competitive | 0.896728515625 |
| priority | scan | 0.2705078125 |

## 3. Compatible-oracle minus learned endpoints

Source: [A.2 gap](../results/experiment_A2_learnability_gap.csv), status=A1_EXISTING, seeds11/22/33/44, step900 source A.1, N separate; equal-seed mean of exact_gap. Scalar A.1 Competitive was not run: do not fill missing entries. Phase C negative differences use an incompatible chosen information oracle, not a learnability estimate.

| Code | Reader | N | Learned exact fraction | Oracle−learned fraction |
|---|---|---|---|---|
| phase | competitive | 4 | 0.91357421875 | -0.91357421875 |
| phase | competitive | 6 | 0.782958984375 | -0.782958984375 |
| phase | scan | 4 | 0.727294921875 | 0.272705078125 |
| phase | scan | 6 | 0.182861328125 | 0.817138671875 |
| position | scan | 4 | 0.477783203125 | 0.522216796875 |
| position | scan | 6 | 0.0068359375 | 0.9931640625 |
| priority | scan | 4 | 0.2919921875 | 0.7080078125 |
| priority | scan | 6 | 0.037841796875 | 0.962158203125 |

## 4. Phase geometry, alignment and seed consistency

Source: [A.3 geometry](../results/experiment_A3_geometry_summary.csv), phase, step900. Equal four-seed means,1024episodes/load/seed. Minimal occupied arc is mean of trial-wise1−max circular gap/(2π), not the arc of a pooled ensemble. Score ties use absolute score difference≤1e−6.

| N | Reader | Arc fraction | Actual score-order fraction | ≤1e−6 pair tie fraction | Semicircle fraction |
|---|---|---|---|---|---|
| 4 | competitive | 0.3770892918109894 | 0.91357421875 | 0.0 | 0.9765625 |
| 4 | scan | 0.6690092980861664 | 0.00048828125 | 0.0 | 0.00634765625 |
| 6 | competitive | 0.44283036142587656 | 0.782958984375 | 0.0 | 0.7978515625 |
| 6 | scan | 0.7390786409378052 | 0.0 | 0.0 | 0.0 |

Source [paired differences](../results/experiment_A3/paired_geometry_differences.csv), phase/arc_fraction: S−C paired by seed; percentile seed-bootstrap95% CI,10,000 resamples,rng7303. Existing intervals copied after checking paired endpoint arithmetic; not independently re-bootstrap-tested here.

| N | Mean difference turns | Min seed effect | Max seed effect | Existing CI low | Existing CI high |
|---|---|---|---|---|---|
| 4 | 0.291920006275177 | 0.2576168775558471 | 0.3231454491615296 | 0.2688222825527191 | 0.3150177299976349 |
| 6 | 0.2962482795119286 | 0.2567923963069916 | 0.3334872722625732 | 0.2681677788496018 | 0.3243287801742553 |

Seed-level final arcs and projected rank (same ordering event as native C exact):

| Seed | N | Reader | Arc | Score-order | Native exact |
|---|---|---|---|---|---|
| 11 | 4 | competitive | 0.3908908367156982 | 0.9072265625 | 0.9072265625 |
| 11 | 4 | scan | 0.6709185242652893 | 0.0009765625 | 0.7314453125 |
| 11 | 6 | competitive | 0.4622222185134887 | 0.775390625 | 0.775390625 |
| 11 | 6 | scan | 0.7417653799057007 | 0.0 | 0.2197265625 |
| 22 | 4 | competitive | 0.4107588529586792 | 0.9169921875 | 0.9169921875 |
| 22 | 4 | scan | 0.6683757305145264 | 0.0 | 0.7392578125 |
| 22 | 6 | competitive | 0.4773202240467071 | 0.7822265625 | 0.7822265625 |
| 22 | 6 | scan | 0.7341126203536987 | 0.0 | 0.103515625 |
| 33 | 4 | competitive | 0.363608181476593 | 0.9140625 | 0.9140625 |
| 33 | 4 | scan | 0.6704981923103333 | 0.0009765625 | 0.7431640625 |
| 33 | 6 | competitive | 0.4264113903045654 | 0.796875 | 0.796875 |
| 33 | 6 | scan | 0.7415816783905029 | 0.0 | 0.234375 |
| 44 | 4 | competitive | 0.343099296092987 | 0.916015625 | 0.916015625 |
| 44 | 4 | scan | 0.6662447452545166 | 0.0 | 0.6953125 |
| 44 | 6 | competitive | 0.4053676128387451 | 0.77734375 | 0.77734375 |
| 44 | 6 | scan | 0.7388548851013184 | 0.0 | 0.173828125 |

Independent saved-array check: all144 panels' accuracy recomputed as mean(all(saved_prediction==target,axis=1)), exactly matches CSV. Phase arc recomputed from saved vectors; maximum absolute CSV discrepancy5.960464477539063e−8 (float32 intermediate versus float64 aggregation), immaterial to stated rounding. Final phase C tie rate0; no inference of arbitrary codebook tie absence. Both loads4/4seed arc direction; eight pairs are not eight independent models.

## 5. Zero-fit transfer, native competence and rank fidelity

Source: [transfer](../results/experiment_A3_cross_readout_transfer.csv), step900. Equal-seed means, N separated. rank_correct from [geometry](../results/experiment_A3_geometry_summary.csv), joined on rep/readout/seed/step/N. These are source-coordinate ranks; Phase S angular rank and C score rank differ. No matched-competence transfer estimator is available from these aggregate rows.

| Code | Source reader | N | Native exact | To other reader exact | Source rank-correct |
|---|---|---|---|---|---|
| phase | competitive | 4 | 0.91357421875 | 0.0 | 0.91357421875 |
| phase | competitive | 6 | 0.782958984375 | 0.0 | 0.782958984375 |
| phase | scan | 4 | 0.727294921875 | 0.00048828125 | 0.88720703125 |
| phase | scan | 6 | 0.182861328125 | 0.0 | 0.757080078125 |
| position | competitive | 4 | 0.892822265625 | 0.26806640625 | 0.892822265625 |
| position | competitive | 6 | 0.736572265625 | 0.02783203125 | 0.736572265625 |
| position | scan | 4 | 0.477783203125 | 0.8876953125 | 0.8876953125 |
| position | scan | 6 | 0.0068359375 | 0.7431640625 | 0.7431640625 |
| priority | competitive | 4 | 0.911376953125 | 0.188720703125 | 0.911376953125 |
| priority | competitive | 6 | 0.796630859375 | 0.02294921875 | 0.796630859375 |
| priority | scan | 4 | 0.2919921875 | 0.86376953125 | 0.86376953125 |
| priority | scan | 6 | 0.037841796875 | 0.673828125 | 0.673828125 |

N6 seed-level scalar competence/transfer check:

| Code | Source | Seed | Native exact | Transfer exact | Rank correct |
|---|---|---|---|---|---|
| priority | competitive | 11 | 0.7783203125 | 0.0205078125 | 0.7783203125 |
| priority | scan | 11 | 0.0478515625 | 0.724609375 | 0.724609375 |
| priority | competitive | 22 | 0.794921875 | 0.021484375 | 0.794921875 |
| priority | scan | 22 | 0.025390625 | 0.703125 | 0.703125 |
| priority | competitive | 33 | 0.7939453125 | 0.02734375 | 0.7939453125 |
| priority | scan | 33 | 0.0166015625 | 0.6181640625 | 0.6181640625 |
| priority | competitive | 44 | 0.8193359375 | 0.0224609375 | 0.8193359375 |
| priority | scan | 44 | 0.0615234375 | 0.6494140625 | 0.6494140625 |
| position | competitive | 11 | 0.7158203125 | 0.0390625 | 0.7158203125 |
| position | scan | 11 | 0.0068359375 | 0.6982421875 | 0.6982421875 |
| position | competitive | 22 | 0.7197265625 | 0.005859375 | 0.7197265625 |
| position | scan | 22 | 0.01171875 | 0.73828125 | 0.73828125 |
| position | competitive | 33 | 0.791015625 | 0.0361328125 | 0.791015625 |
| position | scan | 33 | 0.0 | 0.7744140625 | 0.7744140625 |
| position | competitive | 44 | 0.7197265625 | 0.0302734375 | 0.7197265625 |
| position | scan | 44 | 0.0087890625 | 0.76171875 | 0.76171875 |

## 6. Frozen Phase Competitive reembedding

Source: [counterfactuals](../results/experiment_A3_counterfactual_geometry.csv), representation=phase/readout=competitive/step900, group N/geometry/information, equal four-seed mean. Historical evaluations retained; no decode recomputed. target arcs100%, full-circle0%, source-inferred arc preserves native ranking errors (91.357421875% N4,78.2958984375% N6).

| N | Geometry | Saved information label | Exact fraction | Native sequence preservation |
|---|---|---|---|---|
| 4 | inferred_semicircle | SOURCE_INFERRED | 0.91357421875 | 1.0 |
| 4 | learned | LEARNED | 0.91357421875 | 1.0 |
| 4 | learned_span_arc | TARGET_INFORMED | 1.0 | 0.91357421875 |
| 4 | oracle_slots | TARGET_INFORMED | 0.0 | 0.000244140625 |
| 4 | semicircle | TARGET_INFORMED | 1.0 | 0.91357421875 |
| 4 | source_rank_uniform | SOURCE_INFERRED | 0.0 | 0.0 |
| 6 | inferred_semicircle | SOURCE_INFERRED | 0.782958984375 | 1.0 |
| 6 | learned | LEARNED | 0.782958984375 | 1.0 |
| 6 | learned_span_arc | TARGET_INFORMED | 1.0 | 0.782958984375 |
| 6 | oracle_slots | TARGET_INFORMED | 0.0 | 0.0 |
| 6 | semicircle | TARGET_INFORMED | 1.0 | 0.782958984375 |
| 6 | source_rank_uniform | SOURCE_INFERRED | 0.0 | 0.0 |

## 7. Saved Scan error composition — new read-only audit statistic

Source: runs/experiment_A1/calibration/{rep}_scan/{seed}/eval_900_6.npz, four seeds×1024=4096 episodes/family. failed=any(prediction!=target); null=any(prediction<0); wrong=any(prediction≥0 AND prediction!=target). Count intersections, not independent event rates. Null and wrong can coexist. This audit statistic was not preregistered; label EXPLORATORY/DESCRIPTIVE.

| Code | Failures | Failures with ≥1 null | Failures with ≥1 wrong non-null | Wrong complete sequences (no null) |
|---|---|---|---|---|
| priority | 3941 | 3928 | 2879 | 13 |
| position | 4068 | 4062 | 3221 | 6 |
| phase | 3347 | 3297 | 1230 | 50 |

These counts show rejection dominance and nonzero misassignment. They do not estimate what a threshold-free reader would do. A.2 noise archives contain aggregate null/coverage statistics and rank-stratum counts, not the individual noisy predictions needed to condition null events jointly on preserved rank; that decomposition is UNRESOLVED, not silently borrowed from learned panels.

## Rounding and reproducibility rule

All draft anchors must cite the row/filter above, load and checkpoint. Do not swap P(failure|rank preserved) with A.3 P(rank-correct/metric-poor|failure). Do not present geometry/score/exact coincidences as independent replication. Arithmetic and saved-array recomputation are permitted audit checks; no scientific evaluator was run.

## 8. Native monotonic-branch containment caveat

Read-only exploratory check on final Phase C arrays: wrapped atan2 angles all lie in either [0,π] or [π,2π], the two native θ=0 cosine branches. Fractions by seed/load (branch containment alone does not assert correct target order):

| N | Seed | Branch-contained fraction |
|---|---|---|
| 4 | 11 | 0.77734375 |
| 4 | 22 | 0.7451171875 |
| 4 | 33 | 0.9072265625 |
| 4 | 44 | 0.880859375 |
| 6 | 11 | 0.404296875 |
| 6 | 22 | 0.2861328125 |
| 6 | 33 | 0.66015625 |
| 6 | 44 | 0.662109375 |

A small occupied arc or correct score sequence does not imply every learned trial occupies one monotonic chart. The manuscript may say actual projected ranks are compatible, and constructed oriented charts are compatible; native universal chart containment is UNSAFE. This is a descriptive saved-array diagnostic, not a new experiment or preregistered observation.

# Experiment A.1 calibration results

Status: **STOP A.1 after calibration.** This is a methodological repair stage, not a repaired factorial result.

| Decision | Result |
| --- | --- |
| SCAN VALIDITY | **FAIL** |
| PHASE STABILITY (full preregistered P1–P4 gate) | **FAIL** |
| Numerical/no-collapse subgate P1 | **PASS in both phase cells, 4/4 seeds each** |
| FACTORIAL RERUN | **NOT RUN** |
| Experiment B | **NOT READY FOR EXPERIMENT B** |

The overall phase gate fails because Phase/Scan is not competent at N6, **not because numerical instability persists**. Phase/Competitive passes all P gates. No repaired interaction was tested; original **A-COMPAT-6** remains unresolved. No failed seeds were removed, and no second repair, tuning, OOD evaluation, history/reset, synchronization, control variation or hybrid followed this stop.

## Provenance and repair scope

Original Experiment A is preserved at `135141f83f09977e7cc0b28ff80fab4ee98a8e68`. [A.1 preregistration](experiment_A1_preregistered_gates.md) was committed at **7e1560c** before calibration; implementation at **8c1dfe3**. [Source manifest](../experiment_A1_source.json) records training/evaluation hashes. [Specification](experiment_A1_mechanism_validity_repair.md) gives exact equations and asymmetries. Legacy A code, CSVs, checkpoints and figures were not modified.

Sixteen new calibration runs: Priority/Scan, Position/Scan, Phase/Scan, Phase/Competitive × seeds 11,22,33,44. All use A's unchanged scalar-key task, alternating N4/N6, identical per-seed data streams, 96-dimensional two-layer/four-head backbone, 164,162 parameters, zero learned adapter parameters, hard used-item mask, batch 32, AdamW .001/weight decay .01/clip 1 and 900 steps. Standard checkpoints are 300/600/900; observations every 100 steps detect collapse without selecting or extending runs. Final performance uses 1,024 held-out trials per load; interventions use a separate paired 1,024, and phase probe fits use an independent 256.

Repair S adds a fixed `.45/N` slot neighborhood and explicit NO_MATCH; there is no nearest-remaining fallback. The priority scan's old extrema are mapped to the first/last cursor centers. A fixed boundary-score rejection alternative makes slot eligibility differentiably trainable by the same item-label cross-entropy; no auxiliary rank/phase targets are added. This modifies the scan loss denominator as disclosed before training. Repair P uses normalized 2-D vectors directly, continuous dot-product competition and chord-distance scan. atan2 occurs only in diagnostics. The phase competitive projection has cosine symmetry and is not asserted equivalent to old angular sorting.

## Original Scan diagnosis reproduced

The 24 old Scan checkpoints were replayed from a read-only mount; all normal outputs exactly matched saved A outputs on 48 panels. Freeze preserved **97.80% Priority/Scan** and **100% Position/Scan** outputs, versus 0% Phase/Scan. Cyclic shift and cursor permutation also reproduced weak slot-following behavior in the linear readers. See [old failure mode](experiment_A1_old_scan_failure_mode.md) and [diagnostic CSV](../results/experiment_A1_old_scan_diagnostics.csv). These are implementation diagnoses of existing evidence, not new compatibility claims.

## Final ordinary performance

Exact accuracy is mean ± seed SD, in percent. Pairwise accuracy includes every target pair: missing items receive zero credit, preventing abstention from looking like preserved order. Conditional Kendall tau is separately stored with pair coverage and is undefined with fewer than two present unique items.

| Cell | N4 exact | N6 exact | N4 pairwise | N6 pairwise | N4/N6 NO_MATCH rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Priority/Scan | 29.20 ± 12.54 | 3.78 ± 2.06 | .6113 | .4974 | .2024 / .2787 |
| Position/Scan | 47.78 ± 7.36 | .68 ± .50 | .7164 | .4403 | .1472 / .3169 |
| Phase/Scan | 72.73 ± 2.19 | 18.29 ± 5.89 | .8625 | .6254 | .0685 / .2017 |
| Phase/Competitive | 91.36 ± .44 | 78.30 ± .97 | .9852 | .9840 | .0000 / .0000 |

Per-seed exact percentages (N4 / N6):

| Cell | 11 | 22 | 33 | 44 |
| --- | ---: | ---: | ---: | ---: |
| Priority/Scan | 36.82 / 4.79 | 20.12 / 2.54 | 17.09 / 1.66 | 42.77 / 6.15 |
| Position/Scan | 50.98 / .68 | 54.59 / 1.17 | 37.50 / .00 | 48.05 / .88 |
| Phase/Scan | 73.14 / 21.97 | 73.93 / 10.35 | 74.32 / 23.44 | 69.53 / 17.38 |
| Phase/Competitive | 90.72 / 77.54 | 91.70 / 78.22 | 91.41 / 79.69 | 91.60 / 77.73 |

All three Scan cells fail the cross-load competence requirement. Phase/Scan **passes all Scan gates at N4 in all four seeds**, a bounded positive result; none passes at both N4 and N6. This is not a license to discard N6 or proceed with an N4-only factorial after inspecting results.

## Scan causal gates

On the separate causal panel, freeze changes 100% of Priority/Scan and Phase/Scan sequences and 99.99% of Position/Scan sequences. Exact accuracy becomes zero. Mean all-target-pair drops are **.5312 Priority**, **.5713 Position**, **.7369 Phase**. Every seed/load passes S1. Frozen NO_MATCH rates are .7522/.8195/.8071 respectively. Multiple incorrectly co-located items can still be emitted within one neighborhood; the reader never moves to a different neighborhood as a fallback.

Cursor shift and permutation have **100% exact transformed-output agreement on normal-correct trials**, across defined denominators. This demonstrates slot causality on competent trials, but cannot rescue low unconditional competence. Their all-trial transformed-target accuracy averages .1621/.2321/.4440, reflecting the same missing-slot failures as normal inference on that panel. Gates S2/S3 require both conditional agreement and >=.50 unconditional accuracy. Raw denominators are retained; an empty competent subset never passes.

Assay-coverage limitation: the preregistered permutation was a reverse cyclic shift, not a general noncyclic rearrangement. A clearly labeled **post-calibration saved-code check** additionally used [2,0,3,1] at N4 and [2,0,4,1,5,3] at N6. Normal saved-code replay was exact; noncyclic transformed-output agreement was also 100% on normal-correct trials, with the same low unconditional accuracy. [Supplementary CSV](../results/experiment_A1/noncyclic_cursor_audit.csv) preserves these 24 rows. It changes no model, training, preregistration, gate or stop decision; no additional checkpoints were trained or selected.

| Scan gate | Priority | Position | Phase |
| --- | ---: | ---: | ---: |
| S1 freeze, both loads | 4/4 | 4/4 | 4/4 |
| S2 shift, both loads | 0/4 | 0/4 | 0/4 |
| S3 permutation, both loads | 0/4 | 0/4 | 0/4 |
| S4 competence, both loads | 0/4 | 0/4 | 0/4 |
| All S gates, both loads | 0/4 | 0/4 | 0/4 |

Representation swaps achieve 100% exact intended transformation on normal-correct trials. Expected invariances preserve all sequences. Representation ablation damages competent performance, but many low-accuracy conditions cannot meet the preregistered absolute .20 accuracy-drop gate. We do not lower this gate after seeing floor effects.

Code-only pairwise order decoding remains high: Priority .9758/.9734, Position .9805/.9805, Phase/Scan .9803/.9816 for N4/N6. Thus ordinal information is present while precise slot placement is inadequate. Relative rank and sufficiently accurate metric slot location are different requirements. The observed loss of performance is not evidence that these representation families are theoretically incapable of scan.

## Phase stability and learned use

There were **zero NaN/Inf events, zero preregistered late collapses, and zero qualifying abrupt loss spikes** in all eight phase runs. Both phase cells pass P1 in all four seeds. Raw vector norms vary, but normalized vectors meet the >=.99 norm criterion throughout monitoring; no radial-amplitude shortcut was detected by this test. Raw norms, unit norms, distributions, dispersion/resultant and pre-clip gradient norms are retained in arrays/CSV. Large finite pre-clip gradients are not counted as NaN or collapse.

Phase/Competitive passes P1/P2/P3/P4 in 4/4 seeds at both loads. Its independent phase-vector rank-probe pairwise accuracy, averaged over N4/N6, is .9834/.9850/.9854/.9847 for seeds 11/22/33/44; circular/rank association .9677/.9737/.9701/.9643. Targeted vector swaps change the intended pair; a score boost moves the late target earlier. Common rotations .37/2.1, including the reference, preserve 100% of output sequences, with score differences below 2e−6.

Phase/Scan independent-fit phase probe accuracy is .8329/.7745/.7886/.8317 across seeds (N4/N6 average), and circular/rank association .8657/.8331/.8438/.8697. P1 and P4 pass in all seeds; P2/P3 fail their **cross-load** requirements because N6 competence/readout gates fail. Its anchored code ordering is stronger than its simple linear rank probe; unanchored pair-difference decoding is reported separately, not substituted for primary criteria.

Structural rotation invariance and code-swap covariance are distinguished from learned ordinal information and task competence. A continuous phase vector with a cosine projection is an artificial relative-direction code; these results do not show a unique phase mechanism, biological superiority, or equivalence to the old unwrapped-phase competition.

## Original A versus this calibration, not a new factorial test

The following comparison uses only the four common seeds and averages N4/N6 equally. These are separate datasets. A.1's stricter reader can abstain, whereas A was forced to emit N items.

| Cell | Original A exact % ± SD, same four seeds | A.1 calibration exact % ± SD |
| --- | ---: | ---: |
| Priority/Scan | 78.74 ± 2.59 | 16.49 ± 7.29 |
| Position/Scan | 82.59 ± 1.75 | 24.23 ± 3.91 |
| Phase/Scan | 62.07 ± 40.36 | 45.51 ± 3.22 |
| Phase/Competitive | 54.86 ± 30.21 | 84.83 ± .59 |

The phase competitive optimization repair is promising within these four seeds; the genuine-slot scan is not competent across the fixed task loads. We cannot determine whether the original significant R×O interaction would persist, weaken, reverse or disappear after a successful full repair. **No repaired interaction, factorial p-value or OOD result was produced.** Original F(2,14)=4.7988/p=.00355 remains attached only to original A.

## Artifacts and validation

Final verification: 14/14 targeted tests passed in the pinned remote Docker environment. All 1,232 original raw-artifact hashes and all 529 transferred A.1 hashes match; 12 frozen source hashes match. Independent calculation verified exact accuracy, missing-aware pairwise accuracy and pair coverage on all 288 monitoring panels. The 96 standard-checkpoint panels use exactly the original A item IDs, numeric cues and targets. All five task-owned containers exited successfully; their logs were retained locally before removal. Both remote checkpoint directories remain intact.

Repository delivery note: preregistration and implementation commits are recorded above. Final report/artifact changes remain in the working tree because the current execution environment exposes `.git` as read-only; no final commit or push was attempted under that restriction.

- [Scan calibration](../results/experiment_A1_scan_calibration.csv), [phase stability](../results/experiment_A1_phase_stability.csv), [causal gates](../results/experiment_A1_causal_gates.csv), [invariance](../results/experiment_A1_invariance.csv).
- [Results index and eight plots](../results/experiment_A1/README.md), including all seed values, checkpoint metrics, decisions and verification.
- Training code: `experiment_a1/model.py`, `run.py`, `evaluate.py`; read-only reporting: `report.py`. `old_scan.py` is explicitly limited to original checkpoint diagnosis. Source hashes in `experiment_A1_source.json`.
- Raw results: `runs/experiment_A1/calibration/<cell>/<seed>/`; 48 checkpoints, optimizer/RNG states, source/config, monitoring arrays and final causal arrays. Remote retained copy: `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a1-20260929/`. Original A was mounted read-only for replay.
- No full-factorial or OOD files are fabricated for a stage that was not run. Only task-owned completed containers are removed after artifact verification; checkpoint directories remain preserved.

**NOT READY FOR EXPERIMENT B.** Parameter matching alone did not identify causal readout functions in A; causal readout geometry alone did not produce usable multi-load competence in A.1. This is the methodological boundary established here. No further repair was attempted.

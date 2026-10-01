# Experiment A.3 — learned geometry adaptation audit

**A3-GEO-5 — Mixed. DO NOT RERUN FACTORIAL YET. EXPERIMENT B: BLOCKED.**

There is strong, functionally supported phase geometry adaptation to the frozen readout package. Scalar geometry differences are smaller or inconsistent, while genuine Scan remains calibration-limited. This does not establish two equally competent learned solutions for every family.

## Provenance and comparability

[Comparability audit](experiment_A3_checkpoint_comparability.md), [specification](experiment_A3_learned_geometry_adaptation.md), and [preregistration](experiment_A3_preregistered_hypotheses.md) preceded primary geometry interpretation. Scalar Competitive uses original A, scalar Scan uses A.1; their code/head/backbone/initialization/data/optimizer/budget match, and the Scan adapter/rejection loss belongs to the intended readout treatment. Phase uses A.1 for both readers, with identical continuous S1 parameterization. Original A phase is not pooled with A.1 phase. No additional training was necessary.

Four shared seeds11/22/33/44; checkpoints300/600/900; N4/N6, 1024 trials/panel. All 72 readout-paired inputs match exactly in identity, cue and target, and all 144 native predictions replay exactly. The contrast identifies effects of the **readout package and its learning objective**, not a readout decision rule isolated from its loss geometry. Existing poor Scan competence remains an interpretive limitation. No prior artifact or hypothesis was overwritten.

## Learned family versus learned geometry

Final means across four seeds:

| Family/readout | N4 exact | N6 exact | N4/N6 canonical aligned RMSE | N4/N6 spacing CV |
| --- | ---: | ---: | ---: | ---: |
| Priority/C | .9114 | .7966 | .1109 / .0988 | .6572 / .7876 |
| Priority/S | .2920 | .0378 | .0998 / .0911 | .5969 / .7505 |
| Position/C | .8928 | .7366 | .0889 / .0793 | .5421 / .7256 |
| Position/S | .4778 | .0068 | .0651 / .0627 | .3862 / .5497 |
| Phase/C | .9136 | .7830 | .1683 / .1719 | .4560 / .6083 |
| Phase/S | .7273 | .1829 | .0477 / .0519 | .3017 / .4793 |

Linear RMSE is in endpoint-normalized coordinates after positive affine fit; phase RMSE is in turns after common rotation. These are family-specific measures, not a cross-family quality ranking. Canonical error does not measure fitness to the actual reader.

**Priority:** no uniform cross-seed systematic signature at preregistered effect sizes. Scan-minus-C RMSE differences are −.0111 N4 and −.0077 N6, with paired seed bootstrap intervals crossing zero. Spacing changes also change sign across seeds. Raw dynamic range is larger under Scan (N4/N6 mean11.20 vs8.17), but priority is affine-invariant, so raw amplitude is not standalone functional compression evidence.

**Position:** Scan has consistently lower affine RMSE in4/4seeds at both loads (differences−.0238/−.0167) and lower spacing CV (−.1558/−.1759). These are reproducible directional differences, below the preregistered .05-RMSE/.20-CV effect-size cutoffs. They do not resolve its severe N6 slot-calibration deficit. Raw range averages .828 Scan vs .862 Competitive; do not confuse raw range with calibrated slot coverage.

**Phase:** strong same-signed geometry differences in4/4seeds at both loads:

| Measure | Competitive N4 / N6 | Scan N4 / N6 |
| --- | ---: | ---: |
| Minimum occupied arc / full circle | .3771 / .4428 | .6690 / .7391 |
| Fraction fitting a semicircle | .9766 / .7979 | .0063 / .0000 |
| Actual cosine scores monotonic in target rank | .9136 / .7830 | .0005 / .0000 |
| Correct cursor-slot capture per item | .2171 / .1074 | .9079 / .7645 |

Paired Scan-minus-C arc differences are+.2919 turns N4 (seed-bootstrap95% CI .2688–.3150) and+.2962 N6 (.2682–.3243). Phase/Scan rotation-aligned canonical RMSE is lower by .1206/.1200 turns. Minimal arc does not itself prove monotonic projection; the actual score measurements and counterfactuals supply that additional evidence. Four seeds provide limited population inference; no trial-level pseudo-replicated significance claim is made.

## Transfer and geometric counterfactuals

Direct transfer uses the source's learned code with the other frozen reader, no fitting:

| Transfer | N4 exact | N6 exact |
| --- | ---: | ---: |
| Priority C→S | .1887 | .0229 |
| Priority S→C | .8638 | .6738 |
| Position C→S | .2681 | .0278 |
| Position S→C | .8877 | .7432 |
| Phase C→S | .0000 | .0000 |
| Phase S→C | .0005 | .0000 |

Scalar transfer is asymmetric: Scan-trained codes often retain useful rank for competition, but C codes do not satisfy precise Scan slots. Phase transfer is poor in both directions because circular slot geometry and cosine-score geometry differ. Since native Scan is weak at N6, these results do not prove two fully learned successful strategies or justify a factorial rerun.

Under the same frozen Phase/Competitive reader:

| Geometry | N4 | N6 | Information used |
| --- | ---: | ---: | --- |
| Learned | .9136 | .7830 | saved model code |
| Uniform full circle | 0 | 0 | target rank |
| Monotonic semicircle | 1 | 1 | target rank |
| Monotonic arc using learned span | 1 | 1 | target rank; span capped below π if necessary |
| Monotonic semicircle | .9136 | .7830 | source-inferred score rank only |
| Uniform full circle | 0 | 0 | source-inferred score rank only |

The source-inferred semicircle preserves native output, so the explanation is not solely target-rank correction. The target-informed arc relocates/orients the code into the monotonic cosine region and may cap the span; it is not merely rotating the original code. H-A3-6 is supported under these defined manipulations. A.2's canonical full-circle failure remains valid and unmodified.

For scalar competition, source-rank uniform and cubic coordinates preserve native output100%, despite changed metric spacing. This follows from the imposed ranking decoder; the learned evidence is that the trained code supplies task-aligned rank. It does not prove competition learns invariance autonomously.

For Scan:

| Geometry | Priority N4/N6 | Position N4/N6 | Phase N4/N6 |
| --- | ---: | ---: | ---: |
| Learned | .2920/.0378 | .4778/.0068 | .7273/.1829 |
| Nearest-slot snap, collisions retained | .3391/.0601 | .6047/.0295 | .7690/.2717 |
| Uniform slots from inferred rank | .8638/.6738 | .8877/.7432 | .8872/.7571 |
| Target oracle slots | 1/1 | 1/1 | 1/1 |
| Target-rank-preserving cubic metric distortion | 0/0 | 0/0 | 0/0 |

Nearest snapping is not a bijection: collisions remain, and the priority reader retains its original extrema normalization. Inferred-rank uniformization explicitly computes a rank and assigns metric slots. It is a diagnostic counterfactual, not an implemented learned calibration remedy or authorization to insert sorting into the model.

## Rank versus metric failure

At N6, rank-correct/metric-poor cases account for **66.1% Priority**, **74.1% Position**, and **70.3% Phase** of Scan errors. Thus most observed failure is not loss of ordinal rank, although rank errors remain substantial. Every metric-poor, rank-correct Scan trial fails; every metric-good, rank-correct trial succeeds. This split is partly structural because metric-good is defined by all target items lying inside their true disjoint capture windows. The informative quantities are the prevalence of each stratum and the rank-preserving causal replays, not treating that conditional identity as an independent learned law.

All rank-correct/metric-poor competitive trials succeed, including 6129 Priority,5462 Position,6949 Phase final trials pooled over both loads. For phase C, rank means actual score rank; onset angular ordering is reported separately. Score monotonicity and deterministic competition accuracy are structurally linked, so they are not independent confirmations.

## Geometry evolution

Phase means over seeds and N4/N6:

| Reader / checkpoint | Arc fraction | Canonical RMSE | Exact |
| --- | ---: | ---: | ---: |
| C / 300 | .3316 | .1880 | .7159 |
| C / 600 | .4119 | .1731 | .7987 |
| C / 900 | .4100 | .1701 | .8483 |
| S / 300 | .6163 | .0907 | .1127 |
| S / 600 | .6774 | .0600 | .3369 |
| S / 900 | .7040 | .0498 | .4551 |

A restricted competitive arc is already present at300, but it **expands rather than progressively compresses** as accuracy improves. Scan approaches broader, more calibrated circular slots. Do not impose a monotonic compression narrative. Per-cell geometry/performance correlations and eight lagged transitions per load are saved; these sparse, dependent observations cannot establish that geometry changes causally preceded competence. No earlier-checkpoint rerun was introduced to strengthen that claim.

## Answers and gate

- **Q1:** Priority geometry shows small, inconsistent differences; no preregistered systematic adaptation signature.
- **Q2:** Position Scan is more uniformly spaced on average and directionally consistent across seeds, but below the predeclared effect-size cutoffs and still poorly slot-calibrated.
- **Q3:** Phase geometry differs strongly by readout.
- **Q4:** Yes: Phase C usually occupies a restricted region with task-aligned monotonic cosine projection; not every trial fits a semicircle.
- **Q5:** Yes: Phase S is closer to cursor-aligned circular slots, despite inadequate precision at N6.
- **Q6:** Most N6 Scan errors are rank-correct metric failures; ordering errors are not absent.
- **Q7:** Yes for the tested scalar competitive readers and rank-preserving transformations; this is a reader property exercised by learned task-aligned codes.
- **Q8:** Scalar transfer is asymmetric; phase transfer is poor in both directions. No retraining.
- **Q9:** Rank-uniformization preserves scalar competition, improves Scan, and harms cosine phase competition if it spreads code around a full circle. Nearest-slot snapping helps only partially.
- **Q10:** Yes: monotonic semicircle/arc rescues the frozen cosine reader relative to full-circle geometry; source-inferred rank preserves native errors instead of secretly fixing them.
- **Q11:** **A3-GEO-5 — Mixed.** Strong phase adaptation coexists with modest scalar geometry changes and substantial Scan learnability/calibration limits.
- **Q12:** **DO NOT RERUN FACTORIAL YET.** No demonstrated learned calibration remedy makes the repeated factorial a clean new comparison.
- **Q13:** **EXPERIMENT B: BLOCKED.**

[Evidence index](../results/experiment_A3/README.md) contains all required tables, twelve plots, seed-paired effect intervals, trajectories, geometry/performance associations and provenance checks. The source manifest freezes the primary protocol before results. Final artifacts remain uncommitted because this environment exposes Git metadata read-only. No biological optimality, neural geometry, novelty, or theoretical impossibility claim follows.

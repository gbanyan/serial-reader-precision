# A-series statistical audit — pre-manuscript red-team

2026-10-01. No new inferential tests or experiment runs. [Exact anchors](A_series_manuscript_anchor_numbers.md), [provenance](A_series_reproducibility_audit.md). Learned-system unit=training seed; oracle/noise unit=independent data/noise panel. Pairing by episode/seed/load/checkpoint is dependence, not new model replication.

## Manuscript-facing analysis table

| Analysis | n seeds/panels | n trials | Primary unit | Test / estimator | Effect size | CI | Status |
|---|---|---|---|---|---|---|---|
| Original A interaction |8 training seeds |1024 eval/load/cell/checkpoint;6cells,reference separate | Paired training seed |F(2,14)=4.7988;20,000 within-seed permutations,p=.00355 | Readout difference by code family | Existing seed bootstrap | PREREGISTERED historical; confounded, Supplement only |
| A.1 repair/endpoints |4 seeds×4cells |1024 eval/load;256 causal/load/cell/seed | Seed, declared per-load gate | Mean/SD and operational competence/causality gates | N6Scan3.78/.68/18.29%,phase C78.30% | No new CI | PREREGISTERED calibration; overall gates failed |
| A.2 compatible oracles |4 data panels |1024/condition;120 cells including both readers | Random panel, same trials paired | Exact supplied-code capability | Scan100% N4–12 | Descriptive counts; no population-theorem CI | PREREGISTERED |
| A.2 noise/rank strata |4 noise/data seeds |1024×960condition rows=983040 paired reader evaluations | Noise/data panel; conditional episode sampling | Counts/rates; saved Wilson intervals | N6σ.35 preserved-rankScan69.83/69.22/63.55%,scalar C0 | Existing per-panel Wilson95%,not training-seed CI | PREREGISTERED assay; illustrative anchor not new selective test |
| A.2 learned gap |4 A.1 seeds |1024/load/seed;32 endpoint panels | Training seed | Mean oracle−learned | N6Scan96.22/99.32/81.71pp | Endpoint seed variation; no new CI | PREREGISTERED diagnostic |
| A.2 error–failure association |Same4 |1024/panel | Within-panel descriptive; seed replicates | Spearman, preserved-rank failure | Positive but floor-limited, one Position/N6 undefined | No association CI promoted | PREREGISTERED diagnostic; no optimizer mediation |
| A.3 phase geometry |4 paired training seeds |1024×2loads×3steps×2phasecells | Seed per load; checkpoints dependent | Paired S−C;10,000 seed bootstrap | Arc+.291920N4/+.296248N6 turns |95% percentile: N4[.268822,.315018],N6[.268168,.324329] | PREREGISTERED within later exploratory program; MODERATE scope |
| A.3 scalar geometry |Same4 |Same panel schedule | Paired seed | Declared .05RMSE/.20CV operational thresholds |Priority inconsistent;Position−.02375/−.01665RMSE,sub-threshold | Saved paired intervals, no multiplicity-adjusted significance | PREREGISTERED exploratory diagnostics; Supplement |
| A.3 transfer |Same4/source |1024/panel,144 condition rows | Paired training seed | Directional native/transfer means | N6S→C67.38/74.32% vsreverse2.29/2.78% | No new CI/competence-adjusted test | DESCRIPTIVE / preregistered functional diagnostic; Supplement |
| A.3 geometry replay |Same4 |1024/load/source/intervention;232 rows total | Paired seed and shared episodes | Frozen fixed-reader exact/preservation | C arc100/fullcircle0,target;source arc native retained | No independent-model CI/test | COUNTERFACTUAL, preregistered constructors; information labels required |
| A.3 checkpoint/lag association |4 independent seeds,12 snapshots or8 transitions/load | Reused codes | Dependent snapshots descriptive | Saved correlations | No causal effect estimate | No valid independent-snapshot CI | DESCRIPTIVE, Supplement |
| Current saved-array omission/branch audit |Same4 |4096/family/load final | Fixed saved cohort | Counts/angle containment only | N6null present in3928/3941,4062/4068,3297/3347Scanerrors;native Cbranch28.6–66.2% | None added | EXPLORATORY / DESCRIPTIVE, not retrospectively preregistered |

No present analysis is upgraded to independent CONFIRMATORY evidence merely because later-stage hypotheses were written before that stage's outputs. Record preregistration timing relative to prior exploratory failures. Existing four-seed bootstrap is a small-cohort descriptive uncertainty estimate, not strong population evidence.

## Dependencies and statistical risks

- C strict score ordering equals exact deterministic output under normal masks; not an independent measure supporting behavior.
- Scan metric-good is defined using target capture and partly equivalent to success. Strong separation of strata is not independently discovered law.
- Oracle-minus-learned gap restates endpoints. Replay/transfer reuse models and episodes. Loads/checkpoints not independent model counts.
- A.2 preserved-rank failure pools failures/counts, not mean panel failure percentages. Different denominator from A.3 share of errors in rank-correct metric-poor stratum.
- Wilson episode intervals reflect sampling given panels; they are not uncertainty over learned seeds. Bootstrap four seeds can look falsely precise: display raw pairs/ranges.
- Original factorial p-value not main support. No new headline p-values or multiple-comparison selection. Show full load/noise tables and preserve null/sub-threshold cases.
- Canonical alignment/target arcs use labels diagnostically, not model input; source rank transformations also perform substantial external computation.
- Phase score and angular ranks differ; full-circle C has unsuitable baseline. A.1 scalar C gap missing, undefined floor correlations missing. Cross-family canonical error scales are not interchangeable.

## Presentation decision

Main: literal reader invariance, supplied-code oracle capability, full controlled-noise curves plus rank-conditioned counts, learned endpoint gaps and four paired phase contrasts with information-labeled replay. Supplement: transfer, original factorial/repair provenance, weak scalar geometry, descriptive trajectory/lag correlations and full numerical tie tests. No inherent learnability ranking, temporal mediation or acceptance nesting significance.

Use exact numbers/rounding from anchor memo. NO ADDITIONAL EXPERIMENT for the red-team narrowed claim; complete-text/access and archive packaging remain submission work.

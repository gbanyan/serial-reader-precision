# A-series reproducibility and provenance audit

2026-10-01. Read-only file/hash/array inspection. PASS means checked scope, not new reproduction of training. [Methods map](A_series_methods_map.md), [anchors](A_series_manuscript_anchor_numbers.md), [statistical units](A_series_statistical_audit.md).

## Checks actually performed

| Check | Status | Evidence and boundary |
|---|---|---|
| Primary source manifests | PASS | A8,A.1 12,A.2 5,A.3 8 frozen entries:33/33 current SHA-256 matches, including preregistrations and decoder/generator modules |
| Result/plot artifact manifests | PASS | A.2 43 and A.3 37 entries match archived SHA-256; no raw data/plot rewritten |
| Git lineage | PASS |7811085,135141f83f09977e7cc0b28ff80fab4ee98a8e68,7e1560c,8c1dfe347a3e0d9d3e6a8ce590e2528fcf9447d4 resolve as commit objects |
| All A.3 saved source panels | PASS |144 NPZs resolve; identity/numeric/target arrays match in72 paired conditions. Saved prediction exact means match all144 CSV rows exactly |
| Phase occupied-arc arithmetic | PASS | Recomputed from vectors; max difference5.96e−8 due to arithmetic precision; headline rounding unchanged |
| Checkpoint and config resolution | PASS for existence |72 distinct checkpoint files across24 source models,144 eval panels, corresponding config and complete files found. This audit did not deserialize or forward weights |
| Checkpoint semantic reproduction | WARNING | Prior A.2/A.3 verification records exact historical saved-prediction replay. Current pass checks archives only; no independent weight execution or training recreation |
| Oracle/noise per-trial reconstruction | WARNING |120 oracle/960 noise/2880 rank-count rows hash-verified and aggregated; noisy codes/predictions not archived as per-trial NPZ. Derivation executable in frozen analysis.py, but not rerun here |
| Parameter matching | PASS for records/source dimensions | Every row of results/experiment_A/parameters.csv gives164162 total,154272 backbone,9890 representation head (reference readout9890),0 adapters. A.1 configs agree; no live parameter counting. Equal count is not equal objective/conditioning |
| Package/config versions | PASS for records | Configs retain steps900,loads4/6,AdamW lr.001/wd.01/clip1/batch32; shared hidden96/two layers/four heads. A.1 radius.45/N and epsilon1e−8 declared; original sample Torch2.8.0+cpu/NumPy2.3.3/Python3.13.15. Exact archive rather than local package assumptions |
| Complete commit captures analyses | WARNING | Many source/report/Markdown/results files currently untracked. Git history alone is not full reproducible release; source/artifact manifests provide file-level provenance. Do not claim all analysis was committed before results |
| Preregistration timing | PASS within recorded chain; WARNING historical certainty | Original A/A.1 prereg commit lineage resolves; A.2/A.3 frozen prereg hashes match and completion/verification records describe pre-primary freeze. Hash match alone does not independently prove temporal order; no retroactive confirmatory label |
| Stage separation | PASS under explicit map |Scalar C A,scalar S A.1; both phase A.1. Original angular phase and old permissive Scan excluded from main repaired-reader comparisons. A.1 scalar C gaps absent, not filled from A |
| Independent complete rerun | NOT PERFORMED | No evaluator/train/test suite executed. This is an evidence audit, not new end-to-end reproducibility demonstration |

## Main-figure/result provenance

| Planned main result | Status | Trace and manuscript caution |
|---|---|---|
| Fig1 reader schematic | PASS | model.py/analysis.py literal scores, adapters, masks, null constants. Analytical schematic not empirical evidence |
| Fig2 oracle/noise | PASS data / WARNING interpretation | A.2 CSV counts and hashed plots/report source; four noise/data panels not training seeds; full-circle C not compatible oracle; conditional omissions not jointly saved |
| Fig3 learned gap/error | PASS data / WARNING inference | A.1 NPZ endpoints→A.2 tables; subset of144 endpoint accuracy checks. Geometry association partly eligibility-defined, not optimizer causal analysis |
| Fig4 phase geometry | PASS data / WARNING generalization | A.1 source NPZ→A.3 phase table/paired effects→09_phase_arc.png,10_phase_monotonicity.png. Four paired seeds, no independent reader/loss isolation; aggregate evolution mixes loads unless stated |
| Fig5 frozen replay | PASS archived output / WARNING information |232 counterfactual rows→11_phase_counterfactual.png; source code main() records rank constructors. No current replay rerun; main arcs rank-informed, not label-free |
| Transfer (Supplement) | PASS data / WARNING competence |144 rows→07_transfer.png; native endpoints/rank inspected. No comparable-native-performance conditional transfer table |
| Original factorial (Supplement) | PASS historical / FAIL as current core support | Eight original seeds, p=.00355 retained; pseudo-scan/angular instability invalidate general compatibility inference. This is inferential FAIL, not missing artifact |

## Plot audit

Saved panels viewed: A.2 rank-conditioned failure/gaps; A.3 transfer/arc/monotonicity/counterfactual. Report modules trace each to named CSV/pivot. Figure07 displays native competence, which must remain visible; Figure11's present legend is insufficient to signal target/source information—draft captions/panels must add that. Figure10 score ordering duplicates native C correctness; it cannot supply independent significance. Existing illustrations use selected seed/load; label example, show paired effects elsewhere. No pixels changed in this audit.

## Release and reporting warnings

Preserve manifests, exact code/configs, evaluator versions, seeds, all failed gates and untrained cells. Package fixed files before submission, retaining useful text diffs; no commit/push performed by this pass. Complete-text prior-art gaps remain. No main anchor is presently missing, but do not claim weight-to-result rerun, complete noisy trial archive or fully committed prereg provenance from this audit.

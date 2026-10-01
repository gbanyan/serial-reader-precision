# Experiment A.1 preregistered gates

Status: frozen before any A.1 calibration interpretation. Commit this document and implementation before training. A.1 is a methodological repair stage, not performance tuning. Do not change thresholds, neighborhood radius, phase score, initialization, loss, seeds or budget after results. If a gate fails, STOP A.1; no automatic second repair.

## Panels and metrics

Four seeds 11/22/33/44 per calibration cell; all retained. N4 and N6 are evaluated separately on 1,024 fixed held-out examples per checkpoint and final causal panel. Standard checkpoints 300/600/900; monitoring every 100 steps measures collapse without changing training. Independent phase probe-fit panel: 256 examples. Means/SD are over seeds; report each seed and both loads.

Exact accuracy requires all target items and order. NO_MATCH=-1 is never a valid item. Primary pairwise accuracy counts every target pair in its denominator: credit only if both items appear exactly once and in the correct order. Missing/duplicate items give zero credit to affected pairs. Also report tau on present unique items, defined only with >=2, plus coverage; do not substitute survivor-only tau for primary accuracy. First error is zero-based, N when correct. Interventions additionally report sequence change, pairwise relation change including missing pairs, first changed position, transformed-target accuracy, model-output transformation agreement, content/NO_MATCH rates, and collateral mismatch.

Fixed cursor schedules: normal [0,...,N-1]; freeze all zero; shift [1,...,N-1,0]; permutation [N-1,0,...,N-2] (distinct from +1 at both loads). These are specified before training, not selected for maximal effect.

## Scan validity (S)

Each Scan cell must pass every requirement below at **both loads in at least 3/4 seeds**. Overall SCAN VALIDITY is PASS only if all three representation Scan cells pass. Otherwise FAIL and do not run the factorial, even if only one pairing appears promising.

- **S-GATE-1:** freeze changes >=.50 of sequences and lowers all-target-pair accuracy by >=.20 absolute relative to normal. Both are required. Report NO_MATCH/stall frequency; destructive failure alone is insufficient.
- **S-GATE-2:** cyclic cursor shift yields >=.80 exact agreement with the correspondingly permuted original model output **on normal-correct trials**, and >=.50 exact accuracy against shifted targets on all trials. Report the conditional denominator. This prevents success through permuting already-invalid outputs.
- **S-GATE-3:** arbitrary preregistered permutation meets the same .80 conditional / .50 unconditional gates. Report per-slot agreement and collateral errors.
- **S-GATE-4:** normal exact accuracy >=.50 and all-target-pair accuracy >=.80. Uniform random ordering is 1/N!; these thresholds require usable competence, not superiority to competition.
- **S-GATE-5:** setting all representation coordinates to one common constant reduces exact accuracy >=.20 and pairwise accuracy >=.20. This preserves all non-code states. Phase ablation replaces every vector by the reference unit vector (removes item-specific phase without changing its norm).
- Additional mechanism requirements: representation-only pairwise order decoding >=.75; targeted first/last-target code swap yields >=.80 exact transformed output on normal-correct trials; each expected invariance preserves >=.99 of sequences. Hard mask alone may not pass freeze; repeated NO_MATCH must not consume a fallback item.

## Phase validity/stability (P)

**P-GATE-1:** no NaN/Inf event and **zero late-collapse runs out of four in each phase cell**. Collapse means a monitoring exact N4/N6 average falls >.30 below an earlier monitoring checkpoint that reached >=.50. Report transient collapse/recovery too; no endpoint-only rescue. An abrupt loss spike is a sampled loss >previous five-sample median+1.0 and >3× that median, diagnostic only. Record pre-clip gradient norms, raw 2-D norms, normalized norms, phase dispersion/order parameter and code distributions. Norm >=.99 for >=99% of evaluated item vectors is required to exclude a radial-amplitude shortcut.

**P-GATE-2:** at final checkpoint, exact >=.50 at each load and phase-only linear-probe pairwise decoding >=.75 in >=3/4 seeds per phase cell. Probe fits normalized rank from two vector channels on independent examples. Also report circular/rank association, reference-based order decoding and unanchored pair-difference decoding with trial-separated folds; none can replace the primary test after looking at outcomes.

**P-GATE-3:** phase code swap (target first/last item vectors, content retained) yields >=.80 exact swapped-output agreement on normal-correct trials in >=3/4 seeds at each load. Phase/Competitive score boost moves the last target item earlier in >=.90 of normal-correct trials. Phase/Scan must meet S's cursor gates. Representation ablation must reduce exact >=.20.

**P-GATE-4:** common rotations .37 and 2.1 radians, including reference and cursors, preserve >=.99 of complete outputs in every seed. Report unmasked score deviations. Norm stability and rotation are structural tests; competent learned code use is separate.

Overall PHASE STABILITY label covers P-GATE-1 through P-GATE-4: PASS only if all pass for both phase cells. Report P-GATE-1 separately so a competence failure is not mislabeled numerical instability. A stable but useless representation does not open the factorial gate.

## Original implementation diagnosis

Before repaired calibration, load the 24 original final Scan checkpoints (8 seeds × 3 cells), evaluate normal/freeze/shift/permutation at both loads, verify exact replay against original saved normal predictions, and write only A.1 diagnostic files. This reproduces the known pseudo-scan limitation; it is not a new hypothesis test. A's raw files and code remain byte-identical.

## Conditional factorial and analysis

Proceed only if S and P both PASS. Complete eight seeds 11,22,33,44,55,66,77,88 × six cells, retaining identical calibration runs. No reference retraining; no model-specific continuation. Same N4/N6 stream and all global settings as A. Final seed-level exact averages across both loads enter the same R×O interaction test: repeated-measures F(2,14), 20,000 within-seed permutations of the three scan-minus-competitive differences; 10,000 seed bootstrap resamples for difference CIs. Final is confirmatory; 300/600/900 effects descriptive. Original versus repaired statistics stay separate.

If rerun: OOD N8/10/12 without retraining only for cells satisfying A's ID stability rule (>=.50 final, no >.10 mid-to-final decline in >=6/8 seeds); otherwise explicit not-tested rows. Report missing-item-aware metrics alongside conditional tau and coverage, because A structurally prevented omissions. Do not pool partial-output A.1 tau with A's complete-sequence tau without this qualification.

Compatibility categories use A's effect-size/direction criteria only after the stricter cell-level causal criteria hold. A-COMPAT-6 takes precedence for instability, invalid readout function or incomparability. If calibration fails, factorial NOT RUN, retain A-COMPAT-6 as unresolved without computing a four-seed substitute interaction. No significance-seeking retest.

Experiment B remains blocked unless both repair gates pass, at least three repaired factorial cells pass the six-part mechanism assay in >=6/8 seeds, at least two representation families work, both readouts are genuinely causal, and optimization confounds do not dominate. Otherwise NOT READY FOR EXPERIMENT B. No claims of biological correctness, impossibility of failed pairings, or novelty.

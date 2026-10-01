# Experiment A preregistered hypotheses and decisions

Status: FROZEN BEFORE MAIN TRAINING, 2026-09-29. Source/config and this file will be committed before the first training run. Bugs may be corrected with an explicit log; hypotheses, budgets and readers will not be adjusted after inspecting scores. This is not preregistration of earlier experiments.

## Hypotheses and units

H_A1: representation and readout have non-identical compatibility. Direction unspecified. Evidence requires an R×O interaction plus task-aligned and causal code/readout diagnostics. The external reference is excluded from factorial tests. Seed is the independent replication unit; evaluation trials are paired across cells, not extra independent training runs.

Primary outcome: final exact accuracy averaged equally over N4 and N6. For each seed form three differences D_R=accuracy(R,scan)-accuracy(R,competitive). Test equality of these differences with repeated-measures one-factor ANOVA (equivalent to the factorial interaction), reporting F with df(2,14) and a within-seed permutation p-value (20,000 random permutations of R labels within D). The exchangeability assumption is approximate; report paired effect sizes and bootstrap intervals over eight seeds, not p alone. Interaction effect size is the range of mean D_R; report each D_R, SD, CI and seed values. Confirmatory alpha .05, no search across checkpoints for the best p.

Secondary: pairwise ordering, Kendall tau, first-error position (N if correct), losses, seed SD; stage-specific R×O effects at 300/600/900 and length-specific effects are descriptive. Report exact counts by component and flag >5% factorial mismatch. No global winner claim.

## Mechanistic measurements and gates

Representation-only order decoding uses the documented coordinate c (earlier is smaller); report Spearman vs target rank, pairwise accuracy and stage-wise code emergence. Also fit a simple ridge linear rank probe on separate examples, test on held-out examples; phase features are sin/cos relative to the onset anchor, priority/position scalar. A circular-linear association is secondary. No identity/content enters probes. Endogenous phase amplitudes are discarded.

At final checkpoint, exchange codes of the first and last **model-predicted** items (chosen before intervention); report selective inversion, exact transposition of the original model output, mean absolute rank shift, unrelated-item movement, and unchanged content. Separately boost the last predicted item's O1 score above all scores at step 0, or advance O2 cursor by one slot at step 0; report intended earlier selection and score/cursor effect. These hooks can act before training: task alignment must be established independently.

Ablate the entire intended code to a constant with other hidden state retained; record exact/pairwise drops. Readout has no hidden-state bypass by construction. Probe failure, small ablation drop or failed directional interventions blocks a strong mechanism-use claim despite high accuracy.

Operational final functional-cell gate (both ID loads averaged): exact >= .50, code pairwise decoding >= .75, representation swap inversions >= .90, O1 boost produces earlier rank in >= .90 or O2 advance chooses a later original output slot in >= .50, exact ablation drop >= .20, and each relevant invariance preserves >= .99 of output sequences. Require these on >=6/8 seeds. Thresholds are assay decisions, not universal definitions. Record failures separately rather than redefining them.

## Invariances

Priority: p→2p+3; min/max adapter transforms with p. Position: u→2u+3 with its origin/span changed from (0,1) to (3,2), and cursor/reference transformed together. Phase: phi→phi+c AND anchor→anchor+c, c=.37 and 2.1; this is relative-to-reference rotation, not items-only rotation. O1: common score offset +3. O2: matched coordinate/reference transform as above; phase distances in turns. Finite precision tolerance is allowed at ties; report sequence changes and maximum logit discrepancies on unmasked entries. Items-only phase rotation is a negative control, not an expected invariance. Positive affine priority invariance follows normalization; these are designed properties, not discoveries.

## Floor, ceiling, OOD and interpretation

Run unit tests and a fixed 900-step external-reference sanity run (seed11, retained as its matrix run) before the remaining matrix. If it cannot reach .50 exact averaged over N4/N6, stop and diagnose, without tuning. If all six final cells average <.40, stop; if all >.98, report ceiling/insufficient discrimination and document a later complexity amendment rather than silently replacing the main data. No main task changes in this version.

OOD evaluation after ID is stable: final exact >= .50 and no >.10 drop from mid on >=6/8 seeds for the cell. Evaluate eligible cells only at N8/10/12 without retraining; ineligible cells get explicit not-tested status. No gate based on comparative OOD results.

Primary classification precedence:

1. A-COMPAT-6 Unresolved if floor/ceiling, serious implementation/capacity confounds, or fewer than three functional cells / fewer than two functional R or O families prevents an interpretable compatibility claim.
2. A-COMPAT-1 Strong interaction if p<.05, mean-D range >=.05, same direction of the largest contrast in >=6/8 seeds, and corresponding cells meet mechanistic gates.
3. A-COMPAT-2 Weak/moderate if interaction is significant but smaller, or material differences are seed/checkpoint-unstable.
4. Without material interaction (mean-D range <.05 and p>=.05), A-COMPAT-4 if representation mean range >=.05 and readout main difference <.05; A-COMPAT-5 for reverse; A-COMPAT-3 if both small and functional gates hold. Other patterns: A-COMPAT-6.

Absence of a detected interaction is not proof of equivalence; broad interchangeability is bounded by eight seeds, scalar sorting and these fixed adapters. Equal param counts do not equal optimization difficulty.

Experiment B remains unstarted. READY FOR EXPERIMENT B requires >=3 functional cells, >=2 representation families, both readouts functional, and no dominant optimization/parameter confound. Otherwise NOT READY FOR EXPERIMENT B. No history, coordination overlays, control variation, hybrid or biological inference is authorized here.

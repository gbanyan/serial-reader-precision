# A.3 checkpoint comparability audit

Before geometry analysis, 2026-09-29. No matched reruns required.

| Pair | Sources/code | Representation | Status and estimand |
| --- | --- | --- | --- |
| Priority C vs genuine S | A C (`7811085` implementation, completed A `135141f`); A.1 S (`8c1dfe3`) | identical raw[0]−raw[1]; same two-output head; positive affine-invariant extrema normalization | VALID for readout-package-induced geometry; Scan adds endpoint-to-center adapter and fixed rejection alternative as part of its reader/loss |
| Position C vs genuine S | A C; A.1 S, same revisions | identical sigmoid(raw[0]−raw[1]) | VALID for readout-package-induced geometry; Scan's rejection denominator differs intentionally |
| Phase C vs genuine S | A.1 C and A.1 S (`8c1dfe3`) | identical raw 2-vector normalized by sqrt(norm²+1e−8) | VALID; cosine Competitive vs chord-distance slot Scan |
| Original A C vs A S, all families | original A | matched within A | PARTIALLY VALID historical comparison only: nominal Scan often bypassed cursor; phase optimization unstable. Excluded from primary genuine-reader comparison |
| Original A Phase vs A.1 Phase | atan2/wrapped angle vs normalized S1 | changed forward code and readout geometry | INVALID as an isolated readout contrast; do not pool |

All primary pairs share hidden96, two SetLayers, four heads, FF192, head100→96→2, total164162 (backbone154272/head9890/adapter0); AdamW .001, weight decay .01, clip1, batch32, 900steps, alternating N4/N6, same scalar-key generator and independent item presentation. Same Torch2.8.0 CPU, NumPy2.3.3, deterministic algorithms, two threads and shared seed initialization. Models have no dropout; evaluation does not consume the explicit training-data generator. A uses global Python/NumPy seed calls in addition to Torch; sampling actually uses the same explicitly seeded NumPy Generator as A.1. Both consume hard used-item masks after actual emission; Scan's NO_MATCH consumes no item, the intended reader-specific abstention semantics.

Primary seeds11/22/33/44; checkpoints300/600/900; 1024 trials/load. A's additional seeds are not selectively pooled. Verify ids/numeric/target identity on all primary panels, and replay saved predictions. A's nonphase competitive score/gradients are unchanged by A.1's impossible-null column, as covered by A.1 equivalence tests; no missing counterpart is manufactured by training again.

Paths: `runs/experiment_A/{priority,position}_competitive/<seed>/checkpoint_<step>.pt` and corresponding eval arrays; `runs/experiment_A1/calibration/{priority_scan,position_scan,phase_scan,phase_competitive}/<seed>/...`. Optimizer/source/config metadata remain beside checkpoints. A3 reads arrays, not weights. Paired learned OOD is unavailable; no new OOD evaluation.

VALID does not mean same differentiable objective independent of readout: the readout includes score geometry, normalization, rejection and its CE likelihood. The causal treatment is this frozen readout package, not a separately isolated cognitive operation. Poor Scan competence limits any claim that both readers converged to equally successful solutions.

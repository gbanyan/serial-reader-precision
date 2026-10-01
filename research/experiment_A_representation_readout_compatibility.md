# Experiment A: representation × readout compatibility

Status: ACTIVE specification, written before Experiment A training on 2026-09-29. This stage is explicitly authorized by the new user request; the consolidation's no-experiment gate is revised for this experiment only. Earlier evidence and hypotheses are unchanged. See [preregistration](experiment_A_preregistered_hypotheses.md).

## Estimand and scope

Does the effect of competitive versus cursor readout depend on the learned order-code parameterization? Control is a hard used-item mask in every cell. No binding, synchronization, history, reset, interruption, control comparison or hybrid is included. R/O identifiers below are local to Experiment A, not the literature taxonomy IDs.

## Common task and architecture

Unique atomic identities are sampled without replacement from 32 symbols, independently of continuous scalar keys sampled uniformly on [0,1]. Sort ascending keys. Input presentation is independently randomized; there is no presentation-position embedding. Scalar cues are raw task information, not target ranks or internal-code supervision. Scalar order may favor monotone mappings; it is shared but not claimed representation-neutral in every mathematical sense. Generality beyond scalar sorting remains open.

Train alternating batches at N=4 and N=6, equal exposure. Evaluate those separately; OOD N=8,10,12 receives no training. Every system receives the identical item identities, scalar keys, and set size, and the same paired data stream per seed.

The existing later baseline's active path is reused: 96 hidden units, two `SetLayer`s, four heads, FF width 192, no dropout; symbol/type embeddings and ten-channel numeric projection. Only scalar numeric channel is populated. A shared-shape head is Linear(100,96), GELU, Linear(96,2), receiving hidden content plus four numeric features. Factorial features are [N/10,0,0,0]; the reference also uses step/N, its square, and used-item flag. Unused legacy relation/query/key modules are omitted in the isolated experimental version. Original modules are untouched. The external reference is a **distributed set encoder with learned step-conditioned scorer**, not a full autoregressive Transformer decoder. Its logits are raw[0]-raw[1].

## Factorial code bottleneck

All six cells share head shape and initialization. Both raw outputs participate in each code. Readout cannot access hidden content, identities, keys, targets, or raw head outputs after code construction.

| R | Learned code | Fixed coordinate adapter c |
| --- | --- | --- |
| Priority | p=raw[0]-raw[1], unbounded | (max(p)-p)/(max(p)-min(p)); constant codes map to 0 |
| Position | u=sigmoid(raw[0]-raw[1]), bounded, noncircular | u; equivalently start/end (u,1-u) |
| Phase | phi=atan2(raw[1],raw[0]) | wrap(phi-anchor)/(2π), anchor initially 0 |

Priority normalization is an affine-invariant scale reference inferred from the set, not a supplied rank. It introduces endpoint coupling and nondifferentiable extrema. Position has fixed [0,1] endpoints. Phase has an explicit onset reference and wrap discontinuity; a circle alone does not specify a first item. These are documented structural asymmetries. Priority and position remain related scalar codes under monotone reparameterization; this experiment tests boundedness, normalization and geometry with specified readers, not fundamentally disjoint representational capacities.

## Readouts and fixed control

Both readers have zero learned adapter parameters and the same fixed logit scale 16. This prevents a universal MLP decoder from bypassing the code. O1: score=-16c, argmax among unused items. O2: cursor q_t=(t+0.5)/N, score=-16 d(c,q_t)^2; d is linear distance for priority/position and shortest circular distance in turns for phase. All use the same slot clock, squared-distance rule, and mask. Circular distance replaces linear distance only where geometry requires it. This is an isolated matched version of the validated phase-slot idea, not the exact legacy cosine kernel. Score scales match, but gradient/curvature and feasible coordinates do not; capacity equality cannot remove this optimization asymmetry.

Teacher-forced cross-entropy masks prior target items during training; evaluation consumes actual emitted items. Fixed N outputs guarantee no omitted/duplicate/invalid identities; zero error rates for those measures are structural, not learned achievements. Ordering remains learned. Content routing simply emits the selected original identity.

## Execution and provenance

Eight seeds 11,22,33,44,55,66,77,88; 900 steps; batch 32; AdamW lr .001, weight decay .01, gradient clip 1; identical initialization for shared components, deterministic CPU operations and two torch threads. Save checkpoints at 300/600/900, optimizer/RNG/provenance/config and training curves. Evaluate 1,024 paired held-out trials per ID condition at each checkpoint; independent 256-trial probe-fit set. Final interventions use a paired 256-trial panel. OOD has 1,024 per length if the ID gate passes.

Execution uses the pinned CPU image `oscillation-pbos-deps:20260928` on `gbminipc`, task directory `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a-20260929/`. Each task-owned container has 2 CPUs, 2 GiB RAM, 512 PIDs, log rotation 10m × 3, no ports. Local durable outputs: `results/experiment_A_*.csv`, plots under `results/experiment_A/`; raw checkpoints/trials under ignored `runs/experiment_A/`. Source hashes and Git revision accompany runs. No old benchmark is rerun.

The prior-art boundary remains [novelty_boundary.md](novelty_boundary.md). Cross-pair success is functional compatibility, not a novelty claim or evidence about brains.

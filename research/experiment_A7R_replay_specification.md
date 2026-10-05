# Experiment A.7R — evaluation-only capture-width replay (prospectively specified 2026-10-04)

Authorization: user approval on 2026-10-04 ("OK, go") after a methodological critique noted that the A.7 width arms changed the training objective as well as the reader, because the NO_MATCH logit (−16w², or its chord equivalent) is part of the training softmax. This file is committed and pushed before any replay is computed.

## Question

With the learned codes and the training objective both held fixed, does moving only the reader's acceptance boundary flip Scan outcomes as the displacement account predicts?

## Design

* Codes: saved A.5 B-b1 evaluation arrays at update 36,000, N=6 (standard width 0.45/N, β=1, trained at N∈{4,6}), eight seeds, 1,024 fixed episodes each; no network execution or retraining.
* Reader: the A.1 Scan rule re-implemented in NumPy with float32 arithmetic (scalar: squared distance of the saved Scan-adapted coordinate to q_t; circular: literal chord distance of the saved normalized vector to the cursor vector), NO_MATCH first in the argmax so exact boundary ties reject, used items masked, lowest index wins other ties. Only the capture width w/N changes, in the NO_MATCH score and therefore the acceptance boundary.
* Widths: 0.25, 0.30, 0.35, 0.45, 0.55, 0.60, 0.65, 0.75 (/N). Hypotheses use 0.30, 0.45 and 0.75; the others are a descriptive sweep.

## Gate

R0: at w=0.45/N the replay reproduces every saved prediction exactly (8 seeds × 3 families × 1,024 episodes). Failure stops analysis.

## Hypotheses (mean over eight seeds)

* **R1 scalar widening.** At 0.75/N, Priority and Position exact accuracy each ≥ 50% and ≥ 40 points above the 0.45/N replay, with ≥ 7/8 seeds higher.
* **R2 circular narrowing.** At 0.30/N, circular exact accuracy ≥ 20 points below the 0.45/N replay, with ≥ 7/8 seeds lower.
* **R3 scalar narrowing.** At 0.30/N, scalar exact accuracy < 5%.

## Interpretation

Supported R1–R3: acceptance of the same learned codes is decided by where the boundary lies relative to their displacement, with code and objective fixed. This complements, and does not replace, the trained A.7 width arms, which show that training with another width (and its NO_MATCH logit) still produces about the same displacement in 1/N units. Replay is deterministic; seeds are the replicate unit. Results are reported whatever their direction.

## Execution

Local NumPy script `experiment_a7/replay_width.py`; outputs in `results/experiment_A7R/`.

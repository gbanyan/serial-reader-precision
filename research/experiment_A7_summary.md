# Experiment A.7 — matched-length control, capture-width crossover and encoder generality: results (2026-10-04)

Specification: [experiment_A7_preregistered_hypotheses.md](experiment_A7_preregistered_hypotheses.md), committed locally (9ed59d7) and pushed to the private remote before training. Implementation commit `6626631`, followed by a test-only expectation correction; hashes in `experiment_A7_source.json`, verified per run. G0a/G0b unit tests passed in the pinned image before training (20/20). 144/144 runs completed on gbminipc (seven task containers, 2 CPUs/2 GiB/512 PIDs, no network), all exit code 0, no nonfinite losses. Raw runs: ignored `runs/experiment_A7/` (local and `/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a7-20261004/`, 5.4 GB). Tables: [results/experiment_A7/](../results/experiment_A7/README.md). The local two-hour wait loop timed out once and was restarted; remote runs were unaffected.

**Classification: G0a, G0b, G0c PASS; M1, M2, W1, W2, W3, E1, E2 all SUPPORTED.**

## Results (N=6, eight seeds, mean exact [seed range]; interior offset in units of the arm's w and of 1/N)

| Arm | Priority | Position | Circular | Scalar interior offset |
|---|---:|---:|---:|---|
| M6-b2 (train N=6 only, β=2, 36k) | 83.5% [66.6, 91.6] | 91.2% [87.9, 95.0] | 91.9% | 0.64w / 0.65w |
| M6-b1 (train N=6 only, β=1, 36k) | 0.6% | 0.0% | 91.1% | 1.10w / 1.12w |
| W30-b1 (w=0.30/N, β=1, 36k) | 0.0% | 0.0% | 23.4% [1.1, 60.8] | 0.46/N / 0.49/N |
| W75-b1 (w=0.75/N, β=1, 36k) | 86.8% [79.1, 90.1] | 91.3% [90.2, 92.5] | 94.5% | 0.52/N / 0.53/N |
| A.5 B-b1 comparator (w=0.45/N, β=1, 36k) | 3.8% | 0.0% | 88.4% | 0.47/N / 0.50/N |
| E-b1 (192-d, 4 blocks, β=1, 14.4k) | 0.1% | 3.4% | 51.0% [0.6, 89.7] | 1.11w / 1.05w |
| E-D (192-d, 4 blocks, distractors removed, 14.4k) | 51.2% [9.0, 73.6] | 92.6% [90.7, 94.4] | 88.9% | −0.01w / 0.05w |

* **M1/M2.** Under single-length training at N=6, β=2 succeeded (83.5%, 91.2%; offsets 0.64w, 0.65w) and β=1 failed (0.6%, 0.0%; offsets 1.10w, 1.12w). Together with A.6 N8-b2L (4.6%, 0.0%), the β=2 contrast between N=6 and N=8 holds with single-length training at both lengths.
* **W1 offset invariance.** Learned β=1 scalar displacement in units of 1/N was 0.464 and 0.494 at w=0.30/N, 0.470 and 0.500 at 0.45/N, and 0.524 and 0.535 at 0.75/N (Priority, Position): within 1.2% at 0.30 and 7–12% at 0.75 of the standard-width value. The objective, not the window, set the displacement.
* **W2 scalar flip.** At w=0.75/N the original β=1 objective reached 86.8% and 91.3% (+83.1 points [78.9, 86.6] and +91.2 points [90.7, 91.9] over the standard width; 8/8 seeds each).
* **W3 circular flip.** At w=0.30/N circular accuracy fell from 88.4% to 23.4% (8/8 seeds below the standard-width mean), and scalar accuracy was 0%.
* **E1/E2.** With a 7.5-fold larger encoder (1,235,714 parameters), β=1 left scalar Scan at 0.1% and 3.4% with offsets 1.11w and 1.05w; removing distractors at β=1 gave offsets −0.01w and 0.05w and 51.2% and 92.6% (+51.1 points [34.6, 65.9] and +89.2 points [81.8, 93.4], 8/8 seeds). Priority was still at 51.2% at 14,400 updates (the small model's distractor-removed Priority was 71.9% at the same budget).

## Interpretation (per the specified rules)

M1 removes the training-mix confound in the A.6 length contrast. W1 shows that the learned displacement is set by the objective: it stayed near 0.5/N while the capture window changed 2.5-fold, so the window position alone decided success. Because wider windows also make noisy codes generally easier to read, W2/W3 alone would not be specific; together with W1 and the opposite-direction flips (scalar codes rescued by widening, circular codes broken by narrowing), the pattern matches the displacement account. E1/E2 show the same displacement and the same distractor-removal rescue with a larger encoder. A–A.6 records are unchanged; Experiment B, the repaired full factorial and Dynamic Routing remain closed.

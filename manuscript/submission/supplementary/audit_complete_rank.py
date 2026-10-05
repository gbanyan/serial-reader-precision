"""A03: strict representation rank among complete-but-incorrect saved Scan outputs; no model, reader or experimental rerun."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript/submission"


def strict_rank(coordinate, target, circular):
    ordered = np.take_along_axis(coordinate, target, 1)
    if circular:
        ordered = ordered % 1.0
    return np.all(np.diff(ordered, axis=1) > 0, axis=1)


def main():
    rows = []
    for representation in ("priority", "position", "phase"):
        for seed in (11, 22, 33, 44):
            source = ROOT / f"runs/experiment_A1/calibration/{representation}_scan/{seed}/eval_900_6.npz"
            with np.load(source, allow_pickle=False) as saved:
                target, prediction, coordinate = saved["target"], saved["prediction"], saved["coordinate"]
            failed = np.any(prediction != target, axis=1)
            complete_wrong = failed & ~np.any(prediction == -1, axis=1)
            preserved = strict_rank(coordinate, target, representation == "phase")
            rows.append(dict(representation=representation, readout="scan", seed=seed, n=6, step=900,
                             episodes=len(target), strict_rank_preserved=int(preserved.sum()),
                             wrong_complete=int(complete_wrong.sum()),
                             wrong_complete_rank_preserved=int((complete_wrong & preserved).sum()),
                             failed_rank_preserved=int((failed & preserved).sum()),
                             source=str(source.relative_to(ROOT)),
                             source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    output = OUT / "complete_wrong_rank_audit.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    provenance = dict(operation="Later deterministic arithmetic on saved Scan coordinates and predictions; no model or reader call",
                      status="Descriptive provenance audit (A03), added after external review; not preregistered",
                      rank_definition="strictly increasing Scan coordinate in target order; circular angle in turns cut at 0; no tolerance",
                      numpy_version=np.__version__, source_files=len(rows),
                      script="manuscript/tools/audit_complete_rank.py",
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      output=str(output.relative_to(ROOT)),
                      output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    (OUT / "complete_wrong_rank_audit_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    for rep in ("priority", "position", "phase"):
        print(rep, {k: sum(r[k] for r in rows if r["representation"] == rep)
                    for k in ("strict_rank_preserved", "wrong_complete", "wrong_complete_rank_preserved", "failed_rank_preserved")})


if __name__ == "__main__":
    main()

"""Tabulate existing saved predictions; no model, reader or experimental rerun."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript/submission"


def main():
    rows = []
    for representation in ("priority", "position", "phase"):
        for seed in (11, 22, 33, 44):
            source = ROOT / f"runs/experiment_A1/calibration/{representation}_scan/{seed}/eval_900_6.npz"
            with np.load(source, allow_pickle=False) as saved:
                target, prediction = saved["target"], saved["prediction"]
                assert target.shape == prediction.shape == (1024, 6)
                assert np.all(target >= 0)
                failed = np.any(prediction != target, axis=1)
                no_match = np.any(prediction == -1, axis=1)
                assert np.all(~no_match | failed)
                complete_wrong = failed & ~no_match
                assert int(failed.sum()) == int(no_match.sum() + complete_wrong.sum())
            rows.append(dict(representation=representation, readout="scan", seed=seed,
                             n=6, step=900, episodes=len(failed), failed=int(failed.sum()),
                             with_no_match=int(no_match.sum()), wrong_complete=int(complete_wrong.sum()),
                             source=str(source.relative_to(ROOT)),
                             source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    output = OUT / "saved_scan_failure_audit.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    provenance = dict(operation="Later deterministic arithmetic on saved predictions; no model or reader call",
                      status="Descriptive provenance audit, not a new experiment or preregistered analysis",
                      numpy_version=np.__version__, source_files=len(rows),
                      script="manuscript/tools/audit_saved_scan_failures.py",
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      output=str(output.relative_to(ROOT)),
                      output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    (OUT / "saved_scan_failure_audit_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({rep: [sum(r[k] for r in rows if r["representation"] == rep)
                            for k in ("failed", "with_no_match", "wrong_complete")]
                      for rep in ("priority", "position", "phase")}))


if __name__ == "__main__":
    main()

"""Reproduce an existing descriptive diagnostic from saved codes; no models/readers."""
from pathlib import Path
import csv
import hashlib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "manuscript/submission/native_branch_audit.csv"


def main():
    rows = []
    for n in (4, 6):
        for seed in (11, 22, 33, 44):
            source = ROOT / f"runs/experiment_A1/calibration/phase_competitive/{seed}/eval_900_{n}.npz"
            with np.load(source, allow_pickle=False) as saved:
                code = saved["code"]
                assert code.ndim == 3 and code.shape[1:] == (n, 2)
                angles = np.mod(np.arctan2(code[..., 1], code[..., 0]), 2 * np.pi)
                # Wrapped theta=0 branches [0, pi] and [pi, 2*pi); no added tolerance.
                contained = np.all(angles <= np.pi, axis=1) | np.all(angles >= np.pi, axis=1)
                rows.append(dict(
                    representation="phase", readout="competitive", seed=seed, n=n,
                    step=900, episodes=len(contained), contained=int(contained.sum()),
                    fraction=float(contained.mean()), code_dtype=str(code.dtype),
                    numpy_version=np.__version__, source=str(source.relative_to(ROOT)),
                    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                ))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {OUTPUT.relative_to(ROOT)}; saved-array geometry only.")


if __name__ == "__main__":
    main()

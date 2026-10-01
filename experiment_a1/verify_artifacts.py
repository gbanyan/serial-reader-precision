"""Read-only raw-evidence audit; writes only new A.1 verification manifests."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, manifest):
    for name, record in manifest.items():
        path = root / name
        assert path.stat().st_size == record['bytes'], path
        assert digest(path) == record['sha256'], path
    return len(manifest)


def main():
    root = Path('runs/experiment_A1')
    out = Path('results/experiment_A1')
    source = json.loads(Path('experiment_A1_source.json').read_text())
    for name, sha in source['sha256'].items():
        assert digest(Path(name)) == sha, name
    old = json.loads(Path('results/experiment_A/artifact_manifest.json').read_text())
    old_count = verify(Path('runs/experiment_A'), old['raw_artifacts'])
    raw = json.loads((root / 'remote_manifest.json').read_text())
    new_count = verify(root, raw)
    protected = ['experiment_a', 'results/experiment_A',
                 'research/experiment_A_representation_readout_compatibility.md',
                 'research/experiment_A_preregistered_hypotheses.md',
                 'research/experiment_A_summary.md']
    protected += [str(p) for p in Path('results').glob('experiment_A_*.csv')]
    diff = subprocess.check_output(['git', 'diff', source['original_A_commit'], '--', *protected])
    assert not diff, 'Original A tracked evidence changed'
    rows = list(csv.DictReader((out / 'checkpoint_metrics.csv').open()))
    matched_inputs = 0
    for row in rows:
        system, seed, step, n = (row[k] for k in ['system', 'seed', 'step', 'n'])
        a = np.load(root / 'calibration' / system / seed / f'eval_{step}_{n}.npz')
        pred, target = a['prediction'], a['target']
        exact = np.mean(np.all(pred == target, axis=1))
        correct = covered = 0
        for p, t in zip(pred.tolist(), target.tolist()):
            positions = {item: p.index(item) for item in t if p.count(item) == 1}
            for i in range(len(t)):
                for j in range(i + 1, len(t)):
                    if t[i] in positions and t[j] in positions:
                        covered += 1
                        correct += positions[t[i]] < positions[t[j]]
        denominator = len(pred) * int(n) * (int(n)-1) / 2
        assert abs(exact - float(row['exact_accuracy'])) < 1e-12
        assert abs(correct / denominator - float(row['pairwise_accuracy'])) < 1e-12
        assert abs(covered / denominator - float(row['pair_coverage'])) < 1e-12
        if int(step) in (300, 600, 900):
            previous = np.load(Path('runs/experiment_A') / system / seed / f'eval_{step}_{n}.npz')
            for key in ('ids', 'numeric', 'target'):
                assert np.array_equal(a[key], previous[key]), (system, seed, step, key)
            matched_inputs += 1
    runs = len(list((root / 'calibration').glob('*/*/complete.json')))
    checkpoints = len(list((root / 'calibration').glob('*/*/checkpoint_*.pt')))
    assert (runs, checkpoints, len(rows)) == (16, 48, 288)
    assert not Path('results/experiment_A1_main_factorial.csv').exists()
    assert not Path('results/experiment_A1_ood_length.csv').exists()
    record = dict(status='PASS', original_A_commit=source['original_A_commit'],
                  original_raw_hashes_verified=old_count, remote_local_hashes_verified=new_count,
                  frozen_source_hashes_verified=len(source['sha256']),
                  original_tracked_evidence_unchanged=True, calibration_runs=runs,
                  checkpoints=checkpoints, independently_checked_metric_panels=len(rows),
                  original_task_input_panels_identical=matched_inputs,
                  remote_tests={'command': 'python -m pytest -q tests/test_experiment_a1.py',
                                'passed': 14, 'container': 'oscillation-expa1-final-tests', 'exit_code': 0},
                  factorial_run=False, ood_run=False)
    (out / 'verification.json').write_text(json.dumps(record, indent=2) + '\n')
    manifest = dict(source_commit=source['git_commit'],
                    original_A_commit=source['original_A_commit'],
                    remote_root='/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a1-20260929/runs/experiment_A1',
                    raw_artifacts=raw)
    (out / 'artifact_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

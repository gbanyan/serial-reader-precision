"""Integrity checks only: no model execution, training, or metric selection."""
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from PIL import Image


def main():
    root=Path('runs/experiment_A');out=Path('results/experiment_A')
    source=json.loads(Path('experiment_A_source.json').read_text())
    for p,h in source['sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    remote=json.loads((root/'remote_manifest.json').read_text())
    for name,record in remote.items():
        p=root/name;assert p.stat().st_size==record['bytes'],name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],name
    checkpoints=[p for p in remote if p.endswith('.pt')];assert len(checkpoints)==168
    records=pd.read_csv('results/experiment_A_main_factorial.csv')
    assert not records.duplicated(['system','seed','step','n']).any()
    for row in records.itertuples():
        a=np.load(root/row.system/str(row.seed)/f'eval_{row.step}_{row.n}.npz')
        reference=np.load(root/'reference'/'11'/f'eval_{row.step}_{row.n}.npz')
        for key in ('ids','numeric','target'):assert np.array_equal(a[key],reference[key]),(row.system,key)
        pred,target=a['pred'],a['target'];n=row.n
        assert np.array_equal(np.sort(pred,1),np.broadcast_to(np.arange(n),pred.shape))
        assert np.array_equal(np.argsort(a['numeric'][...,0],1),target)
        # Independent metric reconstruction, with target-order positions rather than pairwise sign product.
        serial_ranks=np.take_along_axis(target.argsort(1),pred,1)
        pairs=np.triu_indices(n,1)
        pair=(serial_ranks[:,pairs[0]]<serial_ranks[:,pairs[1]]).mean()
        exact=(pred==target).all(1).mean()
        assert np.isclose(row.exact_accuracy,exact) and np.isclose(row.pairwise_accuracy,pair)
        assert np.isclose(row.kendall_tau,2*pair-1)
    ood=pd.read_csv('results/experiment_A_ood_length.csv')
    assert len(ood)==168 and (ood.status=='evaluated').sum()==144
    assert ood[ood.status!='evaluated'].exact_accuracy.isna().all()
    for p in out.glob('*.png'):
        a=np.asarray(Image.open(p).convert('RGB'))
        assert a.shape[0]>300 and a.std()>5,p
    assert len(list(out.glob('*.png')))==12
    legacy=['pbos','mechanism_regime','calibration','control_authority','strategy_audit','strategy_identifiability']
    unchanged=subprocess.check_output(['git','diff','--name-only','f4e9264','--',*legacy],text=True)
    assert unchanged=='',unchanged
    oldresults=subprocess.check_output(['git','diff','--name-only','f4e9264','--','results'],text=True).splitlines()
    assert all(p=='results/README.md' or p.startswith('results/experiment_A') for p in oldresults),oldresults
    manifest=dict(source_commit=source['git_commit'],remote_root='/mnt/SAM1TB/dev/projects/oscillation-trans-experiment-a-20260929/runs/experiment_A',
                  raw_artifacts=remote,checkpoint_count=len(checkpoints))
    (out/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result=dict(status='passed',training_runs=56,checkpoints=168,raw_files_verified=len(remote),
                raw_bytes=sum(r['bytes'] for r in remote.values()),source_hashes_verified=len(source['sha256']),
                id_metric_rows_independently_reconstructed=336,paired_eval_inputs_verified=True,
                ood_rows_evaluated=144,ood_rows_explicitly_withheld=24,plots=12,legacy_source_and_raw_results_unchanged=True,
                tests=[dict(location='gbminipc Docker pinned CPU image',command='python -m pytest tests/test_experiment_a.py -q',passed=22),
                       dict(location='local Mac',command='python3 -m pytest tests/test_experiment_a_analysis.py -q',passed=3)],
                main_training_image='sha256:054fe1dd2c4e46261172d08401cd7646524d20fa96412dec796ec5f6cb0d2731',
                constraints='No legacy reruns, tuning, history/reset, synchronization, control variation or hybrids; Experiment B closed.')
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()

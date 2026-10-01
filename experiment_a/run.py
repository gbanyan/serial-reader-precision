"""Fixed-budget runner. Refuses to overwrite runs; no optimization search."""
import argparse
import hashlib
import json
import platform
import random
import time
from pathlib import Path
import numpy as np
import torch
from .data import batch, VERSION
from .model import FactorialModel, SYSTEMS
from .evaluate import panel, interventions

SEEDS = [11,22,33,44,55,66,77,88]
ROOT = Path('runs/experiment_A')


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def train(system, seed):
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.manual_seed(seed); np.random.seed(seed); random.seed(seed)
    model = FactorialModel(system)
    dest = ROOT/system/str(seed); dest.mkdir(parents=True, exist_ok=False)
    provenance = json.loads(Path('experiment_A_source.json').read_text())
    for name, digest in provenance['sha256'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
    cfg = dict(system=system, seed=seed, steps=900, checkpoints=[300,600,900], train_loads=[4,6], batch_size=32,
               lr=.001, weight_decay=.01, grad_clip=1, hidden=96, layers=2, heads=4,
               generator=VERSION, counts=model.counts(), torch=torch.__version__, numpy=np.__version__, python=platform.python_version())
    write(dest/'config.json', cfg); write(dest/'provenance.json', provenance)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.01)
    rng = np.random.default_rng(seed); curves=[]; rows=[]; diagnostics=[]; started=time.monotonic()
    for step in range(1,901):
        model.train(); x=batch(rng,32,4 if step%2 else 6)
        out=model(x,teacher=True); loss=torch.nn.functional.cross_entropy(out['logits'].flatten(0,1),x['target'].flatten())
        if not torch.isfinite(loss): raise RuntimeError('STOP nonfinite loss')
        optimizer.zero_grad(set_to_none=True); loss.backward()
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True); optimizer.step()
        if step%20 == 0:
            curves.append(dict(step=step,loss=float(loss.detach()),gradient_norm=float(norm),seconds=time.monotonic()-started))
            write(dest/'curves.json',curves)
        if step in (300,600,900):
            torch.save(dict(model=model.state_dict(),optimizer=optimizer.state_dict(),step=step,
                            torch_rng=torch.get_rng_state(),numpy_rng=rng.bit_generator.state),dest/f'checkpoint_{step}.pt')
            for n in (4,6):
                score, diag, arrays=panel(model,seed,n)
                rows.append(dict(system=system,seed=seed,step=step,n=n,**score))
                diagnostics.extend(dict(system=system,seed=seed,step=step,n=n,**r) for r in diag)
                np.savez_compressed(dest/f'eval_{step}_{n}.npz',**arrays)
            write(dest/'metrics.json',rows);write(dest/'diagnostics.json',diagnostics)
            print(system,seed,step,[(r['n'],round(r['exact_accuracy'],4)) for r in rows[-2:]],flush=True)
    if system!='reference':
        allcausal=[];allinv=[]
        for n in (4,6):
            causal, inv, raw=interventions(model,n)
            allcausal.extend(dict(system=system,seed=seed,n=n,**r) for r in causal)
            allinv.extend(dict(system=system,seed=seed,n=n,**r) for r in inv)
            np.savez_compressed(dest/f'interventions_{n}.npz',**raw)
        write(dest/'interventions.json',allcausal);write(dest/'invariance.json',allinv)
    write(dest/'complete.json',dict(seconds=time.monotonic()-started))


def ood():
    torch.set_num_threads(2)
    for system in SYSTEMS:
        eligible=0
        for seed in SEEDS:
            rows=json.loads((ROOT/system/str(seed)/'metrics.json').read_text())
            final=np.mean([r['exact_accuracy'] for r in rows if r['step']==900])
            mid=np.mean([r['exact_accuracy'] for r in rows if r['step']==600])
            eligible+=int(final>=.50 and final-mid>=-.10)
        for seed in SEEDS:
            dest=ROOT/system/str(seed); rows=[]
            if (dest/'ood.json').exists(): raise RuntimeError('OOD already exists')
            model=FactorialModel(system); model.load_state_dict(torch.load(dest/'checkpoint_900.pt',weights_only=False)['model'])
            for n in (8,10,12):
                if eligible>=6:
                    score,diag,arrays=panel(model,seed,n)
                    np.savez_compressed(dest/f'ood_{n}.npz',**arrays)
                    rows.append(dict(system=system,seed=seed,n=n,status='evaluated',**score))
                else: rows.append(dict(system=system,seed=seed,n=n,status='ID_gate_failed'))
            write(dest/'ood.json',rows)
        print('ood',system,'eligible seeds',eligible,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--system',choices=SYSTEMS);p.add_argument('--seed',type=int);p.add_argument('--worker',type=int);p.add_argument('--ood',action='store_true');args=p.parse_args()
    if args.ood: ood()
    elif args.system: train(args.system,args.seed)
    else:
        jobs=[(s,k) for s in SYSTEMS for k in SEEDS if (s,k)!=('reference',11)]
        for i,(s,k) in enumerate(jobs):
            if i%3==args.worker: train(s,k)

import argparse
import hashlib
import json
import platform
from pathlib import Path
import time
import numpy as np
import torch
from experiment_a.data import batch,VERSION
from .model import RepairedModel,CELLS
from .evaluate import panel,causal

ROOT=Path('runs/experiment_A1/calibration');SEEDS=[11,22,33,44]


def write(p,data):p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def train(system,seed):
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    path=ROOT/system/str(seed);path.mkdir(parents=True,exist_ok=False)
    source=json.loads(Path('experiment_A1_source.json').read_text())
    for p,h in source['sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    model=RepairedModel(system);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01);rng=np.random.default_rng(seed)
    write(path/'config.json',dict(system=system,seed=seed,steps=900,lr=.001,weight_decay=.01,batch=32,clip=1,train_loads=[4,6],
                                 counts=model.counts(),slot_radius='.45/N',phase_epsilon=1e-8,generator=VERSION,
                                 torch=torch.__version__,numpy=np.__version__,python=platform.python_version()))
    write(path/'source.json',source);curves=[];metrics=[];start=time.monotonic()
    for step in range(1,901):
        model.train();n=4 if step%2 else 6;x=batch(rng,32,n);out=model(x,teacher=True)
        loss=torch.nn.functional.cross_entropy(out['logits'].flatten(0,1),(x['target']+1).flatten())
        if not torch.isfinite(loss):
            write(path/'failure.json',dict(step=step,reason='nonfinite_loss'));raise RuntimeError('STOP nonfinite')
        opt.zero_grad(set_to_none=True);loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);opt.step()
        curves.append(dict(step=step,n=n,loss=loss.item(),gradient_norm=float(norm)))
        if step%100==0:
            write(path/'curves.json',curves)
            for n in (4,6):
                row,raw=panel(model,n);metrics.append(dict(step=step,n=n,**row))
                np.savez_compressed(path/f'eval_{step}_{n}.npz',**raw)
            write(path/'metrics.json',metrics)
            if step in (300,600,900):
                torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),step=step,
                                torch_rng=torch.get_rng_state(),data_rng=rng.bit_generator.state),path/f'checkpoint_{step}.pt')
                print(system,seed,step,[(r['n'],round(r['exact_accuracy'],4)) for r in metrics[-2:]],flush=True)
    causalrows=[];invrows=[]
    for n in (4,6):
        ca,iv,raw=causal(model,n)
        causalrows.extend(dict(n=n,**r) for r in ca);invrows.extend(dict(n=n,**r) for r in iv)
        np.savez_compressed(path/f'causal_{n}.npz',**raw)
    write(path/'causal.json',causalrows);write(path/'invariance.json',invrows)
    write(path/'complete.json',dict(seconds=time.monotonic()-start,nan_inf_events=0))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=int,choices=[0,1],required=True);a=p.parse_args()
    for i,(s,k) in enumerate((s,k) for s in CELLS for k in SEEDS):
        if i%2==a.worker:train(s,k)

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import time
import numpy as np
import torch
from experiment_a.data import batch,VERSION
from experiment_a1.model import RepairedModel
from experiment_a1.evaluate import panel

ROOT=Path('runs/experiment_A4');SEEDS=[11,22,33,44,55,66,77,88]
SCAN=['priority_scan','position_scan','phase_scan']
COMP=['priority_competitive','position_competitive','phase_competitive']
ARMS={'S-b1':(SCAN,'ce',1.,900),'S-b4':(SCAN,'ce',4.,900),'S-b16':(SCAN,'ce',16.,900),
      'L-b1':(SCAN,'ce',1.,3600),'L-b16':(SCAN,'ce',16.,3600),'R':(SCAN,'reg',None,900),'C':(COMP,'ce',1.,900)}
EVAL_N=(4,6,8)


def jobs():
    return [(a,s,k) for a,(cells,_,_,_) in ARMS.items() for s in cells for k in SEEDS]


def write(p,data):p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def regression_loss(model,out,target):
    """Squared distance of each item's reader coordinate to its target slot reference, in capture-boundary units."""
    n=target.shape[1];rank=target.argsort(1).float();q=(rank+.5)/n;c=out['coordinate']
    if model.rep=='phase':
        ref=torch.stack((torch.cos(2*math.pi*q),torch.sin(2*math.pi*q)),-1)
        d2=(c-ref).square().sum(-1)/(4*math.pi**2);bound=(math.sin(math.pi*.45/n)/math.pi)**2
    else:d2=(c-q).square();bound=(.45/n)**2
    return (d2/bound).mean()


def objective(model,x,kind,beta):
    out=model(x,teacher=True)
    if kind=='reg':return regression_loss(model,out,x['target'])
    logits=out['logits'] if beta==1. else beta*out['logits']
    return torch.nn.functional.cross_entropy(logits.flatten(0,1),(x['target']+1).flatten())


def train(arm,system,seed):
    _,kind,beta,steps=ARMS[arm]
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    path=ROOT/arm/system/str(seed);path.mkdir(parents=True,exist_ok=False)
    source=json.loads(Path('experiment_A4_source.json').read_text())
    for p,h in source['sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    model=RepairedModel(system);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01);rng=np.random.default_rng(seed)
    write(path/'config.json',dict(arm=arm,system=system,seed=seed,objective=kind,beta=beta,steps=steps,lr=.001,weight_decay=.01,
                                 batch=32,clip=1,train_loads=[4,6],eval_loads=list(EVAL_N),counts=model.counts(),slot_radius='.45/N',
                                 generator=VERSION,torch=torch.__version__,numpy=np.__version__,python=platform.python_version()))
    write(path/'source.json',source);curves=[];metrics=[];start=time.monotonic()
    for step in range(1,steps+1):
        model.train();n=4 if step%2 else 6;x=batch(rng,32,n)
        loss=objective(model,x,kind,beta)
        if not torch.isfinite(loss):
            write(path/'failure.json',dict(step=step,reason='nonfinite_loss'));raise RuntimeError('STOP nonfinite')
        opt.zero_grad(set_to_none=True);loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);opt.step()
        curves.append(dict(step=step,n=n,loss=loss.item(),gradient_norm=float(norm)))
        if step%300==0:
            write(path/'curves.json',curves)
            for n in EVAL_N:
                row,raw=panel(model,n);metrics.append(dict(step=step,n=n,**row))
                np.savez_compressed(path/f'eval_{step}_{n}.npz',**raw)
            write(path/'metrics.json',metrics)
            torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),step=step,
                            torch_rng=torch.get_rng_state(),data_rng=rng.bit_generator.state),path/f'checkpoint_{step}.pt')
            print(arm,system,seed,step,[(r['n'],round(r['exact_accuracy'],4)) for r in metrics[-3:]],flush=True)
    write(path/'complete.json',dict(seconds=time.monotonic()-start,nan_inf_events=0))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=int,required=True);p.add_argument('--workers',type=int,required=True)
    p.add_argument('--arm',action='append');a=p.parse_args()
    todo=[j for j in jobs() if a.arm is None or j[0] in a.arm]
    for i,(arm,s,k) in enumerate(todo):
        if i%a.workers==a.worker and not (ROOT/arm/s/str(k)/'complete.json').exists():train(arm,s,k)

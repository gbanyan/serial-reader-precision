import argparse
import hashlib
import json
import platform
from pathlib import Path
import time
import numpy as np
import torch
from experiment_a.data import batch,VERSION
from experiment_a1.model import RepairedModel
from experiment_a1.evaluate import panel
from experiment_a4.run import objective as a4_objective

ROOT=Path('runs/experiment_A6');SEEDS=[11,22,33,44,55,66,77,88]
SCAN=['priority_scan','position_scan','phase_scan']
EVALS=(900,1800,3600,7200,14400,28800,36000)
ARMS={'X46-b2':((4,6),'ce',2.,(4,6,8)),'N8-b2L':((8,),'ce',2.,(6,8)),'N8-b4L':((8,),'ce',4.,(6,8)),
      'N8-b16L':((8,),'ce',16.,(6,8)),'D':((4,6),'target_only',1.,(4,6,8)),'RL':((4,6),'reg',None,(4,6,8))}


def jobs():return [(a,s,k) for a in ARMS for s in SCAN for k in SEEDS]


def write(p,data):p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def target_only_loss(model,x):
    """CE at beta=1 over NO_MATCH and the target only: later unused items are removed from each step's softmax."""
    out=model(x,teacher=True);logits=out['logits'];cls=(x['target']+1)
    keep=torch.zeros_like(logits,dtype=torch.bool);keep[...,0]=True;keep.scatter_(2,cls.unsqueeze(-1),True)
    logits=logits.masked_fill(~keep,-1e9)
    return torch.nn.functional.cross_entropy(logits.flatten(0,1),cls.flatten())


def objective(model,x,kind,beta):
    return target_only_loss(model,x) if kind=='target_only' else a4_objective(model,x,kind,beta)


def train(arm,system,seed):
    loads,kind,beta,eval_n=ARMS[arm];steps=EVALS[-1]
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    path=ROOT/arm/system/str(seed);path.mkdir(parents=True,exist_ok=False)
    source=json.loads(Path('experiment_A6_source.json').read_text())
    for p,h in source['sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    model=RepairedModel(system);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01);rng=np.random.default_rng(seed)
    write(path/'config.json',dict(arm=arm,system=system,seed=seed,objective=kind,beta=beta,steps=steps,lr=.001,weight_decay=.01,
                                 batch=32,clip=1,train_loads=list(loads),eval_steps=list(EVALS),eval_loads=list(eval_n),
                                 counts=model.counts(),slot_radius='.45/N',generator=VERSION,
                                 torch=torch.__version__,numpy=np.__version__,python=platform.python_version()))
    write(path/'source.json',source);curves=[];metrics=[];start=time.monotonic()
    for step in range(1,steps+1):
        model.train();n=(4 if step%2 else 6) if loads==(4,6) else loads[0];x=batch(rng,32,n)
        loss=objective(model,x,kind,beta)
        if not torch.isfinite(loss):
            write(path/'failure.json',dict(step=step,reason='nonfinite_loss'));raise RuntimeError('STOP nonfinite')
        opt.zero_grad(set_to_none=True);loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);opt.step()
        curves.append(dict(step=step,n=n,loss=loss.item(),gradient_norm=float(norm)))
        if step in EVALS:
            write(path/'curves.json',curves)
            for n in eval_n:
                row,raw=panel(model,n);metrics.append(dict(step=step,n=n,**row))
                np.savez_compressed(path/f'eval_{step}_{n}.npz',**raw)
            write(path/'metrics.json',metrics)
            torch.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),step=step,
                            torch_rng=torch.get_rng_state(),data_rng=rng.bit_generator.state),path/f'checkpoint_{step}.pt')
            print(arm,system,seed,step,[(r['n'],round(r['exact_accuracy'],4)) for r in metrics[-len(eval_n):]],flush=True)
    write(path/'complete.json',dict(seconds=time.monotonic()-start,nan_inf_events=0))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=int,required=True);p.add_argument('--workers',type=int,required=True)
    a=p.parse_args()
    for i,(arm,s,k) in enumerate(jobs()):
        if i%a.workers==a.worker and not (ROOT/arm/s/str(k)/'complete.json').exists():train(arm,s,k)

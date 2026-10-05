import argparse
import hashlib
import json
import platform
from pathlib import Path
import time
import numpy as np
import torch
from experiment_a.data import batch,VERSION
from experiment_a1.evaluate import panel
from experiment_a6.run import objective
from experiment_a7.model import WidthModel,EncoderModel

ROOT=Path('runs/experiment_A7');SEEDS=[11,22,33,44,55,66,77,88]
SCAN=['priority_scan','position_scan','phase_scan']
LONG=(900,1800,3600,7200,14400,28800,36000);SHORT=(900,1800,3600,7200,14400)
# arm: (training loads, objective kind, beta, capture width, encoder (d, layers), evaluation steps)
ARMS={'M6-b2':((6,),'ce',2.,.45,(96,2),LONG),'M6-b1':((6,),'ce',1.,.45,(96,2),LONG),
      'W30-b1':((4,6),'ce',1.,.30,(96,2),LONG),'W75-b1':((4,6),'ce',1.,.75,(96,2),LONG),
      'E-b1':((4,6),'ce',1.,.45,(192,4),SHORT),'E-D':((4,6),'target_only',1.,.45,(192,4),SHORT)}
EVAL_N=(4,6,8)


def jobs():
    # Larger-encoder runs first: they are the slowest.
    order=['E-b1','E-D','M6-b2','M6-b1','W30-b1','W75-b1']
    return [(a,s,k) for a in order for s in SCAN for k in SEEDS]


def build(arm,system):
    _,_,_,width,(d,layers),_=ARMS[arm]
    if (d,layers)!=(96,2):return EncoderModel(system,d,layers)
    return WidthModel(system,width)


def write(p,data):p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def train(arm,system,seed):
    loads,kind,beta,width,(d,layers),evals=ARMS[arm];steps=evals[-1]
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    path=ROOT/arm/system/str(seed);path.mkdir(parents=True,exist_ok=False)
    source=json.loads(Path('experiment_A7_source.json').read_text())
    for p,h in source['sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    model=build(arm,system);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01);rng=np.random.default_rng(seed)
    write(path/'config.json',dict(arm=arm,system=system,seed=seed,objective=kind,beta=beta,capture_width=f'{width}/N',encoder=dict(d=d,layers=layers),
                                 steps=steps,lr=.001,weight_decay=.01,batch=32,clip=1,train_loads=list(loads),eval_steps=list(evals),
                                 eval_loads=list(EVAL_N),counts=model.counts(),generator=VERSION,
                                 torch=torch.__version__,numpy=np.__version__,python=platform.python_version()))
    write(path/'source.json',source);curves=[];metrics=[];start=time.monotonic()
    for step in range(1,steps+1):
        model.train();n=(4 if step%2 else 6) if loads==(4,6) else loads[0];x=batch(rng,32,n)
        loss=objective(model,x,kind,beta)
        if not torch.isfinite(loss):
            write(path/'failure.json',dict(step=step,reason='nonfinite_loss'));raise RuntimeError('STOP nonfinite')
        opt.zero_grad(set_to_none=True);loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);opt.step()
        curves.append(dict(step=step,n=n,loss=loss.item(),gradient_norm=float(norm)))
        if step in evals:
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
    a=p.parse_args()
    for i,(arm,s,k) in enumerate(jobs()):
        if i%a.workers==a.worker and not (ROOT/arm/s/str(k)/'complete.json').exists():train(arm,s,k)

"""Replay old final checkpoints into new diagnostics only; no training or writes to A."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from experiment_a.model import FactorialModel
from experiment_a.data import batch
from .metrics import changes


@torch.no_grad()
def main(root,dest):
    torch.set_num_threads(2);dest.mkdir(parents=True,exist_ok=False);rows=[]
    for rep in ('priority','position','phase'):
        for seed in (11,22,33,44,55,66,77,88):
            system=rep+'_scan';model=FactorialModel(system).eval()
            checkpoint=root/system/str(seed)/'checkpoint_900.pt'
            model.load_state_dict(torch.load(checkpoint,weights_only=False)['model'])
            for n in (4,6):
                x=batch(np.random.default_rng(810000+n),1024,n);out=model(x)
                normal=out['prediction'].numpy();c=out['coordinate'];target=x['target'].numpy()
                saved=np.load(root/system/str(seed)/f'eval_900_{n}.npz')['pred']
                assert np.array_equal(normal,saved),(system,seed,n,'checkpoint replay mismatch')
                schedules=dict(normal=list(range(n)),freeze=[0]*n,shift=list(range(1,n))+[0],permutation=[n-1]+list(range(n-1)))
                raw=dict(base=normal,target=target,coordinate=c.numpy())
                for label,schedule in schedules.items():
                    used=torch.zeros_like(c,dtype=torch.bool);pred=[]
                    for slot in schedule:
                        d=c-(slot+.5)/n
                        if rep=='phase':d=(d+.5).remainder(1)-.5
                        k=(-16*d.square()).masked_fill(used,-1e9).argmax(1)
                        pred.append(k);used=used.scatter(1,k[:,None],True)
                    p=torch.stack(pred,1).numpy();raw[label]=p
                    if label=='normal':assert np.array_equal(p,normal)
                    rows.append(dict(system=system,seed=seed,n=n,intervention=label,
                                     checkpoint=str(checkpoint),**changes(p,normal,target,normal[:,schedule])))
                np.savez_compressed(dest/f'{system}_{seed}_{n}.npz',**raw)
    (dest/'metrics.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    print('Verified 24 final checkpoints, 48 paired panels, 192 old-scan rows',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--dest',type=Path,default=Path('runs/experiment_A1/old_scan'));a=p.parse_args();main(a.root,a.dest)

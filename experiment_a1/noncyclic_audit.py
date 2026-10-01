"""Post-calibration assay-coverage check; cannot change preregistered gate decisions."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
from .metrics import changes


def decode(code,rep,n,schedule):
    if rep=='priority':
        span=np.maximum(np.ptp(code,axis=1,keepdims=True),1e-7)
        c=.5/n+(1-1/n)*(code.max(1,keepdims=True)-code)/span
    else:c=code
    used=np.zeros((len(code),n),bool);pred=[];r=.45/n
    for slot in schedule:
        q=(slot+.5)/n
        if rep=='phase':
            cursor=np.array([math.cos(2*math.pi*q),math.sin(2*math.pi*q)],np.float32)
            d2=((c-cursor)**2).sum(-1)/(4*math.pi**2);boundary=(math.sin(math.pi*r)/math.pi)**2
        else:d2=(c-q)**2;boundary=r*r
        scores=np.where(used,-1e9,-16*d2)
        k=np.concatenate([np.full((len(c),1),-16*boundary,np.float32),scores],1).argmax(1)-1
        pred.append(k);valid=k>=0;used[np.arange(len(c))[valid],k[valid]]=True
    return np.stack(pred,1)


def main():
    rows=[]
    for p in Path('runs/experiment_A1/calibration').glob('*_scan/*/causal_*.npz'):
        a=np.load(p);system=p.parents[1].name;rep=system.split('_')[0];seed=int(p.parent.name);n=a['base'].shape[1]
        normal=decode(a['code'],rep,n,list(range(n)))
        assert np.array_equal(normal,a['base']),(p,'normal replay mismatch')
        schedule=[2,0,3,1] if n==4 else [2,0,4,1,5,3]
        pred=decode(a['code'],rep,n,schedule)
        rows.append(dict(system=system,seed=seed,n=n,schedule=str(schedule),
                         status='POST_CALIBRATION_NOT_USED_TO_CHANGE_GATES',
                         transformed_target_accuracy=float((pred==a['target'][:,schedule]).all(1).mean()),
                         **changes(pred,a['base'],a['target'],a['base'][:,schedule])))
    df=pd.DataFrame(rows);df.to_csv('results/experiment_A1/noncyclic_cursor_audit.csv',index=False)
    print(df.groupby('system')[['transformed_agreement_on_normal_correct','transformed_target_accuracy']].mean().to_string())


if __name__=='__main__':main()

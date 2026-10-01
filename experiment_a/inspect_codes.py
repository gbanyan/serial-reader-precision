"""Post-main descriptive code/readout checks from saved states; no weights changed."""
import json
from pathlib import Path
import numpy as np
import pandas as pd


def decode(c, reader, phase=False, frozen=False):
    b,n=c.shape;used=np.zeros_like(c,bool);pred=[]
    for t in range(n):
        if reader=='competitive':score=-16*c
        else:
            q=(.5 if frozen else t+.5)/n
            d=c-q
            if phase:d=(d+.5)%1-.5
            score=-16*d*d
        k=np.where(used,-1e9,score).argmax(1);pred.append(k);used[np.arange(b),k]=True
    return np.stack(pred,1)


def main():
    rows=[];phase_rows=[]
    for path in Path('runs/experiment_A').glob('*/*/eval_*.npz'):
        system=path.parents[1].name
        if system=='reference':continue
        _,step,n=path.stem.split('_');step,n=int(step),int(n)
        seed=int(path.parent.name);a=np.load(path); c=a['coordinate'];pred=a['pred'];rep,reader=system.split('_')
        replay=decode(c,reader,rep=='phase')
        assert np.array_equal(pred,replay),(path,'saved-state replay mismatch')
        frozen=decode(c,'scan',rep=='phase',True)
        ranking=np.argsort(c,axis=1)
        targetrank=np.argsort(a['target'],axis=1)
        ideal=(targetrank+.5)/n
        error=c-ideal
        if rep=='phase':error=(error+.5)%1-.5
        rows.append(dict(system=system,seed=seed,step=step,n=n,coordinate_min=c.min(1).mean(),
                         coordinate_max=c.max(1).mean(),coordinate_span=np.ptp(c,axis=1).mean(),
                         ideal_slot_rmse=np.sqrt(np.mean(error**2)),
                         monotone_sort_agreement=np.mean(np.all(pred==ranking,axis=1)),
                         frozen_cursor_agreement=np.mean(np.all(pred==frozen,axis=1)) if reader=='scan' else None,
                         boundary_fraction=np.mean((c<.02)|(c>.98))))
        if rep=='phase':
            i,j=np.triu_indices(n,1);y=(targetrank[:,i]<targetrank[:,j]).astype(float)
            # Secondary two-fold trial-grouped linear decoder of unanchored pair differences.
            for layer in range(3):
                phi=a[f'code_{layer}'];delta=phi[:,j]-phi[:,i]
                x=np.stack((np.ones_like(delta),np.sin(delta),np.cos(delta)),axis=-1)
                predictions=np.zeros_like(y)
                for parity in (0,1):
                    test=np.arange(len(x))%2==parity;train=~test
                    z=x[train].reshape(-1,3).astype(np.float64);labels=y[train].ravel()
                    assert np.isfinite(z).all()
                    w=np.linalg.solve(np.einsum('ni,nj->ij',z,z)+1e-3*np.eye(3),np.einsum('ni,n->i',z,labels))
                    assert np.isfinite(w).all()
                    predictions[test]=np.einsum('bni,i->bn',x[test],w)>=.5
                phase_rows.append(dict(system=system,seed=seed,step=step,n=n,layer=layer,
                                       unanchored_delta_pairwise_accuracy=np.mean(predictions==y),
                                       analysis='secondary_post_main_trial_grouped_twofold_ridge'))
    out=Path('results/experiment_A')
    pd.DataFrame(rows).to_csv(out/'readout_geometry.csv',index=False)
    pd.DataFrame(phase_rows).to_csv(out/'unanchored_phase_decoding.csv',index=False)
    print(pd.DataFrame(rows).query('step==900').groupby('system').mean(numeric_only=True).round(4).to_string())


if __name__=='__main__':main()

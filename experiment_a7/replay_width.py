"""A.7R: read saved A.5 B-b1 codes with a different Scan capture width; NumPy only, no model or training."""
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

SRC=Path('runs/experiment_A5/B-b1');OUT=Path('results/experiment_A7R')
SEEDS=[11,22,33,44,55,66,77,88];FAMS=['priority','position','phase'];WIDTHS=[.25,.30,.35,.45,.55,.60,.65,.75];N=6;STEP=36000


def scan(raw,fam,width):
    """A.1 Scan rule in float32: NO_MATCH first in argmax (boundary ties reject), used items masked, lowest index wins."""
    b,n=raw['target'].shape;rows=np.arange(b);used=np.zeros((b,n),bool);pred=np.empty((b,n),np.int64);radius=width/n
    for t in range(n):
        q=(t+.5)/n
        if fam=='phase':
            z=raw['code'];cursor=np.array([math.cos(2*math.pi*q),math.sin(2*math.pi*q)],np.float32)
            d2=np.square(z-cursor).sum(-1)/np.float32(4*math.pi**2);boundary=(math.sin(math.pi*radius)/math.pi)**2
        else:
            d2=np.square(raw['coordinate']-np.float32(q));boundary=radius**2
        s=(np.float32(-16)*d2).astype(np.float32);s[used]=np.float32(-1e9)
        s=np.concatenate([np.full((b,1),np.float32(-16*boundary),np.float32),s],1)
        k=s.argmax(1)-1;pred[:,t]=k;valid=k>=0;used[rows[valid],k[valid]]=True
    return pred


def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[];gate=dict(checked=0,mismatched_episodes=0);sources={}
    for fam in FAMS:
        for seed in SEEDS:
            p=SRC/f'{fam}_scan'/str(seed)/f'eval_{STEP}_{N}.npz';sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
            raw=dict(np.load(p))
            for width in WIDTHS:
                pred=scan(raw,fam,width)
                if width==.45:
                    gate['checked']+=len(pred);gate['mismatched_episodes']+=int((pred!=raw['prediction']).any(1).sum())
                exact=float((pred==raw['target']).all(1).mean());nomatch=float((pred==-1).mean())
                rows.append(dict(family=fam,seed=seed,width=width,exact=exact,no_match_rate=nomatch))
    gate['passed']=gate['mismatched_episodes']==0
    with open(OUT/'replay_seed_metrics.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    def g(fam,width):return np.array([r['exact'] for r in rows if r['family']==fam and r['width']==width])
    with open(OUT/'replay_summary.csv','w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['family','width','seeds','exact_mean','exact_min','exact_max'])
        for fam in FAMS:
            for width in WIDTHS:
                v=g(fam,width);w.writerow([fam,width,len(v),f'{v.mean():.6f}',f'{v.min():.6f}',f'{v.max():.6f}'])
    h={'R0_gate':gate}
    for fam in ('priority','position'):
        d=g(fam,.75)-g(fam,.45)
        h[f'R1_{fam}']=dict(w45=float(g(fam,.45).mean()),w75=float(g(fam,.75).mean()),diff=float(d.mean()),seeds_higher=int((d>0).sum()),
                            supported=bool(g(fam,.75).mean()>=.5 and d.mean()>=.4 and (d>0).sum()>=7))
        h[f'R3_{fam}']=dict(w30=float(g(fam,.30).mean()),supported=bool(g(fam,.30).mean()<.05))
    d=g('phase',.45)-g('phase',.30)
    h['R2_circular']=dict(w45=float(g('phase',.45).mean()),w30=float(g('phase',.30).mean()),drop=float(d.mean()),seeds_lower=int((d>0).sum()),
                          supported=bool(d.mean()>=.2 and (d>0).sum()>=7))
    h['R1']=h['R1_priority']['supported'] and h['R1_position']['supported'];h['R3']=h['R3_priority']['supported'] and h['R3_position']['supported'];h['R2']=h['R2_circular']['supported']
    h['provenance']=dict(script='experiment_a7/replay_width.py',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                         numpy=np.__version__,sources=sources,models_executed=False)
    (OUT/'hypotheses.json').write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps({k:v for k,v in h.items() if k!='provenance'},indent=1))
    for fam in FAMS:print(fam,' '.join(f'{w}:{100*g(fam,w).mean():.1f}' for w in WIDTHS))


if __name__=='__main__':main()

"""Summarize A.7 saved evaluations and test the prospectively specified hypotheses; NumPy only, no model execution."""
import csv
import json
from pathlib import Path
import numpy as np
from experiment_a5.report import interior,boot

ROOT=Path('runs/experiment_A7');A5=Path('runs/experiment_A5');A6=Path('runs/experiment_A6');OUT=Path('results/experiment_A7')
SEEDS=[11,22,33,44,55,66,77,88];SCAN=['priority_scan','position_scan','phase_scan'];SCALAR=SCAN[:2]
ARMS={'M6-b2':.45,'M6-b1':.45,'W30-b1':.30,'W75-b1':.75,'E-b1':.45,'E-D':.45}


def offsets(raw,system,n,width):
    """Median signed offset per target rank, in units of the arm's own capture radius width/N."""
    q=(np.arange(n)+.5)/n;w=width/n;c=np.take_along_axis(raw['coordinate'],raw['target'],1)
    d=((c-q+.5)%1-.5) if system.startswith('phase') else c-q
    return np.median(d/w,0)


def rows():
    out=[]
    for arm,width in ARMS.items():
        for s in SCAN:
            for k in SEEDS:
                p=ROOT/arm/s/str(k)
                for m in json.loads((p/'metrics.json').read_text()):
                    n,st=m['n'],m['step'];off=offsets(np.load(p/f'eval_{st}_{n}.npz'),s,n,width);io=float(off[interior(s,n)].mean())
                    out.append(dict(arm=arm,system=s,seed=k,n=n,step=st,width=width,exact=m['exact_accuracy'],pairwise=m['pairwise_accuracy'],
                                    no_match=m['no_match_rate'],interior_offset=io,interior_offset_per_N=io*width,offsets=' '.join(f'{v:.3f}' for v in off)))
    return out


def get(R,arm,s,n=6,st=36000,key='exact'):
    v={r['seed']:r[key] for r in R if (r['arm'],r['system'],r['n'],r['step'])==(arm,s,n,st)};return np.array([v[k] for k in SEEDS])


def saved(root,arm,s,n,st,key):
    """Seed values from an earlier experiment's metrics, or interior offset in 1/N units at width .45."""
    out=[]
    for k in SEEDS:
        p=root/arm/s/str(k)
        if key=='exact':out.append([m['exact_accuracy'] for m in json.loads((p/'metrics.json').read_text()) if m['n']==n and m['step']==st][0])
        else:
            raw=np.load(p/f'eval_{st}_{n}.npz');q=(np.arange(n)+.5)/n;c=np.take_along_axis(raw['coordinate'],raw['target'],1)
            d=((c-q+.5)%1-.5) if s.startswith('phase') else c-q
            out.append(float(np.median(d*n,0)[interior(s,n)].mean()))
    return np.array(out)


def hypotheses(R):
    h={}
    for s in SCALAR:
        e,o=get(R,'M6-b2',s),get(R,'M6-b2',s,key='interior_offset')
        h[f'M1_{s}']=dict(exact=float(e.mean()),offset=float(o.mean()),supported=bool(e.mean()>=.70 and o.mean()<.9))
        e,o=get(R,'M6-b1',s),get(R,'M6-b1',s,key='interior_offset')
        h[f'M2_{s}']=dict(exact=float(e.mean()),offset=float(o.mean()),supported=bool(e.mean()<.15 and o.mean()>.8))
        base=saved(A5,'B-b1',s,6,36000,'offset_per_N');w30=get(R,'W30-b1',s,key='interior_offset_per_N');w75=get(R,'W75-b1',s,key='interior_offset_per_N')
        rel=[float(abs(x.mean()-base.mean())/abs(base.mean())) for x in (w30,w75)]
        h[f'W1_{s}']=dict(B_b1_per_N=float(base.mean()),W30_per_N=float(w30.mean()),W75_per_N=float(w75.mean()),relative_differences=rel,supported=bool(max(rel)<.25))
        b1=saved(A5,'B-b1',s,6,36000,'exact');w=get(R,'W75-b1',s);d=w-b1
        h[f'W2_{s}']=dict(W75=float(w.mean()),B_b1=float(b1.mean()),diff=float(d.mean()),ci=boot(d),seeds_positive=int((d>0).sum()),
                          supported=bool(w.mean()>=.50 and d.mean()>=.40 and (d>0).sum()>=7))
        h[f'W3_scalar_{s}']=dict(W30=float(get(R,'W30-b1',s).mean()),supported=bool(get(R,'W30-b1',s).mean()<.05))
        e1,o1=get(R,'E-b1',s,st=14400),get(R,'E-b1',s,st=14400,key='interior_offset')
        h[f'E1_{s}']=dict(exact=float(e1.mean()),offset=float(o1.mean()),supported=bool(o1.mean()>.8 and e1.mean()<.15))
        ed,od=get(R,'E-D',s,st=14400),get(R,'E-D',s,st=14400,key='interior_offset');d=ed-e1
        h[f'E2_{s}']=dict(exact=float(ed.mean()),offset=float(od.mean()),diff=float(d.mean()),ci=boot(d),seeds_positive=int((d>0).sum()),
                          supported=bool(abs(od.mean())<.3 and d.mean()>=.40 and (d>0).sum()>=7))
    pb1=saved(A5,'B-b1','phase_scan',6,36000,'exact');pw=get(R,'W30-b1','phase_scan')
    h['W3_circular']=dict(W30=float(pw.mean()),B_b1=float(pb1.mean()),drop=float(pb1.mean()-pw.mean()),seeds_below_B_mean=int((pw<pb1.mean()).sum()),
                          supported=bool(pb1.mean()-pw.mean()>=.20 and (pw<pb1.mean()).sum()>=7))
    for k in ('M1','M2','W1','W2','E1','E2'):h[k]=all(h[f'{k}_{s}']['supported'] for s in SCALAR)
    h['W3']=bool(h['W3_circular']['supported'] and all(h[f'W3_scalar_{s}']['supported'] for s in SCALAR))
    return h


def main():
    OUT.mkdir(parents=True,exist_ok=True);R=rows()
    assert len({(r['arm'],r['system'],r['seed']) for r in R})==144
    with open(OUT/'seed_metrics.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(R[0]),lineterminator='\n');w.writeheader();w.writerows(R)
    agg={}
    for r in R:agg.setdefault((r['arm'],r['system'],r['n'],r['step']),[]).append(r)
    with open(OUT/'summary.csv','w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['arm','system','n','step','seeds','width','exact_mean','exact_min','exact_max','no_match_mean','interior_offset_mean','interior_offset_per_N_mean'])
        for (a,s,n,st),v in sorted(agg.items()):
            e=[x['exact'] for x in v];w.writerow([a,s,n,st,len(v),v[0]['width'],f'{np.mean(e):.6f}',f'{min(e):.6f}',f'{max(e):.6f}',f'{np.mean([x["no_match"] for x in v]):.6f}',
                                                f'{np.mean([x["interior_offset"] for x in v]):.4f}',f'{np.mean([x["interior_offset_per_N"] for x in v]):.4f}'])
    h=hypotheses(R);(OUT/'hypotheses.json').write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(h,indent=1))


if __name__=='__main__':main()

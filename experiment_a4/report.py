"""Summarize A.4 saved evaluations; no model execution."""
import csv
import json
from pathlib import Path
import numpy as np
from experiment_a4.run import ARMS,SEEDS,ROOT

OUT=Path('results/experiment_A4')


def interior(system,n):
    return range(1,n-1) if system.startswith('priority') else range(1,n)


def offsets(raw,system,n):
    """Median signed offset from each target rank's slot centre, in units of w=.45/N (Scan-adapted coordinates)."""
    q=(np.arange(n)+.5)/n;w=.45/n;c=np.take_along_axis(raw['coordinate'],raw['target'],1)
    if system.startswith('phase'):
        if system.endswith('competitive'):return None
        d=(c-q+.5)%1-.5
    else:d=c-q
    return np.median(d/w,0)


def competitive_transfer(raw,system):
    """Exact accuracy of the frozen Competitive reader on the same saved code (scalar: oriented score; circular: 8(z1-1))."""
    code=raw['code'];t=raw['target']
    score=code[...,0] if system.startswith('phase') else (code if system.startswith('priority') else -code)
    if code.ndim==3 and not system.startswith('phase'):score=score[...,0]
    order=np.argsort(-score,1,kind='stable')
    return float((order==t).all(1).mean())


def rows():
    out=[]
    for arm,(cells,kind,beta,steps) in ARMS.items():
        for system in cells:
            for seed in SEEDS:
                path=ROOT/arm/system/str(seed)
                if not (path/'complete.json').exists():continue
                for m in json.loads((path/'metrics.json').read_text()):
                    n,step=m['n'],m['step'];r=dict(arm=arm,system=system,seed=seed,objective=kind,beta=beta,n=n,step=step,
                                                   exact=m['exact_accuracy'],pairwise=m['pairwise_accuracy'],no_match=m['no_match_rate'])
                    raw=np.load(path/f'eval_{step}_{n}.npz');off=offsets(raw,system,n)
                    if off is not None:
                        r['interior_offset']=float(np.mean([off[i] for i in interior(system,n)]))
                        r['offsets']=' '.join(f'{v:.3f}' for v in off)
                    if system.endswith('scan'):r['competitive_transfer_exact']=competitive_transfer(raw,system)
                    out.append(r)
    return out


def boot(d,rng=np.random.default_rng(0)):
    d=np.asarray(d);m=d[rng.integers(0,len(d),(10000,len(d)))].mean(1);return [float(np.quantile(m,.025)),float(np.quantile(m,.975))]


def get(R,arm,system,n,step,key='exact'):
    v={r['seed']:r[key] for r in R if (r['arm'],r['system'],r['n'],r['step'])==(arm,system,n,step)}
    return np.array([v[s] for s in SEEDS])


def hypotheses(R):
    h={}
    for fam in ('priority','position'):
        s=fam+'_scan';b1,b4,b16=(get(R,a,s,6,900) for a in ('S-b1','S-b4','S-b16'));d=b16-b1
        h[f'H1_{fam}']=dict(means=[float(b1.mean()),float(b4.mean()),float(b16.mean())],diff=float(d.mean()),ci=boot(d),
                           seeds_positive=int((d>0).sum()),
                           supported=bool(b1.mean()<b4.mean()<b16.mean() and d.mean()>=.30 and (d>0).sum()>=7))
        o1,o16=get(R,'S-b1',s,6,900,'interior_offset'),get(R,'S-b16',s,6,900,'interior_offset')
        h[f'H2_{fam}']=dict(offset_b1=float(o1.mean()),offset_b16=float(o16.mean()),supported=bool(o1.mean()>.8 and o16.mean()<.3))
        l1=get(R,'L-b1',s,6,3600);ol=get(R,'L-b1',s,6,3600,'interior_offset')
        h[f'H3_{fam}']=dict(L_b1_3600=float(l1.mean()),S_b16_900=float(b16.mean()),L_b1_offset=float(ol.mean()),
                           supported=bool(l1.mean()<b16.mean() and ol.mean()>.8))
    for k in ('H1','H2','H3'):h[k]=bool(h[f'{k}_priority']['supported'] and h[f'{k}_position']['supported'])
    return h


def main():
    OUT.mkdir(parents=True,exist_ok=True);R=rows()
    keys=['arm','system','seed','objective','beta','n','step','exact','pairwise','no_match','interior_offset','competitive_transfer_exact','offsets']
    with open(OUT/'seed_metrics.csv','w',newline='') as f:
        w=csv.DictWriter(f,keys);w.writeheader();[w.writerow(r) for r in R]
    agg={}
    for r in R:agg.setdefault((r['arm'],r['system'],r['n'],r['step']),[]).append(r)
    with open(OUT/'summary.csv','w',newline='') as f:
        w=csv.writer(f);w.writerow(['arm','system','n','step','seeds','exact_mean','exact_min','exact_max','no_match_mean','interior_offset_mean','competitive_transfer_mean'])
        for (a,s,n,st),v in sorted(agg.items()):
            e=[x['exact'] for x in v];o=[x['interior_offset'] for x in v if 'interior_offset' in x];t=[x['competitive_transfer_exact'] for x in v if 'competitive_transfer_exact' in x]
            w.writerow([a,s,n,st,len(v),f'{np.mean(e):.6f}',f'{min(e):.6f}',f'{max(e):.6f}',f'{np.mean([x["no_match"] for x in v]):.6f}',
                        f'{np.mean(o):.4f}' if o else '',f'{np.mean(t):.6f}' if t else ''])
    h=hypotheses(R);(OUT/'hypotheses.json').write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(h,indent=1))


if __name__=='__main__':main()

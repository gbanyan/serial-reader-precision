"""Summarize A.5 saved evaluations and test preregistered hypotheses; NumPy only, no model execution."""
import csv
import json
from pathlib import Path
import numpy as np

ROOT=Path('runs/experiment_A5');A4=Path('runs/experiment_A4');OUT=Path('results/experiment_A5')
SEEDS=[11,22,33,44,55,66,77,88];SCAN=['priority_scan','position_scan','phase_scan']
ARMS={'B-b1':(900,1800,3600,7200,14400,28800,36000),'B-b16':(900,1800,3600,7200,14400,28800,36000),
      'N8-b1':(900,1800,3600),'N8-b16':(900,1800,3600)}
ANALYTIC_N8_B1={'priority_scan':[0,1.118,1.651,1.784,1.798,1.760,1.728,0],'position_scan':[0,1.119,1.654,1.792,1.825,1.824,1.836,1.109],
                'phase_scan':[0,.416,.802,1.021,1.089,.991,.741,.548]}


def interior(system,n):return list(range(1,n-1)) if system.startswith('priority') else list(range(1,n))


def offsets(raw,system,n):
    q=(np.arange(n)+.5)/n;w=.45/n;c=np.take_along_axis(raw['coordinate'],raw['target'],1)
    d=((c-q+.5)%1-.5) if system.startswith('phase') else c-q
    return np.median(d/w,0)


def gate():
    bad=[];checked=0
    for arm,a4 in (('B-b1','L-b1'),('B-b16','L-b16')):
        for s in SCAN:
            for k in SEEDS:
                for st in (900,1800,3600):
                    for n in (4,6,8):
                        x=np.load(ROOT/arm/s/str(k)/f'eval_{st}_{n}.npz');y=np.load(A4/a4/s/str(k)/f'eval_{st}_{n}.npz');checked+=1
                        if not all(np.array_equal(x[f],y[f]) for f in ('prediction','code','target')):bad.append((arm,s,k,st,n))
    return dict(checked=checked,mismatches=len(bad),examples=bad[:5],passed=not bad)


def rows():
    out=[]
    for arm,steps in ARMS.items():
        for s in SCAN:
            for k in SEEDS:
                p=ROOT/arm/s/str(k)
                for m in json.loads((p/'metrics.json').read_text()):
                    n,st=m['n'],m['step'];off=offsets(np.load(p/f'eval_{st}_{n}.npz'),s,n)
                    out.append(dict(arm=arm,system=s,seed=k,n=n,step=st,exact=m['exact_accuracy'],pairwise=m['pairwise_accuracy'],
                                    no_match=m['no_match_rate'],interior_offset=float(off[interior(s,n)].mean()),offsets=' '.join(f'{v:.3f}' for v in off)))
    return out


def get(R,arm,s,n,st,key='exact'):
    v={r['seed']:r[key] for r in R if (r['arm'],r['system'],r['n'],r['step'])==(arm,s,n,st)};return np.array([v[k] for k in SEEDS])


def spearman(a,b):
    ra=np.argsort(np.argsort(a));rb=np.argsort(np.argsort(b));return float(np.corrcoef(ra,rb)[0,1])


def boot(d,rng=np.random.default_rng(0)):
    d=np.asarray(d);m=d[rng.integers(0,len(d),(10000,len(d)))].mean(1);return [float(np.quantile(m,.025)),float(np.quantile(m,.975))]


def hypotheses(R):
    h={};a4={'priority_scan':1.0198,'position_scan':1.0734}  # A.4 L-b1 N=6 interior offsets (results/experiment_A4/summary.csv)
    for s in ('priority_scan','position_scan'):
        e1,o1=get(R,'B-b1',s,6,36000),get(R,'B-b1',s,6,36000,'interior_offset');e16=get(R,'B-b16',s,6,36000)
        h[f'B1_{s}']=dict(exact=float(e1.mean()),offset=float(o1.mean()),supported=bool(o1.mean()>.8 and e1.mean()<.15))
        d=e16-e1;h[f'B3_{s}']=dict(diff=float(d.mean()),ci=boot(d),seeds_positive=int((d>0).sum()),supported=bool((d>0).sum()>=7))
        o=get(R,'N8-b1',s,8,3600,'interior_offset')
        h[f'N1_{s}']=dict(offset=float(o.mean()),a4_n6=a4[s],supported=bool(o.mean()>1.2 and o.mean()>a4[s]))
        e=get(R,'N8-b1',s,8,3600);h[f'N4_{s}']=dict(exact=float(e.mean()),supported=bool(e.mean()<.05))
    for s in SCAN:
        e=get(R,'B-b16',s,6,36000);m=get(R,'B-b16',s,6,14400)
        cls='CLOSES' if e.mean()>=.9 else ('PLATEAU' if e.mean()-m.mean()<.03 else 'STILL-RISING')
        h[f'B2_{s}']=dict(exact_14400=float(m.mean()),exact_36000=float(e.mean()),seed_range=[float(e.min()),float(e.max())],classification=cls)
        o=get(R,'N8-b16',s,8,3600,'interior_offset');h[f'N2_{s}']=dict(offset=float(o.mean()),supported=bool(abs(o.mean())<.3))
        prof=np.mean([[float(v) for v in r['offsets'].split()] for r in R if (r['arm'],r['system'],r['n'],r['step'])==('N8-b1',s,8,3600)],0)
        rho=spearman(prof[1:],np.array(ANALYTIC_N8_B1[s])[1:])
        h[f'N3_{s}']=dict(learned_profile=[round(float(v),3) for v in prof],analytic=ANALYTIC_N8_B1[s],spearman=rho,supported=bool(rho>=.6))
    for k in ('B1','B3','N1','N4'):h[k]=all(h[f'{k}_{s}']['supported'] for s in ('priority_scan','position_scan'))
    for k in ('N2','N3'):h[k]=all(h[f'{k}_{s}']['supported'] for s in SCAN)
    return h


def main():
    OUT.mkdir(parents=True,exist_ok=True);g=gate();(OUT/'gate.json').write_text(json.dumps(g,indent=2)+'\n');print('G0',g)
    if not g['passed']:raise SystemExit('G0 failed: stop before analysis')
    R=rows()
    with open(OUT/'seed_metrics.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(R[0]),lineterminator='\n');w.writeheader();w.writerows(R)
    agg={}
    for r in R:agg.setdefault((r['arm'],r['system'],r['n'],r['step']),[]).append(r)
    with open(OUT/'summary.csv','w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['arm','system','n','step','seeds','exact_mean','exact_min','exact_max','no_match_mean','interior_offset_mean'])
        for (a,s,n,st),v in sorted(agg.items(),key=lambda x:(x[0][0],x[0][1],x[0][2],x[0][3])):
            e=[x['exact'] for x in v];w.writerow([a,s,n,st,len(v),f'{np.mean(e):.6f}',f'{min(e):.6f}',f'{max(e):.6f}',
                                                f'{np.mean([x["no_match"] for x in v]):.6f}',f'{np.mean([x["interior_offset"] for x in v]):.4f}'])
    h=hypotheses(R);(OUT/'hypotheses.json').write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(h,indent=1))


if __name__=='__main__':main()

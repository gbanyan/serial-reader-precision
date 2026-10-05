"""Summarize A.6 saved evaluations and test preregistered hypotheses; NumPy only, no model execution."""
import csv
import json
from pathlib import Path
import numpy as np
from experiment_a5.report import offsets,interior,boot

ROOT=Path('runs/experiment_A6');A4=Path('runs/experiment_A4');A5=Path('runs/experiment_A5');OUT=Path('results/experiment_A6')
SEEDS=[11,22,33,44,55,66,77,88];SCAN=['priority_scan','position_scan','phase_scan'];SCALAR=SCAN[:2]
EVALS=(900,1800,3600,7200,14400,28800,36000)
ARMS={'X46-b2':(4,6,8),'N8-b2L':(6,8),'N8-b4L':(6,8),'N8-b16L':(6,8),'D':(4,6,8),'RL':(4,6,8)}


def same(a,b):
    x,y=np.load(a),np.load(b);return all(np.array_equal(x[f],y[f]) for f in ('prediction','code','target'))


def gate():
    bad=[];n=0
    for s in SCAN:
        for k in SEEDS:
            for st in (900,1800,3600):
                for N in (6,8):
                    n+=1
                    if not same(ROOT/'N8-b16L'/s/str(k)/f'eval_{st}_{N}.npz',A5/'N8-b16'/s/str(k)/f'eval_{st}_{N}.npz'):bad.append(('N8-b16L',s,k,st,N))
            for N in (4,6,8):
                n+=1
                if not same(ROOT/'RL'/s/str(k)/f'eval_900_{N}.npz',A4/'R'/s/str(k)/f'eval_900_{N}.npz'):bad.append(('RL',s,k,900,N))
    return dict(checked=n,mismatches=len(bad),examples=bad[:5],passed=not bad)


def rows():
    out=[]
    for arm in ARMS:
        for s in SCAN:
            for k in SEEDS:
                p=ROOT/arm/s/str(k)
                for m in json.loads((p/'metrics.json').read_text()):
                    N,st=m['n'],m['step'];off=offsets(np.load(p/f'eval_{st}_{N}.npz'),s,N)
                    out.append(dict(arm=arm,system=s,seed=k,n=N,step=st,exact=m['exact_accuracy'],pairwise=m['pairwise_accuracy'],
                                    no_match=m['no_match_rate'],interior_offset=float(off[interior(s,N)].mean()),offsets=' '.join(f'{v:.3f}' for v in off)))
    return out


def get(R,arm,s,N,st=36000,key='exact'):
    v={r['seed']:r[key] for r in R if (r['arm'],r['system'],r['n'],r['step'])==(arm,s,N,st)};return np.array([v[k] for k in SEEDS])


def b1(s,N=6):
    return np.array([[m['exact_accuracy'] for m in json.loads((A5/'B-b1'/s/str(k)/'metrics.json').read_text()) if m['n']==N and m['step']==36000][0] for k in SEEDS])


def hypotheses(R):
    h={}
    for s in SCALAR:
        a=get(R,'X46-b2',s,6);b=get(R,'N8-b2L',s,8);bo=get(R,'N8-b2L',s,8,key='interior_offset');c=get(R,'N8-b4L',s,8);d=c-b
        h[f'X1_{s}']=dict(X46_b2_N6=float(a.mean()),N8_b2_N8=float(b.mean()),N8_b2_offset=float(bo.mean()),N8_b4_N8=float(c.mean()),
                          b4_minus_b2=float(d.mean()),ci=boot(d),seeds_positive=int((d>0).sum()),
                          parts=dict(a=bool(a.mean()>=.70),b=bool(b.mean()<.10 and bo.mean()>.9),c=bool(d.mean()>=.30 and (d>0).sum()>=7)))
        h[f'X1_{s}']['supported']=all(h[f'X1_{s}']['parts'].values())
        do=get(R,'D',s,6,key='interior_offset');dd=get(R,'D',s,6)-b1(s)
        h[f'D1_{s}']=dict(offset=float(do.mean()),exact=float(get(R,'D',s,6).mean()),diff_vs_B_b1=float(dd.mean()),ci=boot(dd),
                          seeds_positive=int((dd>0).sum()),supported=bool(abs(do.mean())<.3 and dd.mean()>=.5 and (dd>0).sum()>=7))
        rd=get(R,'RL',s,6)-b1(s);h[f'R1_{s}']=dict(exact=float(get(R,'RL',s,6).mean()),diff_vs_B_b1=float(rd.mean()),supported=bool(rd.mean()>=.5))
    ph=get(R,'N8-b2L','phase_scan',8).mean()
    h['X2']=dict(phase=float(ph),scalar={s:float(get(R,'N8-b2L',s,8).mean()) for s in SCALAR},
                 supported=bool(all(ph-get(R,'N8-b2L',s,8).mean()>=.20 for s in SCALAR)))
    for k in ('X1','D1','R1'):h[k]=all(h[f'{k}_{s}']['supported'] for s in SCALAR)
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
        for (a,s,n,st),v in sorted(agg.items()):
            e=[x['exact'] for x in v];w.writerow([a,s,n,st,len(v),f'{np.mean(e):.6f}',f'{min(e):.6f}',f'{max(e):.6f}',
                                                f'{np.mean([x["no_match"] for x in v]):.6f}',f'{np.mean([x["interior_offset"] for x in v]):.4f}'])
    h=hypotheses(R);(OUT/'hypotheses.json').write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(h,indent=1))


if __name__=='__main__':main()

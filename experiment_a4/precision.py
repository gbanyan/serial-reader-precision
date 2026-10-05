"""Descriptive precision diagnostics on saved A.4 evaluations (no model): within-window rate, strict rank, raw-key similarity."""
import csv
from pathlib import Path
import numpy as np

ROOT=Path('runs/experiment_A4');OUT=Path('results/experiment_A4');SEEDS=[11,22,33,44,55,66,77,88]
CASES=[(a,s,st) for a,st in (('S-b1',900),('S-b4',900),('S-b16',900),('R',900),('L-b1',3600),('L-b16',3600)) for s in ('priority_scan','position_scan','phase_scan')]


def diagnostics(raw,system,n):
    q=(np.arange(n)+.5)/n;w=.45/n;t=raw['target'];c=np.take_along_axis(raw['coordinate'],t,1)
    d=((c-q+.5)%1-.5) if system.startswith('phase') else c-q
    within=np.abs(d)<w;cc=c%1 if system.startswith('phase') else c
    strict=np.all(np.diff(cc,axis=1)>0,1)
    key=np.take_along_axis(raw['numeric'][...,0],t,1)
    if system.startswith('priority'):key=.5/n+(1-1/n)*(key-key[:,:1])/(key[:,-1:]-key[:,:1])
    keydist=np.mean(np.abs(c-key)/w)
    return dict(item_within_window=float(within.mean()),all_within=float(within.all(1).mean()),strict_rank=float(strict.mean()),
                abs_offset_w=float(np.mean(np.abs(d)/w)),rank_preserved_within=float(within.all(1)[strict].mean()) if strict.any() else float('nan'),
                distance_to_raw_key_w=float(keydist))


def main():
    rows=[]
    for arm,system,step in CASES:
        for n in (4,6):
            for seed in SEEDS:
                raw=np.load(ROOT/arm/system/str(seed)/f'eval_{step}_{n}.npz')
                rows.append(dict(arm=arm,system=system,step=step,n=n,seed=seed,**diagnostics(raw,system,n)))
    with open(OUT/'precision_diagnostics.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    for arm,system,step in CASES:
        v=[r for r in rows if (r['arm'],r['system'],r['n'])==(arm,system,6)]
        print(f"{arm:6}{system:15} N6 in-window/item {np.mean([r['item_within_window'] for r in v]):.3f} |off| {np.mean([r['abs_offset_w'] for r in v]):.2f}w strict {np.mean([r['strict_rank'] for r in v]):.3f} dist-to-rawkey {np.mean([r['distance_to_raw_key_w'] for r in v]):.2f}w")


if __name__=='__main__':main()

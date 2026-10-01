import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/oscillation-a3-matplotlib')
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from experiment_a3.analyze import source,scalar

OUT=Path('results/experiment_A3')
def read(name):return pd.read_csv(f'results/experiment_A3_{name}.csv')
def finish(name):plt.tight_layout();plt.savefig(OUT/name,dpi=160);plt.close()
def corr(x,y):return float(spearmanr(x,y).statistic) if np.ptp(x)>0 and np.ptp(y)>0 else np.nan
def main():
    g=read('geometry_summary');t=read('cross_readout_transfer');c=read('counterfactual_geometry');d=read('rank_metric_decomposition');f=g[g.step==900].copy()
    differences=[];rng=np.random.default_rng(7303)
    for rep in ['priority','position','phase']:
        for n in [4,6]:
            a=f[(f.representation==rep)&(f.n==n)].pivot(index='seed',columns='readout')
            for metric in ['canonical_rmse','spacing_cv','dynamic_range','slot_rmse','arc_fraction','score_monotonicity']:
                values=(a[metric]['scan']-a[metric]['competitive']).dropna().to_numpy()
                if not len(values):continue
                boot=values[rng.integers(0,len(values),(10000,len(values)))].mean(1)
                differences.append(dict(representation=rep,n=n,metric=metric,scan_minus_competitive=values.mean(),minimum=values.min(),maximum=values.max(),same_sign=bool((values>0).all()or(values<0).all()),ci_low=np.quantile(boot,.025),ci_high=np.quantile(boot,.975)))
    pd.DataFrame(differences).to_csv(OUT/'paired_geometry_differences.csv',index=False)
    correlations=[];lag=[]
    for key,df in g.groupby(['representation','readout','n']):
        base=dict(zip(['representation','readout','n'],key))
        for metric in ['pairwise_decoding','canonical_rmse','slot_rmse','spacing_cv','dynamic_range','arc_fraction','score_min_margin']:
            z=df.dropna(subset=[metric])
            if not len(z):continue
            for behavior in ['exact_accuracy','pairwise_accuracy','kendall_tau_present']:
                correlations.append(dict(**base,geometry=metric,behavior=behavior,rho=corr(z[metric],z[behavior]),aggregate_points=len(z),independent_seeds=4))
            x=[];y=[]
            for seed,ss in z.groupby('seed'):
                ss=ss.sort_values('step');x.extend(ss[metric].to_numpy()[:-1]);y.extend(ss.exact_accuracy.to_numpy()[1:])
            lag.append(dict(**base,geometry=metric,future_exact_rho=corr(x,y),transitions=len(x),independent_seeds=4))
    pd.DataFrame(correlations).to_csv(OUT/'geometry_performance_correlations.csv',index=False)
    pd.DataFrame(lag).to_csv(OUT/'lagged_geometry_associations.csv',index=False)
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader in ['competitive','scan']:
            a=np.load(source(rep,reader,11,900,6));code=a['code'];target=a['target']
            if rep=='phase':
                z=code[:60].reshape(-1,2);ax.scatter(z[:,0],z[:,1],s=6,alpha=.3,label=reader);ax.set_aspect('equal');ax.set(xlabel='cos phase',ylabel='sin phase')
            else:
                vals=np.take_along_axis(scalar(code,rep,reader),target,1);ax.errorbar(np.arange(6),vals.mean(0),yerr=vals.std(0),marker='o',label=reader);ax.set(xlabel='Target rank',ylabel='Oriented code (native units)')
        ax.set_title(rep+'; illustrative seed11 N6');ax.legend()
    finish('01_learned_geometry.png')
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader,z in f[f.representation==rep].groupby('readout'):ax.scatter(z.pairwise_decoding,z.canonical_rmse,label=reader)
        ax.set(title=rep,xlabel='Pairwise ordinal decoding',ylabel='Canonical aligned RMSE');ax.legend()
    finish('02_rank_metric.png')
    spacing=pd.read_csv(OUT/'adjacent_spacing.csv');fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader,z in spacing[(spacing.representation==rep)&(spacing.step==900)&(spacing.n==6)].groupby('readout'):
            z=z.groupby('adjacent_position')[['mean','p05','p95']].mean();ax.plot(z.index,z['mean'],label=reader);ax.fill_between(z.index,z.p05,z.p95,alpha=.15)
        ax.set(title=rep,xlabel='Adjacent target ranks',ylabel='Spacing (native units; phase in turns)');ax.legend()
    finish('03_adjacent_spacing.png')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    f.assign(cell=f.representation+'/'+f.readout).groupby('cell').slot_rmse.mean().plot.bar(ax=axes[0]);axes[0].set_title('Actual Scan slot RMSE (all codes)')
    f.assign(cell=f.representation+'/'+f.readout).groupby('cell').score_monotonicity.mean().plot.bar(ax=axes[1]);axes[1].set_title('Competitive score monotonicity (all codes)')
    finish('04_readout_alignment.png')
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader,z in g[g.representation==rep].groupby('readout'):
            for n,zz in z.groupby('n'):ax.plot(zz.groupby('step').canonical_rmse.mean(),label=f'{reader} N{n}',marker='o')
        ax.set(title=rep,xlabel='Checkpoint',ylabel='Aligned canonical RMSE');ax.legend(fontsize=7)
    finish('05_trajectory.png')
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader,z in g[g.representation==rep].groupby('readout'):ax.scatter(z.canonical_rmse,z.exact_accuracy,label=reader,alpha=.7)
        ax.set(title=rep,xlabel='Aligned canonical RMSE',ylabel='Exact accuracy');ax.legend()
    finish('06_geometry_performance.png')
    fig,axes=plt.subplots(1,3,figsize=(11,3.5))
    for ax,rep in zip(axes,['priority','position','phase']):
        z=t[(t.representation==rep)&(t.step==900)&(t.n==6)];matrix=np.zeros((2,2))
        for i,reader in enumerate(['competitive','scan']):
            rr=z[z.readout==reader];matrix[i,i]=rr.native_exact.mean();matrix[i,1-i]=rr.transfer_exact.mean()
        ax.imshow(matrix,vmin=0,vmax=1);ax.set_xticks([0,1],['C','S']);ax.set_yticks([0,1],['C-trained','S-trained']);ax.set_title(rep+' N6')
        for i in range(2):
            for j in range(2):ax.text(j,i,f'{matrix[i,j]:.3f}',ha='center',color='white')
    finish('07_transfer.png')
    fig,ax=plt.subplots(figsize=(11,4));z=c[c.geometry.isin(['learned','oracle_slots','source_rank_uniform'])].copy();z['cell']=z.representation+'/'+z.readout;z.pivot_table(index='cell',columns='geometry',values='exact_accuracy').plot.bar(ax=ax);ax.set_ylabel('Exact, N4/N6 mean');finish('08_canonicalization.png')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,metric in zip(axes,['arc_fraction','semicircle']):
        f[f.representation=='phase'].pivot_table(index='n',columns='readout',values=metric).plot.bar(ax=ax);ax.set_title(metric)
    finish('09_phase_arc.png')
    fig,ax=plt.subplots(figsize=(7,4));g[g.representation=='phase'].pivot_table(index='step',columns='readout',values='score_monotonicity').plot(ax=ax,marker='o');ax.set_ylabel('Cosine score monotonicity, N4/N6 mean');finish('10_phase_monotonicity.png')
    fig,ax=plt.subplots(figsize=(12,4));c[(c.representation=='phase')&(c.readout=='competitive')].pivot_table(index='geometry',columns='n',values='exact_accuracy').plot.bar(ax=ax);ax.set_ylabel('Exact accuracy');finish('11_phase_counterfactual.png')
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for ax,rep in zip(axes,['priority','position','phase']):
        c[(c.representation==rep)&(c.readout=='scan')].pivot_table(index='geometry',columns='n',values='exact_accuracy').plot.bar(ax=ax);ax.set(title=rep,ylabel='Exact accuracy')
    finish('12_scan_snap.png')
    decision=dict(classification='A3-GEO-5',reason='Phase readout-specific warping and causal geometry replay coexist with poor Scan calibration; scalar operational adaptation thresholds are not uniformly met.',factorial='DO NOT RERUN FACTORIAL YET',experiment_B='BLOCKED',training_runs=0)
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')

if __name__=='__main__':main()

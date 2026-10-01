"""Report saved A.2 results; no model execution or training."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/oscillation-a2-matplotlib')
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('results/experiment_A2')
def read(name):return pd.read_csv(f'results/experiment_A2_{name}.csv')
def finish(name):
    plt.tight_layout();plt.savefig(OUT/name,dpi=160);plt.close()
def main():
    a=read('noise_curves');o=read('oracle_matrix');g=read('learnability_gap');e=read('learned_geometry_error');r=read('rank_inversion_analysis');c=read('cursor_interventions');v=read('invariance')
    for df in (a,o,g,e,r,c,v):df['cell']=df.representation+'/'+df.readout
    thresholds=[];aucs=[]
    for keys,df in a.groupby(['representation','readout','n','noise_seed']):
        df=df.sort_values('sigma');base=dict(zip(['representation','readout','n','noise_seed'],keys))
        for metric in ['exact_accuracy','pairwise_accuracy']:
            aucs.append(dict(**base,metric=metric,auc=np.trapezoid(df[metric],df.sigma)))
            for threshold in [.9,.75,.5]:
                failed=np.flatnonzero(df[metric].to_numpy()<threshold)
                ix=int(failed[0]) if len(failed) else None
                thresholds.append(dict(**base,metric=metric,threshold=threshold,
                                       lower_sigma=df.sigma.iloc[ix-1] if ix is not None and ix>0 else np.nan,
                                       upper_sigma=df.sigma.iloc[ix] if ix is not None else np.nan,
                                       status='NOT_REACHED' if ix is None else 'ALREADY_BELOW_AT_ZERO' if ix==0 else 'GRID_INTERVAL'))
    th=pd.DataFrame(thresholds);th.to_csv(OUT/'noise_thresholds.csv',index=False)
    pd.DataFrame(aucs).to_csv(OUT/'robustness_auc.csv',index=False)
    fig,axes=plt.subplots(1,5,figsize=(13,3))
    for ax,n in zip(axes,[4,6,8,10,12]):
        mat=o[o.n==n].pivot_table(index='representation',columns='readout',values='exact_accuracy')
        ax.imshow(mat,vmin=0,vmax=1,cmap='viridis');ax.set_title(f'N={n}');ax.set_xticks(range(2),['C','S']);ax.set_yticks(range(3),mat.index)
        for i in range(3):
            for j in range(2):ax.text(j,i,f'{mat.iloc[i,j]:.2f}',ha='center',color='white')
    fig.suptitle('Oracle exact accuracy; same code within representation');finish('01_oracle_heatmap.png')
    plt.figure(figsize=(8,4))
    for cell,df in o.groupby('cell'):plt.plot(df.groupby('n').exact_accuracy.mean(),label=cell,marker='o')
    plt.ylabel('Exact accuracy');plt.xlabel('N');plt.legend(fontsize=7);finish('02_oracle_length.png')
    for metric,name in [('exact_accuracy','03_noise_exact.png'),('pairwise_accuracy','04_noise_pairwise.png')]:
        fig,axes=plt.subplots(1,5,figsize=(17,3.5),sharey=True)
        for ax,n in zip(axes,[4,6,8,10,12]):
            for cell,df in a[a.n==n].groupby('cell'):
                z=df.groupby('sigma')[metric].agg(['mean','std']);ax.plot(z.index,z['mean'],label=cell);ax.fill_between(z.index,z['mean']-z['std'],z['mean']+z['std'],alpha=.10)
            ax.set(title=f'N={n}',xlabel='SD / ordinal spacing',ylim=(-.02,1.02))
        axes[0].set_ylabel(metric);axes[-1].legend(fontsize=6);finish(name)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,n in zip(axes,[4,6]):
        z=r[(r.n==n)&(r.sigma==.35)].groupby(['cell','rank_state'])[['failures','count']].sum();z['rate']=z.failures/z['count']
        z.rate.unstack().plot.bar(ax=ax);ax.set(title=f'N={n}, noise=.35',ylabel='Failure rate',ylim=(0,1.05));ax.tick_params(axis='x',rotation=70)
    finish('05_rank_preserved_failure.png')
    fig,axes=plt.subplots(1,3,figsize=(12,3.5),sharey=True)
    for ax,rep in zip(axes,['priority','position','phase']):
        for reader,df in a[(a.n==6)&(a.representation==rep)].groupby('readout'):
            ax.plot(df.groupby('sigma').exact_accuracy.mean(),label=reader,marker='o')
        ax.set(title=rep,xlabel='SD / ordinal spacing',ylabel='Exact accuracy');ax.legend()
    finish('06_readout_robustness.png')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,metric in zip(axes,['exact_accuracy','pairwise_accuracy']):
        t=th[(th.n==6)&(th.metric==metric)].copy();t['cell']=t.representation+'/'+t.readout
        t.pivot_table(index='cell',columns='threshold',values='upper_sigma').plot.bar(ax=ax)
        ax.set(title=metric,ylabel='First grid SD below threshold (not interpolated)');ax.tick_params(axis='x',rotation=70)
    finish('07_thresholds.png')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,n in zip(axes,[4,6]):
        g[(g.n==n)&(g.status=='A1_EXISTING')].groupby('cell')[['oracle_exact','learned_exact']].mean().plot.bar(ax=ax)
        ax.set(title=f'N={n}',ylabel='Exact accuracy');ax.tick_params(axis='x',rotation=60)
    finish('08_learned_gap.png')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,n in zip(axes,[4,6]):
        e[e.n==n].groupby('cell')[['aligned_error']].mean().plot.bar(ax=ax,legend=False)
        ax.set(title=f'N={n}',ylabel='Aligned absolute error / slot spacing');ax.tick_params(axis='x',rotation=60)
    finish('09_geometry_error.png')
    trials=pd.read_csv('runs/experiment_A2/learned_trial_geometry.csv');fig,axes=plt.subplots(1,3,figsize=(12,4),sharey=True)
    for ax,rep in zip(axes,['priority','position','phase']):
        for n in [4,6]:
            t=trials[(trials.representation==rep)&(trials.readout=='scan')&(trials.n==n)].copy();t['bin']=pd.qcut(t.aligned_error,10,duplicates='drop');z=t.groupby('bin',observed=True)[['aligned_error','failure']].mean()
            ax.plot(z.aligned_error,z.failure,label=f'N{n}',marker='o')
        ax.set(title=rep,xlabel='Aligned error / slot spacing',ylabel='Failure probability');ax.legend()
    finish('10_error_failure.png')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    cs=c[c.readout=='scan'];cs[cs.kind=='freeze'].groupby('representation').sequence_change.mean().plot.bar(ax=axes[0]);axes[0].set_title('Oracle freeze: sequence change')
    cs[cs.kind.isin(['shift','permutation'])].pivot_table(index='representation',columns='kind',values='transformed_target_accuracy').plot.bar(ax=axes[1]);axes[1].set_title('Oracle cursor: intended transformation')
    finish('11_cursor.png')
    plt.figure(figsize=(9,4));v.groupby('cell').output_preserved.mean().plot.bar();plt.ylabel('Sequence preservation');plt.title('Oracle invariance; phase/C symmetric-score tie caveat');finish('12_invariance.png')
    # Apply preregistered thresholds without fitting a new decision rule.
    valid=[]; fragile=[]; learned_flags=[]
    for rep in ['priority','position','phase']:
        z=o[(o.representation==rep)&(o.readout=='scan')&(o.n<=6)]
        if ((z.exact_accuracy>=.75)&(z.pairwise_accuracy>=.9)).all():valid.append(rep)
        ok=True
        for n in [4,6]:
            zz=a[(a.representation==rep)&(a.readout=='scan')&(a.n==n)&(a.sigma<=.35)&(a.sigma>0)]
            rr=r[(r.representation==rep)&(r.readout=='scan')&(r.n==n)&(r.rank_state=='preserved')]
            joined=zz.merge(rr,on=['representation','readout','n','noise_seed','sigma'],suffixes=('','_r'))
            flags=[]
            for sigma,j in joined.groupby('sigma'):
                flags.append(len(j)==4 and (j.exact_accuracy<=.8).all() and (j.failure_rate>=.2).all() and j['count'].sum()>=256)
            ok &= any(flags)
        if ok:fragile.append(rep)
        ee=e[(e.representation==rep)&(e.readout=='scan')]
        condition=True
        for n in [4,6]:
            j=ee[ee.n==n];gg=g[(g.representation==rep)&(g.readout=='scan')&(g.n==n)]
            condition &= (gg.exact_gap>=.2).sum()>=3 and (((j.aligned_error_failure_spearman>=.2)|(j.anchored_error_failure_spearman>=.2)).sum()>=3 or (j.failure_given_preserved>=.2).sum()>=3)
        if condition:learned_flags.append(rep)
    category='A2-SCAN-5' if len(valid)>=2 and len(fragile)>=2 and learned_flags else 'A2-SCAN-2' if len(fragile)>=2 else 'A2-SCAN-3' if len(valid)>=2 else 'A2-SCAN-1'
    decision=dict(oracle_scan_valid=len(valid)>=2,oracle_competent_families=valid,metric_fragility_families=fragile,
                  learned_bottleneck_families=learned_flags,classification=category,compatibility='STILL UNRESOLVED',
                  recommendation='DO NOT RERUN FACTORIAL YET',experiment_B='BLOCKED')
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');print(json.dumps(decision,indent=2))


if __name__=='__main__':main()

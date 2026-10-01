"""Rebuild scientific CSVs/plots from immutable Experiment A run artifacts."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('runs/experiment_A'); OUT=Path('results/experiment_A')
REPS=['priority','position','phase']; READERS=['competitive','scan']
SYSTEMS=[f'{r}_{o}' for r in REPS for o in READERS]+['reference']
SEEDS=[11,22,33,44,55,66,77,88]
SHORT=['Priority/C','Priority/S','Position/C','Position/S','Phase/C','Phase/S','Reference']


def read(name):
    rows=[]
    for s in SYSTEMS:
        for seed in SEEDS:
            path=ROOT/s/str(seed)/name
            if path.exists():
                value=json.loads(path.read_text())
                rows.extend(dict(system=s,seed=seed,**{k:v for k,v in r.items() if k not in ('system','seed')}) for r in value)
    return pd.DataFrame(rows)


def fstat(d):
    n,r=d.shape[-2:]; g=d.mean(axis=(-2,-1),keepdims=True)
    cm=d.mean(-2,keepdims=True); rm=d.mean(-1,keepdims=True)
    effect=n*((cm-g)**2).sum(axis=(-2,-1))/(r-1)
    residual=((d-cm-rm+g)**2).sum(axis=(-2,-1))/((n-1)*(r-1))
    return effect/np.maximum(residual,1e-16)


def interaction(frame):
    table=frame.groupby(['seed','system']).exact_accuracy.mean().unstack().reindex(SEEDS)
    d=np.stack([(table[f'{r}_scan']-table[f'{r}_competitive']).values for r in REPS],1)
    rng=np.random.default_rng(4501)
    perms=np.argsort(rng.random((20000,8,3)),axis=-1)
    null=fstat(np.take_along_axis(np.broadcast_to(d,(20000,8,3)),perms,axis=-1))
    f=float(fstat(d)); p=float((1+(null>=f).sum())/20001)
    boot=d[rng.integers(8,size=(10000,8))].mean(1)
    means=d.mean(0); hi,lo=int(means.argmax()),int(means.argmin())
    return dict(F=f,df=[2,14],permutation_p=p,effect_range=float(np.ptp(means)),
                largest_contrast=f'{REPS[hi]} minus {REPS[lo]}',
                directional_seeds=int(((d[:,hi]-d[:,lo])>0).sum()),
                differences={r:dict(mean=float(means[i]),sd=float(d[:,i].std(ddof=1)),
                                   ci95=np.quantile(boot[:,i],[.025,.975]).tolist(),values=d[:,i].tolist()) for i,r in enumerate(REPS)})


def functional(main,diag,causal,inv):
    rows=[]
    for s in SYSTEMS[:-1]:
        for seed in SEEDS:
            sel=lambda d:d[(d.system==s)&(d.seed==seed)]
            exact=sel(main).exact_accuracy.mean()
            decoding=sel(diag).pairwise_decoding.mean()
            c=sel(causal); invariant=sel(inv)
            invariant=invariant[invariant.intervention!='items_only_rotation']
            swap=c[c.intervention=='representation_swap'].inversion_probability.mean()
            ablation=-c[c.intervention=='representation_ablation'].exact_change.mean()
            rr=c[c.intervention.str.startswith('readout_')]
            ro=rr.later_item_moves_earlier.mean() if s.endswith('competitive') else rr.first_selection_later.mean()
            iv=invariant.sequence_preservation.min()
            ok=exact>=.5 and decoding>=.75 and swap>=.9 and ablation>=.2 and ro>=(.9 if s.endswith('competitive') else .5) and iv>=.99
            rows.append(dict(system=s,seed=seed,exact=exact,decoding=decoding,swap=swap,readout=ro,ablation_drop=ablation,invariance=iv,functional=bool(ok)))
    return pd.DataFrame(rows)


def savefig(name,title,ylabel):
    ax=plt.gca(); ax.set_title(title); ax.set_ylabel(ylabel); ax.grid(axis='y',alpha=.2)
    plt.tight_layout(); plt.savefig(OUT/f'{name}.png',dpi=160);plt.close()


def cellplot(df,col,name,title,ylim=None):
    plt.figure(figsize=(10,4))
    for i,s in enumerate(SYSTEMS):
        v=df[df.system==s].groupby('seed')[col].mean().values
        if not len(v): continue
        plt.scatter(i+np.linspace(-.12,.12,len(v)),v,s=20,alpha=.65)
        plt.errorbar(i,v.mean(),yerr=v.std(ddof=1),fmt='ks',capsize=4)
    plt.xticks(range(7),SHORT,rotation=25,ha='right')
    if ylim: plt.ylim(*ylim)
    savefig(name,title+' (points: seeds; bars: SD)',col)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for s in SYSTEMS:
        for seed in SEEDS: assert (ROOT/s/str(seed)/'complete.json').exists(),(s,seed)
    allmain=read('metrics.json');diag=read('diagnostics.json');causal=read('interventions.json');inv=read('invariance.json');ood=read('ood.json');curves=read('curves.json')
    assert len(allmain)==336 and len(diag)==864 and len(causal)==288 and len(inv)==256
    assert len(ood)==168, 'Wait for all gated OOD rows, including explicit not-tested rows'
    for name,df in [('main_factorial',allmain),('representation_diagnostics',diag),('interventions',causal),('invariance',inv),('ood_length',ood)]:
        df=df.copy()
        df['factorial_cell']=df.system!='reference'
        df['representation']=df.system.map(lambda s:s.split('_')[0] if s!='reference' else 'distributed')
        df['readout']=df.system.map(lambda s:s.split('_')[1] if s!='reference' else 'step_conditioned_scorer')
        df.to_csv(f'results/experiment_A_{name}.csv',index=False)
    curves.to_csv(OUT/'training_curves.csv',index=False)
    configs=[]
    for s in SYSTEMS:
        cfg=json.loads((ROOT/s/'11/config.json').read_text())
        configs.append(dict(system=s,**cfg['counts']))
    params=pd.DataFrame(configs);params.to_csv(OUT/'parameters.csv',index=False)
    final=allmain[allmain.step==900];finaldiag=diag[(diag.step==900)&(diag.layer==2)]
    fun=functional(final,finaldiag,causal,inv);fun.to_csv(OUT/'mechanistic_gates.csv',index=False)
    primary=interaction(final); phases={str(t):interaction(allmain[allmain.step==t]) for t in (300,600,900)}
    functional_counts=fun.groupby('system').functional.sum().to_dict(); valid=[s for s,v in functional_counts.items() if v>=6]
    rcount=len(set(s.split('_')[0] for s in valid));ocount=len(set(s.split('_')[1] for s in valid))
    m=final.groupby('system').exact_accuracy.mean();factor=m.drop('reference')
    repmeans=np.array([np.mean([m[f'{r}_{o}'] for o in READERS]) for r in REPS])
    omeans=np.array([np.mean([m[f'{r}_{o}'] for r in REPS]) for o in READERS])
    confound=len(valid)<3 or rcount<2 or ocount<2 or factor.max()<.4 or factor.min()>.98 or params.total.max()/params.total.min()>1.05
    if confound: category='A-COMPAT-6'
    elif primary['permutation_p']<.05 and primary['effect_range']>=.05 and primary['directional_seeds']>=6:
        rhi,rlo=primary['largest_contrast'].split(' minus ')
        category='A-COMPAT-1' if all(f'{r}_{o}' in valid for r in (rhi,rlo) for o in READERS) else 'A-COMPAT-2'
    elif primary['permutation_p']<.05 or primary['effect_range']>=.05:category='A-COMPAT-2'
    elif np.ptp(repmeans)>=.05 and np.ptp(omeans)<.05:category='A-COMPAT-4'
    elif np.ptp(omeans)>=.05 and np.ptp(repmeans)<.05:category='A-COMPAT-5'
    elif np.ptp(omeans)<.05 and np.ptp(repmeans)<.05:category='A-COMPAT-3'
    else:category='A-COMPAT-6'
    # Qualitative confound review applies the preregistered precedence, without changing thresholds.
    review_path=Path('research/experiment_A_confound_review.json')
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    pre_review=category
    if review.get('dominant_confound'): category='A-COMPAT-6'
    stats=dict(primary=primary,checkpoint_descriptive=phases,functional_seed_counts={s:int(v) for s,v in functional_counts.items()},
               functional_cells=valid,pre_review_category=pre_review,confound_review=review,category=category,
               experiment_B='NOT READY FOR EXPERIMENT B' if confound or review.get('dominant_confound') else 'REQUIRES_CONFOUND_REVIEW',
               representation_mean_range=float(np.ptp(repmeans)),readout_mean_difference=float(np.ptp(omeans)))
    (OUT/'statistics.json').write_text(json.dumps(stats,indent=2)+'\n')
    # Summary data include independent seed estimates; no pooling trials as training replications.
    summary=final.groupby(['system','n']).agg(exact_mean=('exact_accuracy','mean'),exact_sd=('exact_accuracy','std'),
             pairwise_mean=('pairwise_accuracy','mean'),pairwise_sd=('pairwise_accuracy','std'),tau_mean=('kendall_tau','mean'),first_error_mean=('first_error','mean')).reset_index()
    summary.to_csv(OUT/'behavior_summary.csv',index=False)
    seed_final=final.groupby(['system','seed']).exact_accuracy.mean().unstack('seed').reindex(SYSTEMS)
    seed_final.to_csv(OUT/'final_exact_by_seed.csv')
    efficiency=[]
    for (s,seed),g in allmain.groupby(['system','seed']):
        cp=g.groupby('step').exact_accuracy.mean(); passed=cp[cp>=.75]
        efficiency.append(dict(system=s,seed=seed,first_checkpoint_ge_075=passed.index[0] if len(passed) else None,
                               final_exact=cp.loc[900],mid_to_final=cp.loc[900]-cp.loc[600],
                               runtime_seconds=json.loads((ROOT/s/str(seed)/'complete.json').read_text())['seconds']))
    pd.DataFrame(efficiency).to_csv(OUT/'convergence_summary.csv',index=False)
    plt.figure(figsize=(7,4))
    for o in READERS:
        vv=[final[final.system==f'{r}_{o}'].groupby('seed').exact_accuracy.mean().values for r in REPS]
        plt.errorbar(REPS,[v.mean() for v in vv],yerr=[v.std(ddof=1) for v in vv],marker='o',capsize=4,label=o)
    plt.ylim(0,1);plt.legend();savefig('01_interaction','Final R × O interaction; N4/N6 average; SD','Exact accuracy')
    cellplot(final,'exact_accuracy','02_exact','Final exact sequence accuracy',(0,1))
    cellplot(final,'pairwise_accuracy','03_pairwise','Final pairwise order accuracy',(0,1))
    cellplot(final,'kendall_tau','04_tau','Final Kendall tau',(-1,1))
    cellplot(finaldiag,'pairwise_decoding','05_representation','Representation-only order decoding',(0,1))
    cellplot(causal[causal.intervention=='representation_swap'],'inversion_probability','06_rep_swap','Targeted code swap inversion',(0,1.05))
    cellplot(causal[causal.intervention.str.startswith('readout_')],'first_selection_later','07_readout','Readout intervention selects later original slot',(0,1.05))
    cellplot(inv[inv.intervention!='items_only_rotation'],'sequence_preservation','08_invariance','Matched-reference invariances',(0,1.05))
    fig,axs=plt.subplots(2,4,figsize=(13,6),sharex=True,sharey=True)
    for ax,s,label in zip(axs.ravel(),SYSTEMS,SHORT):
        for seed,g in curves[curves.system==s].groupby('seed'):ax.plot(g.step,g.loss,alpha=.4,lw=.7)
        ax.set_title(label);ax.set_xlabel('Step');ax.set_ylabel('N6 sampled CE');ax.grid(alpha=.2)
    axs.ravel()[-1].axis('off');fig.suptitle('Training curves; fixed steps, no tuning');fig.tight_layout();fig.savefig(OUT/'09_training.png',dpi=160);plt.close(fig)
    plt.figure(figsize=(9,4))
    for s,label in zip(SYSTEMS,SHORT):
        g=allmain[allmain.system==s].groupby(['seed','step']).exact_accuracy.mean().unstack('seed')
        plt.errorbar(g.index,g.mean(1),yerr=g.std(1),marker='o',label=label,capsize=2)
    plt.ylim(0,1);plt.legend(ncol=2,fontsize=8);plt.xlabel('Checkpoint');savefig('10_checkpoints','Compatibility trajectories; seed SD','Exact accuracy')
    plt.figure(figsize=(9,4))
    if len(ood) and 'exact_accuracy' in ood:
        for s,label in zip(SYSTEMS,SHORT):
            g=ood[(ood.system==s)&(ood.status=='evaluated')].groupby('n').exact_accuracy.agg(['mean','std'])
            if len(g):plt.errorbar(g.index,g['mean'],yerr=g['std'],marker='o',label=label,capsize=2)
        plt.legend(ncol=2,fontsize=8)
    plt.ylim(0,1);plt.xlabel('OOD N (no retraining)');savefig('11_ood','ID-eligible cells only; seed SD','Exact accuracy')
    plt.figure(figsize=(10,4)); bottom=np.zeros(7)
    for col in ('backbone','representation','readout'):
        v=params[col].values;plt.bar(range(7),v,bottom=bottom,label=col);bottom+=v
    plt.xticks(range(7),SHORT,rotation=25,ha='right');plt.legend();savefig('12_parameters','Exact parameter count; adapters have zero parameters','Parameters')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()

"""Read-only aggregation of calibration; never launches the conditional factorial."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('runs/experiment_A1/calibration');OUT=Path('results/experiment_A1')
CELLS=['priority_scan','position_scan','phase_scan','phase_competitive'];SEEDS=[11,22,33,44]


def load(name):
    rows=[]
    for s in CELLS:
        for k in SEEDS:
            p=ROOT/s/str(k)/name
            for r in json.loads(p.read_text()):rows.append(dict(system=s,seed=k,**r))
    return pd.DataFrame(rows)


def stability(m,c):
    rows=[]
    for s in CELLS[-2:]:
        for seed in SEEDS:
            history=m[(m.system==s)&(m.seed==seed)].groupby('step').exact_accuracy.mean()
            best=0.;events=[]
            for step,val in history.items():
                if best>=.5 and best-val>.30:events.append(int(step))
                best=max(best,val)
            curves=c[(c.system==s)&(c.seed==seed)].sort_values('step');loss=curves.loss.values;spikes=[]
            for i in range(5,len(loss)):
                med=np.median(loss[i-5:i])
                if loss[i]>med+1 and loss[i]>3*med:spikes.append(int(curves.iloc[i].step))
            done=json.loads((ROOT/s/str(seed)/'complete.json').read_text())
            rows.append(dict(system=s,seed=seed,collapse=bool(events),collapse_steps=','.join(map(str,events)),
                             loss_spikes=len(spikes),gradient_max=float(curves.gradient_norm.max()),
                             nan_inf_events=done['nan_inf_events']))
    return pd.DataFrame(rows)


def gates(m,ca,inv,st):
    rows=[]
    for s in CELLS:
        for seed in SEEDS:
            for n in (4,6):
                a=m[(m.system==s)&(m.seed==seed)&(m.n==n)&(m.step==900)].iloc[0]
                c=ca[(ca.system==s)&(ca.seed==seed)&(ca.n==n)].set_index('intervention')
                v=inv[(inv.system==s)&(inv.seed==seed)&(inv.n==n)]
                ab=c.loc['ablation'];sw=c.loc['swap'];baseline=ab.normal_correct_count/1024
                drop=baseline-ab.exact_accuracy
                row=dict(system=s,seed=seed,n=n,normal_exact=a.exact_accuracy,normal_pairwise=a.pairwise_accuracy,
                         code_pairwise=a.code_pairwise_decoding,ablation_exact_drop=drop,
                         swap_transformed=sw.transformed_agreement_on_normal_correct,
                         invariance_preserved=1-v.sequence_change_rate.max())
                invariance=row['invariance_preserved']>=.99
                if s.endswith('scan'):
                    fr,sh,pe=c.loc['freeze'],c.loc['shift'],c.loc['permutation']
                    row.update(freeze_sequence_change=fr.sequence_change_rate,freeze_pairwise_drop=-fr.pairwise_accuracy_change,
                               shift_conditional=sh.transformed_agreement_on_normal_correct,shift_all=sh.transformed_target_accuracy,
                               permutation_conditional=pe.transformed_agreement_on_normal_correct,permutation_all=pe.transformed_target_accuracy)
                    row.update(S1=bool(fr.sequence_change_rate>=.5 and -fr.pairwise_accuracy_change>=.2),
                               S2=bool(sh.transformed_agreement_on_normal_correct>=.8 and sh.transformed_target_accuracy>=.5),
                               S3=bool(pe.transformed_agreement_on_normal_correct>=.8 and pe.transformed_target_accuracy>=.5),
                               S4=bool(a.exact_accuracy>=.5 and a.pairwise_accuracy>=.8),
                               S5=bool(drop>=.2 and -ab.pairwise_accuracy_change>=.2),
                               S_extra=bool(a.code_pairwise_decoding>=.75 and sw.transformed_agreement_on_normal_correct>=.8 and invariance))
                    row['scan_pass']=all(row[k] for k in ('S1','S2','S3','S4','S5','S_extra'))
                if s.startswith('phase'):
                    stabilityrow=st[(st.system==s)&(st.seed==seed)].iloc[0]
                    normok=m[(m.system==s)&(m.seed==seed)].unit_norm_ge099.min()>=.99
                    ro=(row['scan_pass'] if s.endswith('scan') else c.loc['boost'].boost_moves_earlier>=.9)
                    row.update(P1=bool(not stabilityrow.collapse and stabilityrow.nan_inf_events==0 and normok),
                               P2=bool(a.exact_accuracy>=.5 and a.phase_probe_pairwise>=.75),
                               P3=bool(sw.transformed_agreement_on_normal_correct>=.8 and drop>=.2 and ro),P4=bool(invariance))
                rows.append(row)
    return pd.DataFrame(rows)


def finish(name,title,ylabel):
    plt.title(title);plt.ylabel(ylabel);plt.grid(axis='y',alpha=.2);plt.tight_layout();plt.savefig(OUT/f'{name}.png',dpi=160);plt.close()


def plotcells(df,col,name,title,ylim=(0,1)):
    plt.figure(figsize=(8,4))
    for i,s in enumerate(CELLS):
        vals=df[df.system==s].groupby('seed')[col].mean().values
        if not len(vals):continue
        plt.scatter(i+np.linspace(-.10,.10,len(vals)),vals)
        plt.errorbar(i,np.mean(vals),yerr=np.std(vals,ddof=1),fmt='ks',capsize=4)
    plt.xticks(range(4),['Priority/S','Position/S','Phase/S','Phase/C']);plt.ylim(*ylim);finish(name,title+'; seeds and SD',col)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for s in CELLS:
        for k in SEEDS:assert (ROOT/s/str(k)/'complete.json').exists(),(s,k)
    m=load('metrics.json');ca=load('causal.json');inv=load('invariance.json');curves=load('curves.json');st=stability(m,curves);g=gates(m,ca,inv,st)
    m.to_csv(OUT/'checkpoint_metrics.csv',index=False);curves.to_csv(OUT/'training_curves.csv',index=False);ca.to_csv(OUT/'interventions.csv',index=False)
    scan=ca[ca.system.str.endswith('scan')&ca.intervention.isin(['normal','freeze','shift','permutation'])]
    scan.to_csv('results/experiment_A1_scan_calibration.csv',index=False)
    m[m.system.str.startswith('phase')].merge(st,on=['system','seed']).to_csv('results/experiment_A1_phase_stability.csv',index=False)
    g.to_csv('results/experiment_A1_causal_gates.csv',index=False);inv.to_csv('results/experiment_A1_invariance.csv',index=False)
    scan_counts={s:int(g[g.system==s].groupby('seed').scan_pass.all().sum()) for s in CELLS[:3]}
    ps={}
    for s in CELLS[-2:]:
        a=g[g.system==s]
        ps[s]={p:int(a.groupby('seed')[p].all().sum()) for p in ['P1','P2','P3','P4']}
        ps[s]['all']=int(a.assign(all=a[['P1','P2','P3','P4']].all(axis=1)).groupby('seed')['all'].all().sum())
    sg=all(v>=3 for v in scan_counts.values())
    pg=all(v['P1']==4 and v['P4']==4 and v['all']>=3 for v in ps.values())
    decision=dict(scan_validity='PASS' if sg else 'FAIL',phase_stability='PASS' if pg else 'FAIL',
                  scan_seed_pass_counts=scan_counts,phase_seed_gate_counts=ps,
                  factorial_rerun='AUTHORIZED_NOT_YET_RUN' if sg and pg else 'NOT RUN',
                  experiment_B='NOT READY FOR EXPERIMENT B',compatibility='A-COMPAT-6' if not(sg and pg) else 'pending factorial')
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    final=m[m.step==900];final.to_csv(OUT/'final_by_seed.csv',index=False)
    # Required eight calibration figures, no factorial plot or surrogate interaction.
    plt.figure(figsize=(8,4))
    for offset,label in [(-.12,'normal'),(.12,'freeze')]:
        for i,s in enumerate(CELLS[:3]):
            vals=scan[(scan.system==s)&(scan.intervention==label)].groupby('seed').exact_accuracy.mean().values
            plt.errorbar(i+offset,vals.mean(),yerr=vals.std(ddof=1),fmt='o',capsize=4,color='C0' if label=='normal' else 'C1',label=label if i==0 else None)
            plt.scatter(i+offset+np.linspace(-.035,.035,4),vals,s=15,color='C0' if label=='normal' else 'C1')
    plt.xticks(range(3),['Priority/S','Position/S','Phase/S']);plt.ylim(0,1);plt.legend();finish('01_freeze','Normal vs frozen cursor; seed SD','Exact accuracy')
    for label,num in [('shift','02_shift'),('permutation','03_permutation')]:
        plotcells(scan[scan.intervention==label],'transformed_agreement_on_normal_correct',num,label+' conditional transformation agreement')
    plotcells(final[final.system.str.endswith('scan')],'exact_accuracy','04_scan_competence','Ordinary scan competence')
    fig,axs=plt.subplots(1,2,figsize=(10,4),sharey=True)
    for ax,s in zip(axs,CELLS[-2:]):
        for seed,a in curves[curves.system==s].groupby('seed'):
            smooth=a.loss.rolling(20,min_periods=1).mean();ax.plot(a.step,smooth,label=str(seed),lw=1)
        ax.set_title(s);ax.set_xlabel('Step');ax.set_ylabel('CE, 20-step rolling mean');ax.legend(title='Seed');ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'05_phase_loss.png',dpi=160);plt.close(fig)
    plt.figure(figsize=(9,4))
    for s in CELLS[-2:]:
        for seed,a in m[m.system==s].groupby('seed'):
            a=a.groupby('step').exact_accuracy.mean();plt.plot(a.index,a.values,label=f'{s} {seed}',linestyle='-' if s.endswith('scan') else '--')
    plt.ylim(0,1);plt.xlabel('Monitoring step');plt.legend(fontsize=7,ncol=2);finish('06_phase_collapse','Phase competence trajectories (all seeds)','Exact accuracy')
    plt.figure(figsize=(9,4))
    for s in CELLS[-2:]:
        for seed,a in m[m.system==s].groupby('seed'):
            a=a.groupby('step').phase_probe_pairwise.mean();plt.plot(a.index,a.values,label=f'{s} {seed}',linestyle='-' if s.endswith('scan') else '--')
    plt.ylim(0,1);plt.axhline(.5,color='k',alpha=.3);plt.xlabel('Monitoring step');plt.legend(fontsize=7,ncol=2);finish('07_phase_decoding','Phase-only independent-fit rank probe','Pairwise decoding')
    iv=inv[inv.system.str.startswith('phase')].copy();iv['sequence_preservation']=1-iv.sequence_change_rate
    plotcells(iv,'sequence_preservation','08_rotation','Common phase/reference rotation invariance',(0,1.05))
    print(json.dumps(decision,indent=2));print(final.groupby('system')[['exact_accuracy','pairwise_accuracy','no_match_rate']].mean().round(4).to_string())


if __name__=='__main__':main()

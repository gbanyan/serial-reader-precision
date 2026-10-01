import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from experiment_a2.analysis import decode, oracle, coordinates
from experiment_a1.metrics import metrics,mean

SEEDS=(11,22,33,44);STEPS=(300,600,900);REPS=('priority','position','phase');READERS=('competitive','scan')
OUT=Path('results/experiment_A3');RAW=Path('runs/experiment_A3')

def source(rep,reader,seed,step,n):
    root=Path('runs/experiment_A') if rep!='phase' and reader=='competitive' else Path('runs/experiment_A1/calibration')
    return root/f'{rep}_{reader}'/str(seed)/f'eval_{step}_{n}.npz'

def scalar(code,rep,reader):
    if rep=='priority':return -code
    if rep=='position':return code
    if reader=='competitive':return -code[...,0]
    return np.mod(np.arctan2(code[...,1],code[...,0]),2*np.pi)/(2*np.pi)

def fidelity(x,target):
    b,n=x.shape;z=np.take_along_axis(x,target,1);i,j=np.triu_indices(n,1);d=z[:,j]-z[:,i]
    rank=np.argsort(np.argsort(z,axis=1),axis=1)
    return dict(spearman=1-6*((rank-np.arange(n))**2).sum(1)/(n*(n*n-1)),
                kendall=((d>0).sum(1)-(d<0).sum(1))/len(i),pairwise_decoding=(d>0).mean(1),
                inversion_rate=(d<0).mean(1),rank_correct=(d>0).all(1))

def geometric(code,rep,reader,target):
    b,n=target.shape;rows=np.arange(b);rank=np.argsort(target,1);q=(rank+.5)/n;ideal=oracle(rank,rep)
    x=scalar(code,rep,reader);f=fidelity(x,target)
    angles=None;g={}
    if rep=='phase':
        angles=np.mod(np.arctan2(code[...,1],code[...,0]),2*np.pi)
        sorted_a=np.sort(angles,axis=1);gaps=np.diff(np.concatenate([sorted_a,sorted_a[:,:1]+2*np.pi],1),axis=1)
        arc=2*np.pi-gaps.max(1); delta=np.angle(np.exp(1j*(2*np.pi*q-angles)))
        rotation=np.angle(np.exp(1j*delta).mean(1));residual=np.angle(np.exp(1j*(delta-rotation[:,None])))/(2*np.pi)
        order=np.take_along_axis(angles,target,1);spacing=np.abs(np.angle(np.exp(1j*np.diff(order,axis=1))))/(2*np.pi)
        g.update(arc_fraction=arc/(2*np.pi),semicircle=(arc<=np.pi+1e-6),wrap_usage=(np.abs(np.diff(order,axis=1))>np.pi).any(1),
                 canonical_rmse=np.sqrt((residual**2).mean(1)),canonical_max_error=np.abs(residual).max(1),dynamic_range=arc/(2*np.pi),
                 angular_pairwise=fidelity(angles,target)['pairwise_decoding'])
        dist=np.abs(np.angle(np.exp(1j*(angles-2*np.pi*q))))/(2*np.pi)
        all_dist=np.abs(np.angle(np.exp(1j*(angles[:,:,None]-2*np.pi*(np.arange(n)+.5)/n))))/(2*np.pi)
        score=8*(code[...,0]-1)
    else:
        orient=-code if rep=='priority' else code
        ordered=np.take_along_axis(orient,target,1);spacing=np.diff(ordered,axis=1)
        y=rank/(n-1);xc=orient-orient.mean(1,keepdims=True);yc=y-y.mean(1,keepdims=True)
        slope=np.maximum(0,(xc*yc).sum(1)/np.maximum((xc*xc).sum(1),1e-15));intercept=y.mean(1)-slope*orient.mean(1)
        residual=slope[:,None]*orient+intercept[:,None]-y
        g.update(canonical_rmse=np.sqrt((residual**2).mean(1)),canonical_max_error=np.abs(residual).max(1),
                 calibration_slope=slope,calibration_intercept=intercept,endpoint_early=residual[rows,target[:,0]],endpoint_late=residual[rows,target[:,-1]],
                 dynamic_range=np.ptp(code,axis=1))
        c=coordinates(code,rep,'scan');dist=np.abs(c-q);all_dist=np.abs(c[:,:,None]-(np.arange(n)+.5)/n)
        score=-16*coordinates(code,rep,'competitive')
    av=spacing.mean(1);cv=np.divide(spacing.std(1),np.abs(av),out=np.full(b,np.nan),where=np.abs(av)>1e-12)
    ordered_score=np.take_along_axis(score,target,1);sm=-np.diff(ordered_score,axis=1);i,j=np.triu_indices(n,1)
    projected=fidelity(-score,target)
    other=all_dist.copy();other[rows[:,None],np.arange(n)[None,:],rank]=np.inf
    g.update(**f,spacing_mean=av,spacing_sd=spacing.std(1),spacing_cv=cv,
             score_monotonicity=projected['rank_correct'],score_pairwise=projected['pairwise_decoding'],
             score_tie_rate=(np.abs(ordered_score[:,j]-ordered_score[:,i])<=1e-6).mean(1),score_min_margin=sm.min(1),score_range=np.ptp(score,axis=1),
             slot_rmse=np.sqrt((dist**2).mean(1))*n,slot_capture=(dist<.45/n).mean(1),metric_good=(dist<.45/n).all(1),
             nearest_slot_accuracy=(all_dist.argmin(2)==rank).mean(1),slot_margin=(other.min(2)-dist).min(1)*n)
    return g,spacing

def averages(g):return {k:float(np.nanmean(v)) if np.isfinite(v).any() else np.nan for k,v in g.items()}

def phase_arc(rank,span):
    n=rank.shape[1];angle=np.pi/2-span[:,None]/2+span[:,None]*(rank+.5)/n
    return np.stack([np.cos(angle),np.sin(angle)],-1)

def snap(code,rep):
    n=code.shape[1]
    if rep=='phase':
        angle=np.mod(np.arctan2(code[...,1],code[...,0]),2*np.pi);idx=np.floor(angle*n/(2*np.pi)).astype(int)%n
        return oracle(idx,rep)
    c=coordinates(code,rep,'scan');idx=np.clip(np.floor(c*n),0,n-1)
    # Priority adapter renormalizes extrema exactly as frozen; do not bypass it.
    return oracle(idx,rep)

def main():
    OUT.mkdir(exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'complete.json').exists(),'A3 already completed'
    summaries=[];alignment=[];decomp=[];transfer=[];cf=[];phase=[];spacing_rows=[];trials=[];matched=0
    for rep in REPS:
        for seed in SEEDS:
            for step in STEPS:
                for n in (4,6):
                    panels={o:np.load(source(rep,o,seed,step,n)) for o in READERS}
                    for key in ['ids','numeric','target']:assert np.array_equal(panels['competitive'][key],panels['scan'][key]),(rep,seed,step,n,key)
                    matched+=1
                    for reader,a in panels.items():
                        code=a['code'];target=a['target'];rank=np.argsort(target,1);pred,_=decode(code,rep,reader)
                        saved=a['prediction'] if 'prediction' in a else a['pred'];assert np.array_equal(pred,saved),(rep,reader,seed,step,n)
                        base=dict(representation=rep,readout=reader,seed=seed,step=step,n=n,source=str(source(rep,reader,seed,step,n)))
                        geo,spacing=geometric(code,rep,reader,target);behavior=metrics(pred,target);exact=behavior['exact_accuracy'].astype(bool)
                        summaries.append(dict(**base,**averages(geo),**mean(behavior)))
                        alignment.append(dict(**base,**{k:averages(geo)[k] for k in ['score_monotonicity','score_pairwise','score_min_margin','score_tie_rate','score_range','slot_rmse','slot_capture','slot_margin','nearest_slot_accuracy']},no_match_rate=float((pred<0).mean())))
                        if rep=='phase':phase.append(dict(**base,**{k:averages(geo)[k] for k in ['arc_fraction','semicircle','wrap_usage','canonical_rmse','angular_pairwise','score_monotonicity','score_tie_rate','dynamic_range']}))
                        strata=np.where(~geo['rank_correct'],'rank_incorrect',np.where(geo['metric_good'],'rank_correct_metric_good','rank_correct_metric_poor'))
                        for s in ['rank_incorrect','rank_correct_metric_poor','rank_correct_metric_good']:
                            mask=strata==s;count=int(mask.sum());fail=int((~exact[mask]).sum())
                            decomp.append(dict(**base,stratum=s,count=count,failures=fail,failure_rate=fail/count if count else np.nan))
                        for j in range(n-1):spacing_rows.append(dict(**base,adjacent_position=j,mean=spacing[:,j].mean(),sd=spacing[:,j].std(),p05=np.quantile(spacing[:,j],.05),p95=np.quantile(spacing[:,j],.95)))
                        for j in range(len(target)):
                            trials.append(dict(**base,trial=j,exact=exact[j],canonical_rmse=geo['canonical_rmse'][j],slot_rmse=geo['slot_rmse'][j],spacing_cv=geo['spacing_cv'][j],dynamic_range=geo['dynamic_range'][j],arc_fraction=geo.get('arc_fraction',np.full(len(target),np.nan))[j]))
                        other='scan' if reader=='competitive' else 'competitive';p,_=decode(code,rep,other)
                        transfer.append(dict(**base,target_readout=other,native_exact=exact.mean(),transfer_exact=float((p==target).all(1).mean()),**mean(metrics(p,target))))
                        # All counterfactuals are final-checkpoint only; no geometry selected on outcomes.
                        if step!=900:continue
                        inferred=np.argsort(np.argsort(scalar(code,rep,reader),axis=1),axis=1)
                        variants={'learned':(code,'LEARNED'),'oracle_slots':(oracle(rank,rep),'TARGET_INFORMED'),
                                  'source_rank_uniform':(oracle(inferred,rep),'SOURCE_INFERRED')}
                        if reader=='scan':
                            u=.5/n+(1-1/n)*(rank/(n-1))**3
                            distorted=1-(rank/(n-1))**3 if rep=='priority' else u if rep=='position' else np.stack([np.cos(2*np.pi*u),np.sin(2*np.pi*u)],-1)
                            variants.update(metric_distorted=(distorted,'TARGET_RANK_PRESERVED'),slot_snapped=(snap(code,rep),'SOURCE_NEAREST_SLOT'))
                        if rep=='phase' and reader=='competitive':
                            span=np.minimum(geo['arc_fraction']*2*np.pi,np.pi-1e-4)
                            variants.update(semicircle=(phase_arc(rank,np.full(len(rank),np.pi)),'TARGET_INFORMED'),
                                            learned_span_arc=(phase_arc(rank,span),'TARGET_INFORMED'),
                                            inferred_semicircle=(phase_arc(inferred,np.full(len(rank),np.pi)),'SOURCE_INFERRED'))
                        if rep!='phase' and reader=='competitive':
                            v=(inferred/(n-1))**3;variants['source_rank_cubic']=(1-v if rep=='priority' else v,'SOURCE_RANK_PRESERVED')
                        for name,(v,info) in variants.items():
                            p,_=decode(v,rep,reader)
                            cf.append(dict(**base,geometry=name,information=info,**mean(metrics(p,target)),
                                           learned_output_preserved=float((p==pred).all(1).mean()),
                                           arc_capped_rate=float((geo['arc_fraction']*2*np.pi>np.pi-1e-4).mean()) if name=='learned_span_arc' else np.nan))
                    print(rep,seed,step,n,flush=True)
    for name,rows in [('geometry_summary',summaries),('readout_alignment',alignment),('rank_metric_decomposition',decomp),('cross_readout_transfer',transfer),('counterfactual_geometry',cf),('phase_arc_analysis',phase),('geometry_trajectory',summaries)]:
        pd.DataFrame(rows).to_csv(f'results/experiment_A3_{name}.csv',index=False)
    pd.DataFrame(spacing_rows).to_csv(OUT/'adjacent_spacing.csv',index=False);pd.DataFrame(trials).to_csv(RAW/'geometry_trials.csv',index=False)
    (OUT/'complete.json').write_text(json.dumps(dict(matched_panels=matched,native_replays=len(summaries),training_runs=0),indent=2)+'\n')

if __name__=='__main__':main()

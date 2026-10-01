import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from experiment_a1.metrics import metrics, mean

REPS = ('priority', 'position', 'phase')
READERS = ('competitive', 'scan')
LEVELS = (0, .05, .10, .20, .35, .50, .75, 1.)
LENGTHS = (4, 6, 8, 10, 12)
SEEDS = (101, 202, 303, 404)
OUT = Path('results/experiment_A2')
RAW = Path('runs/experiment_A2')


def coordinates(code, rep, reader):
    if rep == 'phase':
        return code
    if rep == 'priority':
        c = (code.max(1, keepdims=True)-code)/np.maximum(np.ptp(code, axis=1, keepdims=True), 1e-7)
        if reader == 'scan':
            n = code.shape[1]
            c = .5/n + (1-1/n)*c
        return c
    return code


def decode(code, rep, reader, slots=None, angle=0., boost=None):
    """Literal A.1 fixed-score/null/mask semantics, no learned adapter."""
    b, n = code.shape[:2]
    c = coordinates(code, rep, reader).copy()
    if rep == 'phase':
        rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]], dtype=c.dtype)
        c = c @ rot.T
    used = np.zeros((b,n), bool)
    predictions, collisions, matches = [], [], []
    for t, slot in enumerate(range(n) if slots is None else slots):
        if reader == 'competitive':
            s = 8*((c*np.array([np.cos(angle), np.sin(angle)], dtype=c.dtype)).sum(-1)-1) if rep == 'phase' else -16*c
            null = -1e9
            if boost is not None and t == 0:
                s = s.copy(); s[np.arange(b), boost] = s.max(1)+10
        else:
            q = (slot+.5)/n; radius = .45/n
            if rep == 'phase':
                cursor = np.array([np.cos(2*np.pi*q+angle), np.sin(2*np.pi*q+angle)], dtype=c.dtype)
                d2 = ((c-cursor)**2).sum(-1)/(4*np.pi**2)
                boundary = (np.sin(np.pi*radius)/np.pi)**2
            else:
                d2 = (c-q)**2; boundary = radius**2
            s = -16*d2; null = -16*boundary
            collisions.append((s > null).sum(1) > 1)
        s = np.where(used, -1e9, s)
        k = np.concatenate([np.full((b,1), null, dtype=s.dtype), s], 1).argmax(1)-1
        predictions.append(k)
        valid = k >= 0
        used[np.arange(b)[valid], k[valid]] = True
    return np.stack(predictions,1), (np.stack(collisions,1).mean(1) if collisions else np.zeros(b))


def oracle(rank, rep):
    n=rank.shape[1]; u=(rank+.5)/n
    if rep=='priority': return 1-rank/(n-1)
    if rep=='position': return u
    return np.stack([np.cos(2*np.pi*u), np.sin(2*np.pi*u)],-1)


def coord_order(code, rep, target, projected=False):
    if rep=='priority': x=-code
    elif rep=='position': x=code
    elif projected: x=-code[...,0]
    else: x=np.mod(np.arctan2(code[...,1],code[...,0]),2*np.pi)
    ordered=np.take_along_axis(x,target,1)
    i,j=np.triu_indices(target.shape[1],1)
    delta=ordered[:,j]-ordered[:,i]
    # Ties do not count as preserved strict rank. Tolerance flags cosine symmetry.
    inv=(delta < -1e-10).sum(1); ties=(np.abs(delta)<=1e-10).sum(1)
    return inv,ties


def error(code, ideal, rep, align=False):
    n=code.shape[1]
    if rep=='phase':
        a=np.arctan2(code[...,1],code[...,0]); b=np.arctan2(ideal[...,1],ideal[...,0])
        delta=np.angle(np.exp(1j*(b-a)))
        if align: delta=np.angle(np.exp(1j*(delta-np.angle(np.exp(1j*delta).mean(1))[:,None])))
        return np.abs(delta).mean(1)/(2*np.pi/n)
    x=code.copy(); y=ideal
    spacing=1/(n-1) if rep=='priority' else 1/n
    if align:
        xc=x-x.mean(1,keepdims=True); yc=y-y.mean(1,keepdims=True)
        slope=np.maximum(0,(xc*yc).sum(1)/np.maximum((xc*xc).sum(1),1e-15))
        x=slope[:,None]*xc+y.mean(1,keepdims=True)
    return np.abs(x-y).mean(1)/spacing


def wilson(k,n):
    if not n:return (np.nan,np.nan)
    p=k/n; z=1.96; d=1+z*z/n; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return ((p+z*z/(2*n))/d-h,(p+z*z/(2*n))/d+h)


def conditional_row(base,pred,target,inv,ties,metric_error):
    rows=[]; failure=~(pred==target).all(1)
    for state,mask in [('preserved',(inv==0)&(ties==0)),('inverted',inv>0),('tied',(inv==0)&(ties>0))]:
        count=int(mask.sum()); k=int(failure[mask].sum()); lo,hi=wilson(k,count)
        rows.append(dict(**base,rank_state=state,count=count,failures=k,
                         failure_rate=k/count if count else np.nan,ci_low=lo,ci_high=hi,
                         mean_metric_error=float(metric_error[mask].mean()) if count else np.nan))
    return rows


def save(name, rows):
    import pandas as pd
    pd.DataFrame(rows).to_csv(Path('results')/f'experiment_A2_{name}.csv',index=False)


def primary():
    OUT.mkdir(exist_ok=True); RAW.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'primary_complete.json').exists(), 'Primary outputs already frozen'
    rows=[]; conditional=[]; interventions=[]; invariances=[]
    for n in LENGTHS:
        for seed in SEEDS:
            rng=np.random.default_rng(seed+n*1000)
            rank=np.argsort(rng.random((1024,n)),axis=1); target=np.argsort(rank,axis=1)
            noise=rng.normal(size=(1024,n))
            for rep in REPS:
                ideal=oracle(rank,rep)
                for sigma in LEVELS:
                    if rep=='phase':
                        a=2*np.pi*(rank+.5)/n+noise*sigma*2*np.pi/n
                        code=np.stack([np.cos(a),np.sin(a)],-1)
                    else:code=ideal+noise*sigma*(1/(n-1) if rep=='priority' else 1/n)
                    inv,ties=coord_order(code,rep,target); err=error(code,ideal,rep)
                    for reader in READERS:
                        base=dict(representation=rep,readout=reader,n=n,noise_seed=seed,sigma=sigma)
                        pred,collision=decode(code,rep,reader)
                        m=mean(metrics(pred,target)); pinv,ptie=coord_order(code,rep,target,True)
                        rows.append(dict(**base,**m,trials=len(pred),cursor_slot_match=float((pred==target).mean()) if reader=='scan' else np.nan,
                                         slot_miss_rate=float((pred<0).mean()),cursor_collision=float(collision.mean()),
                                         inversion_rate=float(inv.mean()/(n*(n-1)/2)),rank_preserved=float(((inv==0)&(ties==0)).mean()),
                                         projected_rank_preserved=float(((pinv==0)&(ptie==0)).mean()),mean_metric_error=float(err.mean())))
                        conditional.extend(conditional_row(base,pred,target,inv,ties,err))
                        if sigma:continue
                        if reader=='scan':
                            for kind,slots in [('freeze',[0]*n),('shift',list(range(1,n))+[0]),('permutation',list(range(0,n,2))+list(range(1,n,2)))]:
                                changed,_=decode(code,rep,reader,slots)
                                expected=target[:,slots]
                                interventions.append(dict(**base,kind=kind,sequence_change=float((changed!=pred).any(1).mean()),
                                                          transformed_target_accuracy=float((changed==expected).all(1).mean()),**mean(metrics(changed,target))))
                        else:
                            boosted,_=decode(code,rep,reader,boost=target[:,-1]); ix=target[:,-1,None]
                            before=(pred==ix).argmax(1); after=(boosted==ix).argmax(1); eligible=before>0
                            interventions.append(dict(**base,kind='boost',eligible_count=int(eligible.sum()),upward_rate=float((after[eligible]<before[eligible]).mean()) if eligible.any() else np.nan,
                                                      mean_rank_shift=float((after-before).mean()),sequence_change=float((boosted!=pred).any(1).mean())))
                        swapped=code.copy(); ii=target[:,0];jj=target[:,-1]; br=np.arange(len(code))
                        swapped[br,ii],swapped[br,jj]=code[br,jj],code[br,ii]
                        ps,_=decode(swapped,rep,reader)
                        expected=np.where(pred==ii[:,None],jj[:,None],np.where(pred==jj[:,None],ii[:,None],pred))
                        interventions.append(dict(**base,kind='swap',sequence_change=float((ps!=pred).any(1).mean()),
                                                  transformed_target_accuracy=float((ps==expected).all(1).mean())))
                        if rep=='phase':
                            pi,_=decode(code,rep,reader,angle=.37)
                            kind='common_rotation'
                        else:
                            transformed=2*code+3
                            # Matched position reference transform is the frozen canonical-coordinate adapter.
                            pi,_=decode(transformed if rep=='priority' else (transformed-3)/2,rep,reader)
                            kind='positive_affine' if rep=='priority' else 'matched_affine_reference'
                        invariances.append(dict(**base,kind=kind,output_preserved=float((pi==pred).all(1).mean()),
                                                invariant_pass=bool((pi==pred).all(1).mean()>=.99),
                                                oracle_exact=m['exact_accuracy'],score_tie_trials=float((ptie>0).mean())))
            print(f'Completed oracle/noise N={n}, seed={seed}',flush=True)
    save('noise_curves',rows);save('oracle_matrix',[r for r in rows if r['sigma']==0])
    save('rank_inversion_analysis',conditional);save('cursor_interventions',interventions);save('invariance',invariances)
    (OUT/'primary_complete.json').write_text(json.dumps(dict(noise_rows=len(rows),trials_per_row=1024,training_runs=0),indent=2)+'\n')


def learned():
    import pandas as pd
    from scipy.stats import spearmanr
    gaps=[]; geometry=[]; trial_rows=[]; replay=0
    oracle_df=pd.read_csv('results/experiment_A2_oracle_matrix.csv')
    for path in sorted(Path('runs/experiment_A1/calibration').glob('*/*/eval_900_*.npz')):
        system=path.parent.parent.name; seed=int(path.parent.name);rep,reader=system.split('_')
        a=np.load(path);code=a['code']; target=a['target'];n=target.shape[1];rank=np.argsort(target,1)
        pred,_=decode(code,rep,reader)
        assert np.array_equal(pred,a['prediction']), str(path)
        replay+=1; ideal=oracle(rank,rep); raw=error(code,ideal,rep);aligned=error(code,ideal,rep,True)
        inv,ties=coord_order(code,rep,target); fail=~(pred==target).all(1);preserved=(inv==0)&(ties==0)
        pair=metrics(pred,target)['pairwise_accuracy']
        base=dict(representation=rep,readout=reader,seed=seed,n=n)
        actual=mean(metrics(pred,target));oo=oracle_df.query('representation==@rep and readout==@reader and n==@n')
        gaps.append(dict(**base,status='A1_EXISTING',oracle_exact=oo.exact_accuracy.mean(),learned_exact=actual['exact_accuracy'],
                         exact_gap=oo.exact_accuracy.mean()-actual['exact_accuracy'],oracle_pairwise=oo.pairwise_accuracy.mean(),
                         learned_pairwise=actual['pairwise_accuracy'],pairwise_gap=oo.pairwise_accuracy.mean()-actual['pairwise_accuracy']))
        geometry.append(dict(**base,anchored_error=raw.mean(),aligned_error=aligned.mean(),inversion_count=inv.mean(),
                             rank_preserved=preserved.mean(),failure_given_preserved=fail[preserved].mean() if preserved.any() else np.nan,
                             preserved_count=preserved.sum(),anchored_error_failure_spearman=spearmanr(raw,fail).statistic,
                             aligned_error_failure_spearman=spearmanr(aligned,fail).statistic,
                             exact_accuracy=actual['exact_accuracy'],no_match_rate=actual['no_match_rate']))
        for j in range(len(pred)):
            trial_rows.append(dict(**base,trial=j,anchored_error=raw[j],aligned_error=aligned[j],inversions=int(inv[j]),
                                   rank_preserved=bool(preserved[j]),failure=bool(fail[j]),pairwise_accuracy=pair[j]))
    for rep in ('priority','position'):
        for n in (4,6):gaps.append(dict(representation=rep,readout='competitive',n=n,status='NOT_AVAILABLE_A1_NOT_TRAINED'))
    save('learnability_gap',gaps);save('learned_geometry_error',geometry)
    pd.DataFrame(trial_rows).to_csv(RAW/'learned_trial_geometry.csv',index=False)
    (OUT/'learned_replay.json').write_text(json.dumps(dict(exact_saved_prediction_replays=replay,training_runs=0),indent=2)+'\n')


if __name__=='__main__':
    import sys
    (primary if sys.argv[1]=='primary' else learned)()

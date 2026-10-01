"""Requested margin/alignment summaries and numerical-tie verification on saved codes."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import spearmanr
from experiment_a2.analysis import oracle, decode, error, LENGTHS, SEEDS, REPS, READERS, LEVELS


def main():
    extra=[]
    for p in sorted(Path('runs/experiment_A1/calibration').glob('*/*/eval_900_*.npz')):
        system=p.parent.parent.name;rep,reader=system.split('_');a=np.load(p);x=a['code'];target=a['target'];n=target.shape[1];ideal=oracle(np.argsort(target,1),rep)
        b=dict(representation=rep,readout=reader,seed=int(p.parent.name),n=n)
        if rep!='phase':
            xc=x-x.mean(1,keepdims=True);yc=ideal-ideal.mean(1,keepdims=True)
            slope=(xc*yc).sum(1)/np.maximum((xc*xc).sum(1),1e-15)
            ordered=np.take_along_axis(x,target,1);margin=np.diff(ordered,axis=1)*(-1 if rep=='priority' else 1)
            span=np.maximum(np.ptp(x,axis=1),1e-15)/(n-1);norm=margin/span[:,None]
            b.update(positive_affine_slope_mean=np.maximum(slope,0).mean(),nonpositive_slope_rate=(slope<=0).mean(),
                     normalized_margin_p05=np.quantile(norm,.05),normalized_margin_median=np.median(norm),normalized_margin_p95=np.quantile(norm,.95))
        else:
            da=np.angle(ideal[...,0]+1j*ideal[...,1])-np.angle(x[...,0]+1j*x[...,1]);rot=np.angle(np.exp(1j*da).mean(1))
            residual=np.angle(np.exp(1j*(da-rot[:,None])))/(2*np.pi/n)
            b.update(rotation_abs_mean=np.abs(rot).mean(),slot_deviation_p05=np.quantile(residual,.05),slot_deviation_p95=np.quantile(residual,.95))
        extra.append(b)
    path=Path('results/experiment_A2_learned_geometry_error.csv');df=pd.read_csv(path)
    additions=pd.DataFrame(extra); keys=['representation','readout','seed','n']
    df=df.drop(columns=[c for c in additions.columns if c not in keys and c in df.columns])
    df.merge(additions,on=keys,validate='one_to_one').to_csv(path,index=False)
    checks=[]
    for n in LENGTHS:
        for seed in SEEDS:
            rng=np.random.default_rng(seed+n*1000);rank=np.argsort(rng.random((1024,n)),1);code=oracle(rank,'phase')
            a,_=decode(code,'phase','competitive');b,_=decode(code,'phase','competitive',angle=.37)
            scores=code[...,0];sa=np.take_along_axis(scores,a,1);sb=np.take_along_axis(scores,b,1)
            checks.append(dict(n=n,noise_seed=seed,sequence_preserved=(a==b).all(1).mean(),
                               sorted_score_sequences_equal=np.isclose(sa,sb,atol=1e-12,rtol=0).all(1).mean(),max_score_discrepancy=np.max(np.abs(sa-sb))))
    pd.DataFrame(checks).to_csv('results/experiment_A2/phase_tie_invariance_check.csv',index=False)
    a=pd.read_csv('results/experiment_A2_noise_curves.csv');z=a[(a.representation=='position')&(a.readout=='scan')].copy()
    z['analytical_exact']=z.apply(lambda row:1. if row.sigma==0 else (2*ndtr(.45/row.sigma)-1)**int(row.n),axis=1)
    z['observed_minus_analytical']=z.exact_accuracy-z.analytical_exact
    z[['n','noise_seed','sigma','exact_accuracy','analytical_exact','observed_minus_analytical']].to_csv('results/experiment_A2/analytical_scan_check.csv',index=False)
    associations=[]
    # Reconstruct the identical frozen noise draws; no new conditions or fitting.
    for n in LENGTHS:
        for seed in SEEDS:
            rng=np.random.default_rng(seed+n*1000); rank=np.argsort(rng.random((1024,n)),1);target=np.argsort(rank,1);noise=rng.normal(size=(1024,n))
            for rep in REPS:
                ideal=oracle(rank,rep)
                for sigma in LEVELS:
                    if rep=='phase':
                        angle=2*np.pi*(rank+.5)/n+noise*sigma*2*np.pi/n
                        code=np.stack([np.cos(angle),np.sin(angle)],-1)
                    else:code=ideal+noise*sigma*(1/(n-1) if rep=='priority' else 1/n)
                    err=error(code,ideal,rep)
                    for reader in READERS:
                        pred,_=decode(code,rep,reader);fail=~(pred==target).all(1)
                        old=a[(a.n==n)&(a.noise_seed==seed)&(a.representation==rep)&(a.readout==reader)&(a.sigma==sigma)].iloc[0]
                        assert abs((~fail).mean()-old.exact_accuracy)<1e-12
                        associations.append(dict(n=n,noise_seed=seed,representation=rep,readout=reader,sigma=sigma,
                                                 error_failure_spearman=spearmanr(err,fail).statistic if np.ptp(err)>0 and np.ptp(fail.astype(int))>0 else np.nan,
                                                 mean_error_correct=err[~fail].mean() if (~fail).any() else np.nan,
                                                 mean_error_failed=err[fail].mean() if fail.any() else np.nan,
                                                 exact_replay=True))
    pd.DataFrame(associations).to_csv('results/experiment_A2/noise_error_association.csv',index=False)
    print('Saved margin, alignment, cosine-tie and analytical Gaussian checks')


if __name__=='__main__':main()

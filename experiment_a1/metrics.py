import numpy as np


def relations(pred, n):
    ids=np.arange(n)
    hit=pred[:,:,None]==ids[None,None,:]
    present=hit.sum(1)==1
    pos=hit.argmax(1)
    i,j=np.triu_indices(n,1)
    valid=present[:,i]&present[:,j]
    rel=np.where(valid,np.where(pos[:,i]<pos[:,j],1,-1),0)
    return rel,present,pos


def metrics(pred,target):
    n=target.shape[1];rel,present,pos=relations(pred,n);truth,_,_=relations(target,n)
    pair=(rel==truth)&(rel!=0)
    count=(rel!=0).sum(1)
    conditional=np.divide((rel*truth).sum(1),count,out=np.full(len(pred),np.nan),where=count>0)
    exact=(pred==target).all(1)
    return dict(exact_accuracy=exact.astype(float),pairwise_accuracy=pair.mean(1),
                kendall_tau_present=conditional,pair_coverage=(rel!=0).mean(1),
                first_error=np.where(exact,n,(pred!=target).argmax(1)),
                omission_rate=1-present.mean(1),no_match_rate=(pred<0).mean(1),
                duplicate_rate=np.maximum(0,((pred[:,:,None]==np.arange(n)[None,None,:]).sum(1)-1)).sum(1)/n)


def mean(rows):
    return {k:float(np.nanmean(v)) if np.isfinite(v).any() else None for k,v in rows.items()}


def changes(pred,base,target,expected=None):
    n=target.shape[1];r,_,_=relations(pred,n);rb,_,_=relations(base,n)
    changed=(pred!=base).any(1);correct=(base==target).all(1)
    a,b=metrics(pred,target),metrics(base,target)
    out=dict(sequence_change_rate=float(changed.mean()),pairwise_relation_change=float((r!=rb).mean()),
             pairwise_accuracy_change=float((a['pairwise_accuracy']-b['pairwise_accuracy']).mean()),
             first_changed_position=float(np.where(changed,(pred!=base).argmax(1),n).mean()),
             normal_correct_count=int(correct.sum()),**mean(a))
    finite=np.isfinite(a['kendall_tau_present'])&np.isfinite(b['kendall_tau_present'])
    out['kendall_tau_change']=float((a['kendall_tau_present'][finite]-b['kendall_tau_present'][finite]).mean()) if finite.any() else None
    if expected is not None:
        matches=pred==expected
        out.update(transformed_sequence_agreement=float(matches.all(1).mean()),slot_agreement=float(matches.mean()),
                   transformed_agreement_on_normal_correct=float(matches[correct].all(1).mean()) if correct.any() else None,
                   collateral_mismatch=float((~matches[correct]).mean()) if correct.any() else None)
    return out

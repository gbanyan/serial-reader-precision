import numpy as np
import torch
from experiment_a.data import batch
from experiment_a.evaluate import corr,ridge_fit,ridge_apply
from .metrics import metrics,mean,changes,relations


@torch.no_grad()
def panel(model,n,size=1024):
    model.eval();x=batch(np.random.default_rng(810000+n),size,n);out=model(x)
    target=x['target'].numpy();pred=out['prediction'].numpy();code=out['code'].numpy()
    teacher=model(x,teacher=True)
    loss=torch.nn.functional.cross_entropy(teacher['logits'].flatten(0,1),(x['target']+1).flatten()).item()
    row=dict(**mean(metrics(pred,target)),validation_loss=loss)
    raw=dict(target=target,prediction=pred,code=code,ids=x['ids'].numpy(),numeric=x['numeric'].numpy())
    rank=target.argsort(1).astype(float)
    if model.rep=='phase':
        angle=np.arctan2(code[...,1],code[...,0]);coordinate=(-code[...,0] if model.reader=='competitive' else angle%(2*np.pi)/(2*np.pi))
        fitx=batch(np.random.default_rng(710000+n),256,n);fitout=model(fitx)
        fit=ridge_fit(fitout['code'].numpy(),fitx['target'].numpy().argsort(1)/(n-1))
        estimated=ridge_apply(code,fit)
        row['phase_probe_pairwise']=mean(metrics(estimated.argsort(1),target))['pairwise_accuracy']
        r,c,s=rank.ravel(),code[...,0].ravel(),code[...,1].ravel()
        rc,rs,cs=corr(r,c),corr(r,s),corr(c,s)
        row['circular_rank_association']=float(np.sqrt(max(0,(rc**2+rs**2-2*rc*rs*cs)/(1-cs**2+1e-12))))
        norm=out['raw_norm'].numpy();unit=np.linalg.norm(code,axis=-1)
        row.update(raw_norm_min=float(norm.min()),raw_norm_mean=float(norm.mean()),raw_norm_p05=float(np.quantile(norm,.05)),
                   unit_norm_min=float(unit.min()),unit_norm_ge099=float((unit>=.99).mean()),
                   phase_resultant=float(np.linalg.norm(code.mean(1),axis=-1).mean()),
                   phase_dispersion=float((1-np.linalg.norm(code.mean(1),axis=-1)).mean()))
        raw.update(raw_norm=norm,angle=angle,unit_norm=unit)
        # Independent fit examples decode unanchored pair differences; probe cannot access content.
        fc=fitout['code'].numpy();fr=fitx['target'].numpy().argsort(1);i,j=np.triu_indices(n,1)
        def pairfeature(v):
            cross=v[:,i,0]*v[:,j,1]-v[:,i,1]*v[:,j,0]
            dot=(v[:,i]*v[:,j]).sum(-1)
            return np.stack((cross,dot),-1)
        pf=ridge_fit(pairfeature(fc),(fr[:,i]<fr[:,j]).astype(float))
        py=ridge_apply(pairfeature(code),pf)>=.5
        row['unanchored_pairwise_decoding']=float((py==(rank[:,i]<rank[:,j])).mean())
    else:coordinate=out['coordinate'].numpy()
    row['code_pairwise_decoding']=mean(metrics(coordinate.argsort(1),target))['pairwise_accuracy']
    row['code_rank_spearman']=float(corr(coordinate.argsort(1).argsort(1).astype(float),rank).mean())
    raw['coordinate']=coordinate
    return row,raw


@torch.no_grad()
def causal(model,n):
    model.eval();x=batch(np.random.default_rng(910000+n),1024,n);out=model(x)
    h=out['stages'][-1];code=out['code'];base=out['prediction'].numpy();target=x['target'].numpy();pair=x['target'][:,[0,-1]]
    controls=[('ablation',dict(kind='ablation')),('swap',dict(kind='swap',pair=pair))]
    if model.reader=='scan':controls=[(k,dict(kind=k)) for k in ('normal','freeze','shift','permutation')]+controls
    else:controls.append(('boost',dict(kind='boost',index=pair[:,1])))
    invariances=[('rotation_037',dict(kind='rotation',value=.37)),('rotation_210',dict(kind='rotation',value=2.1))] if model.rep=='phase' else [('affine',dict(kind='affine'))]
    records=[];inv=[];raw=dict(base=base,target=target,code=code.numpy())
    for label,ctl in controls+invariances:
        new=model.decode(h,code,intervention=ctl);pred=new['prediction'].numpy();raw[label]=pred
        expected=None;transformed=None
        if label in ('shift','permutation'):
            schedule=list(range(1,n))+[0] if label=='shift' else [n-1]+list(range(n-1))
            expected=base[:,schedule];transformed=target[:,schedule]
        elif label=='swap':
            i,j=pair.numpy().T
            expected=np.where(base==i[:,None],j[:,None],np.where(base==j[:,None],i[:,None],base))
            transformed=target.copy();transformed[:,[0,-1]]=target[:,[-1,0]]
        row=dict(intervention=label,**changes(pred,base,target,expected))
        if transformed is not None:row['transformed_target_accuracy']=float((pred==transformed).all(1).mean())
        correct=(base==target).all(1)
        if label=='boost':
            _,present,pos=relations(pred,n);_,_,oldpos=relations(base,n);item=pair[:,1].numpy();ii=np.arange(len(pred))
            row['boost_moves_earlier']=float((pos[ii,item]<oldpos[ii,item])[correct].mean()) if correct.any() else None
        if label.startswith('rotation') or label=='affine':
            a,b=new['logits'].numpy(),out['logits'].numpy();valid=(a>-1e8)&(b>-1e8)
            row['max_logit_difference']=float(np.abs(a-b)[valid].max());inv.append(row)
        else:records.append(row)
    return records,inv,raw

import inspect
import numpy as np
import pytest
import torch
from experiment_a.data import batch
from experiment_a.model import FactorialModel
from experiment_a1.model import RepairedModel,CELLS
from experiment_a1.metrics import metrics


@pytest.mark.parametrize('rep',['priority','position','phase'])
def test_scan_slots_and_mask_cannot_replace_cursor(rep):
    m=RepairedModel(rep+'_scan');n=6;h=torch.zeros(3,n,96)
    q=(torch.arange(n)+.5)/n
    code=-torch.arange(n).float() if rep=='priority' else q if rep=='position' else torch.stack((torch.cos(2*torch.pi*q),torch.sin(2*torch.pi*q)),-1)
    code=code.unsqueeze(0).expand(3,*code.shape)
    normal=m.decode(h,code)['prediction'];assert torch.equal(normal,torch.arange(n).expand(3,-1))
    frozen=m.decode(h,code,intervention={'kind':'freeze'})['prediction']
    assert (frozen[:,0]==0).all() and (frozen[:,1:]==-1).all()
    for kind,schedule in [('shift',[1,2,3,4,5,0]),('permutation',[5,0,1,2,3,4])]:
        assert torch.equal(m.decode(h,code,intervention={'kind':kind})['prediction'],normal[:,schedule])
    control={'kind':'rotation','value':2.1} if rep=='phase' else {'kind':'affine'}
    assert torch.equal(m.decode(h,code,intervention=control)['prediction'],normal)


@pytest.mark.parametrize('system',CELLS)
def test_gradients_and_capacity(system):
    torch.manual_seed(11);m=RepairedModel(system);x=batch(np.random.default_rng(51),8,4)
    o=m(x,teacher=True);loss=torch.nn.functional.cross_entropy(o['logits'].flatten(0,1),(x['target']+1).flatten())
    loss.backward();assert torch.isfinite(loss)
    assert torch.isfinite(m.head[-1].weight.grad).all() and m.head[-1].weight.grad.abs().sum()>0
    assert m.counts()==FactorialModel(system).counts()
    assert 'atan2' not in inspect.getsource(RepairedModel)


def test_incomplete_predictions_do_not_get_survivor_accuracy():
    p=np.array([[0,-1,-1,-1],[0,1,2,3]]);t=np.tile(np.arange(4),(2,1));r=metrics(p,t)
    assert r['pairwise_accuracy'].tolist()==[0,1]
    assert np.isnan(r['kendall_tau_present'][0]) and r['kendall_tau_present'][1]==1
    assert r['no_match_rate'].tolist()==[.75,0]


@pytest.mark.parametrize('system',['priority_competitive','position_competitive'])
def test_other_competitive_readouts_unchanged(system):
    torch.manual_seed(4);old=FactorialModel(system).eval()
    new=RepairedModel(system).eval();new.load_state_dict(old.state_dict())
    x=batch(np.random.default_rng(12),16,6)
    with torch.no_grad():a,b=old(x),new(x)
    assert torch.equal(a['prediction'],b['prediction'])
    assert torch.equal(a['logits'],b['logits'][...,1:])


@pytest.mark.parametrize('system',CELLS)
def test_permutation_equivariance_and_code_bottleneck(system):
    m=RepairedModel(system).eval();x=batch(np.random.default_rng(21),8,4);p=torch.tensor([2,0,3,1])
    with torch.no_grad():
        a=m(x);b=m({k:v[:,p] for k,v in x.items() if k!='target'})
        z=b['prediction'];remapped=torch.where(z>=0,p[z.clamp_min(0)],-1)
        assert torch.equal(a['prediction'],remapped)
        assert torch.equal(a['prediction'],m.decode(a['stages'][-1]*0,a['code'])['prediction'])

import numpy as np
import pytest
import torch
from experiment_a.data import batch
from experiment_a1.model import RepairedModel
from experiment_a4.run import ARMS,jobs,objective,regression_loss


def test_job_matrix():
    assert len(jobs())==168 and len(set(jobs()))==168


@pytest.mark.parametrize('system',['priority_scan','position_scan','phase_scan','position_competitive'])
def test_beta_one_is_a1_loss_and_beta_keeps_reader(system):
    torch.manual_seed(3);m=RepairedModel(system);x=batch(np.random.default_rng(5),8,6)
    out=m(x,teacher=True)
    a1=torch.nn.functional.cross_entropy(out['logits'].flatten(0,1),(x['target']+1).flatten())
    assert torch.equal(objective(m,x,'ce',1.),a1)
    assert torch.equal((16*out['logits']).argmax(-1),out['logits'].argmax(-1))


@pytest.mark.parametrize('rep',['priority','position','phase'])
def test_regression_zero_at_reference_codes(rep):
    m=RepairedModel(rep+'_scan');n=6;target=torch.tensor([[2,0,5,1,4,3]])
    rank=target.argsort(1).float();q=(rank+.5)/n
    if rep=='phase':c=torch.stack((torch.cos(2*torch.pi*q),torch.sin(2*torch.pi*q)),-1)
    else:c=q
    assert regression_loss(m,dict(coordinate=c),target).item()<1e-10
    assert regression_loss(m,dict(coordinate=c+(.01 if rep!='phase' else 0)*torch.ones_like(c) if rep!='phase' else -c),target).item()>0


def test_regression_gradient_reaches_head():
    torch.manual_seed(1);m=RepairedModel('position_scan');x=batch(np.random.default_rng(2),4,6)
    objective(m,x,'reg',None).backward()
    assert m.head[0].weight.grad.abs().sum()>0

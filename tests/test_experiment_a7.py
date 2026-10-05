import numpy as np
import pytest
import torch
from experiment_a.data import batch
from experiment_a1.model import RepairedModel
from experiment_a7.model import WidthModel,EncoderModel
from experiment_a7.run import jobs,ARMS


def test_job_matrix():
    assert len(jobs())==144 and len(set(jobs()))==144


@pytest.mark.parametrize('system',['priority_scan','position_scan','phase_scan','position_competitive'])
def test_g0a_width_045_reproduces_a1_reader(system):
    torch.manual_seed(7);a=RepairedModel(system).eval()
    torch.manual_seed(7);b=WidthModel(system,.45).eval()
    x=batch(np.random.default_rng(3),16,6)
    for teacher in (False,True):
        with torch.no_grad():ra,rb=a(x,teacher=teacher),b(x,teacher=teacher)
        assert torch.equal(ra['prediction'],rb['prediction']) and torch.equal(ra['logits'],rb['logits'])


@pytest.mark.parametrize('system',['priority_scan','phase_scan'])
def test_g0b_encoder_96_2_reproduces_a1_model(system):
    torch.manual_seed(5);a=RepairedModel(system).eval()
    torch.manual_seed(5);b=EncoderModel(system,96,2).eval()
    assert all(torch.equal(p,q) for p,q in zip(a.state_dict().values(),b.state_dict().values()))
    x=batch(np.random.default_rng(4),8,6)
    with torch.no_grad():assert torch.equal(a(x)['logits'],b(x)['logits'])


def test_width_changes_acceptance_only_at_boundary():
    m=WidthModel('position_scan',.75);n=6;h=torch.zeros(1,n,96)
    q=(torch.arange(n)+.5)/n;code=(q+.6/n).unsqueeze(0)  # offset .6/N: outside .45/N, inside .75/N
    assert torch.equal(m.decode(h,code)['prediction'],torch.arange(n).unsqueeze(0))
    narrow=WidthModel('position_scan',.45).decode(h,code)['prediction']
    # At .45/N the displaced item is rejected at its own slot and captured one slot late.
    assert narrow[0,0]==-1 and torch.equal(narrow[0,1:],torch.arange(n-1))


def test_large_encoder_shapes():
    m=EncoderModel('position_scan',192,4);x=batch(np.random.default_rng(1),2,6)
    assert m(x)['code'].shape==(2,6) and m.counts()['total']>164162

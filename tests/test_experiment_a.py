import numpy as np
import pytest
import torch
from experiment_a.data import batch
from experiment_a.model import FactorialModel, SYSTEMS
from experiment_a.evaluate import metrics


def test_order_metrics_have_correct_denominators():
    pred=np.array([[0,2,1],[0,1,2]])
    target=np.array([[0,1,2],[0,1,2]])
    result=metrics(pred,target)
    assert np.allclose(result['pairwise_accuracy'],[2/3,1])
    assert np.allclose(result['kendall_tau'],[1/3,1])
    assert result['first_error'].tolist()==[1,3]
    assert result['exact_accuracy'].tolist()==[0,1]


def test_data_balance():
    x = batch(np.random.default_rng(541), 4096, 6)
    assert all(len(set(row)) == 6 for row in x['ids'].tolist())
    assert torch.equal(x['target'], x['numeric'][..., 0].argsort(1))
    ranks = x['target'].argsort(1).numpy()
    assert abs(np.corrcoef(x['ids'].numpy().ravel(), ranks.ravel())[0, 1]) < .04
    assert max(abs(np.bincount(x['target'][:, 0], minlength=6)/4096-1/6)) < .025


@pytest.mark.parametrize('system', SYSTEMS)
def test_equivariance_mask_counts(system):
    torch.manual_seed(11); m = FactorialModel(system).eval()
    x = batch(np.random.default_rng(5), 8, 6)
    p = torch.tensor([4, 1, 3, 0, 5, 2])
    y = {k: v[:, p] for k, v in x.items() if k != 'target'}
    with torch.no_grad(): a, b = m(x), m(y)
    assert torch.equal(a['prediction'], p[b['prediction']])
    assert torch.equal(a['prediction'].sort(1).values, torch.arange(6).expand(8, -1))
    assert m.counts()['total'] == FactorialModel('reference').counts()['total']


@pytest.mark.parametrize('system', SYSTEMS[:-1])
def test_code_causality_invariance_bottleneck(system):
    m = FactorialModel(system).eval(); h = torch.randn(4, 6, 96)
    c = torch.tensor([.08, .23, .4, .57, .72, .91]).expand(4, -1)
    code = -c if m.rep == 'priority' else c*2*np.pi if m.rep == 'phase' else c
    a = m.decode(h, code)
    pair = a['prediction'][:, [0, -1]]
    b = m.decode(h*100, code, intervention={'kind': 'swap', 'pair': pair})
    expected = a['prediction'].clone(); expected[:, 0], expected[:, -1] = a['prediction'][:, -1], a['prediction'][:, 0]
    assert torch.equal(b['prediction'], expected)
    inv = {'kind': 'rotation', 'value': 2.1} if m.rep == 'phase' else {'kind': 'affine'}
    assert torch.equal(a['prediction'], m.decode(h, code, intervention=inv)['prediction'])
    assert torch.equal(a['prediction'], m.decode(h*100, code)['prediction'])
    assert torch.equal(a['prediction'], m.decode(h, code, intervention={'kind': 'score_offset'})['prediction'])
    control = {'kind': 'boost', 'index': a['prediction'][:, -1]} if m.reader == 'competitive' else {'kind': 'cursor'}
    changed = m.decode(h, code, intervention=control)['prediction']
    assert (changed[:, 0] != a['prediction'][:, 0]).all()


@pytest.mark.parametrize('system', SYSTEMS)
def test_loss_gradients(system):
    m = FactorialModel(system); x = batch(np.random.default_rng(55), 8, 4)
    info = m(x, teacher=True)
    loss = torch.nn.functional.cross_entropy(info['logits'].flatten(0, 1), x['target'].flatten())
    loss.backward()
    assert torch.isfinite(loss)
    assert torch.isfinite(m.head[-1].weight.grad).all()
    assert m.head[-1].weight.grad.abs().sum() > 0

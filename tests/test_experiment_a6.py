import numpy as np
import torch
from experiment_a.data import batch
from experiment_a1.model import RepairedModel
from experiment_a6.run import jobs,target_only_loss


def test_job_matrix():
    assert len(jobs())==144 and len(set(jobs()))==144


def test_target_only_ignores_distractors_and_is_minimized_at_slot_centres():
    torch.manual_seed(0);m=RepairedModel('position_scan');x=batch(np.random.default_rng(1),4,6)
    out=m(x,teacher=True);cls=x['target']+1
    two=torch.stack((out['logits'][...,0],out['logits'].gather(2,cls.unsqueeze(-1)).squeeze(-1)),-1)
    ref=torch.nn.functional.cross_entropy(two.flatten(0,1),torch.ones(two.shape[:2],dtype=torch.long).flatten())
    assert torch.allclose(target_only_loss(m,x),ref,atol=1e-6)
    # With distractors removed, slot-centred codes are a stationary point (no displacement pressure).
    n=6;w=.45/n;q=(torch.arange(n,dtype=torch.float64)+.5)/n;c=q.clone().requires_grad_(True)
    loss=sum(torch.logsumexp(torch.stack((torch.tensor(-16*w*w,dtype=torch.float64),-16*(c[t]-q[t])**2)),0)+16*(c[t]-q[t])**2 for t in range(n))
    loss.backward();assert c.grad.abs().max()<1e-12

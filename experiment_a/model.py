import math
import torch
from torch import nn
from pbos.models.transformer import SetLayer

SYSTEMS = [f'{r}_{o}' for r in ('priority', 'position', 'phase') for o in ('competitive', 'scan')] + ['reference']


class FactorialModel(nn.Module):
    def __init__(self, system):
        super().__init__()
        assert system in SYSTEMS
        self.system = system
        self.rep, self.reader = system.split('_') if system != 'reference' else ('distributed', 'scorer')
        self.symbol = nn.Embedding(33, 96)
        self.type_embedding = nn.Embedding(5, 96)
        self.numeric = nn.Linear(10, 96)
        self.encoder = nn.ModuleList([SetLayer(96, 4) for _ in range(2)])
        self.head = nn.Sequential(nn.Linear(100, 96), nn.GELU(), nn.Linear(96, 2))

    def counts(self):
        head = sum(p.numel() for p in self.head.parameters())
        total = sum(p.numel() for p in self.parameters())
        return dict(total=total, backbone=total-head,
                    representation=head if self.system != 'reference' else 0,
                    readout=head if self.system == 'reference' else 0, adapter=0)

    def encode(self, x):
        h = self.symbol(x['ids']) + self.type_embedding(torch.full_like(x['ids'], 2)) + self.numeric(x['numeric'])
        stages = [h]
        for layer in self.encoder:
            h, _ = layer(h)
            stages.append(h)
        return stages

    def code(self, h, step=None, used=None):
        n = h.shape[1]
        f = torch.zeros((*h.shape[:2], 4), device=h.device)
        f[..., 0] = n/10
        if step is not None:
            f[..., 1], f[..., 2], f[..., 3] = step/n, (step/n)**2, used.float()
        z = self.head(torch.cat((h, f), -1))
        if self.rep == 'phase':
            return torch.atan2(z[..., 1], z[..., 0])
        p = z[..., 0] - z[..., 1]
        return p.sigmoid() if self.rep == 'position' else p

    def coordinates(self, code, transform=None):
        transform = transform or {}
        k = transform.get('kind')
        if self.rep == 'priority':
            if k == 'affine': code = 2*code+3
            span = code.max(1, keepdim=True).values-code.min(1, keepdim=True).values
            return (code.max(1, keepdim=True).values-code)/span.clamp_min(1e-7)
        if self.rep == 'position':
            if k == 'affine': return ((2*code+3)-3)/2
            return code
        anchor = 0.
        if k in ('rotation', 'items_rotation'):
            code = code+transform.get('value', .37)
            if k == 'rotation': anchor = transform.get('value', .37)
        return torch.remainder(code-anchor, 2*math.pi)/(2*math.pi)

    def decode(self, h, code, target=None, intervention=None):
        ctl = intervention or {}
        b, n = h.shape[:2]
        used = torch.zeros((b, n), dtype=torch.bool, device=h.device)
        if code is not None:
            code = code.clone()
            if ctl.get('kind') == 'swap':
                rows = torch.arange(b); i, j = ctl['pair'].unbind(1)
                old = code.clone(); code[rows, i], code[rows, j] = old[rows, j], old[rows, i]
            elif ctl.get('kind') == 'ablation': code = code*0
            c = self.coordinates(code, ctl)
        else: c = None
        preds, logits, margins = [], [], []
        for step in range(n):
            if self.reader == 'scorer': s = self.code(h, step, used)
            elif self.reader == 'competitive': s = -16*c
            else:
                q = (step+.5)/n
                if ctl.get('kind') == 'cursor' and step == 0: q += 1/n
                d = c-q
                if self.rep == 'phase': d = torch.remainder(d+.5, 1)-.5
                s = -16*d.square()
            if ctl.get('kind') == 'boost' and step == 0:
                s = s.clone(); s.scatter_(1, ctl['index'][:, None], s.max(1).values[:, None]+10)
            if ctl.get('kind') == 'score_offset': s = s+3
            s = s.masked_fill(used, -1e9)
            chosen = s.argmax(1)
            logits.append(s); preds.append(chosen)
            if step < n-1: margins.append(s.topk(2, 1).values.diff(dim=1).abs()[:, 0])
            used = used.scatter(1, (chosen if target is None else target[:, step])[:, None], True)
        return dict(logits=torch.stack(logits, 1), prediction=torch.stack(preds, 1),
                    code=code, coordinate=c, margin=torch.stack(margins, 1).mean(1))

    def forward(self, x, teacher=False, intervention=None):
        stages = self.encode(x)
        code = None if self.system == 'reference' else self.code(stages[-1])
        info = self.decode(stages[-1], code, x['target'] if teacher else None, intervention)
        info['stages'] = stages
        return info

"""Small permutation-invariant set-to-ordered-slots Transformer."""
import torch
from torch import nn
from pbos.data.generator import VOCAB, KEYS


class SetLayer(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.norm1 = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, heads, dropout=0, batch_first=True)
        self.norm2 = nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d,2*d), nn.GELU(), nn.Linear(2*d,d))

    def forward(self, h):
        z = self.norm1(h)
        msg, weights = self.attn(z,z,z,need_weights=True,average_attn_weights=True)
        h = h + msg
        return h + self.ff(self.norm2(h)), weights


class Transformer(nn.Module):
    def __init__(self, d=192, layers=2, heads=4):
        super().__init__()
        self.d, self.layers = d, layers
        self.a = nn.Embedding(VOCAB,d)
        self.b = nn.Embedding(VOCAB,d)
        self.key = nn.Linear(1,d)
        self.context = nn.Linear(3*d,d)
        self.types = nn.Parameter(torch.zeros(3,d))
        nn.init.normal_(self.types, std=.02)
        self.encoder = nn.ModuleList([SetLayer(d,heads) for _ in range(layers)])
        self.query = nn.Sequential(nn.Linear(4,d), nn.GELU(), nn.Linear(d,d))
        self.decoder = nn.TransformerDecoderLayer(d,heads,dim_feedforward=2*d,
                         dropout=0,activation='gelu',batch_first=True,norm_first=True)
        self.output = nn.Linear(d,2*VOCAB)

    def embed(self, objects):
        a, b = self.a(objects[...,0]), self.b(objects[...,1])
        k = self.key(objects[...,2:].float() / (KEYS-1))
        context = self.context(torch.cat((a,b,k),-1))
        return (torch.stack((a,b,k),2) + context[:,:,None] + self.types).flatten(1,2)

    def phase_start(self, h):
        return None

    def phase_step(self, h, phi, weights, layer, intervention):
        return h, phi, weights

    def forward(self, objects, intervention=None, diagnostics=False):
        if objects[...,2].min() < 0:
            raise NotImplementedError('Relation-chain model not implemented')
        b, n, _ = objects.shape
        h = self.embed(objects)
        phi = self.phase_start(h)
        phases = [] if phi is None else [phi.reshape(b,n,3,-1)]
        couplings = []
        for i, layer in enumerate(self.encoder):
            h, w = layer(h)
            h, phi, j = self.phase_step(h,phi,w,i,intervention)
            if phi is not None:
                phases.append(phi.reshape(b,n,3,-1))
                couplings.append(j)
        rank = torch.arange(n,device=h.device,dtype=h.dtype) / max(n-1,1)
        q = torch.stack((rank,rank.square(),torch.full_like(rank,n/12),torch.ones_like(rank)),-1)
        q = self.query(q).unsqueeze(0).expand(b,-1,-1)
        logits = self.output(self.decoder(q,h)).reshape(b,n,2,VOCAB)
        info = {}
        if diagnostics and phases:
            info = {'phi':torch.stack(phases), 'coupling':torch.stack(couplings)}
        return logits, info


def parameter_count(model):
    return sum(p.numel() for p in model.parameters())

import math
import torch
from torch import nn
from experiment_a.model import SYSTEMS
from experiment_a1.model import RepairedModel
from pbos.models.transformer import SetLayer


class WidthModel(RepairedModel):
    """RepairedModel whose Scan capture radius is width/N (A.1 uses .45). Normal decoding only, no interventions."""
    def __init__(self, system, width=.45):
        super().__init__(system);self.width=width

    def decode(self,h,code,target=None,intervention=None):
        assert intervention is None
        if self.reader!='scan':return super().decode(h,code,target)
        b,n=h.shape[:2];rows=torch.arange(b,device=h.device)
        c=code if self.rep=='phase' else self.coordinates(code,{})
        if self.rep=='priority':c=.5/n+(1-1/n)*c
        used=torch.zeros((b,n),dtype=torch.bool,device=h.device);logits=[];pred=[];radius=self.width/n
        for t in range(n):
            q=(t+.5)/n
            if self.rep=='phase':
                cursor=c.new_tensor([math.cos(2*math.pi*q),math.sin(2*math.pi*q)])
                d2=(c-cursor).square().sum(-1)/(4*math.pi**2);boundary=(math.sin(math.pi*radius)/math.pi)**2
            else:d2=(c-q).square();boundary=radius**2
            s=(-16*d2).masked_fill(used,-1e9)
            s=torch.cat((s.new_full((b,1),-16*boundary),s),1)
            k=s.argmax(1)-1;pred.append(k);logits.append(s)
            emitted=k if target is None else target[:,t]
            valid=emitted>=0;used=used.clone();used[rows[valid],emitted[valid]]=True
        return dict(prediction=torch.stack(pred,1),logits=torch.stack(logits,1),code=code,coordinate=c)


class EncoderModel(RepairedModel):
    """RepairedModel with encoder width d and depth L; modules are created in FactorialModel order so d=96, L=2 is identical."""
    def __init__(self, system, d=96, layers=2):
        nn.Module.__init__(self)
        assert system in SYSTEMS
        self.system=system;self.rep,self.reader=system.split('_')
        self.symbol=nn.Embedding(33,d);self.type_embedding=nn.Embedding(5,d);self.numeric=nn.Linear(10,d)
        self.encoder=nn.ModuleList([SetLayer(d,4) for _ in range(layers)])
        self.head=nn.Sequential(nn.Linear(d+4,d),nn.GELU(),nn.Linear(d,2))

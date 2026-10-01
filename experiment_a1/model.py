import math
import torch
from experiment_a.model import FactorialModel

CELLS=['priority_scan','position_scan','phase_scan','phase_competitive']


class RepairedModel(FactorialModel):
    """Only slot eligibility and continuous phase geometry differ from A."""
    def raw(self,h):
        f=torch.zeros((*h.shape[:2],4),device=h.device);f[...,0]=h.shape[1]/10
        return self.head(torch.cat((h,f),-1))

    def code(self,h,step=None,used=None):
        if self.rep!='phase':return super().code(h,step,used)
        v=self.raw(h)
        return v/torch.sqrt(v.square().sum(-1,keepdim=True)+1e-8)

    def decode(self,h,code,target=None,intervention=None):
        ctl=intervention or {};kind=ctl.get('kind');b,n=h.shape[:2]
        code=code.clone();rows=torch.arange(b,device=h.device)
        if kind=='swap':
            i,j=ctl['pair'].unbind(1);old=code.clone();code[rows,i],code[rows,j]=old[rows,j],old[rows,i]
        if kind=='ablation':
            code=code*0
            if self.rep=='phase':code[...,0]=1
        angle=ctl.get('value',0.) if kind=='rotation' else 0.
        if self.rep=='phase':
            rotation=code.new_tensor([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
            c=code@rotation.T
            ref=code.new_tensor([math.cos(angle),math.sin(angle)])
        else:
            c=self.coordinates(code,ctl)
            if self.rep=='priority' and self.reader=='scan':c=.5/n+(1-1/n)*c
        slots=list(range(n))
        if kind=='freeze':slots=[0]*n
        elif kind=='shift':slots=slots[1:]+slots[:1]
        elif kind=='permutation':slots=slots[-1:]+slots[:-1]
        used=torch.zeros((b,n),dtype=torch.bool,device=h.device);logits=[];pred=[]
        radius=.45/n
        for t,slot in enumerate(slots):
            if self.reader=='competitive':
                s=8*((c*ref).sum(-1)-1) if self.rep=='phase' else -16*c
                null=-1e9
                if kind=='boost' and t==0:
                    s=s.clone();s.scatter_(1,ctl['index'][:,None],s.max(1).values[:,None]+10)
            else:
                q=(slot+.5)/n
                if self.rep=='phase':
                    cursor=c.new_tensor([math.cos(2*math.pi*q+angle),math.sin(2*math.pi*q+angle)])
                    d2=(c-cursor).square().sum(-1)/(4*math.pi**2)
                    boundary=(math.sin(math.pi*radius)/math.pi)**2
                else:d2=(c-q).square();boundary=radius**2
                s=-16*d2;null=-16*boundary
            s=s.masked_fill(used,-1e9)
            # Null first: exact boundary ties reject, never fall back to an invalid item.
            s=torch.cat((s.new_full((b,1),null),s),1)
            k=s.argmax(1)-1;pred.append(k);logits.append(s)
            emitted=k if target is None else target[:,t]
            valid=emitted>=0;used=used.clone();used[rows[valid],emitted[valid]]=True
        return dict(prediction=torch.stack(pred,1),logits=torch.stack(logits,1),code=code,coordinate=c)

    def forward(self,x,teacher=False,intervention=None):
        h=self.encode(x);out=self.decode(h[-1],self.code(h[-1]),x['target'] if teacher else None,intervention)
        out['stages']=h
        if self.rep=='phase':out['raw_norm']=self.raw(h[-1]).norm(dim=-1)
        return out

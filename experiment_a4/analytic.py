"""Code-space analysis of the A.1 Scan training objective and raw-key baselines (NumPy/SciPy; no model)."""
import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

OUT=Path('results/experiment_A4')


def scores(x,n,family):
    """Teacher-forced Scan logits per step, index 0 = NO_MATCH, index 1 = target; earlier items masked."""
    q=(np.arange(n)+.5)/n;w=.45/n
    if family=='phase':
        b=(math.sin(math.pi*w)/math.pi)**2
        return [np.concatenate([[-16*b],-16*(2-2*np.cos(x[t:]-2*np.pi*q[t]))/(4*np.pi**2)]) for t in range(n)]
    c=x
    if family=='priority':c=(x.max()-x)/(x.max()-x.min());c=.5/n+(1-1/n)*c
    return [np.concatenate([[-16*w*w],-16*(c[t:]-q[t])**2]) for t in range(n)]


def loss(x,n,family,beta):
    return sum(-beta*s[1]+np.log(np.exp(beta*s).sum()) for s in scores(x,n,family))


def coordinate(x,n,family):
    if family=='priority':return .5/n+(1-1/n)*(x.max()-x)/(x.max()-x.min())
    if family=='phase':return np.mod(x,2*np.pi)/(2*np.pi)
    return x


def scan_exact(c,n,family):
    q=(np.arange(n)+.5)/n;w=.45/n;used=np.zeros(n,bool)
    for t in range(n):
        if family=='phase':d=(2-2*np.cos(2*np.pi*(c-q[t])))/(4*np.pi**2);b=(math.sin(math.pi*w)/math.pi)**2
        else:d=(c-q[t])**2;b=w*w
        d=np.where(used,np.inf,d);j=int(d.argmin())
        if not (d[j]<b and j==t):return False
        used[j]=True
    return True


def optimum(n,family,beta,rng):
    q=(np.arange(n)+.5)/n
    if family=='phase':x0,bounds=lambda:2*np.pi*q+rng.normal(0,.05,n),None
    elif family=='priority':x0,bounds=lambda:-q+rng.normal(0,.02,n),None
    else:x0,bounds=lambda:np.clip(q+rng.normal(0,.02,n),1e-3,1-1e-3),[(1e-4,1-1e-4)]*n
    best=min((minimize(loss,x0(),args=(n,family,beta),bounds=bounds) for _ in range(8)),key=lambda r:r.fun)
    c=coordinate(best.x,n,family);off=c-q
    if family=='phase':off=(off+.5)%1-.5
    centre=2*np.pi*q if family=='phase' else (-q if family=='priority' else q)
    return off/(.45/n),scan_exact(c,n,family),best.fun,loss(centre,n,family,beta)


def main():
    OUT.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(2);rows=[]
    for beta in (1,2,4,8,16):
        for n in (4,6,8):
            for family in ('priority','position','phase'):
                off,ok,lopt,lcen=optimum(n,family,beta,rng)
                rows.append(dict(beta=beta,n=n,family=family,max_abs_offset_w=round(float(np.abs(off).max()),4),
                                 offsets_w=' '.join(f'{v:.3f}' for v in off),optimum_scan_exact=ok,
                                 loss_optimum=round(lopt,5),loss_slot_centres=round(lcen,5)))
    with open(OUT/'analytic_objective_optimum.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    base=[]
    for n in (4,6,8):
        base.append(dict(n=n,position_raw_key=math.factorial(n)*(.9/n)**n,priority_raw_key=math.factorial(n-2)*(.9/(n-1))**(n-2),competitive_raw_key=1.0))
    with open(OUT/'raw_key_baseline.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(base[0]));w.writeheader();w.writerows(base)
    for r in rows:
        if r['beta'] in (1,4,16):print(r['beta'],r['n'],r['family'],r['max_abs_offset_w'],r['optimum_scan_exact'])
    print(base)


if __name__=='__main__':main()

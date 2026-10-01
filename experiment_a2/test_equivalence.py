"""Run with the existing pinned PyTorch image; never trains or changes weights."""
import json
import numpy as np
import torch
from experiment_a1.model import RepairedModel
from experiment_a2.analysis import decode, REPS, READERS, LENGTHS


def main():
    torch.set_num_threads(2)
    rng=np.random.default_rng(909)
    checked=0
    for n in LENGTHS:
        for rep in REPS:
            code=rng.uniform(-1,1,(128,n)).astype('float32')
            if rep=='position':code=(code+1)/2
            if rep=='phase':
                a=code*np.pi;code=np.stack([np.cos(a),np.sin(a)],-1)
            for reader in READERS:
                model=RepairedModel(f'{rep}_{reader}')
                for kind,slots in [(None,None),('freeze',[0]*n),('shift',list(range(1,n))+[0]),('permutation',[n-1]+list(range(n-1)))]:
                    if reader=='competitive' and kind:continue
                    pred,_=decode(code,rep,reader,slots)
                    with torch.no_grad():
                        actual=model.decode(torch.zeros(128,n,96),torch.from_numpy(code),intervention={'kind':kind})['prediction'].numpy()
                    assert np.array_equal(pred,actual),(n,rep,reader,kind)
                    checked+=1
    print(json.dumps({'randomized_frozen_decoder_panels':checked,'trials_per_panel':128,'status':'PASS','training_runs':0}))


if __name__=='__main__':main()

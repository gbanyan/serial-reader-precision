import unittest
import numpy as np
from experiment_a2.analysis import oracle, decode, error, LENGTHS


class OracleContracts(unittest.TestCase):
    def test_scan_permutation_and_no_fallback(self):
        for n in LENGTHS:
            rank=np.arange(n)[None,:]; slots=list(range(0,n,2))+list(range(1,n,2))
            for rep in ('priority','position','phase'):
                code=oracle(rank,rep)
                self.assertTrue(np.array_equal(decode(code,rep,'scan')[0],rank))
                self.assertTrue(np.array_equal(decode(code,rep,'scan',slots)[0],rank[:,slots]))
                self.assertTrue(np.array_equal(decode(code,rep,'scan',[0]*n)[0],np.array([[0]+[-1]*(n-1)])))

    def test_phase_cosine_is_not_full_circle_order(self):
        for n in LENGTHS:
            rank=np.arange(n)[None,:]; pred,_=decode(oracle(rank,'phase'),'phase','competitive')
            self.assertFalse(np.array_equal(pred,rank))

    def test_allowed_alignment_removes_only_common_transform(self):
        rank=np.array([[2,0,3,1]])
        for rep in ('priority','position'):
            ideal=oracle(rank,rep); transformed=ideal*2+3
            self.assertLess(error(transformed,ideal,rep,True).max(),1e-12)
        ideal=oracle(rank,'phase'); angle=.73
        rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        self.assertLess(error(ideal@rot.T,ideal,'phase',True).max(),1e-12)

    def test_metric_failure_without_rank_inversion(self):
        n=6; rank=np.arange(n)[None,:]; shifted=oracle(rank,'position')+.46/n
        self.assertTrue(np.array_equal(decode(shifted,'position','competitive')[0],rank))
        self.assertTrue((decode(shifted,'position','scan')[0]==-1).all())


if __name__=='__main__':unittest.main()

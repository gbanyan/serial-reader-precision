import unittest
import numpy as np
from experiment_a2.analysis import oracle,decode
from experiment_a3.analyze import geometric,phase_arc,snap


class GeometryAudit(unittest.TestCase):
    def test_oracle_geometry_and_arc(self):
        for n in (4,6):
            target=np.arange(n)[None,:]
            for rep in ('priority','position','phase'):
                code=oracle(target,rep);g,_=geometric(code,rep,'scan',target)
                self.assertLess(g['canonical_rmse'][0],1e-7)
                self.assertEqual(g['slot_capture'][0],1)
                if rep=='phase':self.assertAlmostEqual(g['arc_fraction'][0],1-1/n)

    def test_semicircle_readout_direction(self):
        target=np.array([[2,0,3,1]]);rank=np.argsort(target,1)
        code=phase_arc(rank,np.array([np.pi]))
        self.assertTrue(np.array_equal(decode(code,'phase','competitive')[0],target))

    def test_snap_retains_collisions(self):
        code=np.array([[.125,.14,.625,.875]])
        snapped=snap(code,'position')
        self.assertEqual(snapped[0,0],snapped[0,1])
        self.assertTrue((decode(snapped,'position','scan')[0]<0).any())

    def test_rotation_alignment_does_not_hide_projection_change(self):
        target=np.arange(4)[None,:];code=oracle(target,'phase')
        g,_=geometric(code,'phase','scan',target)
        rotated=-code;h,_=geometric(rotated,'phase','scan',target)
        self.assertAlmostEqual(g['canonical_rmse'][0],h['canonical_rmse'][0])
        self.assertGreater(h['slot_rmse'][0],g['slot_rmse'][0]+1)

if __name__=='__main__':unittest.main()

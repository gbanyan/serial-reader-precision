import numpy as np
from experiment_a.inspect_codes import decode
from experiment_a.report import fstat


def test_interaction_ignores_common_seed_and_global_readout_shifts():
    rng=np.random.default_rng(81);d=rng.normal(size=(8,3))
    assert np.isclose(fstat(d), fstat(d+np.arange(8)[:,None]+5))
    assert np.isclose(fstat(d), fstat(d[:,[2,0,1]]))


def test_interaction_detects_nonparallel_difference_profiles():
    rng=np.random.default_rng(81);d=rng.normal(scale=.01,size=(8,3))
    assert fstat(d+np.array([0,.1,.3]))>100


def test_frozen_scan_can_reduce_to_masked_sort():
    c=np.array([[.3,.5,.7,.9]])
    assert np.array_equal(decode(c,'scan',frozen=True),np.argsort(c,axis=1))
    # A phase circle needs a moving reference: static nearest-neighbor distance is not total order.
    c=np.array([[.125,.375,.625,.875]])
    assert not np.array_equal(decode(c,'scan',phase=True),decode(c,'scan',phase=True,frozen=True))

import numpy as np
import torch

VERSION = 'experiment-a-scalar-v1'


def batch(rng, size, n):
    ids = np.stack([rng.choice(32, n, replace=False) for _ in range(size)])
    keys = rng.uniform(0, 1, (size, n)).astype(np.float32)
    # Independent presentation permutation: identity, key, target correspondence move together.
    perm = np.stack([rng.permutation(n) for _ in range(size)])
    ids = np.take_along_axis(ids, perm, 1)
    keys = np.take_along_axis(keys, perm, 1)
    numeric = np.zeros((size, n, 10), np.float32)
    numeric[..., 0] = keys
    return dict(ids=torch.from_numpy(ids), numeric=torch.from_numpy(numeric),
                target=torch.from_numpy(np.argsort(keys, axis=1)))

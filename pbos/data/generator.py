"""PBOS-v1: independent keys/presentation and atomic typed symbols."""
from dataclasses import dataclass
import numpy as np

VERSION = 'pbos-v1'
VOCAB = 16
KEYS = 32


@dataclass
class Sample:
    objects: np.ndarray
    target: np.ndarray
    relations: np.ndarray
    serialization_level: int = 1


def pair_allowed(a, b, split):
    return split == 'all' or (((a + b) % 4 == 0) == (split == 'heldout'))


def generate(rng, n, ambiguity='low', serialization_level=1,
             delay_length=0, num_distractors=0, split='all'):
    if delay_length or num_distractors:
        raise NotImplementedError('Delay/distractors reserved; disabled in v1')
    if not 2 <= n <= 12 or ambiguity not in ('low', 'medium', 'high'):
        raise ValueError('Unsupported load or ambiguity')
    if split not in ('all', 'train', 'heldout') or serialization_level not in (1, 2):
        raise ValueError('Invalid split/serialization')
    if n == 2 and ambiguity == 'high':
        raise ValueError('Two unique pairs cannot repeat both features')
    for _ in range(10000):
        if ambiguity == 'high':
            k = int(np.ceil(np.sqrt(n)))
            if split == 'heldout':
                r = rng.integers(4)
                aa = rng.choice(np.arange(r, VOCAB, 4), k, replace=False)
                bb = rng.choice(np.arange((-r) % 4, VOCAB, 4), k, replace=False)
            else:
                aa = rng.choice(VOCAB, k, replace=False)
                bb = rng.choice(VOCAB, k, replace=False)
            grid = np.array([(a, b) for a in aa for b in bb
                             if pair_allowed(a, b, split)])
            if len(grid) < n:
                continue
            pairs = grid[rng.choice(len(grid), n, replace=False)]
            # Majority of occurrences of BOTH features must be ambiguous.
            if any(sum((pairs[:, j] == v).sum() > 1 for v in pairs[:, j]) / n < .75
                   for j in (0, 1)):
                continue
        else:
            size = n if ambiguity == 'low' else (n + 1) // 2
            aa = rng.choice(VOCAB, size, replace=False)
            aa = aa if ambiguity == 'low' else np.resize(aa, n)
            bb, available = [], list(range(VOCAB))
            for a in aa:
                candidates = [b for b in available if pair_allowed(a, b, split)]
                if not candidates:
                    break
                b = int(rng.choice(candidates))
                bb.append(b)
                available.remove(b)
            if len(bb) != n:
                continue
            pairs = np.column_stack((aa, bb))
        keys = rng.choice(KEYS, n, replace=False)
        obj = np.column_stack((pairs, keys))
        obj = obj[rng.permutation(n)]
        order = np.argsort(obj[:, 2])
        target = obj[order, :2].copy()
        edges = np.column_stack((order[:-1], order[1:]))
        if serialization_level == 2:
            # Object keys are hidden. Only chain edges define the target order.
            obj[:, 2] = -1
        return Sample(obj, target, edges, serialization_level)
    raise ValueError('Cannot satisfy requested ambiguity/split within 10000 attempts')


def batch(rng, size, n, ambiguity, **kwargs):
    samples = [generate(rng, n, ambiguity, **kwargs) for _ in range(size)]
    if any(s.serialization_level != 1 for s in samples):
        raise NotImplementedError('Current tensor/model interface supports scalar sorting only')
    return np.stack([s.objects for s in samples]), np.stack([s.target for s in samples])

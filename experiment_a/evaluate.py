import math
import numpy as np
import torch
from .data import batch


def metrics(pred, target):
    n = pred.shape[1]
    a, b = np.argsort(pred, axis=1), np.argsort(target, axis=1)
    i, j = np.triu_indices(n, 1)
    pair = ((a[:, i]-a[:, j])*(b[:, i]-b[:, j]) > 0).mean(1)
    exact = (pred == target).all(1)
    return dict(exact_accuracy=exact.astype(float), pairwise_accuracy=pair,
                kendall_tau=2*pair-1, first_error=np.where(exact, n, (pred != target).argmax(1)),
                omission_rate=np.zeros(len(pred)), duplication_rate=np.zeros(len(pred)), invalid_rate=np.zeros(len(pred)))


def average(row):
    return {k: float(np.mean(v)) for k, v in row.items()}


def feature(code, rep):
    if rep == 'phase': return np.stack((np.cos(code), np.sin(code)), -1)
    return code[..., None]


def ridge_fit(f, y):
    x = f.reshape(-1, f.shape[-1]); mu, sd = x.mean(0), x.std(0).clip(1e-6)
    x = np.c_[np.ones(len(x)), (x-mu)/sd]
    w = np.linalg.solve(x.T@x+1e-3*np.eye(x.shape[1]), x.T@y.ravel())
    return mu, sd, w


def ridge_apply(f, fit):
    mu, sd, w = fit
    return w[0]+((f-mu)/sd)@w[1:]


def corr(x, y):
    x, y = x-x.mean(-1, keepdims=True), y-y.mean(-1, keepdims=True)
    return (x*y).sum(-1)/np.sqrt((x*x).sum(-1)*(y*y).sum(-1)).clip(1e-12)


@torch.no_grad()
def panel(model, seed, n, size=1024):
    model.eval(); data = batch(np.random.default_rng(810000+n), size, n)
    arrays = {k: v.numpy() for k, v in data.items()}
    infos = []
    for start in range(0, size, 128):
        x = {k: v[start:start+128] for k, v in data.items()}
        out = model(x)
        teacher = model(x, teacher=True)
        item = dict(pred=out['prediction'].numpy(), margin=out['margin'].numpy(),
                    validation_loss=torch.nn.functional.cross_entropy(teacher['logits'].flatten(0, 1), x['target'].flatten(), reduction='none').reshape(-1, n).mean(1).numpy())
        if model.rep != 'distributed':
            item.update(code=out['code'].numpy(), coordinate=out['coordinate'].numpy())
            for layer, h in enumerate(out['stages']): item[f'code_{layer}'] = model.code(h).numpy()
        infos.append(item)
    arrays.update({k: np.concatenate([i[k] for i in infos]) for k in infos[0]})
    score = dict(average(metrics(arrays['pred'], arrays['target'])),
                 validation_loss=float(arrays['validation_loss'].mean()), score_margin=float(arrays['margin'].mean()))
    diagnostics = []
    if model.rep != 'distributed':
        fitdata = batch(np.random.default_rng(710000+n), 256, n)
        fitout = model(fitdata); targetrank = arrays['target'].argsort(1)
        for layer in range(3):
            code = arrays[f'code_{layer}']
            coord = model.coordinates(torch.from_numpy(code)).numpy()
            decoded = np.argsort(coord, axis=1)
            fitcode = model.code(fitout['stages'][layer]).numpy()
            probe = ridge_fit(feature(fitcode, model.rep), fitdata['target'].numpy().argsort(1)/(n-1))
            rankhat = ridge_apply(feature(code, model.rep), probe)
            row = dict(layer=layer, pairwise_decoding=average(metrics(decoded, arrays['target']))['pairwise_accuracy'],
                       rank_spearman=float(corr(coord.argsort(1).argsort(1).astype(float), targetrank.astype(float)).mean()),
                       linear_probe_pairwise=average(metrics(np.argsort(rankhat, 1), arrays['target']))['pairwise_accuracy'],
                       linear_probe_rmse=float(np.sqrt(np.mean((rankhat-targetrank/(n-1))**2))),
                       code_dispersion=float(code.std(1).mean()))
            if model.rep == 'phase':
                r = targetrank.ravel().astype(float); s, c = np.sin(code).ravel(), np.cos(code).ravel()
                rs, rc, cs = corr(r, s), corr(r, c), corr(c, s)
                row['circular_linear'] = float(np.sqrt(max(0, (rc**2+rs**2-2*rc*rs*cs)/(1-cs**2+1e-12))))
                arrays[f'relative_phase_{layer}'] = np.angle(np.exp(1j*(code[:, :, None]-code[:, None, :])))
            diagnostics.append(row)
    return score, diagnostics, arrays


@torch.no_grad()
def interventions(model, n):
    x = batch(np.random.default_rng(910000+n), 256, n)
    out = model(x); base = out['prediction'].numpy(); target = x['target'].numpy()
    code, h = out['code'], out['stages'][-1]
    pair = out['prediction'][:, [0, -1]]
    controls = [('representation_swap', dict(kind='swap', pair=pair)), ('representation_ablation', dict(kind='ablation'))]
    controls.append(('readout_boost', dict(kind='boost', index=pair[:, 1])) if model.reader == 'competitive' else ('readout_cursor', dict(kind='cursor')))
    invariances = [('code_affine', dict(kind='affine'))] if model.rep != 'phase' else [('rotation_037', dict(kind='rotation', value=.37)), ('rotation_210', dict(kind='rotation', value=2.1)), ('items_only_rotation', dict(kind='items_rotation', value=2.1))]
    invariances.append(('score_offset', dict(kind='score_offset')))
    rows, invrows, raw = [], [], dict(base=base, target=target, code=code.numpy())
    basesc = average(metrics(base, target)); basepos = base.argsort(1); a, b = pair.numpy().T; ii = np.arange(len(base))
    for label, ctl in controls+invariances:
        new = model.decode(h, code, intervention=ctl); pred = new['prediction'].numpy(); pos = pred.argsort(1)
        score = average(metrics(pred, target)); raw[label] = pred
        expected = base.copy(); expected[:, 0], expected[:, -1] = base[:, -1], base[:, 0]
        unrelated = np.ones_like(base, bool); unrelated[ii, a] = False; unrelated[ii, b] = False
        delta = np.abs(new['logits'].numpy()-out['logits'].numpy())
        finite = (new['logits'].numpy()>-1e8)&(out['logits'].numpy()>-1e8)
        row = dict(intervention=label, exact_accuracy=score['exact_accuracy'], exact_change=score['exact_accuracy']-basesc['exact_accuracy'],
                   pairwise_change=score['pairwise_accuracy']-basesc['pairwise_accuracy'],
                   sequence_preservation=float((pred == base).all(1).mean()),
                   inversion_probability=float((pos[ii, a] > pos[ii, b]).mean()),
                   exact_transposition=float((pred == expected).all(1).mean()),
                   later_item_rank_shift=float((pos[ii, b]-basepos[ii, b]).mean()),
                   mean_abs_rank_shift=float(np.abs(pos-basepos).mean()),
                   collateral_rank_shift=float(np.abs(pos-basepos)[unrelated].mean()),
                   first_selection_later=float((basepos[ii, pred[:, 0]] > 0).mean()),
                   later_item_moves_earlier=float((pos[ii, b] < basepos[ii, b]).mean()),
                   content_preservation=float((np.sort(pred, 1) == np.sort(base, 1)).all(1).mean()),
                   max_logit_difference=float(delta[finite].max()))
        (invrows if (label, ctl) in invariances else rows).append(row)
    return rows, invrows, raw

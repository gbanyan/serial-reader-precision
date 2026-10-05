"""Render v2 manuscript figures from saved result tables only; never imports or executes experiments."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('FIGURE_OUT', ROOT / 'manuscript/submission/figures'))
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.labelsize': 10, 'savefig.dpi': 180,
    'lines.linewidth': 2, 'lines.solid_capstyle': 'round', 'axes.edgecolor': '#555555'})
# Okabe-Ito subset; validated (light surface) with the dataviz palette checker.
BLUE, ORANGE, GREEN, DARK, GRID, BAND = '#0072B2', '#D55E00', '#009E73', '#333333', '#e3e3e3', '#eef3f7'
FAMILY = {'priority': 'Priority', 'position': 'Position', 'phase': 'Circular'}
manifest = {'operation': 'presentation of saved result tables; no experiment replay', 'sources': {}, 'figures': {}}


def rows(name):
    p = ROOT / name
    manifest['sources'][name] = hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open() as f:
        return list(csv.DictReader(f))


def save(fig, number, records):
    for ext in ('pdf', 'png', 'svg'):
        fig.savefig(OUT / f'Figure_{number}.{ext}', bbox_inches='tight')
    plt.close(fig)
    manifest['figures'][f'Figure_{number}'] = records


def tidy(ax, grid_axis='y'):
    ax.grid(axis=grid_axis, color=GRID, linewidth=.7)
    ax.set_axisbelow(True)


def panel_label(ax, letter):
    ax.text(-.14, 1.06, letter, transform=ax.transAxes, fontsize=12, fontweight='bold', va='bottom')


# Figure 1: schematic of codes, readers and the training objective.
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.set_xlim(-.02, 1.01); ax.set_ylim(0, 1); ax.axis('off')
def box(x, y, w, h, text, color='#f3f5f7'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.015', linewidth=1, edgecolor=DARK, facecolor=color))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=9.5, linespacing=1.45)
def arrow(start, end, style='-|>', color=DARK, ls='-'):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=12, color=color, linewidth=1.2, linestyle=ls))
box(.01, .40, .18, .30, 'Unordered item set\ndistinct identities\nIID scalar keys')
box(.26, .38, .22, .34, 'Shared set encoder\n(two attention blocks)\nstatic item code:\nscalar or circular')
box(.58, .64, .40, .27, 'Competitive reader\nhighest unused score\nreads order only', '#edf5fa')
box(.58, .25, .40, .31, 'Scan reader\nfixed reference per slot\nnearest item inside capture window,\notherwise NO_MATCH', '#fdf0ea')
arrow((.20, .55), (.25, .55)); arrow((.49, .60), (.57, .76)); arrow((.49, .50), (.57, .42))
box(.26, .02, .72, .15, 'Training: cross entropy on the reader\'s own logits (teacher forcing).\n'
    'Later items are distractors at earlier steps, so the loss pushes them\naway from their own references (Section 3.3).', '#f7f7f2')
arrow((.62, .175), (.62, .245), color='#777777', ls='--')
save(fig, 1, {'type': 'schematic', 'model_sources': ['experiment_a/model.py', 'experiment_a1/model.py', 'experiment_a1/run.py']})

# Figure 2: (A) all-episode noise response at N=6 with analytic Position Scan curve; (B) rank-preserved failure at sigma=.35.
curves = rows('results/experiment_A2_noise_curves.csv')
fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.2, 4.2), gridspec_kw={'width_ratios': [1.35, 1]})
conds = [('priority', 'competitive', BLUE, '-', 'o'), ('position', 'competitive', BLUE, '-', 's'),
         ('priority', 'scan', ORANGE, '-', 'o'), ('position', 'scan', ORANGE, '-', 's'), ('phase', 'scan', ORANGE, '-', '^')]
rec = []
for rep, reader, col, ls, mk in conds:
    sig = sorted({float(r['sigma']) for r in curves})
    m = [100 * np.mean([float(r['exact_accuracy']) for r in curves if r['representation'] == rep and r['readout'] == reader
                        and int(r['n']) == 6 and float(r['sigma']) == s]) for s in sig]
    ax.plot(sig, m, color=col, ls=ls, marker=mk, ms=5, mec='white', mew=1, label=f'{FAMILY[rep]} {reader.capitalize()}')
    rec.append({'representation': rep, 'readout': reader, 'n': 6, 'sigma': sig, 'exact_mean_pct': m})
xs = np.linspace(.001, 1, 200)
phi = np.array([.5 * (1 + math.erf(.45 / x / math.sqrt(2))) for x in xs])
ax.plot(xs, 100 * (2 * phi - 1) ** 6, color=DARK, lw=1.2, ls=(0, (4, 2)), label='Position Scan, closed form')
ax.axvline(.35, color='#999999', lw=.8); ax.text(.36, 4, 'B', color='#666666', fontsize=9)
ax.set_xlabel('Normalized code noise σ (adjacent-rank spacing)'); ax.set_ylabel('Exact sequence accuracy, N = 6 (%)')
ax.set_ylim(-3, 103); tidy(ax, 'both'); ax.legend(frameon=False, fontsize=8, loc='upper right'); panel_label(ax, 'A')
noise = rows('results/experiment_A2_rank_inversion_analysis.csv')
bars = [('priority', 'competitive'), ('position', 'competitive'), ('priority', 'scan'), ('position', 'scan'), ('phase', 'scan')]
for x, (rep, reader) in enumerate(bars):
    g = [r for r in noise if r['representation'] == rep and r['readout'] == reader and int(r['n']) == 6
         and float(r['sigma']) == .35 and r['rank_state'] == 'preserved']
    assert len(g) == 4
    f, c = sum(int(r['failures']) for r in g), sum(int(r['count']) for r in g)
    col = BLUE if reader == 'competitive' else ORANGE
    for o, r in zip([-.15, -.05, .05, .15], sorted(g, key=lambda r: int(r['noise_seed']))):
        bx.scatter(x + o, 100 * float(r['failure_rate']), s=16, color=col, alpha=.55, lw=0)
    bx.scatter(x, 100 * f / c, marker='D', s=40, color=col, edgecolor='white', lw=1, zorder=4)
    bx.annotate(f'{f:,}/{c:,}', (x, 100 * f / c), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=7.5)
    rec.append({'panel': 'B', 'representation': rep, 'readout': reader, 'failures': f, 'preserved': c})
bx.set_xticks(range(5), ['Priority\nComp.', 'Position\nComp.', 'Priority\nScan', 'Position\nScan', 'Circular\nScan'], fontsize=8)
bx.set_ylim(-3, 103); bx.set_ylabel('Failure among rank-preserved episodes (%)'); tidy(bx); panel_label(bx, 'B')
bx.set_title('N = 6, σ = 0.35', fontsize=9.5)
fig.tight_layout(); save(fig, 2, rec)

# Figure 3: per-rank code offsets, analytic optimum versus learned (A.4 at N=6; A.5 at N=8).
analytic = rows('results/experiment_A4/analytic_objective_optimum.csv')
a4 = rows('results/experiment_A4/seed_metrics.csv'); a5 = rows('results/experiment_A5/seed_metrics.csv')
fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.2), sharey='row'); rec = []
def learned(table, arm, system, n, step):
    g = [r for r in table if r['arm'] == arm and r['system'] == system and int(r['n']) == n and int(r['step']) == step]
    assert len(g) == 8, (arm, system, n, step, len(g))
    return np.array([[float(v) for v in r['offsets'].split()] for r in g])
for row, (table, arm1, arm16, n, step, label) in enumerate([(a4, 'S-b1', 'S-b16', 6, 900, 'Trained N = 4/6, 900 updates; read at N = 6'),
                                                            (a5, 'N8-b1', 'N8-b16', 8, 3600, 'Trained N = 8 only, 3,600 updates')]):
    for col, fam in enumerate(['priority', 'position', 'phase']):
        ax = axes[row, col]; ranks = np.arange(n)
        ax.axhspan(-1, 1, color=BAND, zorder=0)
        for beta, arm, colr in [(1, arm1, ORANGE), (16, arm16, BLUE)]:
            an = next(r for r in analytic if int(r['beta']) == beta and int(r['n']) == n and r['family'] == fam)
            ay = np.array([float(v) for v in an['offsets_w'].split()])
            ax.plot(ranks, ay, color=colr, lw=1.3, ls=(0, (4, 2)), zorder=2)
            L = learned(table, arm, f'{fam}_scan', n, step)
            # Seed median and interquartile range: robust to a collapsed seed (circular beta=16, seed 33, 0% accuracy).
            md, q1, q3 = np.median(L, 0), np.quantile(L, .25, 0), np.quantile(L, .75, 0)
            ax.errorbar(ranks, md, yerr=[md - q1, q3 - md], fmt='o', ms=5, color=colr,
                        mec='white', mew=1, elinewidth=.9, capsize=0, zorder=3)
            rec.append({'n': n, 'family': fam, 'beta': beta, 'analytic': ay.tolist(), 'learned_seed_median': md.tolist(),
                        'learned_q1': q1.tolist(), 'learned_q3': q3.tolist()})
        ax.set_xticks(ranks); tidy(ax)
        if row == 0: ax.set_title(FAMILY[fam], fontsize=10)
        if row == 1: ax.set_xlabel('Target rank')
        if col == 0: ax.set_ylabel('Offset from slot centre (w)')
    axes[row, 0].text(0, 1.13, label, transform=axes[row, 0].transAxes, fontsize=9.5, color='#444444')
    panel_label(axes[row, 0], 'AB'[row])
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
for ax in axes[0]: ax.set_ylim(-1.6, 2.4)
for ax in axes[1]: ax.set_ylim(-1.2, 2.4)
handles = [Line2D([], [], color=ORANGE, lw=1.3, ls=(0, (4, 2)), label='Loss optimum, β = 1'),
           Line2D([], [], color=ORANGE, marker='o', ls='none', label='Learned, β = 1 (seed median, IQR)'),
           Line2D([], [], color=BLUE, lw=1.3, ls=(0, (4, 2)), label='Loss optimum, β = 16'),
           Line2D([], [], color=BLUE, marker='o', ls='none', label='Learned, β = 16 (seed median, IQR)'),
           Patch(color=BAND, label='Capture window (|offset| < w)')]
fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(.5, -.06))
fig.tight_layout(); save(fig, 3, rec)

# Figure 4: (A) training-budget curves at N=6 (A.5); (B) A.6 endpoint tests of the displacement account.
a5s = rows('results/experiment_A5/summary.csv'); a5seed = rows('results/experiment_A5/seed_metrics.csv')
a6seed = rows('results/experiment_A6/seed_metrics.csv'); a7seed = rows('results/experiment_A7/seed_metrics.csv'); a7r = rows('results/experiment_A7R/replay_seed_metrics.csv')
fig = plt.figure(figsize=(12, 8)); gs = fig.add_gridspec(2, 12, height_ratios=[1, 1.1], hspace=.6, wspace=1.2); rec = []
top = [fig.add_subplot(gs[0, 4*k:4*k+4]) for k in range(3)]; cx = fig.add_subplot(gs[1, 9:])
for ax, fam in zip(top, ['priority', 'position', 'phase']):
    ax.axhline(100, color='#999999', lw=.8); ax.text(1000, 101.5, 'compatible oracle', fontsize=7.5, color='#666666')
    for arm, colr, lab in [('B-b1', ORANGE, 'β = 1 (A.1 objective)'), ('B-b16', BLUE, 'β = 16')]:
        g = sorted([r for r in a5s if r['arm'] == arm and r['system'] == f'{fam}_scan' and int(r['n']) == 6], key=lambda r: int(r['step']))
        x = [int(r['step']) for r in g]; m = [100 * float(r['exact_mean']) for r in g]
        lo = [100 * float(r['exact_min']) for r in g]; hi = [100 * float(r['exact_max']) for r in g]
        ax.fill_between(x, lo, hi, color=colr, alpha=.12, lw=0); ax.plot(x, m, color=colr, marker='o', ms=4.5, mec='white', mew=1, label=lab)
        rec.append({'panel': 'A', 'family': fam, 'arm': arm, 'steps': x, 'mean_pct': m, 'min_pct': lo, 'max_pct': hi})
    ax.set_xscale('log'); ax.set_xticks([900, 3600, 14400, 36000], ['900', '3.6k', '14.4k', '36k']); ax.minorticks_off()
    ax.set_title(FAMILY[fam], fontsize=10); ax.set_xlabel('Training updates'); tidy(ax); ax.set_ylim(-3, 106)
top[0].set_ylabel('Exact Scan accuracy, N = 6 (%)'); top[0].legend(frameon=False, fontsize=8, loc='center left')
for ax in top[1:]: ax.set_yticklabels([])
panel_label(top[0], 'A')
bx = fig.add_subplot(gs[1, :9])
# (C) A.7R: the same saved beta=1 codes (column 1 of B) read with other capture widths; no retraining.
WID = sorted({float(r['width']) for r in a7r})
for fam, colr, mk in [('priority', DARK, 'o'), ('position', DARK, 's'), ('phase', '#888888', '^')]:
    m = [100 * np.mean([float(r['exact']) for r in a7r if r['family'] == fam and float(r['width']) == w]) for w in WID]
    cx.plot(WID, m, color=colr, marker=mk, ms=4.5, mec='white', mew=.8, lw=1.6, label=FAMILY[fam])
    rec.append({'panel': 'C', 'family': fam, 'widths_per_N': WID, 'mean_exact_pct': m})
cx.axvline(.45, color='#999999', lw=.8, ls=(0, (3, 2))); cx.text(.44, 30, 'trained\nradius', fontsize=7, color='#666666', ha='right')
cx.axvline(.5, color=GRID, lw=.8)
cx.set_xlabel('Read radius w (×1/N)'); cx.set_ylim(-3, 106); cx.set_xticks([.25, .45, .65]); tidy(cx)
cx.set_title('Same codes, new read radius', fontsize=9.5); cx.legend(frameon=False, fontsize=7.5, loc='lower right'); panel_label(cx, 'C')
# (label, table, arm, read N, families whose analytic optimum lies inside the capture windows)
conds = [('β = 1\ntrain 4/6\nread 6', a5seed, 'B-b1', 6, {'phase'}),
         ('β = 2\ntrain 4/6\nread 6', a6seed, 'X46-b2', 6, {'priority', 'position', 'phase'}),
         ('β = 2\ntrain 6\nread 6', a7seed, 'M6-b2', 6, {'priority', 'position', 'phase'}),
         ('β = 2\ntrain 8\nread 8', a6seed, 'N8-b2L', 8, {'phase'}),
         ('β = 4\ntrain 8\nread 8', a6seed, 'N8-b4L', 8, {'priority', 'position', 'phase'}),
         ('β = 1, no\ndistractors\nread 6', a6seed, 'D', 6, {'priority', 'position', 'phase'}),
         ('β = 1\nw = 0.30/N\nread 6', a7seed, 'W30-b1', 6, set()),
         ('β = 1\nw = 0.75/N\nread 6', a7seed, 'W75-b1', 6, {'priority', 'position', 'phase'})]
marks = {'priority': ('o', -.22), 'position': ('s', 0), 'phase': ('^', .22)}
for x, (lab, table, arm, n, inside) in enumerate(conds):
    for fam, (mk, off) in marks.items():
        if table is a7r: g = [r for r in table if r['family'] == fam and float(r['width']) == arm]
        else: g = [r for r in table if r['arm'] == arm and r['system'] == f'{fam}_scan' and int(r['n']) == n and int(r['step']) == 36000]
        assert len(g) == 8, (arm, fam, len(g))
        v = np.array([100 * float(r['exact']) for r in g])
        bx.scatter(np.full(8, x + off) + np.linspace(-.05, .05, 8), v, s=10, color='#9a9a9a', lw=0, zorder=2)
        fill = DARK if fam in inside else 'white'
        bx.scatter(x + off, v.mean(), marker=mk, s=70, facecolor=fill, edgecolor=DARK, lw=1.4, zorder=3)
        rec.append({'panel': 'B', 'condition': arm, 'read_n': n, 'family': fam, 'optimum_inside_window': fam in inside,
                    'seed_exact_pct': v.tolist(), 'mean_pct': float(v.mean())})
bx.set_xticks(range(len(conds)), [c[0] for c in conds], fontsize=8)
bx.axvline(5.5, color='#bbbbbb', lw=.8); bx.text(6.5, 103, 'A.7: radius changed\nin training', ha='center', va='bottom', fontsize=7.5, color='#555555'); bx.set_ylim(-3, 103)
bx.set_ylabel('Exact Scan accuracy at 36k updates (%)'); bx.set_ylim(-3, 114); bx.set_yticks([0, 20, 40, 60, 80, 100]); tidy(bx); panel_label(bx, 'B')
from matplotlib.lines import Line2D
h = [Line2D([], [], marker=m, ls='none', color=DARK, label=FAMILY[f]) for f, (m, _) in marks.items()]
h += [Line2D([], [], marker='D', ls='none', markerfacecolor=DARK, markeredgecolor=DARK, label='Filled: loss optimum inside windows'),
      Line2D([], [], marker='D', ls='none', markerfacecolor='white', markeredgecolor=DARK, label='Open: loss optimum outside windows'),
      Line2D([], [], marker='o', ls='none', color='#9a9a9a', markersize=4, label='Individual seeds')]
bx.legend(handles=h, frameon=False, fontsize=8, ncol=3, loc='upper center', bbox_to_anchor=(.5, -.3))
save(fig, 4, rec)

# Figure S1 (Supplement): circular geometry (A) occupied arc by reader; (B) frozen-reader replay construction check.
arcs = rows('results/experiment_A3_phase_arc_analysis.csv'); replay = rows('results/experiment_A3_counterfactual_geometry.csv')
fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.2, 4.0), gridspec_kw={'width_ratios': [1, 1.25]}); rec = []
for center, n in enumerate([4, 6]):
    for i, seed in enumerate([11, 22, 33, 44]):
        pair = [100 * float(next(r for r in arcs if int(r['step']) == 900 and int(r['n']) == n and int(r['seed']) == seed
                                 and r['readout'] == rd)['arc_fraction']) for rd in ('competitive', 'scan')]
        j = (i - 1.5) * .03
        ax.plot([center - .17 + j, center + .17 + j], pair, color='#aaaaaa', lw=1)
        ax.scatter(center - .17 + j, pair[0], color=BLUE, s=34, edgecolor='white', lw=1, zorder=3)
        ax.scatter(center + .17 + j, pair[1], color=ORANGE, s=34, edgecolor='white', lw=1, zorder=3)
        rec.append({'n': n, 'seed': seed, 'arc_pct_competitive_scan': pair})
ax.set_xticks([0, 1], ['N = 4', 'N = 6']); ax.set_xlim(-.5, 1.5); ax.set_ylim(0, 100)
ax.set_ylabel('Minimal occupied arc (% of circle)'); tidy(ax); panel_label(ax, 'A')
ax.scatter([], [], color=BLUE, label='Competitive-trained'); ax.scatter([], [], color=ORANGE, label='Scan-trained')
ax.legend(frameon=False, fontsize=8, loc='lower right')
geoms = [('learned', 'Native'), ('oracle_slots', 'Full circle\n(target ranks)'), ('semicircle', 'Semicircle\n(target ranks)'),
         ('inferred_semicircle', 'Semicircle\n(native order)')]
for x, (g, lab) in enumerate(geoms):
    grp = [r for r in replay if r['representation'] == 'phase' and r['readout'] == 'competitive' and int(r['step']) == 900
           and int(r['n']) == 6 and r['geometry'] == g]
    assert len(grp) == 4
    v = [100 * float(r['exact_accuracy']) for r in grp]
    bx.scatter(np.array([-.12, -.04, .04, .12]) + x, v, s=18, color=DARK if g == 'learned' else BLUE, alpha=.6, lw=0)
    bx.scatter(x, np.mean(v), marker='D', s=40, color=DARK if g == 'learned' else BLUE, edgecolor='white', lw=1, zorder=3)
    rec.append({'geometry': g, 'mean_pct': float(np.mean(v))})
bx.set_xticks(range(4), [l for _, l in geoms], fontsize=8); bx.set_ylim(-3, 103)
bx.set_ylabel('Exact accuracy, circular Competitive, N = 6 (%)'); tidy(bx); panel_label(bx, 'B')
bx.set_title('Constructed layouts through the frozen reader', fontsize=9.5)
fig.tight_layout(); save(fig, 'S1', rec)

(OUT / 'figure_provenance.json').write_text(json.dumps(manifest, indent=2, allow_nan=False))
print('Rendered v2 Figures 1-4 and S1 from saved tables.')

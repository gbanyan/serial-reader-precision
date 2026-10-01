"""Render saved A-series summaries only; never imports or executes experiments."""
from pathlib import Path
import csv
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manuscript/submission/figures'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.labelsize': 11, 'savefig.dpi': 180})
BLUE, ORANGE, DARK = '#0072B2', '#D55E00', '#333333'
SEEDS = [11, 22, 33, 44]
manifest = {'operation': 'presentation of archived aggregate results; no experiment replay',
            'sources': {}, 'figures': {}}

def rows(name):
    p = ROOT / name
    manifest['sources'][name] = hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open() as f:
        return list(csv.DictReader(f))

def save(fig, number, records):
    fig.savefig(OUT / f'Figure_{number}.pdf', bbox_inches='tight')
    fig.savefig(OUT / f'Figure_{number}.png', bbox_inches='tight')
    fig.savefig(OUT / f'Figure_{number}.svg', bbox_inches='tight')
    plt.close(fig)
    manifest['figures'][f'Figure_{number}'] = records

def percentage_axis(ax, label):
    ax.set_ylim(-3, 105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel(label)
    ax.grid(axis='y', color='#dddddd', linewidth=.6)
    ax.set_axisbelow(True)

# One schematic, not a composite of unrelated graphs.
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
def box(x, y, w, h, text, color='#f3f5f7'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.015',
        linewidth=1, edgecolor=DARK, facecolor=color))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=10, linespacing=1.5)
def arrow(start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=13,
        color=DARK, linewidth=1.2, connectionstyle='arc3'))
box(.02,.33,.19,.32,'Unordered item set\nDistinct identities\nIID scalar keys')
box(.29,.31,.23,.36,'Shared set encoder\n96 hidden dimensions\nTwo attention blocks\nStatic code\nScalar or circular')
box(.63,.59,.34,.29,'Competitive\nHighest unused score\nStrictly increasing scalar\nchanges preserve selection', '#edf5fa')
box(.63,.12,.34,.32,'Scan\nFixed reference at each slot\nNearest eligible item / NO_MATCH\nCapture and rejection included', '#fdf0ea')
arrow((.22,.49),(.275,.49)); arrow((.535,.54),(.61,.735)); arrow((.535,.44),(.61,.28))
ax.text(.5,.025,'Same target: ascending key order. Reader equations and associated losses are specified separately.',
    ha='center',va='bottom',fontsize=9)
save(fig,1,{'type':'analytical schematic','model_sources':['experiment_a/model.py','experiment_a1/model.py'],
    'boundary':'not a universal classification of serial readers'})

noise = rows('results/experiment_A2_rank_inversion_analysis.csv')
conditions = [('priority','competitive'),('priority','scan'),('position','competitive'),
    ('position','scan'),('phase','scan')]
fig,ax = plt.subplots(figsize=(8.5,4.7)); records=[]
for x,(rep,reader) in enumerate(conditions):
    group=[r for r in noise if r['representation']==rep and r['readout']==reader
        and int(r['n'])==6 and float(r['sigma'])==.35 and r['rank_state']=='preserved']
    assert len(group)==4
    group.sort(key=lambda r:int(r['noise_seed']))
    for offset,r in zip([-.18,-.06,.06,.18],group):
        y=float(r['failure_rate'])*100
        # Floating-point Wilson endpoints can differ from zero by roundoff.
        ax.errorbar(x+offset,y,yerr=[[max(0,y-float(r['ci_low'])*100)],[max(0,float(r['ci_high'])*100-y)]],
            fmt='o',ms=4,capsize=2,color=BLUE if reader=='competitive' else ORANGE,lw=.8)
    failures=sum(int(r['failures']) for r in group); count=sum(int(r['count']) for r in group)
    rate=100*failures/count
    ax.scatter(x,rate,marker='D',s=48,color=DARK,zorder=5)
    ax.annotate(f'{failures:,}/{count:,}',(x,rate),xytext=(0,13),textcoords='offset points',
        ha='center',fontsize=9)
    records.append({'representation':rep,'readout':reader,'n':6,'sigma':.35,
        'failure_count':failures,'preserved_count':count,'pooled_rate':failures/count,
        'panels':group})
ax.set_xticks(range(5),['Priority\nCompetitive','Priority\nScan','Position\nCompetitive','Position\nScan','Circular\nScan'])
percentage_axis(ax,'Conditional sequence failure (%)')
ax.text(.01,1.04,'N = 6; noise = 0.35 adjacent-spacing units',transform=ax.transAxes,fontsize=10)
ax.plot([],[], 'o',color=ORANGE,label='Data/noise panel + Wilson 95% interval')
ax.plot([],[], 'D',color=DARK,label='Pooled count ratio')
ax.legend(loc='upper left',bbox_to_anchor=(0,-.20),frameon=False,fontsize=9,ncol=2)
fig.subplots_adjust(bottom=.25)
save(fig,2,records)

gaps=rows('results/experiment_A2_learnability_gap.csv')
fig,ax=plt.subplots(figsize=(8.2,4.7));records=[]
for x,(n,rep) in enumerate((n,rep) for n in [4,6] for rep in ['priority','position','phase']):
    group=[r for r in gaps if r['readout']=='scan' and r['representation']==rep and int(r['n'])==n]
    group.sort(key=lambda r:float(r['seed']));assert len(group)==4
    vals=[float(r['learned_exact'])*100 for r in group]
    ax.scatter(np.array([-.15,-.05,.05,.15])+x,vals,s=33,color=ORANGE,zorder=4)
    ax.scatter(x,np.mean(vals),marker='D',s=45,color=DARK,zorder=5)
    assert all(float(r['oracle_exact'])==1 for r in group)
    ax.scatter(x,100,s=44,marker='s',facecolors='none',edgecolors=BLUE,zorder=5)
    records.append({'n':n,'representation':rep,'learned_mean':np.mean(vals)/100,'seed_rows':group})
ax.set_xticks(range(6),['Priority\nN = 4','Position\nN = 4','Circular\nN = 4','Priority\nN = 6','Position\nN = 6','Circular\nN = 6'])
percentage_axis(ax,'Exact sequence accuracy (%)')
ax.scatter([],[],marker='s',facecolors='none',edgecolors=BLUE,label='Compatible oracle')
ax.scatter([],[],color=ORANGE,label='Each training seed, update 900')
ax.scatter([],[],marker='D',color=DARK,label='Equal-seed mean')
ax.legend(loc='upper left',bbox_to_anchor=(0,-.2),ncol=3,frameon=False,fontsize=9)
fig.subplots_adjust(bottom=.25)
save(fig,3,records)

arcs=rows('results/experiment_A3_phase_arc_analysis.csv')
effects=rows('results/experiment_A3/paired_geometry_differences.csv')
fig,ax=plt.subplots(figsize=(7.7,4.7));records=[]
for center,n in enumerate([4,6]):
    for index,seed in enumerate(SEEDS):
        pair=[]
        for reader in ['competitive','scan']:
            r=next(r for r in arcs if int(r['step'])==900 and int(r['n'])==n
                and int(r['seed'])==seed and r['readout']==reader)
            pair.append(float(r['arc_fraction'])*100);records.append(r)
        jitter=(index-1.5)*.025
        ax.plot([center-.17+jitter,center+.17+jitter],pair,color='#999999',lw=1)
        ax.scatter(center-.17+jitter,pair[0],color=BLUE,s=42,marker=['o','s','^','v'][index],zorder=4)
        ax.scatter(center+.17+jitter,pair[1],color=ORANGE,s=42,marker=['o','s','^','v'][index],zorder=4)
    for offset,reader,col in [(-.17,'competitive',BLUE),(.17,'scan',ORANGE)]:
        vals=[float(r['arc_fraction'])*100 for r in arcs if int(r['step'])==900 and int(r['n'])==n and r['readout']==reader]
        ax.scatter(center+offset,np.mean(vals),s=72,marker='D',color=col,edgecolor='white',zorder=6)
ax.set_xticks([0,1],['N = 4','N = 6']);ax.set_xlim(-.45,1.45)
percentage_axis(ax,'Mean minimal occupied arc (% of circle)')
ax.plot([],[],'o',color=BLUE,label='Competitive-associated')
ax.plot([],[],'o',color=ORANGE,label='Scan-associated')
ax.plot([],[],'D',color=DARK,label='Equal-seed mean')
ax.legend(loc='upper left',bbox_to_anchor=(0,-.15),ncol=3,frameon=False,fontsize=9)
fig.subplots_adjust(bottom=.23)
save(fig,4,{'seed_rows':records,'existing_effect_rows':[r for r in effects if r['representation']=='phase' and r['metric']=='arc_fraction']})

replay=rows('results/experiment_A3_counterfactual_geometry.csv')
geometries=['learned','source_rank_uniform','inferred_semicircle','oracle_slots','semicircle','learned_span_arc']
labels=['Native\nlearned','Source-inferred\nfull circle','Source-inferred\nsemicircle','Target-informed\nfull circle','Target-informed\nsemicircle','Target-informed\ncapped span']
fig,ax=plt.subplots(figsize=(9.0,4.8));records=[]
for x,geom in enumerate(geometries):
    group=[r for r in replay if r['representation']=='phase' and r['readout']=='competitive'
        and int(r['step'])==900 and int(r['n'])==6 and r['geometry']==geom]
    group.sort(key=lambda r:int(r['seed']));assert len(group)==4
    values=[float(r['exact_accuracy'])*100 for r in group]
    color=DARK if geom=='learned' else (BLUE if geom in ['source_rank_uniform','inferred_semicircle'] else ORANGE)
    ax.scatter(np.array([-.15,-.05,.05,.15])+x,values,color=color,s=32,zorder=4)
    ax.scatter(x,np.mean(values),marker='D',s=50,color=color,zorder=5)
    records.append({'geometry':geom,'mean_exact':np.mean(values)/100,'seed_rows':group})
ax.set_xticks(range(6),labels,fontsize=9)
percentage_axis(ax,'Exact sequence accuracy (%)')
ax.text(.01,1.04,'Circular Competitive; N = 6; frozen reader',transform=ax.transAxes,fontsize=10)
ax.text(.5,-.23,'Rank-informed reconstructions are diagnostic manipulations, not learned calibration algorithms.',
    transform=ax.transAxes,ha='center',fontsize=9)
fig.subplots_adjust(bottom=.28)
save(fig,5,records)

(OUT/'figure_provenance.json').write_text(json.dumps(manifest,indent=2,allow_nan=False))
print('Rendered five standalone PDF/SVG/PNG figures from saved tables.')

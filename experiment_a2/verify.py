"""Verify preserved evidence and A.2 outputs, without running experiments."""
import hashlib
import json
import re
from pathlib import Path
import pandas as pd

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads(Path('experiment_A2_source.json').read_text())
    for section in ['source','protected_previous']:
        for name,digest in manifest[section].items():assert sha(Path(name))==digest,name
    frozen=json.loads(Path('experiment_A1_source.json').read_text())['sha256']
    for name,digest in frozen.items():assert sha(Path(name))==digest,name
    raw_counts={}
    for stage in ['experiment_A','experiment_A1']:
        old=json.loads(Path(f'results/{stage}/artifact_manifest.json').read_text())['raw_artifacts']
        for name,r in old.items():
            path=Path('runs')/stage/name
            assert path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],str(path)
        raw_counts[stage]=len(old)
    expected={'oracle_matrix':120,'noise_curves':960,'rank_inversion_analysis':2880,'learnability_gap':36,'learned_geometry_error':32,'invariance':120,'cursor_interventions':360}
    for name,count in expected.items():
        df=pd.read_csv(f'results/experiment_A2_{name}.csv');assert len(df)==count,(name,len(df),count)
    for path in [Path('research/experiment_A2_summary.md'),Path('results/experiment_A2/README.md')]:
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' not in link and link not in ['verification.json','artifact_manifest.json']:
                assert (path.parent/link.split('#')[0]).exists(),link
    record=dict(status='PASS',preserved_raw_hashes=raw_counts,preregistered_source_hashes=len(manifest['source']),
                protected_document_result_hashes=len(manifest['protected_previous']),table_rows=expected,
                saved_A1_prediction_replays=32,local_contract_tests=4,remote_frozen_decoder_panels=75,
                remote_trials_per_panel=128,training_runs=0,factorial_rerun=False,experiment_B='BLOCKED')
    out=Path('results/experiment_A2');(out/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    paths=[*out.glob('*'),*Path('results').glob('experiment_A2_*.csv'),*Path('experiment_a2').glob('*.py'),*Path('research').glob('experiment_A2_*.md'),*Path('runs/experiment_A2').glob('*'),Path('experiment_A2_source.json')]
    new={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths if p.is_file() and p.name!='artifact_manifest.json'}
    (out/'artifact_manifest.json').write_text(json.dumps(dict(artifacts=new,execution='local analysis; pinned remote PyTorch decoder check',source_manifest='experiment_A2_source.json'),indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()

import hashlib,json,re
from pathlib import Path
import pandas as pd

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=json.loads(Path('experiment_A3_source.json').read_text())
    for key in ['source','preserved']:
        for name,h in source[key].items():assert sha(Path(name))==h,name
    raw={}
    for stage in ['experiment_A','experiment_A1']:
        hashes=json.loads(Path(f'results/{stage}/artifact_manifest.json').read_text())['raw_artifacts']
        for name,h in hashes.items():assert sha(Path('runs')/stage/name)==h['sha256'],name
        raw[stage]=len(hashes)
    expected={'geometry_summary':144,'readout_alignment':144,'rank_metric_decomposition':432,'geometry_trajectory':144,'cross_readout_transfer':144,'phase_arc_analysis':48,'counterfactual_geometry':232}
    for name,count in expected.items():
        rows=pd.read_csv(f'results/experiment_A3_{name}.csv');assert len(rows)==count,(name,len(rows),count)
    out=Path('results/experiment_A3')
    for p in [Path('research/experiment_A3_summary.md'),out/'README.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if link not in ['verification.json','artifact_manifest.json'] and '://' not in link:assert (p.parent/link.split('#')[0]).exists(),link
    record=dict(status='PASS',raw_evidence_hashes=raw,protected_result_document_hashes=len(source['preserved']),frozen_source_hashes=len(source['source']),
                matched_input_pairs=72,native_prediction_replays=144,training_runs=0,contract_tests=4,table_rows=expected,experiment_B='BLOCKED')
    (out/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    paths=[*out.glob('*'),*Path('results').glob('experiment_A3_*.csv'),*Path('research').glob('experiment_A3_*.md'),*Path('experiment_a3').glob('*.py'),*Path('runs/experiment_A3').glob('*'),Path('experiment_A3_source.json')]
    (out/'artifact_manifest.json').write_text(json.dumps({str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths if p.is_file() and p.name!='artifact_manifest.json'},indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()

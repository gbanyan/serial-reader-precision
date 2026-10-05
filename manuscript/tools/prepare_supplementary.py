"""Copy saved supplementary artifacts with stable IDs; never delete historical files."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manuscript/submission/supplementary'
OUT.mkdir(parents=True, exist_ok=True)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_record(source, name, identifier, caption):
    p = ROOT / source
    dest = OUT / name
    shutil.copyfile(p, dest)
    assert digest(dest) == digest(p), source
    return dict(id=identifier, file=name, source=source, sha256=digest(p), caption=caption)

previous_path = OUT / 'inventory.json'
previous = json.loads(previous_path.read_text()) if previous_path.exists() else []
prior = {r['source']: r for r in previous}
files = sorted(p for p in (ROOT/'results').rglob('*.csv')
               if p.relative_to(ROOT/'results').parts[0].startswith('experiment_A'))
# Existing IDs are manuscript citations, not positions in a new sorted listing.
# Adjudicated 2026-10-03: existing IDs are kept; new sources may be appended only from the
# preregistered A.4-A.6 result folders, numbered after the highest existing ID in sorted order.
APPENDABLE = ('results/experiment_A4/', 'results/experiment_A5/', 'results/experiment_A6/', 'results/experiment_A7/', 'results/experiment_A7R/')
current = {str(p.relative_to(ROOT)) for p in files}
if previous:
    assert set(prior) <= current, 'Saved source removed: explicitly adjudicate IDs before preparation.'
    assert all(src.startswith(APPENDABLE) for src in current - set(prior)), 'Unexpected new source: adjudicate IDs first.'
next_id = max((int(r['id'][1:]) for r in previous), default=0)
inventory = []
for i, p in enumerate(files, 1):
    source = str(p.relative_to(ROOT))
    relative = p.relative_to(ROOT/'results')
    old = prior.get(source)
    if old:
        assert digest(p) == old['sha256'], 'Saved result content changed: explicitly adjudicate '+old['id']
    if old:
        identifier = old['id']
    else:
        next_id += 1
        identifier = f'D{next_id:02d}' if previous else f'D{i:02d}'
    name = old['file'] if old else identifier + '_' + '_'.join(relative.parts)
    match = re.match(r'experiment_A([1-7]?R?)', str(relative))
    stage = 'A' + ('.' + match.group(1) if match.group(1) else '')
    topic = re.sub(r'^experiment_A[1-7]?R?_', '', p.stem).replace('_', ' ')
    caption = old['caption'] if old else f'Saved {topic} table from {stage}; original condition columns and aggregation retained.'
    inventory.append(copy_record(source, name, identifier, caption))
(OUT/'inventory.json').write_text(json.dumps(inventory, indent=2)+'\n')

historical_path = OUT/'historical_inventory.json'
if historical_path.exists():
    for record in json.loads(historical_path.read_text()):
        assert digest(ROOT / record['source']) == record['sha256'], 'Historical source changed before copy: '+record['id']
        actual = copy_record(record['source'], record['file'], record['id'], record['caption'])
        assert actual['sha256'] == record['sha256'], 'Historical source changed: '+record['id']

audit_path = OUT/'audit_inventory.json'
if audit_path.exists():
    for entry in json.loads(audit_path.read_text()):
        for record in [entry, *entry.get('companions', [])]:
            assert digest(ROOT / record['source']) == record['sha256'], 'Audit source changed: explicitly adjudicate '+record['id']
audits = []
for identifier, stem, script in [
    ('A01', 'native_branch_audit', 'audit_native_branch.py'),
    ('A02', 'saved_scan_failure_audit', 'audit_saved_scan_failures.py'),
    ('A03', 'complete_wrong_rank_audit', 'audit_complete_rank.py')]:
    row = copy_record('manuscript/submission/'+stem+'.csv', stem+'.csv', identifier,
                      'Later descriptive saved-array arithmetic; no model or reader call. Not an original experimental table.')
    row['companions'] = [
        copy_record('manuscript/submission/'+stem+'_provenance.json', stem+'_provenance.json', identifier+'-provenance', 'Recorded audit provenance; original paths refer to the evidence repository.'),
        copy_record('manuscript/tools/'+script, script, identifier+'-script', 'Audit source copied unchanged; execute from its manuscript/tools location in the evidence repository, not this upload folder.')]
    audits.append(row)
(OUT/'audit_inventory.json').write_text(json.dumps(audits, indent=2)+'\n')
print(f'Prepared {len(inventory)} stable saved CSVs and {len(audits)} audit sets; historical files and captions preserved.')

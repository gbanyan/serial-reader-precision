"""Copy and hash A-series evidence including A.4-A.7R; never run scientific modules."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import argparse
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manuscript/release'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label', default='v2_2026_10_04')
parser.add_argument('--stage-root', required=True, help='directory for the GitHub staging copy (not /tmp by default)')
args = parser.parse_args()
assert re.fullmatch(r'[A-Za-z0-9_.-]+', args.label), 'Unsafe package label'
LABEL = args.label
STAGE = Path(args.stage_root) / ('a_series_github_stage_' + LABEL)
assert not STAGE.exists(), 'Preserve previous staging: choose a new package label'
ARCHIVE_NAME = 'A_series_saved_evidence_' + LABEL + '.zip'
assert not (OUT / ARCHIVE_NAME).exists(), 'Preserve historical archives: choose a new label'
OUT.mkdir(parents=True, exist_ok=True)
STAGE.mkdir(parents=True, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def eligible(p):
    return p.is_file() and not any(x in p.parts for x in ['__pycache__', '.pytest_cache', '.DS_Store']) and p.suffix not in ['.pyc']

code = []
for folder in ['experiment_a', 'experiment_a1', 'experiment_a2', 'experiment_a3', 'experiment_a4', 'experiment_a5', 'experiment_a6', 'experiment_a7']:
    code.extend(p for p in (ROOT/folder).rglob('*') if eligible(p))
code.extend(ROOT/p for p in ['pbos/__init__.py','pbos/models/__init__.py','pbos/models/transformer.py','pbos/data/__init__.py','pbos/data/generator.py','requirements.txt','Dockerfile'])
code.extend(ROOT.glob('experiment_A*_source.json'))
code.extend(p for p in (ROOT/'tests').glob('test_experiment_a*.py') if eligible(p))
results = [p for p in (ROOT/'results').rglob('*') if eligible(p) and p.relative_to(ROOT/'results').parts[0].startswith('experiment_A')]
notes = [p for p in (ROOT/'research').glob('experiment_A*.md') if eligible(p)]
notes.extend(ROOT/'research'/p for p in ['A_series_methods_map.md','A_series_manuscript_anchor_numbers.md','A_series_statistical_audit.md','A_series_reproducibility_audit.md'])
code.extend(ROOT/'manuscript/tools'/p for p in ['build_figures.py', 'build_figures_v2.py', 'audit_native_branch.py', 'audit_saved_scan_failures.py', 'audit_complete_rank.py', 'prepare_supplementary.py', 'package_evidence.py', 'package_evidence_v2.py'])
companions = [p for p in (ROOT/'manuscript/submission/supplementary').rglob('*') if eligible(p)]
companions.extend(ROOT/'manuscript/submission'/name for name in ['native_branch_audit.csv', 'native_branch_audit_provenance.json', 'saved_scan_failure_audit.csv', 'saved_scan_failure_audit_provenance.json', 'complete_wrong_rank_audit.csv', 'complete_wrong_rank_audit_provenance.json'])
notes.append(ROOT/'research/experiment_A_confound_review.json')
for p in sorted(set(code + results + notes + companions)):
    dest = STAGE / p.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p, dest)

mit = '''MIT License

Copyright (c) 2026 Jing-Rung Huang and Wen-Hsiang Lu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
(STAGE/'LICENSE').write_text(mit)
(STAGE/'LICENSE-DATA.md').write_text('''# Original data and results

Original synthetic data, saved evaluations, checkpoints and result tables are
licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).
Legal terms: https://creativecommons.org/licenses/by/4.0/legalcode.en
Attribution: Jing-Rung Huang and Wen-Hsiang Lu, *Serial reader precision:
A-series code and synthetic research data*, version v1.0.0, 2026.

Software is MIT (see LICENSE). Third-party dependencies retain their own
licenses and are not vendored. No third-party articles or research datasets
are included. Source-revision records preserve historical repository paths;
their recorded Git commits do not imply those commits exist in this new repo.
''')
(STAGE/'requirements-analysis.txt').write_text('''# Additional reporting dependencies. Historical exact versions not fully recorded.
# These are compatibility ranges, not a reproduction of the original environment.
-r requirements.txt
pandas>=2,<3
scipy>=1.14,<2
''')
(STAGE/'.gitignore').write_text('__pycache__/\n*.pyc\n.venv/\n.pytest_cache/\n*.zip\n')
(STAGE/'.gitattributes').write_text('*.csv text eol=lf\n')
(STAGE/'README.md').write_text('''# Serial reader precision: A-series code and synthetic research data

Controlled artificial serial-order representations and specified readers.
This release preserves A, A.1, A.2 and A.3, including failed mechanism gates, and the
prospectively specified follow-ups A.4-A.7 and the evaluation-only replay A.7R.
It is not a biological study or a universal Competitive/Scan comparison.

## Contents and provenance

* `experiment_a*`: original source and analysis modules. Do not confuse the
  original pseudo-scan with the repaired rejecting fixed-reference reader.
* `pbos/`: only the shared attention-layer dependency and its import dependencies.
* `results/`: saved tables, diagnostics and historical plots, unmodified.
* `research/`: experiment definitions, final summaries and provenance maps.
* `experiment_A*_source.json`: historical revisions and file hashes.
* `SHA256SUMS.json`: inventory of the files in this repository.
* Release asset `A_series_saved_evidence_v1.0.0.zip`: all retained A-series run
  records, checkpoints, configurations, evaluations and original results.
  `archive_inventory.json` records every included path, size and SHA-256.

The archive excludes Dynamic Routing, other research tracks, caches, private
configuration and third-party literature. It does not include an unpublished
manuscript. Code: MIT. Original data/results/checkpoints: CC BY 4.0.

## Reproduction boundary

Historical CPU runs recorded Python 3.13.15, PyTorch 2.8.0+cpu and NumPy 2.3.3.
See per-run records; additional analysis dependencies were not completely pinned.
The supplied Dockerfile and requirements preserve the recorded base environment.
`requirements-analysis.txt` explicitly distinguishes compatible analysis ranges.
No model was retrained or evaluated in assembling this release. A.4-A.7 runs were
trained separately in the pinned container (per-run source hashes in
`experiment_A4_source.json`-`experiment_A7_source.json`); A.7R is a NumPy replay of saved codes. Original
oracle-noise per-trial predictions were not archived: conditional aggregate
tables exist, but a rank-preserved-by-NO_MATCH joint decomposition cannot be
recreated from them without rerunning the original analysis.

To reproduce the version-2 manuscript figures (Figures 1-4 and S1) **from saved tables only**:

```sh
python manuscript/tools/build_figures_v2.py
```

`build_figures.py` reproduces the earlier five-figure version.

This writes to `manuscript/submission/figures/`; it does not import training
modules. Historical experiment scripts are provided for independent future
reproduction, not run as part of release preparation. Serialized checkpoints
should be treated as executable-format artifacts and loaded only when trusted.

## Citation

Use `CITATION.cff` and cite the versioned GitHub release, not an unversioned
branch. This repository is private staging until the authors approve public
release. A private staging link is not a public data-deposit statement.
''')
(STAGE/'CITATION.cff').write_text('''cff-version: 1.2.0
message: "Please cite the versioned code and synthetic-data release."
title: "Serial reader precision: A-series code and synthetic research data"
type: dataset
version: 1.0.0
authors:
  - family-names: Huang
    given-names: Jing-Rung
    orcid: "https://orcid.org/0000-0003-4776-3550"
  - family-names: Lu
    given-names: Wen-Hsiang
    orcid: "https://orcid.org/0009-0002-5149-6790"
license: CC-BY-4.0
repository-code: "https://github.com/gbanyan/serial-reader-precision"
url: "https://github.com/gbanyan/serial-reader-precision/releases/tag/v1.0.0"
''')

# Local review package identity is not a published version/tag or DOI.
for name in ['README.md', 'LICENSE-DATA.md', 'CITATION.cff']:
    path = STAGE/name
    text = path.read_text().replace('A_series_saved_evidence_v1.0.0.zip', ARCHIVE_NAME)
    text = text.replace('version v1.0.0', 'local review package '+LABEL)
    text = text.replace('version: 1.0.0', 'version: "'+LABEL+'"')
    text = text.replace('url: "https://github.com/gbanyan/serial-reader-precision/releases/tag/v1.0.0"\n', '')
    path.write_text(text)
readme = STAGE/'README.md'
readme.write_text(readme.read_text()+'\n## Post-review companion records\n\nA01, A02 and A03 contain later deterministic saved-array diagnostics, their scripts\nand provenance. The supplementary inventory retains stable D01–D46 IDs, H01–H03\nhistorical source copies and a data dictionary, including D37/D38 aliasing;\nD47-D59 are the A.4-A.7R tables. Prospective specifications are in research/experiment_A4-A7R files;\ntheir timing rests on local Git commits, except A.7 and A.7R, which were pushed before running.\nA.2 oracle/noise analyses ran locally outside the recorded training container;\nA02 records its later NumPy version separately. This local package does not\nclaim a published GitHub tag or DOI. Historical v1.0.0 is preserved.\n')

archive_files = set(results)
for name in ['experiment_A','experiment_A1','experiment_A2','experiment_A3','experiment_A4','experiment_A5','experiment_A6','experiment_A7']:
    archive_files.update(p for p in (ROOT/'runs'/name).rglob('*') if eligible(p))
archive_files.update(code + notes + companions)
inventory = {str(p.relative_to(ROOT)): {'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(archive_files)}
(STAGE/'archive_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
archive = OUT / ARCHIVE_NAME
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(archive_files):
        z.write(p,p.relative_to(ROOT))
    for name in ['LICENSE','LICENSE-DATA.md','archive_inventory.json']:
        z.write(STAGE/name,name)

# Verify every archived original byte against its source manifest.
with zipfile.ZipFile(archive) as z:
    for name,record in inventory.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == record['sha256'], name
repo_inventory={str(p.relative_to(STAGE)):sha(p) for p in STAGE.rglob('*') if eligible(p) and '.git' not in p.parts and p.name != 'SHA256SUMS.json'}
(STAGE/'SHA256SUMS.json').write_text(json.dumps(repo_inventory,indent=2)+'\n')
report={'archive':str(archive.relative_to(ROOT)),'sha256':sha(archive),'bytes':archive.stat().st_size,'archived_original_files':len(inventory),'github_stage':str(STAGE),'repo_files':len(repo_inventory),'public_status':'NOT PUBLIC; author release approval pending','verification':'Every original archive entry matched its SHA-256 source inventory'}
(OUT/('package_report_' + LABEL + '.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

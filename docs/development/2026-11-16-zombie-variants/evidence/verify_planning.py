from pathlib import Path
import hashlib,json,re,subprocess
R=Path.cwd();D=R/'docs/development/2026-11-16-zombie-variants';O=D/'evidence'
initial=json.loads((O/'initial-identity.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[p for p,h in initial['files'].items() if sha(R/p)!=h]
assert changed==['docs/README.md'],changed
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==initial['head']
source_count=sum(p.startswith(('game/','engine/','platform/')) for p in initial['files'])
art_count=sum(p.startswith('assets/') for p in initial['files'])
assert art_count==114
links=[]
for p in [R/'AGENTS.md',R/'docs/README.md',*D.glob('*.md')]:
 text=p.read_text(encoding='utf-8')
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).exists():links.append([p.name,target])
assert not links,links
rules=R/'docs/WORK_RULES.md';assert sha(rules)=='b39a349c52440adbc365f7e53c3c511eb698975b5a4bbe4b6f0f9930bfc5c7a7'
# Verify old quarantine files against their retained original manifest.
import csv
old=R/'docs/maintenance/2026-10-23/evidence/protected-artwork.csv'
q=[x for x in csv.DictReader(old.open(encoding='utf-8')) if x['path'].startswith('.artifact-quarantine/')]
assert len(q)==18 and all(sha(R/x['path'])==x['sha256'] for x in q)
subprocess.run(['git','diff','--check'],check=True)
result=dict(date='2026-11-16',task='ZV-01 architecture planning and policy adoption',head_unchanged=initial['head'],production_source_files_unchanged=source_count,all_preexisting_production_tool_asset_inputs_unchanged=True,assets_current_paths_verified=art_count,quarantine_art_verified=len(q),only_preexisting_file_edited='docs/README.md (active assignment navigation)',new_policy_files=['AGENTS.md','docs/WORK_RULES.md'],rules_version='5.2',rules_sha256=sha(rules),documents=['ENGINEERING_ASSIGNMENT.md','SOL_EXECUTION_PROMPT.md','ARTWORK_INSPECTION.md'],broken_links=links,generator_probes='Two focused expected rejections: white in old 8x8 decoder and #03000F in held shotgun fire',runtime_builds_or_campaigns_run=False,internal_agents_or_automatic_transfers=False,commit_or_push=False,owner_dependencies=['Three missing scientist near frames','Explicit #03000F conversion decision'],next_action='Owner manually transfers Sol prompt; Sol starts dependency-ready engineering and preserves dependent content gates',cost='Unavailable')
(O/'planning-completion.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in [R/'AGENTS.md',R/'docs/WORK_RULES.md',R/'docs/README.md',*D.rglob('*')] if p.is_file() and p.name!='handoff-manifest.json'}
(O/'handoff-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))

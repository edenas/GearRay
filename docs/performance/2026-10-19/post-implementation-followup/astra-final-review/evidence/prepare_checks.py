"""Copy reviewed oracle harnesses into this review, redirect all builds and outputs."""
from pathlib import Path
R=Path.cwd();O=Path(__file__).resolve().parent;F=O.parents[1]/'evidence'
s=(F/'run_followup.py').read_text()
start=s.index('builds=');end=s.index('names=',start)
s=s[:start]+'''builds={'base':(ROOT/'build-astra-final-control',ROOT/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'), 'selected':(ROOT/'build-astra-final-selected',ROOT/'rom/GearRay-astra-final-selected.gg')}
build,rom=builds[tag];base,base_rom=builds['base'];java_tools=ROOT/'build-astra-final-selected/java-tools'
'''+s[end:]
(O/'run_oracle.py').write_text(s)
for name in ['occlusion_guard_matrix.py','functional_playthrough.py']:
 s=(F/name).read_text().replace("build-pir-base-20261022/java-tools","build-astra-final-selected/java-tools")
 s=s.replace("['row','combined']","['base','selected']").replace("tag=='row'","tag=='base'").replace("r['variant']=='combined'","r['variant']=='selected'")
 s=s.replace("ROOT/f'build-pir-{tag}-20261022'","ROOT/f'build-astra-final-{\"control\" if tag==\"base\" else \"selected\"}'")
 s=s.replace("ROOT/f'rom/GearRay-pir-{tag}-20261022.gg'","(ROOT/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg' if tag=='base' else ROOT/'rom/GearRay-astra-final-selected.gg')")
 if name=='occlusion_guard_matrix.py':
  # Use the two halves of the SAME central tile column; parity determines the label.
  s=s.replace("[('left',13),('right',14)]","[('left',12),('right',13)]")
 (O/name).write_text(s)
print('Prepared immutable-input oracle adaptations in',O)

"""Local dependency paths; no game changes and no automatic downloads."""
from pathlib import Path
import os,json
ROOT=Path(__file__).resolve().parents[2]
def load():
 values={'python_tools':'tools/.cache/performance/python-tools','ecj':'tools/.cache/performance/ecj-3.26.0.jar','java_home':'D:/Emulicious-with-Java64/java','emulator_jar':'D:/Emulicious-with-Java64/Emulicious.jar'}
 config=Path(os.environ.get('GEARRAY_PERF_CONFIG',str(Path(__file__).with_name('local.json'))))
 if config.exists():
  override=json.loads(config.read_text());unknown=set(override)-set(values)
  if unknown:raise ValueError('Unknown performance config keys: '+str(unknown))
  values.update(override)
 for key in values:
  p=Path(os.environ.get('GEARRAY_PERF_'+key.upper(),values[key]));values[key]=p if p.is_absolute() else ROOT/p
 return values
CONFIG=load()

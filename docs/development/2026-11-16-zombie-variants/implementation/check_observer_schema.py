"""Focused schema boundary assertions without an emulator campaign."""
from pathlib import Path
import json,sys,subprocess
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools/performance'))
from actor_layout import decode_actor,fixture_identity,LEGACY,VISUAL
checks=[]
def check(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append(name)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name)
    else:raise AssertionError(name)
record=bytes([0x80,6,0x80,5,0,0,0,12,0])
check('new standing security serialization',decode_actor(record,VISUAL),['80068005',{'visual_type':0,'animation_token':0},'000c00'])
check('scientist corpse identity',fixture_identity(VISUAL,visual_type=1,animation_token=6),bytes([1,6]))
legacy=record[:4]+bytes([0x34,0x56])+record[6:]
check('historical serializer unchanged',decode_actor(legacy,LEGACY,{0x5634:'_zombie_01_standing_pixels'}),['80068005','_zombie_01_standing_pixels','000c00'])
check('historical identity',fixture_identity(LEGACY,0x5634),bytes([0x34,0x56]))
reject('no layout guessing',lambda:decode_actor(record,None))
reject('no unknown legacy pointers',lambda:decode_actor(record,LEGACY,{}))
reject('new type range',lambda:decode_actor(record[:4]+bytes([2,0])+record[6:],VISUAL))
reject('new animation range',lambda:decode_actor(record[:4]+bytes([0,7])+record[6:],VISUAL))
reject('record size',lambda:decode_actor(record[:8],VISUAL))
reject('fixture type range',lambda:fixture_identity(VISUAL,visual_type=2))
p=subprocess.run([sys.executable,str(ROOT/'tools/performance/benchmark.py'),'--help'],cwd=ROOT,capture_output=True)
assert p.returncode==0 and b'--actor-layout' in p.stdout
checks.append('benchmark CLI declares explicit schema')
out={'status':'PASS','checks':len(checks),'coverage':checks,'emulator_campaign_run':False,'final_candidate_observer_qualification':'Luna pending'}
(Path(__file__).parent/'observer-schema-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

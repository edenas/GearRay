from pathlib import Path
import argparse,hashlib,json,sys,struct
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
from emulation_symbols import symbols
sys.path.insert(0,str(CONFIG['python_tools']))
import jpype
EXPECTED='b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'
COUNT=0xc1aa; ACTORS=0xc162

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--build',type=Path,required=True);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 raw=a.rom.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest==EXPECTED
 s=symbols(a.build.resolve());jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),classpath=[str(CONFIG['emulator_jar']),str(a.build.resolve()/'java-tools')]);J=jpype.JClass
 display=J('platform.DisplayWindow')();win=J('output.SMSDisplayWindow')(display,0,False);snd=J('output.SMSSoundOutput')(None,44100,100,2);snd.setSoundEnabled(False)
 g=J('system.GameGear')(win,snd,0);g.setButtons(J('components.input.SMSButtons')(J('PerfRunner$Pad')()));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(raw))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0);mem=g.getRAM()
 def put(addr,data):
  for i,v in enumerate(data):mem[(addr+i)&8191]=v&255
 def get(addr,n):return bytes(int(mem[(addr+i)&8191])&255 for i in range(n))
 def sym(name):
  for scope,n in [('global',name),('world_sprite',name),('zombie_corpses',name)]:
   if (scope,n) in s:return s[scope,n]&65535
  raise KeyError(name)
 def invoke(name,A=0,HL=0,args=(),expected_cleanup=0):
  pc=sym(name);put(0xdf00,b'\x00\xc5'+bytes(args));g.setRegValue(3,(A&255)<<8);g.setRegValue(2,HL&65535);g.setRegValue(6,0xdf00);g.setRegValue(7,pc);cycles=int(J('PerfRunner').until(g,0xc500,20_000_000));assert g.getSP()==0xdf02+expected_cleanup,(name,hex(g.getSP()),expected_cleanup);assert int(g.readByte(0xffff,0))==2,(name,'slot2 page');return cycles
 def count():return get(COUNT,1)[0]
 def rec(i):return struct.unpack('<hhBBBBB',get(ACTORS+9*i,9))
 def init():invoke('_world_sprites_initialize');assert count()==0
 def spawn(x,y,t):invoke('_world_sprite_initialize',A=x,HL=y,args=[t],expected_cleanup=1)
 def damage(i,d):invoke('_world_sprite_apply_damage',A=i,HL=d)
 def update():invoke('_world_sprites_update')
 def make_corpse(i):invoke('_world_sprite_make_corpse',A=i)
 checks=[];init()
 spawn(10,11,0);spawn(12,13,1)
 assert count()==2 and rec(0)[:4]==(10*256+128,11*256+128,0,0) and rec(1)[:4]==(12*256+128,13*256+128,1,0);checks.append('actual-ABI-spawn-both-types-and-9-byte-record')
 before=get(ACTORS,18);spawn(1,2,2);spawn(1,2,255);assert count()==2 and get(ACTORS,18)==before;checks.append('invalid-types-refused-with-record-preservation')
 for i in range(6):spawn(20+i,20, i&1)
 assert count()==8;last=get(ACTORS+7*9,9);spawn(31,31,0);assert count()==8 and get(ACTORS+7*9,9)==last;checks.append('eight-capacity-and-ninth-refusal')
 # Reinitialize and exercise actual packed hit parity, timer and lethal countdown.
 init();spawn(10,10,1);original=rec(0);damage(0,1);r1=rec(0);assert r1[2]==1 and r1[3]==3 and r1[4]==0 and (r1[5]&15)==11 and r1[6]==3;damage(0,1);r2=rec(0);assert r2[3]==4 and r2[4]==0 and (r2[5]&15)==10 and r2[6]==3;damage(0,1);r3=rec(0);assert r3[3]==3 and r3[4]==0 and (r3[5]&15)==9 and r3[6]==3;assert (r1[3],r2[3],r3[3])==(3,4,3);checks.append('same-type-packed-hit-parity-health-and-cooldown')
 type_before=rec(0)[2];damage(0,12);dead=rec(0);assert dead[2:5]==(1,5,1) and dead[5]==0x40 and dead[6]==4 and dead[0:2]==original[0:2];assert dead[2]==type_before
 for expected in (3,2,1,0):update();r=rec(0);assert r[6]==expected
 assert rec(0)[4]==2 and rec(0)[3]==6 and rec(0)[5]==0;checks.append('lethal-hit-four-frame-shot-dead-to-corpse-finalize')
 # Existing corpse at index 1; finalizing actor0 removes the higher index, preserving actor0.
 init();spawn(10,10,0);spawn(10,10,1);make_corpse(1);damage(0,12)
 for _ in range(4):update()
 assert count()==1 and rec(0)[2:7]==(0,6,2,0,0);checks.append('mixed-type-corpse-merge-survivor-order')
 # Swap removal preserves the complete last record while removing a non-last slot.
 init();spawn(2,2,0);spawn(3,3,1);spawn(4,4,0);last=rec(2);invoke('_world_sprite_remove',A=1);assert count()==2 and rec(1)==last;checks.append('nonlast-swap-remove-preserves-last-record')
 # Door path: one actor in door corridor becomes a corpse, distant actor is untouched.
 init();spawn(6,4,0);spawn(10,10,1);far=rec(1);invoke('_world_sprites_crush_in_door',A=4);assert count()==2 and rec(0)[4]==2 and rec(0)[3]==6 and rec(1)==far;checks.append('door-crush-corpse-and-distant-actor-preservation')
 result={'status':'PASS','candidate_sha256':digest,'candidate_bytes':len(raw),'executed_candidate_checks':len(checks),'checks':checks,'final_actor_count':count(),'slot2_page_after_every_call':2,'interrupts_enabled':False,'notes':['Actual linked Z80 APIs and emitted calling convention were used.','The script validates representative lifecycle branches, not the entire requested activation/LOS/chase/weapon/occlusion permutation campaign.','No IRQ was accepted inside calls in this script.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');jpype.shutdownJVM();print(json.dumps(result,indent=2))
if __name__=='__main__':main()




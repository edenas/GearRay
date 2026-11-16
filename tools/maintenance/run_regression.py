"""Explicit layout/path adapter for preserved compiled acceptance oracles.

Writes adapted source/results only into --output. Historical scripts stay exact.
"""
from pathlib import Path
import sys,argparse,re,importlib.util
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
from actor_layout import LAYOUTS,LEGACY,VISUAL
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['sprite','hud','camera','prep','material','wall','wrapper','ray','occlusion','transitions','playthrough']);ap.add_argument('--build',type=Path,required=True);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--java-tools',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--actor-layout',choices=LAYOUTS,default=LEGACY);ap.add_argument('--prepare-only',action='store_true',help='Write and compile adapted source without executing the campaign');args=ap.parse_args()
if args.actor_layout==VISUAL and args.mode in ('sprite','hud'):
 ap.error('The historical sprite/HUD modes compare old ROM outputs. Use an independent current-PNG scalar oracle for ZV-01; old-art equality is not new-content qualification.')
build=args.build.resolve();rom=args.rom.resolve();java=args.java_tools.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not str(out).casefold().startswith(str(ROOT).casefold()+'\\'):raise ValueError('Output outside GearRay')
restore=ROOT/'build/history-restore/oracles';control=restore/'build-astra-final-control';control_rom=restore/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'
review=ROOT/'docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence'
spec=importlib.util.spec_from_file_location('emulation_symbols',ROOT/'tools/performance/emulation_symbols.py');module=importlib.util.module_from_spec(spec);sys.modules['emulation_symbols']=module;spec.loader.exec_module(module)
def literal(p):return 'Path('+repr(str(p))+')'
def adapt(s):
 s=s.replace('from emulicious_bench import symbols','from emulation_symbols import symbols')
 s=s.replace("OUT=Path(__file__).resolve().parent",'OUT='+literal(out))
 s=s.replace("ROOT/'build-perf-20261019/python-tools'",literal(CONFIG['python_tools']))
 s=s.replace("ROOT/'build-astra-final-selected/java-tools'",literal(java))
 s=s.replace("'D:/Emulicious-with-Java64/java/bin/server/jvm.dll'",repr(str(CONFIG['java_home']/'bin/server/jvm.dll')))
 s=s.replace("'D:/Emulicious-with-Java64/Emulicious.jar'",repr(str(CONFIG['emulator_jar'])))
 s=s.replace("ROOT/f'build-astra-final-{\"control\" if tag==\"base\" else \"selected\"}'",'('+literal(control)+" if tag=='base' else "+literal(build)+')')
 s=s.replace("ROOT/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'",literal(control_rom)).replace("ROOT/'rom/GearRay-astra-final-selected.gg'",literal(rom))
 for name in ['baseline','exact']:
  s=s.replace("ROOT/'build-implementation-"+name+"'",literal(restore/('build-implementation-'+name)))
  s=s.replace("ROOT/'rom/GearRay-implementation-"+name+".gg'",literal(restore/'rom'/('GearRay-implementation-'+name+'.gg')))
 s=s.replace("ROOT/f'build-implementation-{name}'",'('+literal(build)+" if name=='production' else "+literal(restore)+"/f'build-implementation-{name}')")
 s=s.replace("ROOT/f'rom/GearRay-implementation-{name}.gg'",'('+literal(rom)+" if name=='production' else "+literal(restore/'rom')+"/f'GearRay-implementation-{name}.gg')")
 return s
if args.mode in ['occlusion','transitions','playthrough']:
 path=review/{'occlusion':'occlusion_guard_matrix.py','transitions':'renderer_transitions.py','playthrough':'functional_playthrough.py'}[args.mode]
 source=adapt(path.read_text(encoding='utf-8-sig'))
 if args.mode=='transitions' and args.actor_layout==VISUAL:
  # Keep this current-art forced-redraw campaign, but drop only the stale
  # October-vs-new-art VRAM digest equality. Run 24 scenes once on the actual
  # candidate with type/token actors; every incremental-vs-forced comparison,
  # ray guard, page check and dirty-change assertion remains active.
  source=source.replace("for tag in ['base','selected']:","for tag in ['selected']:")
  source=source.replace("def actor(x,y,pose='standing',state=0,health=12,timer=0):\n  return (x,y,pub('zombie_01_'+pose+'_pixels'),state,health,timer)",
   "def actor(x,y,pose='standing',state=0,health=12,timer=0,visual_type=0):\n  token={'standing':0,'walking_01':1,'walking_02':2,'shot_01':3,'shot_dead':5,'corps':6}[pose]\n  return (x,y,visual_type,token,state,health,timer)")
  source=source.replace("struct.pack('<hhHBBB',1664,1408,pub('zombie_01_standing_pixels'),0,12,0)",
                       "struct.pack('<hhBBBBB',1664,1408,0,0,0,12,0)")
  source=source.replace("struct.pack('<hhHBBB',*a)","struct.pack('<hhBBBBB',*a)")
  source=source.replace("[actor(1500+i*40,1200+i*65) for i in range(8)]",
                        "[actor(1500+i*40,1200+i*65,visual_type=i&1) for i in range(8)]")
  source=source.replace("  if tag=='base':reference[name]=digest\n  else:assert reference[name]==digest,(name,'A/B mismatch')",
                        "  reference[name]=digest")
  source=source.replace("assert len(reference)==24 and len(all_records)==48",
                        "assert len(reference)==24 and len(all_records)==24")
  source=source.replace('Incremental versus forced redraw plus control/selected output comparison.',
                        'Current candidate incremental versus forced redraw; no old-art output comparison.')
  required=["for tag in ['selected']:","struct.pack('<hhBBBBB',*a)","visual_type=i&1", "len(all_records)==24"]
  if any(token not in source for token in required):
   raise ValueError('Could not adapt renderer transition fixture to visual-type-animation-v1')
  (out/'transitions-actor-layout.txt').write_text('visual-type-animation-v1; eight-actor scene alternates security/scientist; current candidate runs incremental vs forced redraw\n',encoding='utf-8')
 if args.mode=='occlusion' and args.actor_layout==VISUAL:
  # The same 36 depth/appearance/removal checks run against the current ROM.
  # Only obsolete October/new-art digest equality is removed; each current
  # incremental composition is still compared byte-for-byte to forced redraw.
  source=source.replace("for tag in ['base','selected']:","for tag in ['selected']:")
  source=source.replace("def entity(kind,present):\n  put(local('world_sprite','world_sprite_count'),bytes([int(kind=='actor' and present)]))\n  put(pub('owned_weapons'),bytes([1 if kind=='pickup' and present else 3]))\n  if kind=='actor':put(local('world_sprite','world_sprites'),struct.pack('<hhHBBB',1664,1408,pub('zombie_01_standing_pixels'),0,12,0))",
   "def entity(kind,present,visual_type=0):\n  put(local('world_sprite','world_sprite_count'),bytes([int(kind=='actor' and present)]))\n  put(pub('owned_weapons'),bytes([1 if kind=='pickup' and present else 3]))\n  if kind=='actor':put(local('world_sprite','world_sprites'),struct.pack('<hhBBBBB',1664,1408,visual_type,0,0,12,0))")
  source=source.replace("def setup(kind,present):", "def setup(kind,present,visual_type=0):")
  source=source.replace("entity(kind,present);invalidate();invoke('game_gear_sprite_projection_invalidate')",
                        "entity(kind,present,visual_type);invalidate();invoke('game_gear_sprite_projection_invalidate')")
  source=source.replace("setup(kind,present_before);set_ray(ray,before,offsets[0]);", "setup(kind,present_before,index&1);set_ray(ray,before,offsets[0]);")
  source=source.replace("entity(kind,present_after);set_ray(ray,after,offsets[1]);", "entity(kind,present_after,index&1);set_ray(ray,after,offsets[1]);")
  source=source.replace("struct.pack('<hhHBBB',1664,1408,pub('zombie_01_standing_pixels'),0,12,0)",
                        "struct.pack('<hhBBBBB',1664,1408,visual_type,0,0,12,0)")
  source=source.replace("  if tag=='base':reference[name]=digest\n  else:assert reference[name]==digest,(name,'row/combined mismatch')",
                        "  reference[name]=digest")
  if "struct.pack('<hhHBBB'" in source or "pub('zombie_01_standing_pixels')" in source:
   raise ValueError('Could not adapt occlusion actor fixture to visual-type-animation-v1')
  (out/'occlusion-actor-layout.txt').write_text('visual-type-animation-v1; left half security, right half scientist; current candidate incremental vs forced redraw\n',encoding='utf-8')
 if args.mode=='playthrough' and args.actor_layout==VISUAL:
  source=source.replace('import jpype','from actor_layout import decode_actor,VISUAL\nimport jpype',1)
  source=source.replace("for tag in ['base','selected']:","for tag in ['selected']:")
  old="raw=read(addr('world_sprite','world_sprites')+i*9,9);data['actors'].append([raw[:4].hex(),pointers[int.from_bytes(raw[4:6],'little')],raw[6:].hex()])"
  new="raw=read(addr('world_sprite','world_sprites')+i*9,9);data['actors'].append(decode_actor(raw,VISUAL))"
  if old not in source:raise ValueError('Current playthrough actor decoder pattern changed')
  source=source.replace(old,new)
  old="  if tag=='base':reference[name]=data\n  else:assert reference[name]==data,(name,'A/B mismatch')"
  if old not in source:raise ValueError('Playthrough A/B record boundary changed')
  source=source.replace(old,"  reference[name]=data")
  source=source.replace("'paired_checkpoints':len(reference)","'candidate_checkpoints':len(reference),'actor_layout':'visual-type-animation-v1','rom_sha256':hashlib.sha256(rom).hexdigest()")
  needle="restore();byte(addr('world_sprite','world_sprite_count'),0);initial=read(addr('player','player_position_y'),2)"
  mixed="restore();boot_actors=sim()['actors'];assert [actor[1]['visual_type'] for actor in boot_actors]==[0,0,1,1];"+\
   "[frame() for _ in range(16)];active_actors=sim()['actors'];assert [actor[1]['visual_type'] for actor in active_actors]==[0,0,1,1];record('mixed-live-actor-loop');"+\
   "byte(addr('world_sprite','world_sprite_count'),0);initial=read(addr('player','player_position_y'),2)"
  if needle not in source:raise ValueError('Current playthrough typed-boot boundary changed')
  source=source.replace(needle,mixed,1)
  source=source.replace('Actual compiled ROMs with pinned VDP phase.','Actual current candidate with pinned VDP phase and type/token records; no historical-art digest equality.')
  source=source.replace('paired compiled playthrough checkpoints','candidate compiled playthrough checkpoints')
  required=["for tag in ['selected']:","decode_actor(raw,VISUAL)","'candidate_checkpoints':len(reference)","assert sim()==stable","compiled-death-logo-world-restart","mixed-live-actor-loop"]
  if any(token not in source for token in required):raise ValueError('Incomplete current-candidate playthrough adaptation')
  (out/'playthrough-actor-layout.txt').write_text('visual-type-animation-v1; current candidate only; original movement/fire/pickup/pause/restart predicates retained\n')
 (out/(args.mode+'-executed.py')).write_text(source,encoding='utf-8');sys.argv=[str(path)]
else:
 path=review/'run_oracle.py';source=path.read_text(encoding='utf-8-sig')
 source=source.replace('OUT=Path(__file__).resolve().parent','OUT='+literal(out))
 source=source.replace("str(ROOT/'build-perf-20261019/python-tools')",'str('+literal(CONFIG['python_tools'])+')')
 source=re.sub(r'^builds=.+$',lambda m:"builds={'base':("+literal(control)+','+literal(control_rom)+"),'selected':("+literal(build)+','+literal(rom)+')}',source,flags=re.M)
 source=source.replace("java_tools=ROOT/'build-astra-final-selected/java-tools'",'java_tools='+literal(java))
 # The outer historical adapter transforms the original oracle before this
 # final pass moves its remaining scalar reference and output paths.
 source=source.replace("(OUT/(tag+'-'+mode+'-executed.py')).write_text", "source=adapt(source)\n(OUT/(tag+'-'+mode+'-executed.py')).write_text")
 if args.mode=='prep' and args.actor_layout==VISUAL:
  source=source.replace(
   "source=adapt(source)\n(OUT/(tag+'-'+mode+'-executed.py')).write_text",
   "source=adapt(source)\n"+
   "if mode=='prep':\n"+
   " source=source.replace(\"z=local('world_sprite','world_sprites');pixel=pub('zombie_01_standing_pixels')\",\"z=local('world_sprite','world_sprites')\")\n"+
   " source=source.replace(\"struct.pack('<hhHBBB',x,y,pixel,0,12,0)\",\"struct.pack('<hhBBBBB',x,y,i&1,0,0,12,0)\")\n"+
   " if \"struct.pack('<hhBBBBB',x,y,i&1,0,0,12,0)\" not in source: raise ValueError('Could not adapt prep fixture to visual-type-animation-v1')\n"+
   " Path(OUT/'prep-actor-layout.txt').write_text('visual-type-animation-v1; actors alternate security/scientist; offsets 4/5 are type/token\\n',encoding='utf-8')\n"+
   "(OUT/(tag+'-'+mode+'-executed.py')).write_text")
  (out/'prep-actor-layout.txt').write_text('visual-type-animation-v1; actors alternate security/scientist; offsets 4/5 are type/token\n',encoding='utf-8')
 (out/(args.mode+'-adapter.py')).write_text(source,encoding='utf-8');sys.argv=[str(path),args.mode,'selected']
# Always validate rewritten Python before executing. Preparation alone is not
# evidence that the compiled campaign or its assertions passed.
compile(source,str(path),'exec')
if args.prepare_only:
 print('Prepared syntax-valid',args.mode,args.actor_layout,'without campaign execution')
 sys.exit(0)
# Guard each historical Path write before executing anything. No old result
# can be overwritten by an incomplete path adaptation.
original_write=Path.write_text
def guarded_write(p,*a,**kw):
 if not str(p.resolve()).casefold().startswith(str(out).casefold()+'\\'):raise ValueError('Historical write blocked: '+str(p))
 return original_write(p,*a,**kw)
Path.write_text=guarded_write
exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path),'Path':Path,'adapt':adapt})

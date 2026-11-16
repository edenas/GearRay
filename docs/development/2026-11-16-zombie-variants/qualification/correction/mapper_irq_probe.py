from pathlib import Path
import argparse,hashlib,json,sys,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
from emulation_symbols import symbols
sys.path.insert(0,str(CONFIG['python_tools']))
import jpype
EXPECTED='b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'
PALETTE={'#000000':0,'#ad3e00':1,'#4d4d4d':2,'#797878':3,'#008cb4':4,'#b51a00':5,'#bb2200':5,'#785700':6,'#53602a':7,'#006d8f':8,'#2d2d2d':10,'#ffc4ab':11,'#ffffff':12,'#1a1a1a':13,'#ffa57d':15}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--build',type=Path,required=True);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--loops',type=int,default=400);a=ap.parse_args()
 raw=a.rom.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest==EXPECTED;s=symbols(a.build.resolve());jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),classpath=[str(CONFIG['emulator_jar']),str(a.build.resolve()/'java-tools')]);J=jpype.JClass
 display=J('platform.DisplayWindow')();win=J('output.SMSDisplayWindow')(display,0,False);snd=J('output.SMSSoundOutput')(None,44100,100,2);snd.setSoundEnabled(False);g=J('system.GameGear')(win,snd,0);g.setButtons(J('components.input.SMSButtons')(J('PerfRunner$Pad')()));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(raw))));g.reset();g.execute(100000);mem=g.getRAM();
 def put(addr,data):
  for i,v in enumerate(data):mem[(addr+i)&8191]=v&255
 def read(addr,n):return bytes(int(mem[(addr+i)&8191])&255 for i in range(n))
 def sym(scope,name):return s[scope,'_'+name]&65535
 def count_call(pc,hl=0,de=0,A=0,args=(),pageslot2=None):
  put(0xdf00,b'\x00\xc5'+bytes(args));g.setRegValue(3,(A&255)<<8);g.setRegValue(2,hl&65535);g.setRegValue(1,de&65535);g.setRegValue(6,0xdf00);g.setRegValue(7,pc)
  if pageslot2 is not None:g.writeByte(0xffff,pageslot2,0)
  entered=False; irq=[];cy=0;lo=0xdf00
  while g.getPC()!=0xc500:
   before=int(g.getPC());sp=int(g.getSP()); page2=int(g.readByte(0xffff,0));lo=min(lo,sp);elapsed=-int(g.executeOnce(0));cy+=elapsed;after=int(g.getPC())
   if before==pc:entered=True
   if elapsed==13 and after==0x38:
    irq.append({'after_entry_instruction':entered,'page2':page2,'sp':hex(sp),'slot1':int(g.readByte(0xfffe,0))})
   if cy>2_000_000:raise RuntimeError(('timeout',hex(pc),hex(g.getPC())))
  return cy,irq,lo,int(g.getSP()),int(g.readByte(0xffff,0))
 g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0);g.setInterruptsEnabled(True)
 source_path=ROOT/'assets/sprites/enemies/zombie/zombie_02_attack_01_32x32.png'
 with Image.open(source_path) as im0:
  im=im0.convert('RGBA');rows=[]
  for y in range(im.height):
   row=[]
   for x in range(im.width):
    r,gg,b,alpha=im.getpixel((x,y));row.append(15 if alpha==0 else PALETTE[f'#{r:02x}{gg:02x}{b:02x}'])
   rows.append(row)
 sy,sx=next((y,x) for y,row in enumerate(rows) for x,c in enumerate(row) if c==12)
 tx,ty=(sx*2)//8,(sy*2)//8
 def paint(tile,x,y,col):
  m=128>>(x&7)
  for plane in range(4):
   i=y*4+plane;tile[i]=(tile[i]&~m)|(m if col&(1<<plane) else 0)
 def expected():
  out=bytearray((i*73+41)&255 for i in range(32))
  for py in range(8):
   yy=ty*8+py
   if yy>=64:continue
   v=min(31,(yy*128)>>8)
   for px in range(8):
    xx=tx*8+px
    if xx>=64:continue
    u=min(31,(xx*128)>>8);c=rows[v][u]
    if c!=15:paint(out,px,py,c)
  return bytes(out)
 expected_tile=expected();call_page4=[];irq_page4=[];wrapper=sym('video','game_gear_overlay_sprite_tile')
 proj=struct.pack('<BhhhhHHHBB',1,0,64,0,64,512,128,0,12,32);ray=b''.join(struct.pack('<BBBBH',32,0,0,1,513) for _ in range(28))
 for i in range(a.loops):
  seed=bytes((j*73+41)&255 for j in range(32));put(0xc800,seed);put(0xc900,proj);put(0xcb00,ray);put(0xddff,b'\x5a');put(0xde00,b'\xa5')
  cyc,irqs,lo,sp,page=count_call(wrapper,0xc800,args=bytes([tx,ty,0x00,0xc9,0x00,0xcb]),pageslot2=4);assert sp==0xdf08 and page==4,(hex(sp),page,hex(lo),cyc,irqs);assert read(0xddff,1)==b'\x5a' and read(0xde00,1)==b'\xa5';
  if read(0xc800,32)!=expected_tile:raise AssertionError(('near tile oracle mismatch',i,read(0xc800,32).hex(),expected_tile.hex()))
  call_page4.append(cyc);irq_page4.extend(irqs)
 # Seed valid native wall plans and repeatedly call the actual page-0 wrapper which maps slot2=3,
 # executes _wall_plan_rows there, and restores the exact incoming page.
 left=sym('video','left_wall_plan');right=sym('video','right_wall_plan');wrapper3=sym('video','game_gear_build_native_wall_tile')
 plan=bytes([0]*32+[3]*16+[1,0,64])
 put(left,plan);put(right,plan);call_page3=[];irq_page3=[]
 for i in range(a.loops):
  seed=bytes((j*19+i*7)&255 for j in range(32));put(0xc7ff,b'\xa7'+seed+b'\x5d')
  cyc,irqs,lo,sp,page=count_call(wrapper3,0xc800,args=bytes([8]),pageslot2=2);assert sp==0xdf03 and page==2 and read(0xc7ff,1)==b'\xa7' and read(0xc820,1)==b'\x5d'
  call_page3.append(cyc);irq_page3.extend(irqs)
 hits4=[x for x in irq_page4 if x['after_entry_instruction'] and x['page2']==4]
 hits3=[x for x in irq_page3 if x['after_entry_instruction'] and x['page2']==3]
 result={'status':'PASS' if hits4 and hits3 else 'INCOMPLETE_IRQ_NOT_ACCEPTED_IN_BOTH_SCOPES','candidate_sha256':digest,'candidate_bytes':len(raw),'loops_per_scope':a.loops,'interrupts_enabled':True,'near_page4':{'entry':hex(wrapper),'calls':len(call_page4),'cycles_min_median_max':[min(call_page4),sorted(call_page4)[len(call_page4)//2],max(call_page4)],'accepted_irq_count':len(irq_page4),'accepted_after_entry_with_page4_mapped':len(hits4),'all_returns_page4_sp_df08':True,'min_stack_address':hex(min([0xdf00]+[int(x['sp'],16) for x in irq_page4])),'actual_white_witness_scalar_match_each_call':True},'native_page3_nested_wrapper':{'entry':hex(wrapper3),'callee_page3':hex(sym('global','wall_plan_rows')),'calls':len(call_page3),'cycles_min_median_max':[min(call_page3),sorted(call_page3)[len(call_page3)//2],max(call_page3)],'accepted_irq_count':len(irq_page3),'accepted_after_entry_with_page3_mapped':len(hits3),'all_returns_page2_sp_df03':True,'min_stack_address':hex(min([0xdf00]+[int(x['sp'],16) for x in irq_page3])),'RAM_guards_intact':True,'native_output_changed_from_seed_each_call':True},'irq_page_observations':{'near':irq_page4,'native':irq_page3},'nmi':'No NMI injection/control established by this emulator API; this is IRQ-only evidence and does not establish NMI behavior.','hardware':'No physical Game Gear test.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2));jpype.shutdownJVM()
if __name__=='__main__':main()



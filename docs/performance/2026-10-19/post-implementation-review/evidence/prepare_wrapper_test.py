from pathlib import Path
import subprocess
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence/implementation';OUT=Path(__file__).resolve().parent
s=(E/'WallOracle.java').read_text().replace('public final class WallOracle','public final class WallWrapperOracle')
s=s.replace('int[] edge={1,8,9,16};','int[] edge={1,8,9,16}; int[] heights={1,2,7,8,9,15,16,17,31,32,63,64,65,127,143,144};')
s=s.replace('hi<132','hi<heights.length').replace('int height=hi<4?edge[hi]:hi+13;','int height=heights[hi];')
s=s.replace('call(newer,pc[8],0xd200,0xd300,new int[]{column});call(newer,pc[8],0xd206,0xd340,new int[]{column});','newer.writeByte(0xffff,3,0);call(newer,pc[8],0xd200,pc[10],new int[]{column});call(newer,pc[8],0xd206,pc[11],new int[]{column});newer.writeByte(0xffff,2,0);')
s=s.replace('long after=call(newer,pc[9],0xd000,0xd300,new int[]{0x40,0xd3,y,4});\n                    after+=call(newer,pc[9],0xd010,0xd300,new int[]{0x40,0xd3,y+4,4});','long after=call(newer,pc[12],0xd000,0,new int[]{y});\n                    if(newer.readByte(0xffff,0)!=2 || newer.readByte(0xfffe,0)!=1)throw new IllegalStateException("Mapper restoration");')
(OUT/'WallWrapperOracle.java').write_text(s)
subprocess.run(['D:/Emulicious-with-Java64/java/bin/java.exe','-jar',str(ROOT/'build-implementation-baseline/ecj-3.26.0.jar'),'-1.8','-cp','D:/Emulicious-with-Java64/Emulicious.jar;'+str(ROOT/'build-post-review-20261022/java-tools'),'-d',str(ROOT/'build-post-review-20261022/java-tools'),str(OUT/'WallWrapperOracle.java')],check=True)
s=(OUT/'wall-executed.py').read_text()
s=s.replace("sys.path.insert(0,str(E))", "sys.path.insert(0,str(E));sys.path.insert(0,str(E/'implementation'))")
s=s.replace("result=J('WallOracle')", "pc += [b['video','_'+n]&65535 for n in ['left_wall_plan','right_wall_plan','game_gear_build_native_wall_tile']]\nresult=J('WallWrapperOracle')")
s=s.replace('final-wall-bank3-compiled-oracle.json','wall-wrapper-oracle.json').replace('All 128 near heights plus 1/8/9/16','16 selected heights 1,2,7,8,9,15,16,17,31,32,63,64,65,127,143,144; actual eight-row production wrapper and restoration to slot1=1/slot2=2')
(OUT/'wall-wrapper-executed.py').write_text(s)

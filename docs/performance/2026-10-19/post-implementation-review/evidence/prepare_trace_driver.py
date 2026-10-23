from pathlib import Path
import subprocess
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
s=(ROOT/'docs/performance/2026-10-19/evidence/implementation/EmulationRunner.java').read_text().replace('public final class EmulationRunner','public final class ReviewRunner')
s=s.replace('public long cycles;', 'public long cycles,coldCycles,wallCycles;')
s=s.replace('long start=out.cycles;', 'long start=out.cycles; int page1=g.readByte(0xfffe,0),page2=g.readByte(0xffff,0);')
s=s.replace('pad.time+=elapsed;', 'pad.time+=elapsed;\n            if(pc>=0x4000 && pc<0x8000 && page1==3)out.coldCycles+=elapsed;\n            if(pc>=0x9200 && pc<0xb1d4 && page2==3)out.wallCycles+=elapsed;')
# Local argument-taking workers clean up stacked byte arguments. Bounded to
# this nonrecursive call graph; per-region counts are independent of spans.
s=s.replace('pc==a.ret && sp==a.sp','pc==a.ret && sp>=a.sp && sp<=a.sp+20')
(OUT/'ReviewRunner.java').write_text(s)
subprocess.run(['D:/Emulicious-with-Java64/java/bin/java.exe','-jar',str(ROOT/'build-implementation-baseline/ecj-3.26.0.jar'),'-1.8','-cp','D:/Emulicious-with-Java64/Emulicious.jar','-d',str(ROOT/'build-post-review-20261022/java-tools'),str(OUT/'ReviewRunner.java')],check=True)

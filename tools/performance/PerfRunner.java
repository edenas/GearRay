import system.GameGear;
import components.input.ButtonInputProvider;
import java.util.ArrayList;

/** Measurement driver only. Executes the installed, unmodified emulator core.
 * Events are recorded only when the observed opcode actually executes; IRQ
 * acceptance at the same PC must not duplicate a call/upload/mapper event.
 */
public final class PerfRunner {
    public static final class Pad implements ButtonInputProvider {
        public int held;
        public long time;
        public boolean pulse;
        public long[] eventTimes=new long[0];
        public int[] eventMasks=new int[0];
        public int eventIndex;
        public void setRequireWindowFocus(boolean focus) { }
        public void addButtonListener(ButtonInputProvider.ButtonListener listener) { }
        public void removeButtonListener(ButtonInputProvider.ButtonListener listener) { }
        public void setButtonMap(int[][] map) { }
        public int[] getButtonMap(int button) { return new int[0]; }
        public boolean isButtonDown(int button) {
            while(eventIndex<eventTimes.length && time>=eventTimes[eventIndex]) {
                held=eventMasks[eventIndex++];
            }
            return (held & (1 << button)) != 0
                || (pulse && button == 8 && time >= 100000 && time < 200000);
        }
    }
    public static final class Span {
        public int root, ret, sp, returnPage;
        public long start;
        Span(int r, int a, int s, long t) { this(r,a,s,t,-1); }
        Span(int r,int a,int s,long t,int p) {root=r;ret=a;sp=s;start=t;returnPage=p;}
    }
    public static final class Result {
        public long cycles,coldCycles,wallCycles;
        public int minSP=65535, keys, duplicateInterruptEntries, unclosedSpans, firstInterruptPC=-1;
        public long[] stages;
        public int[] counts;
        Result(int roots, int counters) { stages=new long[roots]; counts=new int[counters]; }
    }
    public static long until(GameGear g, int pc, long limit) {
        long t=0;
        while (g.getPC() != pc) {
            t -= g.executeOnce(0);
            if (t > limit) throw new IllegalStateException("CPU boundary timeout");
        }
        return t;
    }
    public static long[] call(GameGear g,int pc,int hl,int de,int[] args,int probe) {
        int[] ram=g.getRAM();ram[0x1f00]=0;ram[0x1f01]=0xc5;
        for(int i=0;i<args.length;i++)ram[0x1f02+i]=args[i]&255;
        g.setRegValue(6,0xdf00);g.setRegValue(2,hl);g.setRegValue(1,de);g.setRegValue(7,pc);
        long cycles=0,count=0;int low=0xdf00;
        while(g.getPC()!=0xc500) {
            int before=g.getPC(),sp=g.getSP();low=Math.min(low,sp);
            int elapsed=-g.executeOnce(0);cycles+=elapsed;
            boolean irq=elapsed==13 && g.getPC()==0x38 && g.getSP()==((sp-2)&65535);
            if(!irq && before==probe)count++;
            if(cycles>100000000)throw new IllegalStateException("Compiled call timeout");
        }
        return new long[]{cycles,count,g.getSP(),low};
    }
    /** cleanupBytes is verified callee cleanup, excluding the 2-byte return.
     * Match exact SP and physical return page; no bounded-SP heuristic. */
    public static Result frame(GameGear g, Pad pad, int inputPC, int inputReturn,
            int keys, int[] roots, int[] rootPages, int[] cleanupBytes,
            int[] counters,int[] counterPages,int wallBegin,int wallEnd,long limit) {
        if(roots.length!=cleanupBytes.length || roots.length!=rootPages.length)
            throw new IllegalArgumentException("Missing per-symbol ABI metadata");
        Result out=new Result(roots.length,counters.length);
        ArrayList<Span> spans=new ArrayList<Span>();int[] ram=g.getRAM();boolean entered=false;
        do {
            int pc=g.getPC(),sp=g.getSP();long start=out.cycles;
            int page1=g.readByte(0xfffe,0),page2=g.readByte(0xffff,0);
            close(g,spans,out,roots,inputPC,keys,start);
            int ret=ram[sp&8191]|(ram[(sp+1)&8191]<<8);
            int returnPage=ret<0x4000?0:ret<0x8000?page1:ret<0xc000?page2:-1;
            out.minSP=Math.min(out.minSP,sp);
            int elapsed=-g.executeOnce(0);out.cycles+=elapsed;pad.time+=elapsed;
            boolean irq=elapsed==13 && g.getPC()==0x38 && g.getSP()==((sp-2)&65535);
            boolean nmi=elapsed==11 && g.getPC()==0x66 && g.getSP()==((sp-2)&65535);
            if(irq || nmi) {if(out.firstInterruptPC<0)out.firstInterruptPC=pc;out.duplicateInterruptEntries++;continue;}
            if(pc>=0x4000 && pc<0x8000 && page1==3)out.coldCycles+=elapsed;
            if(pc>=wallBegin && pc<wallEnd && page2==3)out.wallCycles+=elapsed;
            if(pc==inputPC)entered=true;
            for(int i=0;i<counters.length;i++)
                if(pc==counters[i] && pageAt(pc,counterPages[i],page1,page2))out.counts[i]++;
            for(int i=0;i<roots.length;i++)
                if(pc==roots[i] && pageAt(pc,rootPages[i],page1,page2))
                    spans.add(new Span(i,ret,(sp+2+cleanupBytes[i])&65535,start,returnPage));
            if(out.cycles>limit)throw new IllegalStateException("Frame timeout at "+Integer.toHexString(pc));
        } while(!entered || g.getPC()!=inputPC);
        close(g,spans,out,roots,inputPC,keys,out.cycles);out.unclosedSpans=spans.size();
        return out;
    }
    private static void close(GameGear g,ArrayList<Span> spans,Result out,
            int[] roots,int inputPC,int keys,long clock) {
        int pc=g.getPC(),sp=g.getSP();int[] ram=g.getRAM();
        for(int i=spans.size()-1;i>=0;i--) {
            Span a=spans.get(i);
            if(pc==a.ret && sp==a.sp && (a.returnPage<0 || page(g,pc,a.returnPage))) {
                out.stages[a.root]+=clock-a.start;
                if(roots[a.root]==inputPC)out.keys=ram[keys&8191]|(ram[(keys+1)&8191]<<8);
                spans.remove(i);
            }
        }
    }
    private static boolean pageAt(int pc,int expected,int slot1,int slot2) {
        return pc<0x4000?expected==0:pc<0x8000?slot1==expected:pc<0xc000?slot2==expected:true;
    }
    static boolean page(GameGear g,int pc,int expected) {
        return pc<0x4000?expected==0:pc<0x8000?g.readByte(0xfffe,0)==expected:
            pc<0xc000?g.readByte(0xffff,0)==expected:true;
    }
}

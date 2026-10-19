import system.GameGear;
import output.SMSDisplayWindow;
import output.SMSSoundOutput;
import java.util.ArrayList;

public final class SchedulerRunner {
    public static final class Gear extends GameGear {
        public boolean trace;
        public RasterWindow raster;
        public int captureEnabled, frontWrites, r2=14, address, command, first=-1;
        public ArrayList<int[]> registerWrites=new ArrayList<int[]>();
        public long clock;
        public int controlLatchResets, unmaskedControlPairs, payloadBytes, mapperWrites;
        public int[] mapperValues=new int[1024];
        public Gear(SMSDisplayWindow window,SMSSoundOutput sound) { super(window,sound,0); }
        public int readPort(int port,int cycles) {
            if((port&255)==191) {
                if(trace && first>=0 && getRAM()[captureEnabled&8191]!=0) controlLatchResets++;
                first=-1;
            }
            return super.readPort(port,cycles);
        }
        public void writePort(int port,int value,int cycles) {
            int p=port&255;
            if(p==191) {
                if(first<0) {
                    first=value;
                    if(trace && getRAM()[captureEnabled&8191]!=0 && isInterruptsEnabled()) unmaskedControlPairs++;
                }
                else {
                    if((value&192)==128) {
                        int reg=value&15;
                        if(reg==2) r2=first;
                        if(trace && (reg==2 || reg==8)) registerWrites.add(new int[]{reg,first,getScanline(),cycles,(int)clock});
                    } else { command=value&192;address=((value&63)<<8)|first; }
                    first=-1;
                }
            } else if(p==190 && command==64) {
                if(trace) payloadBytes++;
                if(trace && getRAM()[captureEnabled&8191]!=0) {
                    int base=(r2&14)==12?0x1ac0:0xcc0;
                    int names=(r2&14)==12?0x3000:0x3800;
                    if((address>=base && address<base+3584) || (address>=names && address<names+1792)) frontWrites++;
                }
                address=(address+1)&16383;
            }
            super.writePort(port,value,cycles);
        }
        public void writeByte(int address,int value,int cycles) {
            if(trace && address>=0xfffc && address<=0xffff) {mapperWrites++;mapperValues[(address-0xfffc)*256+(value&255)]++;}
            super.writeByte(address,value,cycles);
        }
    }
    public static final class Event {
        public int kind,sequence,generation;
        public long cycles;
        public byte[] data, vram;
        Event(int k,int s,int gen,long c,byte[] d,byte[] v) {kind=k;sequence=s;generation=gen;cycles=c;data=d;vram=v;}
    }
    public static final class Result {
        public long cycles;
        public int minSP=65535;
        public int bankViolations,irqRegisterViolations;
        public long[] total,max;
        public int[] count;
        public long[][] phaseMax;
        public ArrayList<Event> events=new ArrayList<Event>();
        Result(int n) {total=new long[n];max=new long[n];count=new int[n];phaseMax=new long[n][256];}
    }
    static int word(int[] ram,int address) {return ram[address&8191]|(ram[(address+1)&8191]<<8);}
    static byte[] ranges(int[] ram,int[] ranges) {
        int count=0;for(int i=1;i<ranges.length;i+=2) count+=ranges[i];
        byte[] out=new byte[count];int n=0;
        for(int i=0;i<ranges.length;i+=2) for(int j=0;j<ranges[i+1];j++) out[n++]=(byte)ram[(ranges[i]+j)&8191];
        return out;
    }
    static byte[] vram(GameGear g) {
        int[] ram=g.getVRAM();byte[] out=new byte[ram.length];for(int i=0;i<ram.length;i++)out[i]=(byte)ram[i];return out;
    }
    public static Result run(Gear g,EmulationRunner.Pad pad,int[] roots,int[] rootPages,int[] phases,
            int sequence,int periods,int[] stateRanges,int snapshot,int snapshotSize,
            int displayedGeneration,int generation,int holdAddress,int holdPeriods,int inputLatest) {
        Result result=new Result(roots.length);int[] ram=g.getRAM();
        int firstSequence=word(ram,sequence),lastDisplayed=word(ram,displayedGeneration);
        ArrayList<EmulationRunner.Span> active=new ArrayList<EmulationRunner.Span>();
        ArrayList<Integer> phaseValues=new ArrayList<Integer>();
        byte[] lastCapture=null;
        int irqReturn=-1,irqSP=0;int[] irqRegisters=new int[6];
        while(((word(ram,sequence)-firstSequence)&65535)<periods || !active.isEmpty()) {
            int pc=g.getPC(),sp=g.getSP(),ret=word(ram,sp);
            result.minSP=Math.min(result.minSP,sp);
            long t=result.cycles;
            int frame=word(ram,sequence);
            if(pc==irqReturn && sp==irqSP) {
                for(int i=0;i<6;i++) if(g.getRegisterValue(i)!=irqRegisters[i]) result.irqRegisterViolations++;
                irqReturn=-1;
            }
            for(int i=active.size()-1;i>=0;i--) {
                EmulationRunner.Span span=active.get(i);
                if(pc!=span.ret || sp!=span.sp) continue;
                int root=span.root;long cost=t-span.start;
                if((root==0 || root==1 || root==5 || root==6 || root==7)
                    && (g.readByte(0xfffe,0)!=1 || g.readByte(0xffff,0)!=2)) result.bankViolations++;
                result.count[root]++;result.total[root]+=cost;result.max[root]=Math.max(result.max[root],cost);
                int phase=phaseValues.get(i);result.phaseMax[root][phase]=Math.max(result.phaseMax[root][phase],cost);
                if(root==9) result.events.add(new Event(7,frame,word(ram,generation),t,ranges(ram,stateRanges),null));
                if(root==13) result.events.add(new Event(5,frame,word(ram,generation),t,ranges(ram,stateRanges),null));
                if(root==0) result.events.add(new Event(0,frame,word(ram,generation),t,ranges(ram,stateRanges),null));
                if(root==2) result.events.add(new Event(3,frame,word(ram,generation),t,
                    new byte[]{(byte)ram[inputLatest&8191]},null));
                if(root==3) {
                    lastCapture=ranges(ram,new int[]{snapshot,snapshotSize});
                    if(holdPeriods>0) {int until=(frame+holdPeriods)&65535;ram[holdAddress&8191]=until&255;ram[(holdAddress+1)&8191]=until>>8;}
                    result.events.add(new Event(1,frame,word(ram,generation),t,lastCapture,null));
                }
                if(root==4 && word(ram,displayedGeneration)!=lastDisplayed) {
                    lastDisplayed=word(ram,displayedGeneration);
                    result.events.add(new Event(2,frame,lastDisplayed,t,lastCapture,vram(g)));
                }
                active.remove(i);phaseValues.remove(i);
            }
            int entry=-1,entryPhase=0;
            for(int i=0;i<roots.length;i++) if(pc==roots[i] && EmulationRunner.page(g,pc,rootPages[i])) {entry=i;entryPhase=phases[i]<0?0:ram[phases[i]&8191];break;}
            int elapsed=-g.executeOnce(0);result.cycles+=elapsed;pad.time+=elapsed;g.clock=result.cycles;if(g.raster!=null)g.raster.clock=result.cycles;
            boolean irq=elapsed==13 && g.getPC()==0x38 && g.getSP()==((sp-2)&65535);
            boolean nmi=elapsed==11 && g.getPC()==0x66 && g.getSP()==((sp-2)&65535);
            if(irq) {
                irqReturn=pc;irqSP=sp;
                for(int i=0;i<6;i++) irqRegisters[i]=g.getRegisterValue(i);
            }
            if(!irq && !nmi && entry>=0) {
                if(entry==13) result.events.add(new Event(4,frame,word(ram,generation),t,ranges(ram,stateRanges),null));
                active.add(new EmulationRunner.Span(entry,ret,sp+2,t));phaseValues.add(entryPhase);
            }
            if(result.cycles>periods*59736L+10000000L) throw new IllegalStateException("Refresh capture stalled active="+active.size()+" first="+(active.isEmpty()?-1:active.get(0).root)+" ret="+(active.isEmpty()?-1:active.get(0).ret)+" sp="+(active.isEmpty()?-1:active.get(0).sp)+" PC="+Integer.toHexString(g.getPC())+" SP="+Integer.toHexString(g.getSP())+" seq="+word(ram,sequence)+" start="+firstSequence);
        }
        return result;
    }
}

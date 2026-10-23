import system.GameGear;
import java.security.MessageDigest;

/** Actual old sampler/native-tile and new planned native-row machine code. */
public final class WallWrapperOracle {
    public static final class Result {
        public int cases,mismatches;
        public long oldTotal,newTotal,oldMax,newMax;
        public String digest;
    }
    static void word(int[] ram,int address,int value) {ram[address&8191]=value&255;ram[(address+1)&8191]=(value>>8)&255;}
    static long call(GameGear g,int pc,int hl,int de,int[] args) {
        int[] ram=g.getRAM();word(ram,0xdf00,0xc500);
        for(int i=0;i<args.length;i++)ram[(0xdf02+i)&8191]=args[i]&255;
        g.setRegValue(6,0xdf00);g.setRegValue(2,hl);g.setRegValue(1,de);g.setRegValue(7,pc);
        long cost=EmulationRunner.until(g,0xc500,2000000);
        if(g.getSP()!=0xdf02+args.length) throw new IllegalStateException("ABI cleanup at "+Integer.toHexString(pc)+" SP="+Integer.toHexString(g.getSP()));
        return cost;
    }
    static void initialize(GameGear g,int pc,int pointer,int material,int side,int offset,int height,int y) {
        int top=(64-height)/2;
        call(g,pc,pointer,0,new int[]{material,side,offset,height,top&255,(top>>8)&255,y});
    }
    static void ray(int[] ram,int address,int height,int side,int offset,int material) {
        ram[address&8191]=height;ram[(address+1)&8191]=side;
        ram[(address+2)&8191]=offset;ram[(address+3)&8191]=material;word(ram,address+4,512);
    }
    public static Result run(GameGear old,GameGear newer,int[] pc) throws Exception {
        Result result=new Result();MessageDigest digest=MessageDigest.getInstance("SHA-256");
        int[] a=old.getRAM(),b=newer.getRAM();int[] edge={1,8,9,16}; int[] heights={1,2,7,8,9,15,16,17,31,32,63,64,65,127,143,144};
        for(int hi=0;hi<heights.length;hi++) {
            int height=heights[hi];
            for(int columnClass=0;columnClass<8;columnClass++) for(int material=1;material<=10;material++) for(int side=0;side<2;side++) {
                int offset=columnClass*32,rightHeight=material%3==0?edge[columnClass%4]:material%3==1?height:17+((height*37)%128);
                int rightSide=side^1,rightMaterial=1+((material+4)%10),rightOffset=255-offset,column=columnClass&1;
                ray(b,0xd200,height,side,offset,material);ray(b,0xd206,rightHeight,rightSide,rightOffset,rightMaterial);
                newer.writeByte(0xffff,3,0);call(newer,pc[8],0xd200,pc[10],new int[]{column});call(newer,pc[8],0xd206,pc[11],new int[]{column});newer.writeByte(0xffff,2,0);
                for(int tileY=0;tileY<8;tileY++) {
                    int y=tileY*8;
                    if(height>16)initialize(old,pc[0],0xd100,material,side,offset,height,y);
                    if(rightHeight>16)initialize(old,pc[0],0xd120,rightMaterial,rightSide,rightOffset,rightHeight,y);
                    int leftFlat=height<=8?pc[6]+column*32:pc[2+side];
                    int rightFlat=rightHeight<=8?pc[7]+column*32:pc[4+rightSide];
                    a[0xfff]=b[0xfff]=167;a[0x1020]=b[0x1020]=93;
                    for(int i=0;i<32;i++)a[0x1000+i]=b[0x1000+i]=(i*73+result.cases*31)&255;
                    int top=(64-height)/2,rightTop=(64-rightHeight)/2;
                    long before=call(old,pc[1],0xd000,0xd100,new int[]{height<=16?1:0,leftFlat&255,leftFlat>>8,top&255,height,0x20,0xd1,rightHeight<=16?1:0,rightFlat&255,rightFlat>>8,rightTop&255,rightHeight,y});
                    long after=call(newer,pc[12],0xd000,0,new int[]{y});
                    if(newer.readByte(0xffff,0)!=2 || newer.readByte(0xfffe,0)!=1)throw new IllegalStateException("Mapper restoration");
                    if(a[0xfff]!=167 || b[0xfff]!=167 || a[0x1020]!=93 || b[0x1020]!=93)throw new IllegalStateException("Native tile guard");
                    for(int i=0;i<32;i++) {
                        if(a[0x1000+i]!=b[0x1000+i]) throw new IllegalStateException("Wall mismatch height="+height+" right="+rightHeight+" offset="+offset+" material="+material+" side="+side+" y="+y+" byte="+i+" old="+a[0x1000+i]+" new="+b[0x1000+i]);
                        digest.update((byte)a[0x1000+i]);
                    }
                    result.cases++;result.oldTotal+=before;result.newTotal+=after;
                    result.oldMax=Math.max(result.oldMax,before);result.newMax=Math.max(result.newMax,after);
                }
            }
            if(hi%32==0)System.out.println("wall height index "+hi+" cases "+result.cases);
        }
        StringBuilder hex=new StringBuilder();for(byte value:digest.digest())hex.append(String.format("%02x",value&255));result.digest=hex.toString();
        return result;
    }
}

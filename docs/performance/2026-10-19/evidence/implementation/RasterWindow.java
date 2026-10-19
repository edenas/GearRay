import output.SMSDisplayWindow;
import platform.DisplayWindow;
import java.util.ArrayList;
/** Copies scanline output after the installed emulator renderer executes. */
public final class RasterWindow extends SMSDisplayWindow {
    public boolean capture;
    public static final class Frame {
        public long clock; public int base; public boolean mixed; public byte[] pixels;
        Frame(long c,int b,boolean m,byte[] p) {clock=c;base=b;mixed=m;pixels=p;}
    }
    public long clock;
    public ArrayList<Frame> frames=new ArrayList<Frame>();
    private byte[] pixels;
    private int base;
    private boolean mixed;
    public RasterWindow(DisplayWindow d) {super(d,0,false);}
    public void renderLine() {
        super.renderLine();
        if(capture && frames.size()<8192) {
            int line=vdp.getLine();
            if(line==24) {pixels=new byte[160*144];base=vdp.getScreenMapBaseAddress();mixed=false;}
            if(pixels!=null && line>=24 && line<168) {
                if(base!=vdp.getScreenMapBaseAddress()) mixed=true;
                for(int x=48;x<208;x++) pixels[(line-24)*160+x-48]=(byte)((lineBuffer[x]>>8)&31);
                if(line==167) {frames.add(new Frame(clock,base,mixed,pixels));pixels=null;}
            }
        }
    }
}

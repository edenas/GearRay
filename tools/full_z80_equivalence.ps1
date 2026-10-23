# Host arithmetic proof checks for compile-only audit candidates.
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
public static class FullZ80ArithmeticAudit {
    public static long Fraction() {
        long count = 0;
        for (int d=-512; d<=512; ++d)
            for (int r=0; r<=65535; ++r) {
                long product=(long)d*r;
                long adjusted=product<0 ? product-255 : product;
                byte before=unchecked((byte)(adjusted/256));
                ushort low=unchecked((ushort)(d*r));
                byte after=(byte)(low>>8);
                if(before!=after) throw new System.Exception("Fraction mismatch");
                ++count;
            }
        return count;
    }
    public static int Movement() {
        int count=0;
        foreach(int scale in new int[]{169,256})
            for(int d=-256; d<=256; ++d) {
                long wide=(long)d*74;
                wide+=wide<0 ? -scale/2 : scale/2;
                short narrow=checked((short)(d*74));
                narrow=checked((short)(narrow+(narrow<0 ? -scale/2 : scale/2)));
                if(wide/scale!=narrow/scale) throw new System.Exception("Movement mismatch");
                ++count;
            }
        for(int m=-148;m<=148;++m) {
            long wide=(long)m*177; wide+=wide<0 ? -128 : 128;
            short narrow=checked((short)(m*177));
            narrow=checked((short)(narrow+(narrow<0 ? -128 : 128)));
            if(wide/256!=narrow/256) throw new System.Exception("Diagonal mismatch");
            ++count;
        }
        return count;
    }
}
'@
@{FractionCases=[FullZ80ArithmeticAudit]::Fraction();MovementCases=[FullZ80ArithmeticAudit]::Movement();Failures=0;Note='Arithmetic identities, not emulator timing or a replacement for production validators.'}|ConvertTo-Json|Set-Content "$PSScriptRoot/../build/release/full-z80-audit/equivalence.json"
Get-Content "$PSScriptRoot/../build/release/full-z80-audit/equivalence.json"

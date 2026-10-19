param([Parameter(Mandatory=$true)][string]$OutputHeader,
      [Parameter(Mandatory=$true)][string]$GeneratedDirectory)
$ErrorActionPreference='Stop'
$lines=[Collections.Generic.List[string]]::new()
$lines.Add('/* Exact clipped source rows, heights 17..144, 64 screen rows. */')
$lines.Add('static const unsigned char wall_source_rows[128][32] = {')
for($height=17;$height -le 144;++$height) {
    $top=[int][Math]::Truncate((64-$height)/2.0)
    $row=@()
    for($y=0;$y -lt 64;$y+=2) {
        $values=@()
        foreach($screen in @($y,($y+1))) {
            $value=if($screen -lt $top -or $screen -ge $top+$height){15}else{[int][Math]::Floor(($screen-$top)*8.0/$height)}
            # Independent exact Q8.8 step/remainder form used by the old sampler.
            if($value -ne 15) {
                $pixel=$screen-$top;$step=[int][Math]::Floor(2048.0/$height);$remainder=2048%$height
                $position=$pixel*$step+[int][Math]::Floor(($pixel*$remainder)/[double]$height)
                if(($position -shr 8) -ne $value) {throw 'Wall schedule proof failure'}
            }
            $values+=$value
        }
        $row+=($values[0] -shl 4) -bor $values[1]
    }
    $lines.Add('    {'+(($row|ForEach-Object{'0x{0:X2}' -f $_}) -join ',')+'},')
}
$lines.Add('};')
$art=Get-Content (Join-Path $GeneratedDirectory 'wall_texture.c') -Raw
$body=[regex]::Match($art,'(?s)const unsigned char wall_textures\[.*?=\s*\{(.*?)\};').Groups[1].Value
$pixels=@([regex]::Matches($body,'0x([0-9a-fA-F]+)')|ForEach-Object{[Convert]::ToInt32($_.Groups[1].Value,16)})
if($pixels.Count -ne 320) {throw 'Expected ten authoritative 8x8 wall textures'}
$palettes=@()
foreach($side in @('x','y')) {
    $body=[regex]::Match($art,"(?s)const unsigned char wall_palette_${side}_indices\[.*?=\s*\{(.*?)\};").Groups[1].Value
    $map=@([regex]::Matches($body,'\d+')|ForEach-Object{[int]$_.Value})
    if($map.Count -ne 10) {throw 'Expected ten indexed wall colors'}
    $palettes+=,@($map)
}
$lines.Add('static const unsigned char wall_color_columns[10][2][8][8] = {')
for($material=0;$material -lt 10;++$material) {
    $lines.Add('{')
    for($side=0;$side -lt 2;++$side) {
        $lines.Add('{')
        for($x=0;$x -lt 8;++$x) {
            $colors=@()
            for($y=0;$y -lt 8;++$y) {
                $packed=$pixels[$material*32+$y*4+[int][Math]::Floor($x/2)]
                $index=if($x -band 1){$packed -band 15}else{$packed -shr 4}
                if($index -ge 10){$index=0}
                $colors+=$palettes[$side][$index]
            }
            $lines.Add('    {'+($colors -join ',')+'},')
        }
        $lines.Add('},')
    }
    $lines.Add('},')
}
$lines.Add('};')
$lines.Add('static const unsigned char native_wall_pairs[256][4] = {')
for($pair=0;$pair -lt 256;++$pair) {
    $planes=@()
    for($p=0;$p -lt 4;++$p) {
        $value=0;if(($pair -shr 4) -band (1 -shl $p)){$value=240}
        if(($pair -band 15) -band (1 -shl $p)){$value=$value -bor 15}
        $planes+=$value
    }
    $lines.Add('    {'+($planes -join ',')+'},')
}
$lines.Add('};')
[IO.File]::WriteAllLines($OutputHeader,$lines,[Text.Encoding]::ASCII)
Write-Output 'Generated 4096 schedule bytes; 8192 clipped screen-row cases match old exact sampler arithmetic.'

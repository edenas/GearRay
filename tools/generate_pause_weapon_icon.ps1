param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputHeader,
    [ValidatePattern('^[A-Za-z_][A-Za-z_0-9]*$')][string]$Symbol='pause_pistol_tiles'
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$image=[System.Drawing.Bitmap]::new($InputPath)
try {
    if($image.Width -ne 16 -or $image.Height -ne 16){throw 'Pause weapon canvas must be exactly 16x16'}
    $pixels=New-Object int[] 256
    $sourceAlpha=New-Object int[] 256
    for($y=0;$y -lt 16;$y++){for($x=0;$x -lt 16;$x++){
        # Native source canvas: alpha zero is background, with no slot border.
        $index=0
        $color=$image.GetPixel($x,$y)
        $sourceAlpha[$y*16+$x]=$color.A
        if($color.A -ne 0){
            if($color.A -ne 255){throw "Partial alpha at ($x,$y)"}
            $rgb='#{0:x2}{1:x2}{2:x2}' -f $color.R,$color.G,$color.B
            $index=switch($rgb){
                '#000000' {0} '#1a1a1a' {13} '#4d4d4d' {2}
                '#797878' {3} '#ffffff' {12}
                default {throw "No existing pause palette mapping for $rgb"}
            }
        }
        $pixels[$y*16+$x]=$index
    }}
} finally {$image.Dispose()}
$lines=[Collections.Generic.List[string]]::new()
$lines.Add('/* Native 16x16 artwork at inset (2,2) in a 20x20 border: one black gap pixel. */')
foreach($sy in @(0,4)){foreach($sx in @(0,4)){
    $ox=(38-$sx)-band 7;$oy=(110+$sy)-band 7
    $columns=[int][Math]::Ceiling(($ox+20)/8.0);$rows=[int][Math]::Ceiling(($oy+20)/8.0)
    $lines.Add("#if SCROLL_X == $sx && SCROLL_Y == $sy")
    $dictionary=[Collections.Generic.List[int]]::new()
    $lookup=@{};$variants=@{}
    foreach($border in @(12,2)){
    $ids=[Collections.Generic.List[int]]::new()
    for($ty=0;$ty -lt $rows;$ty++){for($tx=0;$tx -lt $columns;$tx++){
        for($y=0;$y -lt 8;$y++){
            $planes=New-Object int[] 4
            for($x=0;$x -lt 8;$x++){
                $px=$tx*8+$x-$ox;$py=$ty*8+$y-$oy;$index=0
                if($px -ge 0 -and $px -lt 20 -and $py -ge 0 -and $py -lt 20){
                    if($px -eq 0 -or $px -eq 19 -or $py -eq 0 -or $py -eq 19){$index=$border}
                    elseif($px -ge 2 -and $px -lt 18 -and $py -ge 2 -and $py -lt 18){$index=$pixels[($py-2)*16+$px-2]}
                }
                for($p=0;$p -lt 4;$p++){if($index -band (1 -shl $p)){$planes[$p]=$planes[$p] -bor (128 -shr $x)}}
            }
            $key=$planes -join ','
            if(!$lookup.ContainsKey($key)){$lookup[$key]=[int]($dictionary.Count/4);$dictionary.AddRange([int[]]$planes)}
            $ids.Add($lookup[$key])
        }
    }}
    if($dictionary.Count/4 -gt 128){throw 'Row dictionary exceeds literal token range'}
    $packed=[Collections.Generic.List[int]]::new()
    for($i=0;$i -lt $ids.Count;){
        $id=$ids[$i];$end=$i+1
        while($end -lt $ids.Count -and $ids[$end] -eq $id){$end++}
        $length=$end-$i
        if($length -ge 2){$packed.Add(128 -bor $id);$packed.Add($length-1)}
        else {$packed.Add($id)}
        $i=$end
    }
    $variants[$border]=$packed.ToArray()
    }
    if($Symbol -eq 'pause_pistol_tiles'){
        $empty=foreach($edges in @(1,2,3,4,6,8,9,12)){
            $tx=if($edges -band 8){0}elseif($edges -band 2){$columns-1}else{1}
            $ty=if($edges -band 1){0}elseif($edges -band 4){$rows-1}else{1}
            for($y=0;$y -lt 8;$y++){
                $bits=0
                for($x=0;$x -lt 8;$x++){
                    $px=$tx*8+$x-$ox;$py=$ty*8+$y-$oy
                    if($px -ge 0 -and $px -lt 20 -and $py -ge 0 -and $py -lt 20 -and
                       ($px -eq 0 -or $px -eq 19 -or $py -eq 0 -or $py -eq 19)){$bits=$bits -bor (128 -shr $x)}
                };$bits
            }
        }
        $lines.Add('static const unsigned char pause_empty_rows[64] = {')
        $lines.Add('    '+(($empty|ForEach-Object{'0x{0:x2}' -f $_}) -join ', ')+',');$lines.Add('};')
    }
    foreach($entry in @(@("${Symbol}_rows",$dictionary.ToArray()),@($Symbol,$variants[12]),@("${Symbol}_side",$variants[2]))){
        $data=$entry[1]
        $lines.Add("static const unsigned char $($entry[0])[$($data.Count)] = {")
        $lines.Add('    '+(($data|ForEach-Object{'0x{0:x2}' -f $_}) -join ', ')+',')
        $lines.Add('};')
    }
    $lines.Add('#endif')
}}
New-Item -ItemType Directory -Force -Path (Split-Path $OutputHeader -Parent)|Out-Null
Set-Content -LiteralPath $OutputHeader -Value $lines -Encoding Ascii

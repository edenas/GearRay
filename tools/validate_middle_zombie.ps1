param([string]$BuildDirectory='build',[switch]$RequireMapPlacement)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
function Assert([bool]$Condition,[string]$Message){if(-not$Condition){throw $Message}}
$poses=@('standing','walking_01','walking_02','shot_01','shot_dead','corps')
Add-Type -AssemblyName System.Drawing
function Get-Footprint([string]$Path){
    $bitmap=[Drawing.Bitmap]::new($Path)
    try{
        $minX=$bitmap.Width;$minY=$bitmap.Height;$maxX=-1;$maxY=-1;$opaque=0
        for($y=0;$y-lt$bitmap.Height;$y++){for($x=0;$x-lt$bitmap.Width;$x++){
            $alpha=$bitmap.GetPixel($x,$y).A
            Assert(($alpha-eq0-or$alpha-eq255)) "$Path contains partial alpha."
            if($alpha-ne0){$opaque++;if($x-lt$minX){$minX=$x};if($x-gt$maxX){$maxX=$x};if($y-lt$minY){$minY=$y};if($y-gt$maxY){$maxY=$y}}
        }}
        [pscustomobject]@{Width=$bitmap.Width;Height=$bitmap.Height;BodyWidth=$maxX-$minX+1;BodyHeight=$maxY-$minY+1;Left=$minX;Top=$minY;Right=$bitmap.Width-1-$maxX;Bottom=$bitmap.Height-1-$maxY;Coverage=$opaque/($bitmap.Width*$bitmap.Height)}
    }finally{$bitmap.Dispose()}
}
$payloadHashes=@{}
function Get-ExpectedMiddleBytes([string]$Path){
    $bitmap=[Drawing.Bitmap]::new($Path)
    try{
        $indices=[Collections.Generic.List[byte]]::new(256)
        for($y=0;$y-lt16;$y++){for($x=0;$x-lt16;$x++){
            $pixel=$bitmap.GetPixel($x,$y)
            if($pixel.A-eq0){$indices.Add(15);continue}
            Assert($pixel.A-eq255) "$Path contains partial alpha at ($x,$y)."
            $rgb=('#{0:x2}{1:x2}{2:x2}'-f$pixel.R,$pixel.G,$pixel.B)
            $index=switch($rgb){
                '#000000'{0;break};'#1a1a1a'{13;break};'#006d8f'{8;break}
                '#53602a'{7;break};'#785700'{6;break};'#b51a00'{5;break}
                '#bb2200'{5;break};'#ffffff'{12;break}
                default{throw "Middle zombie color $rgb at ($x,$y) has no exact gameplay palette mapping."}
            }
            $indices.Add($index)
        }}
        [byte[]]$packed=@(for($i=0;$i-lt256;$i+=2){($indices[$i]-shl4)-bor$indices[$i+1]})
        return $packed
    }finally{$bitmap.Dispose()}
}
function Get-GeneratedMiddleBytes([string]$Path,[string]$Symbol){
    $source=Get-Content -Raw $Path
    $match=[regex]::Match($source,"const unsigned char $Symbol\[[^\]]+\] = \{(?<body>[\s\S]*?)\n\};")
    Assert($match.Success) "Generated payload symbol $Symbol is missing from $Path."
    [byte[]]$bytes=@([regex]::Matches($match.Groups['body'].Value,'0x[0-9a-fA-F]{2}')|ForEach-Object{[Convert]::ToByte($_.Value.Substring(2),16)})
    return $bytes
}
function Get-ByteHash([byte[]]$Bytes){
    $sha=[Security.Cryptography.SHA256]::Create()
    try{return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-','')}finally{$sha.Dispose()}
}
foreach($pose in $poses){
    $asset=Join-Path $root "assets\sprites\enemies\zombie\zombie_01_${pose}_16x16.png"
    Assert(Test-Path $asset) "Missing 16x16 zombie asset $pose."
    $bitmap=[Drawing.Bitmap]::new($asset)
    try{Assert($bitmap.Width-eq16-and$bitmap.Height-eq16) "$pose is not 16x16.";for($y=0;$y-lt16;$y++){for($x=0;$x-lt16;$x++){Assert(($bitmap.GetPixel($x,$y).A-eq0-or$bitmap.GetPixel($x,$y).A-eq255)) "$pose contains partial alpha."}}}finally{$bitmap.Dispose()}
    $generated=Join-Path $build "generated\zombie_${pose}_16x16_texture.c"
    Assert(Test-Path $generated) "Missing generated 16x16 texture $pose."
    $symbol="zombie_middle_${pose}_pixels"
    [byte[]]$expected=Get-ExpectedMiddleBytes $asset
    [byte[]]$actual=Get-GeneratedMiddleBytes $generated $symbol
    Assert($actual.Count-eq128) "$pose payload is not 128 bytes."
    for($byteIndex=0;$byteIndex-lt128;$byteIndex++){
        if($expected[$byteIndex]-ne$actual[$byteIndex]){
            $pixelY=[Math]::Floor($byteIndex/8);$pixelX=($byteIndex%8)*2
            throw "$pose generated payload mismatch at byte $byteIndex (pixels $pixelX/$($pixelX+1),$pixelY): expected 0x$($expected[$byteIndex].ToString('X2')), actual 0x$($actual[$byteIndex].ToString('X2'))."
        }
    }
    $payloadHashes[$pose]=Get-ByteHash $actual
}
$assetSets=@(
    [pscustomobject]@{Size=8;Suffix='';Poses=@('standing','walking_01','walking_02','shot_01','shot_02','shot_dead','corps')},
    [pscustomobject]@{Size=16;Suffix='_16x16';Poses=@('standing')+$poses},
    [pscustomobject]@{Size=32;Suffix='_32x32';Poses=@('standing','walking_01','walking_02','standing_attack','attack_01','attack_02','shot_01','corps')}
)
$footprints=@()
foreach($set in $assetSets){foreach($pose in $set.Poses){
    $asset=Join-Path $root "assets\sprites\enemies\zombie\zombie_01_${pose}$($set.Suffix).png"
    Assert(Test-Path $asset) "Missing authoritative zombie asset $pose ($($set.Size)x$($set.Size))."
    $f=Get-Footprint $asset
    Assert($f.Width-eq$set.Size-and$f.Height-eq$set.Size) "$pose is not $($set.Size)x$($set.Size)."
    $footprints+=[pscustomobject]@{Size=$set.Size;Pose=$pose;BodyWidth=$f.BodyWidth;BodyHeight=$f.BodyHeight;Left=$f.Left;Top=$f.Top;Right=$f.Right;Bottom=$f.Bottom;Coverage=$f.Coverage}
}}
$projection=Get-Content -Raw (Join-Path $root 'platform\game_gear\sprite_projection.c')
$header=Get-Content -Raw (Join-Path $root 'platform\game_gear\sprite_projection.h')
$video=Get-Content -Raw (Join-Path $root 'platform\game_gear\video.c')
$world=Get-Content -Raw (Join-Path $root 'game\world_sprite.h')
$cmake=Get-Content -Raw (Join-Path $root 'CMakeLists.txt')
Assert($header-match'ZOMBIE_8X8_MAX_PROJECTED_HEIGHT 32') '8x8 cap is not 32.'
Assert($header-match'SPRITE_MIDDLE_DETAIL_MAX_DISTANCE[\s\\]*\(SPRITE_NEAR_DETAIL_MAX_DISTANCE \+ 4 \* ZOMBIE_MOVEMENT_STEP\)') 'Middle boundary no longer provides four authored 16x16 movement steps.'
Assert($world-match'ZOMBIE_ATTACK_DISTANCE 280'-and$world-match'ZOMBIE_MOVEMENT_STEP 56') 'Gameplay boundaries changed.'
Assert((392 + 4 * 56)-eq616) 'Derived middle-detail boundary is not 616.'
Assert(([regex]::Matches($cmake,'foreach\(middle_pose IN ITEMS STANDING WALKING_01 WALKING_02 SHOT_01 SHOT_DEAD CORPS\)').Count-eq2)) 'Active middle pose set is not declared consistently for configuration and generation.'
Assert(([regex]::Matches($cmake,'set\(GEAR_RAY_MIDDLE_ZOMBIE_\$\{middle_pose\}_INPUT "\$\{CMAKE_SOURCE_DIR\}/assets/sprites/enemies/zombie/zombie_01_\$\{middle_pose_lower\}_16x16\.png"\)').Count-eq1)) 'Middle poses do not have one authoritative current-PNG input formula.'
Assert($projection-match'game_gear_get_middle_zombie_pixels') 'Middle pose selector is missing.'
foreach($pose in $poses){Assert($projection-match"zombie_middle_${pose}_pixels") "Missing middle pose mapping $pose."}
Assert($projection-match'ZOMBIE_PRESENTATION_STANDING:[\s\S]*?zombie_middle_standing_pixels') 'Idle 16x16 zombies do not use the authored standing texture.'
Assert($header-notmatch'NEAR_ZOMBIE_TEXTURE_STANDING\s') 'Unused neutral 32x32 standing texture ID remains.'
Assert($projection-match'ZOMBIE_WALKING_PHASE_MASK[\s\S]*?ZOMBIE_PRESENTATION_WALKING_02[\s\S]*?ZOMBIE_PRESENTATION_WALKING_01'-and$projection-match'ZOMBIE_PRESENTATION_WALKING_02[\s\S]*?zombie_middle_walking_02_pixels') 'Presentation walking phase is not shared by authored resolutions.'
Assert($projection-match'ZOMBIE_STATE_SHOT_DEAD[\s\S]*?zombie_middle_shot_dead_pixels') 'Lethal middle pose is missing.'
Assert($projection-match'ZOMBIE_STATE_CORPSE[\s\S]*?zombie_middle_corps_pixels') 'Middle corpse pose is missing.'
Assert($video-match'projected->source_size'-and$video-match'packed_row_stride = \(unsigned char\)source_size >> 1') 'Shared 8/16/32 compositor metadata is missing.'
Assert($video-match'projected->depth[\s\S]*?>=[\s\S]*?wall_distance') 'Wall-wins occlusion changed.'
Assert($projection-notmatch'ZOMBIE_NATIVE_(WALKING|CLOSE)_VISUAL_DEPTH_OFFSET|ZOMBIE_NATIVE_MIN_VISUAL_DEPTH|visual_depth') 'Obsolete native visual-depth bridge remains.'
Assert($projection-match'WORLD_SPRITE_LIFE_STATE\(sprite\) == ZOMBIE_STATE_ALIVE\s*&& projected->source_size == 8\s*&& projected->near_texture_id == NEAR_ZOMBIE_TEXTURE_NONE') 'The projected-height cap is not restricted to 8x8 living sprites.'
function Height([int]$depth){[int][Math]::Floor(16384/$depth)}
function BodyHeight([int]$height,[int]$body,[int]$source){[int][Math]::Floor(($height*$body)/$source)}
function BodyWidth([int]$height,[int]$body,[int]$source){[int][Math]::Floor(($height*$body)/$source)}
$ladder=@(
    [pscustomobject]@{D=617;S='8x8 walking';H=(Height 617);Source=8;BodyH=8;BodyW=8},
    [pscustomobject]@{D=616;S='16x16 walking';H=(Height 616);Source=16;BodyH=16;BodyW=16},
    [pscustomobject]@{D=560;S='16x16 walking';H=(Height 560);Source=16;BodyH=16;BodyW=16},
    [pscustomobject]@{D=504;S='16x16 walking';H=(Height 504);Source=16;BodyH=16;BodyW=16},
    [pscustomobject]@{D=448;S='16x16 walking';H=(Height 448);Source=16;BodyH=16;BodyW=16},
    [pscustomobject]@{D=393;S='16x16 walking';H=(Height 393);Source=16;BodyH=16;BodyW=16},
    [pscustomobject]@{D=392;S='32x32 walking';H=(Height 392);Source=32;BodyH=32;BodyW=31},
    [pscustomobject]@{D=280;S='32x32 combat';H=(Height 280);Source=32;BodyH=32;BodyW=30})
foreach($row in $ladder){$row|Add-Member BodyPixels (BodyHeight $row.H $row.BodyH $row.Source);$row|Add-Member WidthPixels (BodyWidth $row.H $row.BodyW $row.Source)}
for($i=1;$i-lt$ladder.Count;$i++){Assert($ladder[$i].BodyPixels-ge$ladder[$i-1].BodyPixels) "Approach body scale shrinks at $($ladder[$i].D)."}
Assert(($ladder[1].BodyPixels-$ladder[0].BodyPixels)-le2) '8x8 to 16x16 visible-body discontinuity exceeds two pixels.'
Assert(($ladder[6].BodyPixels-$ladder[5].BodyPixels)-le4) '16x16 to 32x32 visible-body discontinuity exceeds four pixels.'
$reverse=@($ladder|Sort-Object D)
for($i=1;$i-lt$reverse.Count;$i++){Assert($reverse[$i].BodyPixels-le$reverse[$i-1].BodyPixels) "Retreat body scale grows at $($reverse[$i].D)."}
foreach($size in 8,16,32){
    $living=@($footprints|Where-Object{$_.Size-eq$size-and$_.Pose-ne'corps'})
    Assert(($living|Where-Object{$_.BodyHeight-ne$size}).Count-eq0) "Living ${size}x${size} assets do not share full authored body height."
    Assert(($living|Where-Object{$_.Bottom-ne0}).Count-eq0) "Living ${size}x${size} assets do not share the floor row."
}
function Metric([int]$x,[int]$y){$x=[Math]::Abs($x);$y=[Math]::Abs($y);if($x-gt$y){$x+[int]($y/2)}else{$y+[int]($x/2)}}
Assert (((Metric 560 112) -eq 616) -and ((Metric 336 112) -eq 392)) 'Oblique octagonal boundaries changed.'
function LivingTier([int]$distance){if($distance-le392){'32'}elseif($distance-le616){'16'}else{'8'}}
$straightApproach=@(617,616,560,504,448,392,336,280|ForEach-Object{LivingTier $_})
$straightRetreat=@(280,336,392,448,504,560,616,617|ForEach-Object{LivingTier $_})
Assert(($straightApproach-join',')-eq'8,16,16,16,16,32,32,32') 'Straight four-step middle-detail approach changed.'
Assert(($straightRetreat-join',')-eq'32,32,32,16,16,16,16,8') 'Straight four-step middle-detail retreat changed.'
$obliqueApproach=@(@(561,112),@(560,112),@(504,112),@(448,112),@(392,112),@(336,112),@(280,112),@(224,112)|ForEach-Object{LivingTier (Metric $_[0] $_[1])})
Assert(($obliqueApproach-join',')-eq'8,16,16,16,16,32,32,32') 'Oblique four-step middle-detail approach changed.'
Assert($projection-match'ZOMBIE_PRESENTATION_SHOT:[\s\S]*?zombie_middle_shot_01_pixels') 'Extended middle range does not use authored shot_01.'
Assert($projection-match'ZOMBIE_PRESENTATION_DEAD:[\s\S]*?zombie_middle_shot_dead_pixels') 'Extended middle range does not use authored shot_dead.'
if($RequireMapPlacement){
    $map=Get-Content -Raw (Join-Path $build 'GearRay.map')
    foreach($pose in $poses){
        $matches=[regex]::Matches($map,"(?m)^\s*(?<a>[0-9A-Fa-f]{8})\s+_zombie_middle_${pose}_pixels\s+")
        Assert($matches.Count-eq1) "Expected exactly one map symbol for $pose, found $($matches.Count)."
        $a=[Convert]::ToInt32($matches[0].Groups['a'].Value,16)
        Assert(($a -ge 0x14000 -and $a -lt 0x18000)) "$pose is outside Bank 1."
    }
    $generatedSources=@(Get-ChildItem -LiteralPath (Join-Path $build 'generated') -File -Filter 'zombie_*_16x16_texture.c')
    $generatedObjects=@(Get-ChildItem -LiteralPath $build -File -Filter 'generated_zombie_*_16x16_texture.rel')
    Assert($generatedSources.Count-eq6) "Expected six generated middle sources, found $($generatedSources.Count)."
    Assert($generatedObjects.Count-eq6) "Expected six generated middle objects, found $($generatedObjects.Count)."
}
Write-Output 'Middle-detail zombie validation PASS'
Write-Output '- 8x8 at distance >=617; authored 16x16 at 616..393; 32x32 locomotion at 392..281'
Write-Output '- middle interval is four 56-unit movement steps (224 units); near interval remains two steps before melee'
Write-Output ('- footprint-aware body ladder: '+(($ladder|ForEach-Object{"$($_.BodyPixels)h/$($_.WidthPixels)w"})-join', '))
Write-Output '- all living assets use full authored height and floor row; no baseline correction required'
Write-Output '- all 21 authored assets audited; six active 16x16/128-byte poses including idle standing'
foreach($pose in $poses){Write-Output "- $pose payload SHA-256: $($payloadHashes[$pose])"}

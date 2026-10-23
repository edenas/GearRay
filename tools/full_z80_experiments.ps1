# Historical optional compile experiment; excluded from Release/validation.
# Compile-only audit experiments. Never links or modifies production sources.
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$out=Join-Path $root 'build/experiments/full-z80'
New-Item -ItemType Directory -Force $out | Out-Null
$sdcc='C:/Program Files/SDCC/bin/sdcc.exe'
function Compile($name,$sourcePath,$text,$flags) {
    # Resolve quoted includes against the original source directory.
    $dir=Split-Path (Join-Path $root $sourcePath) -Parent
    $text=[regex]::Replace($text,'(?m)^#include "([^"]+)"',{
        param($m)
        $path=[IO.Path]::GetFullPath((Join-Path $dir $m.Groups[1].Value))
        if(Test-Path $path){'#include "'+$path.Replace('\','/')+'"'}else{$m.Value}
    })
    [IO.File]::WriteAllText("$out/$name.c",$text)
    $ErrorActionPreference='Continue'
    & $sdcc -mz80 -DTARGET_GG "-I$root/game" "-I$root/engine/render" "-I$root/platform/game_gear" "-I$root/build/release/generated" '-ID:/Tools/devkitSMS/SMSlib/src' @flags -c "$out/$name.c" -o "$out/$name.rel" *> "$out/$name.log"
    $code=$LASTEXITCODE
    $ErrorActionPreference='Stop'
    if($code){throw "Compile failed: $name"}
}
$video=Get-Content "$root/platform/game_gear/video.c" -Raw
$vflags=@('--peep-file','D:/Tools/devkitSMS/SMSlib/src/peep-rules.txt','--constseg','BANK1')
Compile 'video_baseline' 'platform/game_gear/video.c' $video $vflags
$deleted=$video.Replace("    if (!game_gear_sprite_covers_tile(projected, tile_column, tile_row))`n        return;`n",'')
Compile 'video_delete_duplicate_coverage' 'platform/game_gear/video.c' $deleted $vflags
$row=$video.Replace('    unsigned int texture_y;','    unsigned int texture_y;'+"`n    const unsigned char *source_row;")
$row=$row.Replace('        for (pixel_x = 0; pixel_x < 8; ++pixel_x)',"        source_row = pixels + texture_y * packed_row_stride;`n        for (pixel_x = 0; pixel_x < 8; ++pixel_x)")
$row=$row.Replace("pixels[`n                texture_y * packed_row_stride + (texture_x >> 1)]",'source_row[texture_x >> 1]')
Compile 'video_row_base' 'platform/game_gear/video.c' $row $vflags
foreach($module in @('world','world_sprite','world_initialization','video')) {
    $path=if($module -eq 'video'){'platform/game_gear/video.c'}else{"game/$module.c"}
    $src=Get-Content "$root/$path" -Raw
    $flags=if($module -eq 'video'){$vflags}elseif($module -eq 'world_initialization'){@('--codeseg','BANK1')}else{@()}
    Compile ($module+'_no_unused_metric') $path ("#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC`n"+$src) $flags
}
$ray=Get-Content "$root/engine/render/raycaster.c" -Raw
Compile 'ray_baseline' 'engine/render/raycaster.c' $ray @()
$pattern='(?s)    signed long scaled_offset =.*?return \(unsigned char\)\(impact_position & \(FIXED_POINT_SCALE - 1\)\);'
$replacement=@'
    /* Only bits 8..15 of the product contribute to the fractional texel. */
    unsigned int product = (unsigned int)direction * (unsigned int)ray_distance;
    return (unsigned char)((unsigned int)position + (product >> 8));
'@
$ray=[regex]::Replace($ray,$pattern,$replacement)
Compile 'ray_fraction_only' 'engine/render/raycaster.c' $ray @()
$shot=Get-Content "$root/game/zombie_shooting.c" -Raw
Compile 'shot_baseline' 'game/zombie_shooting.c' $shot @('--codeseg','BANK1')
$shot=$shot.Replace('        if (selected_weapon == WEAPON_SHOTGUN)',"        if (depth >= nearest_depth) continue;`n        if (selected_weapon == WEAPON_SHOTGUN)")
$shot=$shot.Replace('if (depth >= nearest_depth || depth >= wall_depth)','if (depth >= wall_depth)')
Compile 'shot_early_nearest' 'game/zombie_shooting.c' $shot @('--codeseg','BANK1')
$player=Get-Content "$root/game/player.c" -Raw
Compile 'player_baseline' 'game/player.c' $player @()
$player=$player.Replace('unsigned int direction_scale','signed int direction_scale').Replace('signed long movement = (signed long)direction','signed int movement = direction').Replace('signed long scaled_movement =','signed int scaled_movement =').Replace('(signed long)movement * PLAYER_DIAGONAL_SCALE','movement * PLAYER_DIAGONAL_SCALE')
Compile 'player_bounded_int' 'game/player.c' $player @()
$results=@()
 $world=Get-Content "$root/game/world.c" -Raw
 Compile 'world_baseline' 'game/world.c' $world @()
 $world=$world.Replace("    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)`n        return 1;`n",'')
 Compile 'world_delete_double_bounds' 'game/world.c' $world @()
foreach($file in Get-ChildItem $out -Filter '*.rel') {
    $rel=Get-Content $file.FullName -Raw
    $asm=Get-Content ([IO.Path]::ChangeExtension($file.FullName,'.asm')) -Raw
    $areas=@{};foreach($m in [regex]::Matches($rel,'(?m)^A (\S+) size ([0-9A-F]+)')){$areas[$m.Groups[1].Value]=[Convert]::ToInt32($m.Groups[2].Value,16)}
    $f=@();foreach($m in [regex]::Matches($asm,'(?ms)^; Function (\w+)\r?\n(.*?)(?=^; Function |\z)')) {
        $body=$m.Groups[2].Value
        $frame=[regex]::Match($body,'ld\s+(?:hl|iy), #-(\d+)')
        $f+=@{Name=$m.Groups[1].Value;Instructions=[regex]::Matches($body,'(?m)^\t[a-z]+(?:\s|$)').Count;Frame=$(if($frame.Success){[int]$frame.Groups[1].Value}else{0});Helpers=@([regex]::Matches($body,'call\s+(_+(?:mul|div|mod)\w+)')|ForEach-Object{$_.Groups[1].Value})}
    }
    $results+=@{Name=$file.BaseName;Areas=$areas;Functions=$f}
}
$results|ConvertTo-Json -Depth 8|Set-Content "$out/results.json"
$results|ForEach-Object{[pscustomobject]@{Name=$_.Name;Code=$_.Areas['_CODE'];Bank1=$_.Areas['_BANK1']}}|Format-Table

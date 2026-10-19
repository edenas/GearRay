param([string]$BuildDirectory='build')
$ErrorActionPreference='Stop'
. "$PSScriptRoot/production_build_artifacts.ps1"
Add-Type -AssemblyName System.Drawing
. "$PSScriptRoot/pause_weapon_asset_data.ps1"
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
$probe=Join-Path $build 'generated'
$palette=@{'#000000'=0;'#1a1a1a'=13;'#4d4d4d'=2;'#797878'=3;'#ffffff'=12;'#ad3e00'=1;'#ffa57d'=15;'#b51a00'=5;'#785700'=6;'#ffc4ab'=11}
function Require($condition,$message){if(!$condition){throw $message}}
foreach($pose in @(@('shotgun_held.png','shotgun_held',14,20),@('shotgun_held_shoot.png','shotgun_fire',14,20),@('pick_up_shotgun.png','shotgun_world',15,16))){
    $im=[Drawing.Bitmap]::new((Join-Path $root "assets/sprites/weapons/$($pose[0])"))
    try {
        $width=$pose[3];$stride=$width/2
        Require ($im.Width -eq $width -and $im.Height -eq 16) 'Exact held 20x16 / world 16x16 source dimensions'
        $c=Get-Content (Join-Path $probe "$($pose[1]).c") -Raw
        $data=@([regex]::Matches([regex]::Match($c,'(?s)=\s*\{(.*?)\}').Groups[1].Value,'0x[0-9a-f]+')|ForEach-Object{[Convert]::ToInt32($_.Value.Substring(2),16)})
        Require ($data.Count -eq $stride*16) 'Exact 160-byte held / 128-byte world packed size'
        $header=Get-Content (Join-Path $probe "$($pose[1]).h") -Raw
        foreach($metric in @(@('WIDTH',$width),@('HEIGHT',16),@('PACKED_ROW_STRIDE',$stride),@('BYTE_COUNT',($stride*16)),@('TRANSPARENT_INDEX',$pose[2]))){
            Require ($header -match "(?m)^#define $($pose[1])_pixels_$($metric[0]) $($metric[1])\r?$") 'Generated held/world format metadata must match exact source layout'
        }
        for($y=0;$y -lt 16;$y++){for($x=0;$x -lt $width;$x++){
            $p=$im.GetPixel($x,$y)
            Require ($p.A -in @(0,255)) 'Source must have binary alpha'
            $rgb='#{0:x2}{1:x2}{2:x2}' -f $p.R,$p.G,$p.B
            $expected=if($p.A -eq 0){$pose[2]}else{$palette[$rgb]}
            Require ($null -ne $expected) 'Missing palette mapping'
            $byte=$data[$y*$stride+[int][Math]::Floor($x/2)]
            $actual=if($x -band 1){$byte -band 15}else{$byte -shr 4}
            Require ($actual -eq $expected) "Pixel geometry/alpha mismatch at $x,$y"
        }}
    } finally {$im.Dispose()}
}
$im=[Drawing.Bitmap]::new((Join-Path $root 'assets/sprites/weapons/shotgun.png'))
try {
    $header=Get-Content (Join-Path $probe 'pause_shotgun_icon.h') -Raw
    foreach($case in [regex]::Matches($header,'(?s)#if SCROLL_X == (\d) && SCROLL_Y == (\d)\s*(.*?)#endif')){
        $sx=[int]$case.Groups[1].Value;$sy=[int]$case.Groups[2].Value
        $columns=4-[int]($sx -ne 0);$rows=4-[int]($sy -ne 0);$ox=(38-$sx)-band 7;$oy=(110+$sy)-band 7
        $arrays=Get-PauseWeaponArrays $header $sx $sy
        foreach($side in @($false,$true)){
        $data=Expand-PauseWeaponData $arrays 'pause_shotgun_tiles' $sx $sy $side
        Require ($data.Count -eq $columns*$rows*32) 'Pause tile span mismatch'
        for($y=0;$y -lt $rows*8;$y++){for($x=0;$x -lt $columns*8;$x++){
            $px=$x-$ox;$py=$y-$oy;$expected=0
            if($px -ge 0 -and $px -lt 20 -and $py -ge 0 -and $py -lt 20){
                $border=$px -eq 0 -or $px -eq 19 -or $py -eq 0 -or $py -eq 19
                $expected=if($border){if($side){2}else{12}}else{0}
                $p=[Drawing.Color]::Transparent
                if($px -ge 2 -and $px -lt 18 -and $py -ge 2 -and $py -lt 18){$p=$im.GetPixel($px-2,$py-2)}
                if($p.A -ne 0){$expected=$palette[('#{0:x2}{1:x2}{2:x2}' -f $p.R,$p.G,$p.B)]}
            }
            $tile=[int][Math]::Floor($y/8)*$columns+[int][Math]::Floor($x/8)
            $actual=0
            for($plane=0;$plane -lt 4;$plane++){if($data[$tile*32+($y%8)*4+$plane] -band (128 -shr ($x%8))){$actual=$actual -bor (1 -shl $plane)}}
            Require ($actual -eq $expected) 'Authored shotgun canvas / masked destination / alignment mismatch'
        }}
    }
    }
    $worldSource=[Drawing.Bitmap]::new((Join-Path $root 'assets/sprites/weapons/pick_up_shotgun.png'))
    $nearOpaque=@();for($y=0;$y-lt16;$y++){for($x=0;$x-lt16;$x++){if($worldSource.GetPixel($x,$y).A-ne0){$nearOpaque+=$y}}}
    Require (($nearOpaque|Measure-Object -Minimum).Minimum -eq 4 -and ($nearOpaque|Measure-Object -Maximum).Maximum -eq 11) 'NEAR pickup opaque rows / quarter-canvas floor padding changed'
    $approved=@('........','........','........','dddddd..','.ddddddd','.....d..','........','........')
    $pattern=Get-Content (Join-Path $probe 'shotgun_far_pattern.txt')
    Require (($approved -join '/') -eq ($pattern -join '/')) 'Approved FAR silhouette changed'
    $lodHeader=Get-Content (Join-Path $probe 'shotgun_far_lod.h') -Raw
    $farData=@([regex]::Matches($lodHeader,'0x[0-9a-f]+') | ForEach-Object {[Convert]::ToInt32($_.Value.Substring(2),16)})
    Require ($farData.Count -eq 32) 'FAR packed size'
    $lodIndices=@(($approved -join '').ToCharArray() | ForEach-Object {switch -CaseSensitive ($_){'.'{15} 'd'{13}}})
    for($i=0;$i -lt 32;$i++){Require ($farData[$i] -eq (($lodIndices[2*$i] -shl 4) -bor $lodIndices[2*$i+1])) 'FAR header differs from approved packed bytes'}
    $wall=Get-Content (Join-Path $probe 'wall_texture.c') -Raw
    $colors=@([regex]::Matches([regex]::Match($wall,'(?s)wall_palette_colors\[.*?\]\s*=\s*\{(.*?)\}').Groups[1].Value,'0x[0-9a-f]+')|ForEach-Object{[Convert]::ToInt32($_.Value.Substring(2),16)})
    Require ($colors[1] -eq 0x555 -and $colors[12] -eq 0x222) 'FAR palette entries must remain existing gray/dark-gray'
    foreach($byte in $farData){foreach($index in @(($byte -shr 4),($byte -band 15))){
        Require ($index -in @(13,15)) 'FAR contains forbidden white/light outline/non-dark index'
        if($index -ne 15){Require ($colors[$index-1] -ne 0xfff) 'FAR resolves to white in active palette'}
    }}
    Require ($pattern.Count -eq 8 -and @($pattern|Where-Object {$_.Length -ne 8}).Count -eq 0) 'FAR must remain exactly 8x8'
    $farOpaque=0
    for($y=0;$y -lt 8;$y++){for($x=0;$x -lt 8;$x++){
        $byte=$farData[$y*4+[int][Math]::Floor($x/2)]
        $index=if($x -band 1){$byte -band 15}else{$byte -shr 4}
        $sample=$worldSource.GetPixel(2*$x,2*$y)
        Require (($index -eq 15) -eq ($sample.A -eq 0)) 'FAR alpha/occupancy must remain sampled from authored PNG'
        if($index -ne 15){$farOpaque++}
    }}
    Require ($farOpaque -eq 14) 'All 14 dedicated-source FAR opaque positions must remain'
    $farOpaqueRows=@();for($y=0;$y-lt8;$y++){for($x=0;$x-lt8;$x++){if($approved[$y][$x]-ne'.'){$farOpaqueRows+=$y}}}
    Require (($farOpaqueRows|Measure-Object -Minimum).Minimum -eq 3 -and ($farOpaqueRows|Measure-Object -Maximum).Maximum -eq 5) 'FAR pickup opaque rows / quarter-canvas floor padding changed'
    $cmake=Get-Content (Join-Path $root 'CMakeLists.txt') -Raw
    Require ($cmake -match 'set\(asset pick_up_shotgun\.png\)[\s\S]*?set\(sprite_kind WorldPickup\)') 'NEAR world pickup must derive from dedicated source'
    Require ($cmake -match 'generate_shotgun_lod\.ps1"[\s\S]*?-InputPath "\$\{CMAKE_SOURCE_DIR\}/assets/sprites/weapons/pick_up_shotgun\.png"') 'FAR world pickup must derive from dedicated source'
    Require ($cmake -match 'pause_shotgun_icon\.h[\s\S]*?-InputPath "\$\{CMAKE_SOURCE_DIR\}/assets/sprites/weapons/shotgun\.png"') 'Pause icon must continue to derive from shotgun.png'
    Require ((Get-FileHash (Join-Path $root 'assets/sprites/weapons/pick_up_shotgun.png')).Hash -ne (Get-FileHash (Join-Path $root 'assets/sprites/weapons/shotgun.png')).Hash) 'Dedicated world and pause sources must remain distinct'
} finally {$worldSource.Dispose();$im.Dispose()}
Write-Output 'Weapon asset validation PASS: authoritative pause/held source conversions and separate dedicated world source (32-byte FAR / 128-byte NEAR).'
$hud=Get-Content "$root/platform/game_gear/hud_weapon.c" -Raw
$overlay=[regex]::Match($hud,'(?s)void game_gear_overlay_hud_weapon_tile\(.*?\n\}').Value
$overlay=[regex]::Match($hud,'(?s)static void overlay_shotgun_tile\(.*?\n\}').Value+"`n"+$overlay
Require ($overlay.Length -gt 0) 'Production held overlay missing'
$overlay=$overlay.Replace('const unsigned char *mask;','int[] mask; int maskOffset=0, destinationOffset=0;').Replace('unsigned char *destination','int[] destination')
$overlay=$overlay.Replace('mask += (unsigned int)tile_index * 20;','maskOffset += tile_index * 20;').Replace('mask += 5;','maskOffset += 5;').Replace('destination += 4;','destinationOffset += 4;')
$overlay=[regex]::Replace($overlay,'\bmask\[(\d+)\]','mask[maskOffset+$1]')
$overlay=[regex]::Replace($overlay,'\bdestination\[(\d+)\]','destination[destinationOffset+$1]')
$overlay=$overlay.Replace('unsigned char','int').Replace('signed int','int').Replace('unsigned int','int')
$overlay=$overlay.Replace('void game_gear_overlay_hud_weapon_tile','public static void Overlay')
$adapter=@'
public const int HUD_WEAPON_LEFT=80,HUD_WEAPON_TOP=40,HUD_WEAPON_WIDTH=24,HUD_WEAPON_HEIGHT=24,HUD_SHOTGUN_WIDTH=40,HUD_SHOTGUN_HEIGHT=32,WEAPON_SHOTGUN=1,SHOOT=1,hud_weapon_pixels_TRANSPARENT_INDEX=14;
public const int HUD_SHOTGUN_LEFT=64,HUD_SHOTGUN_TOP=32,HUD_WEAPON_RIGHT=104,HUD_WEAPON_BOTTOM=64,shotgun_held_pixels_TRANSPARENT_INDEX=14;
public static int selected_weapon,weapon_state; public static int[] hud_mask_weapon_texture,hud_mask_weapon_shoot_texture,hud_mask_shotgun_held,hud_mask_shotgun_fire;
public static int[] hud_weapon_pixels,hud_weapon_shoot_pixels,shotgun_fire_pixels,shotgun_held_pixels;
public static int[] Tile(int column,int row){
 var data=new int[32];for(int y=0;y<8;y++)for(int x=0;x<8;x++){int c=(column*8+x+row*8+y)&15;for(int p=0;p<4;p++)if((c&(1<<p))!=0)data[y*4+p]|=128>>x;}
 Overlay(data,column,row);return data;
}
'@
Add-Type -TypeDefinition ("public static class HeldWeaponContract {`n"+$overlay+"`n"+$adapter+"`n}")
foreach($asset in @(@('weapon_texture','hud_weapon_pixels'),@('weapon_shoot_texture','hud_weapon_shoot_pixels'),@('shotgun_held','shotgun_held_pixels'),@('shotgun_fire','shotgun_fire_pixels'))){
    $c=Get-Content (Join-Path $probe "$($asset[0]).c") -Raw
    $data=@([regex]::Matches([regex]::Match($c,'(?s)=\s*\{(.*?)\}').Groups[1].Value,'0x[0-9a-f]+') | ForEach-Object {[Convert]::ToInt32($_.Value.Substring(2),16)})
    [HeldWeaponContract]::($asset[1])=$data
}
foreach($name in @('weapon_texture','weapon_shoot_texture','shotgun_held','shotgun_fire')) {
    $m=[regex]::Match((Get-Content "$probe/hud_masks.h" -Raw),"(?s)hud_mask_$name\[\] = \{(.*?)\}")
    Require $m.Success 'Generated native HUD table missing'
    [HeldWeaponContract]::("hud_mask_$name")=@([regex]::Matches($m.Groups[1].Value,'0x([0-9A-Fa-f]+)') | ForEach-Object { [Convert]::ToInt32($_.Groups[1].Value,16) })
}
foreach($pose in @(@(0,0,'gun_12x12.png'),@(0,1,'gun_shoot_12x12.png'),@(1,0,'shotgun_held.png'),@(1,1,'shotgun_held_shoot.png'))){
    [HeldWeaponContract]::selected_weapon=$pose[0];[HeldWeaponContract]::weapon_state=$pose[1]
    $image=[Drawing.Bitmap]::new("$root/assets/sprites/weapons/$($pose[2])")
    $preview=[Drawing.Bitmap]::new(112,64)
    try {
        $left=80-16*$pose[0];$top=40-8*$pose[0];$width=24+16*$pose[0];$height=24+8*$pose[0]
        for($row=0;$row -lt 8;$row++){for($column=0;$column -lt 14;$column++){
            $data=[HeldWeaponContract]::Tile($column,$row)
            for($y=0;$y -lt 8;$y++){for($x=0;$x -lt 8;$x++){
                $screenX=8*$column+$x;$screenY=8*$row+$y;$expected=($screenX+$screenY)-band 15
                if($screenX -ge $left -and $screenX -lt $left+$width -and $screenY -ge $top -and $screenY -lt $top+$height){
                    $p=$image.GetPixel([int][Math]::Floor(($screenX-$left)/2),[int][Math]::Floor(($screenY-$top)/2))
                    if($p.A -ne 0){$expected=$palette[('#{0:x2}{1:x2}{2:x2}' -f $p.R,$p.G,$p.B)]}
                }
                $actual=0;for($plane=0;$plane -lt 4;$plane++){if($data[$y*4+$plane] -band (128 -shr $x)){$actual=$actual -bor (1 -shl $plane)}}
                Require ($actual -eq $expected) 'Production held overlay: exact pistol/shotgun geometry, idle/shoot artwork and alpha no-overwrite'
                $c=if($actual -eq 0){0}else{$colors[$actual-1]}
                $preview.SetPixel($screenX,$screenY,[Drawing.Color]::FromArgb(($c-band 15)*17,(($c-shr 4)-band 15)*17,(($c-shr 8)-band 15)*17))
            }}
        }}
        $preview.Save("$build/held-$($pose[0])-$($pose[1])-preview.png",[Drawing.Imaging.ImageFormat]::Png)
    } finally {$image.Dispose();$preview.Dispose()}
}
Write-Output '- actual held overlay executed: both weapons, both poses, every viewport pixel, unchanged pistol origin/size and transparent destination preservation'
if(Test-Path (Join-Path $build 'GearRay.map')){
    $map=Get-Content "$build/GearRay.map" -Raw
    $rom=[IO.File]::ReadAllBytes((Get-ProductionBuildRom $build))
    function Address([string]$symbol){
        $match=[regex]::Match($map,"(?m)^\s*([0-9A-F]{8})\s+$([regex]::Escape($symbol))\s")
        Require $match.Success "Missing linked weapon symbol $symbol"
        return [Convert]::ToInt32($match.Groups[1].Value,16)
    }
    function LocalAddress([string]$module,[string]$anchor,[string]$symbol){
        $symbols=Get-Content "$build/$module.sym" -Raw
        function Offset([string]$name){$m=[regex]::Match($symbols,"(?m)^\s*\d+\s+$([regex]::Escape($name))\s+([0-9A-F]+)\s");Require $m.Success "Missing local $name";[Convert]::ToInt32($m.Groups[1].Value,16)}
        return (Address $anchor)-(Offset $anchor)+(Offset $symbol)
    }
    function Payload([int]$virtual,[int[]]$bytes,[int]$bank){
        Require (($virtual -shr 16) -eq $bank) 'Weapon payload residency'
        $physical=($virtual -shr 16)*16384+($virtual -band 0x3fff)
        for($i=0;$i -lt $bytes.Length;$i++){Require ($rom[$physical+$i] -eq $bytes[$i]) 'Linked weapon physical payload mismatch'}
    }
    foreach($name in @('world')){
        $c=Get-Content "$probe/shotgun_$name.c" -Raw
        $data=@([regex]::Matches([regex]::Match($c,'(?s)=\s*\{(.*?)\}').Groups[1].Value,'0x[0-9a-f]+') | ForEach-Object {[Convert]::ToInt32($_.Value.Substring(2),16)})
        Payload (Address "_shotgun_${name}_pixels") $data 1
    }
    foreach($name in @('weapon_texture','weapon_shoot_texture','shotgun_held','shotgun_fire')) {
        $m=[regex]::Match((Get-Content "$probe/hud_masks.h" -Raw),"(?s)hud_mask_$name\[\] = \{(.*?)\}")
        Require $m.Success 'Native held mask missing'
        $data=@([regex]::Matches($m.Groups[1].Value,'0x([0-9A-Fa-f]+)')|ForEach-Object{[Convert]::ToInt32($_.Groups[1].Value,16)})
        Payload (LocalAddress 'hud_weapon' '_game_gear_hud_weapon_initialize' "_hud_mask_$name") $data 1
    }
    foreach($obsolete in @('_hud_weapon_pixels','_hud_weapon_shoot_pixels','_shotgun_held_pixels','_shotgun_fire_pixels')) {
        Require ($map -notmatch "(?m)\s+$obsolete\s+") 'Obsolete packed HUD payload is still linked beside native masks'
    }
    Payload (LocalAddress 'sprite_projection' '_game_gear_prepare_world_sprites' '_shotgun_far_pixels') $farData 1
    foreach($weapon in @(@('pause_weapon_icon.h','pause_pistol_tiles'),@('pause_shotgun_icon.h','pause_shotgun_tiles'))){
        $arrays=Get-PauseWeaponArrays (Get-Content "$probe/$($weapon[0])" -Raw) 4 0
        foreach($symbol in $arrays.Keys){Payload (LocalAddress 'pause_map' '_game_gear_pause_map_show' "_$symbol") $arrays[$symbol] 2}
        foreach($side in @($false,$true)){
            $expanded=Expand-PauseWeaponData $arrays $weapon[1] 4 0 $side
            Require ($expanded.Count -eq 384) 'Production pause composite expands to twelve tiles'
        }
    }
    Write-Output '- final ROM: native held masks/world FAR/NEAR Bank 1 bytes and twelve-tile Bank 2 padded pause composites match validated assets'
}

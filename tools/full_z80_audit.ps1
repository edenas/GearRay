param([string]$BuildDirectory='build/release', [switch]$RunValidators, [string]$RomPath='', [string]$OutputDirectory='')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
. "$PSScriptRoot/production_build_artifacts.ps1"
$rom=if (!$RomPath) {Get-ProductionBuildRom $build} elseif ([IO.Path]::IsPathRooted($RomPath)) { $RomPath } else { Join-Path $root $RomPath }
$out=if(!$OutputDirectory){Join-Path $build 'full-z80-audit'}elseif([IO.Path]::IsPathRooted($OutputDirectory)){$OutputDirectory}else{Join-Path $root $OutputDirectory}
New-Item -ItemType Directory -Force $out | Out-Null
if($RunValidators) {
    $results=@()
    foreach($file in Get-ChildItem $PSScriptRoot -Filter 'validate_*.ps1' | Sort-Object Name) {
        $source=Get-Content $file.FullName -Raw
        $argsList=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$file.FullName)
        if($source -match '(?s)^param\([^\)]*\$BuildDirectory') {$argsList+=@('-BuildDirectory',$BuildDirectory)}
        if($source -match '(?s)^param\([^\)]*\$RequireMapPlacement') {$argsList+='-RequireMapPlacement'}
        if($source -match '(?s)^param\([^\)]*\$RequireAssembly') {$argsList+='-RequireAssembly'}
        if($file.BaseName -eq 'validate_bank_layout') {$argsList+=@('-MapPath',"$build/GearRay.map",'-RomPath',$rom)}
        $ErrorActionPreference='Continue'
        & powershell @argsList *> "$out/$($file.BaseName).log"
        $code=$LASTEXITCODE
        $ErrorActionPreference='Stop'
        $results+= [pscustomobject]@{Validator=$file.BaseName;ExitCode=$code}
        Write-Output "$($file.BaseName): $code"
    }
    $results | ConvertTo-Json | Set-Content "$out/validators.json"
}
$modules=@();$functions=@();$ram=@();$helpers=@();$edges=@();$byteArrays=@()
function Frequency($module,$name) {
    if($name -eq 'zombie_distance_metric' -and $module -notin @('zombie_ai','sprite_projection')){return 'J/dead: emitted but never called'}
    if($name -match '^(world_initialize|world_sprites_initialize|world_sprite_initialize|player_initialize|camera_initialize|raycaster_initialize|door_states_initialize|red_door_switch_initialize|game_gear_input_initialize|game_gear_hud_weapon_initialize|game_gear_startup_logo_show)$'){return 'I: startup/restart'}
    switch($module) {
        'main' {return 'A: gameplay coordinator; H/I/event branches'}
        'pause_map' {return 'H: pause entry/UI event; show contains idle input/VBlank loop'}
        'zombie_shooting' {return 'E: shot event, per eligible living target inside scan'}
        'zombie_corpses' {return 'D/G: death-finalization or door-crush event'}
        'zombie_ai' {return 'C: active zombie every fourth gameplay frame; conditional LOS/probes'}
        'enemy_collision' {return 'C: zombie candidate movement probe'}
        'sprite_projection' {return 'C/A: entity projection or frame selection/comparison'}
        'raycaster' {if($name -eq 'raycaster_update'){return 'A: 28 rays/frame; direction rebuild only on basis change'};if($name -eq 'raycaster_get_rendered_rays'){return 'A/C/E: resident shared rays getter'};return 'B: per ray or nonzero ray axis'}
        'render_textures' {return 'B: dirty near-wall half setup or per sampled row'}
        'video' {if($name -eq 'game_gear_video_draw_viewport_border'){return 'I/H: startup/resume visible border'};return 'A/B: frame/column/tile/pixel presentation; dirty gate controls composition'}
        'hud_weapon' {if($name -match 'overlay'){return 'B: dirty HUD tile/pixel'};return 'A/F: frame pose/identity, pickup presence gate'}
        'video_initialization' {return 'I/H/D: startup/resume or health-damage event'}
        'game_over_presentation' {return 'D: player death'}
        'interaction_ray' {return 'G: interaction event, sample loop'}
        'world_interactions' {return 'G: interaction event'}
        'world_initialization' {return 'I: startup/restart'}
        'camera' {if($name -match 'get_'){return 'A/B/C/E/H: shared resident getter'};if($name -eq 'camera_set_fixed_position'){return 'I/D: startup/movement'};return 'D/WARM: rotation input, potentially every turning frame'}
        'player' {if($name -match 'interaction'){return 'A/G: frame edge gate, interaction event body'};if($name -match 'get_|is_dead'){return 'A/C/E/H: shared getter/predicate'};if($name -eq 'player_apply_damage'){return 'D: melee damage'};return 'D/WARM: movement input'}
        'world_sprite' {if($name -eq 'world_sprites_update'){return 'A/C: entity timers/frame'};if($name -match 'get'){return 'A/C/E/G/H: shared entity access'};return 'D/E/G: damage, state change, finalize/dedup/crush'}
        'input' {return 'A/H: gameplay or paused input; intents are gameplay-only'}
        'red_door_switch' {if($name -eq 'red_door_switch_update'){return 'A: authored switch animation'};if($name -match 'activate'){return 'G: interaction event'};return 'B: switch wall material read'}
        'world_objects' {return 'G: interaction metadata'}
        'door_states' {if($name -match 'get'){return 'B/C/G/H: door geometry read'};return 'G: door/switch event'}
        default {if($name -match 'spawn'){return 'I: startup spawn getter'};return 'B/C/G/H/I: world/map geometry queries; transitive callers in calls.csv'}
    }
}
foreach($object in Get-ProductionBuildObjects $build) {
    $rel=Get-Content $object.FullName -Raw
    $asmPath=[IO.Path]::ChangeExtension($object.FullName,'.asm')
    $asm=Get-Content $asmPath -Raw
    foreach($a in [regex]::Matches($asm,'(?m)^(_\w+)::?\r?\n((?:\s*\.db[^\r\n]*\r?\n)+)')) {
        $values=@([regex]::Matches($a.Groups[2].Value,'#0x([0-9a-fA-F]{2})')|ForEach-Object{$_.Groups[1].Value})
        if($values.Count -ge 8){$byteArrays+=[pscustomobject]@{Module=$object.BaseName;Symbol=$a.Groups[1].Value;Bytes=$values.Count;Payload=$values -join ''}}
    }
    foreach($m in [regex]::Matches($rel,'(?m)^A (\S+) size ([0-9A-F]+)')) {
        $size=[Convert]::ToInt32($m.Groups[2].Value,16)
        if($size) {$modules+=[pscustomobject]@{Module=$object.BaseName;Area=$m.Groups[1].Value;Bytes=$size}}
    }
    $area='';$label=''
    foreach($line in $asm -split "`n") {
        if($line -match '^\s*\.area (\S+)') {$area=$Matches[1]}
        if($line -match '^(_\w+)::?\s*$') {$label=$Matches[1]}
        if($area -in @('_DATA','_INITIALIZED') -and $line -match '^\s*\.ds (\d+)') {
            $ram+=[pscustomobject]@{Module=$object.BaseName;Symbol=$label;Bytes=[int]$Matches[1]}
        }
    }
    foreach($m in [regex]::Matches($asm,'(?ms)^; Function (\w+)\r?\n(.*?)(?=^; Function |\z)')) {
        $name=$m.Groups[1].Value;$body=$m.Groups[2].Value
        $areaMatches=[regex]::Matches($asm.Substring(0,$m.Index),'(?m)^\s*\.area (\S+)')
        $area=$areaMatches[$areaMatches.Count-1].Groups[1].Value
        $frame=0
        foreach($a in [regex]::Matches($body,'ld\s+(?:hl|iy),\s*#-(\d+)\s*\r?\n\s*add\s+(?:hl|iy), sp\s*\r?\n\s*ld\s+sp, (?:hl|iy)')) {$frame+=[int]$a.Groups[1].Value}
        $prologue=($body -split '(?m)^;[^\r\n]+:\d+:',3)[0]
        $small=2*[regex]::Matches($prologue,'(?m)^\s*push\s+af').Count+[regex]::Matches($prologue,'(?m)^\s*dec\s+sp').Count
        $pushBound=$frame+2*[regex]::Matches($body,'(?m)^\s*push\s').Count+[regex]::Matches($body,'(?m)^\s*dec\s+sp').Count
        $functions+=[pscustomobject]@{Module=$object.BaseName;Function=$name;Area=$area;Frequency=(Frequency $object.BaseName $name);ExplicitFrame=$frame;SmallFrame=$small;Instructions=[regex]::Matches($body,'(?m)^\t[a-z]+(?:\s|$)').Count;OwnPushBound=$pushBound}
        foreach($c in [regex]::Matches($body,'(?m)^\s*(call|jp)\s+(_\w+)')) {
            $target=$c.Groups[2].Value;$banked=$target -eq '___sdcc_bcall_ehl'
            $before=$body.Substring(0,$c.Index)
            if($banked) {$loads=[regex]::Matches($before,'ld\s+hl, #_(\w+)');$target='_'+$loads[$loads.Count-1].Groups[1].Value}
            $edge=[pscustomobject]@{Module=$object.BaseName;Caller=$name;Target=$target;Banked=$banked;Kind=$c.Groups[1].Value}
            $edges+=$edge
            if($target -match '^_+(mul|div|mod)') {
                $comments=[regex]::Matches($before,'(?m)^;([^\r\n]+:\d+: [^\r\n]+)')
                $expression=if($comments.Count){$comments[$comments.Count-1].Groups[1].Value}else{''}
                $heat=if($object.BaseName -in @('camera','player') -or $name -eq 'raycaster_update'){'WARM'}elseif($object.BaseName -in @('zombie_shooting','interaction_ray','video_initialization')){'EVENT-ONLY (HUD also COLD init)'}else{'HOT'}
                $helpers+=[pscustomobject]@{Module=$object.BaseName;Caller=$name;Helper=$target;Heat=$heat;Frequency=(Frequency $object.BaseName $name);Source=$expression}
            }
        }
    }
}
$modules | Export-Csv "$out/modules.csv" -NoTypeInformation
$ram | Export-Csv "$out/ram.csv" -NoTypeInformation
$functions | Export-Csv "$out/functions.csv" -NoTypeInformation
$helpers | Export-Csv "$out/helpers.csv" -NoTypeInformation
$edges | Export-Csv "$out/calls.csv" -NoTypeInformation
$duplicates=@($byteArrays|Group-Object Payload|Where-Object Count -gt 1|ForEach-Object{$_.Group})
$duplicates|Select-Object Module,Symbol,Bytes|Export-Csv "$out/duplicate-byte-arrays.csv" -NoTypeInformation
@{ScannedByteArrays=$byteArrays.Count;DuplicateMembers=$duplicates.Count;Scope='Consecutive literal .db arrays of at least eight bytes; excludes relocated pointers and .dw arrays.'}|ConvertTo-Json|Set-Content "$out/duplicate-scan.json"
$nodes=@{};$public=@{}
foreach($f in $functions){$key=$f.Module+'::'+$f.Function;$nodes[$key]=$f;if(!$public.ContainsKey($f.Function)){$public[$f.Function]=$key}}
$memo=@{}
function Bound([string]$key,[string[]]$path=@()) {
    if($key -in $path){throw "Recursive path: $key"}
    if($memo.ContainsKey($key)){return $memo[$key]}
    if(!$nodes.ContainsKey($key)){return @{Bytes=64;Path=$key}}
    $f=$nodes[$key];$best=0;$chain=''
    foreach($edge in $edges|Where-Object {$_.Module -eq $f.Module -and $_.Caller -eq $f.Function}) {
        $name=$edge.Target.TrimStart('_');$target=$f.Module+'::'+$name
        if(!$nodes.ContainsKey($target)){$target=if($public.ContainsKey($name)){$public[$name]}else{$name}}
        $child=Bound $target ($path+@($key));$extra=if($edge.Banked){7}else{2}
        if($child.Bytes+$extra -gt $best){$best=$child.Bytes+$extra;$chain=$child.Path}
    }
    $answer=@{Bytes=[int]$f.OwnPushBound+$best;Path=$key+' -> '+$chain}
    $memo[$key]=$answer;return $answer
}
$bounds=@();foreach($name in @('main','raycaster_update','game_gear_video_draw_wall_columns','zombie_shooting_process','zombie_ai_update_all','game_gear_pause_map_show','game_gear_video_restore_gameplay','player_process_interaction')){$b=Bound $public[$name];$bounds+=@{Root=$name;Bytes=$b.Bytes;Path=$b.Path}}
$bounds|ConvertTo-Json -Depth 6|Set-Content "$out/stack-bounds.json"
$addresses=@{};$upper=0
foreach($line in Get-Content "$build/GearRay.ihx") {
    if(!$line.StartsWith(':')){continue};$count=[Convert]::ToInt32($line.Substring(1,2),16);$address=[Convert]::ToInt32($line.Substring(3,4),16);$type=[Convert]::ToInt32($line.Substring(7,2),16)
    if($type -eq 4){$upper=[Convert]::ToInt32($line.Substring(9,4),16)*65536}
    elseif($type -eq 2){$upper=[Convert]::ToInt32($line.Substring(9,4),16)*16}
    elseif($type -eq 0){for($i=0;$i -lt $count;$i++){$addresses[$upper+$address+$i]=$true}}
}
$map=Get-Content "$build/GearRay.map" -Raw
function Sym($n) { $m=[regex]::Match($map,"(?m)^\s*([0-9A-F]{8})\s+$([regex]::Escape($n))\s");if(!$m.Success){throw "Missing $n"};[Convert]::ToInt32($m.Groups[1].Value,16) }
$bankNumbers=@(0)+@([regex]::Matches($map,'(?m)^_BANK(?<number>[0-9]+)\s+[0-9A-Fa-f]{8}\s+(?<size>[0-9A-Fa-f]{8})\b') | ForEach-Object {
    if([Convert]::ToInt32($_.Groups['size'].Value,16) -gt 0){[int]$_.Groups['number'].Value}
})
$banks=@()
foreach($i in $bankNumbers | Sort-Object -Unique){
    $used=if($i -eq 0){(Sym 's__GSFINAL')+(Sym 'l__GSFINAL')}else{Sym "l__BANK$i"}
    # Cold slot-1 and native slot-2 areas share physical page 3; count its
    # disjoint physical extent once, rather than treating BANK3WALL as a page.
    if($i -eq 3 -and $map -match '\s+l__BANK3WALL\s+'){
        $used=[Math]::Max($used,((Sym 's__BANK3WALL') -band 0x3fff)+(Sym 'l__BANK3WALL'))
    }
    $free=16384-$used-$(if($i -eq 1){16}else{0})
    if($free -lt 0){throw "Physical bank $i exceeds its available extent"}
    $banks+=[pscustomobject]@{Bank=$i;Used=$used;Free=$free}
}
$summary=[ordered]@{Banks=$banks;LinkedExtentSum=($banks|Measure-Object Used -Sum).Sum;PersistentRAM=(Sym 'l__DATA')+(Sym 'l__INITIALIZED');DataEnd=(Sym 's__INITIALIZED')+(Sym 'l__INITIALIZED');ROMBytes=(Get-Item $rom).Length;SHA256=(Get-FileHash $rom).Hash;ModuleCount=@(Get-ProductionBuildObjects $build).Count;HelperSites=$helpers.Count;BankCallSites=@($edges|Where-Object Banked).Count}
$summary['EmittedIHXBytes']=$addresses.Count
$summary|ConvertTo-Json -Depth 6|Set-Content "$out/baseline.json"
$summary|ConvertTo-Json -Depth 6
if($RunValidators -and @($results|Where-Object ExitCode -ne 0).Count){exit 1}

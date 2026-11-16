# Development-only generated-call census and conservative stack bound.
function Test-PauseFreezeAssembly {
    $functions=@{}
    . "$PSScriptRoot/production_build_artifacts.ps1"
    foreach($file in Get-ProductionBuildAssembly $build){
        $text=Get-Content $file.FullName -Raw
        $objectPath=[IO.Path]::ChangeExtension($file.FullName,'.rel')
        if(!(Test-Path $objectPath)){continue}
        $object=Get-Content $objectPath -Raw
        $bank=0
        foreach($area in [regex]::Matches($object,'(?m)^A (_BANK\w+) size ([0-9A-Fa-f]+)')){
            if([Convert]::ToInt32($area.Groups[2].Value,16) -eq 0){continue}
            Require ($area.Groups[1].Value -match '^_BANK(?:[1234]|3WALL)$') "Unknown non-empty bank in $($file.Name)"
            $bank=[int]$area.Groups[1].Value.Substring(5,1)
        }
        foreach($m in [regex]::Matches($text,'(?ms)^; Function (\w+)\r?\n(.*?)(?=^; Function |\z)')){
            $name=$m.Groups[1].Value;$body=$m.Groups[2].Value
            $calls=@()
            foreach($call in [regex]::Matches($body,'(?m)^\s*(?:call|jp|rst)\s+(_\w+)')){
                $target=$call.Groups[1].Value.TrimStart('_');$banked=$false
                if($target -eq 'sdcc_bcall_ehl'){
                    $before=$body.Substring(0,$call.Index)
                    $loads=[regex]::Matches($before,'ld\s+hl, #_(\w+)')
                    Require ($loads.Count -gt 0) "Unresolved bank target in $name"
                    $target=$loads[$loads.Count-1].Groups[1].Value;$banked=$true
                }
                $calls+=@{Target=$target;Banked=$banked}
            }
            # Deliberately conservative: count EVERY push/dec-sp and allocation
            # in the function, even on mutually exclusive paths; do not credit
            # pops. Balanced loop iterations do not accumulate stack depth.
            $alloc=0
            foreach($a in [regex]::Matches($body,'ld\s+(?:hl|iy),\s*#-(\d+)\s*\r?\n\s*add\s+(?:hl|iy), sp\s*\r?\n\s*ld\s+sp, (?:hl|iy)')){$alloc+=[int]$a.Groups[1].Value}
            $bound=$alloc+2*[regex]::Matches($body,'(?m)^\s*push\s').Count+[regex]::Matches($body,'(?m)^\s*dec\s+sp').Count
            $entry=@{Name=$name;Module=$file.BaseName;Bank=$bank;OwnPushBound=$bound;Calls=$calls;Body=$body}
            if(!$functions.ContainsKey($name) -or $bound -gt $functions[$name].OwnPushBound){$functions[$name]=$entry}
        }
    }
    $seen=@{}
    function Walk-PauseCalls([string]$name){
        if($seen.ContainsKey($name)){return};$seen[$name]=$true
        if(!$functions.ContainsKey($name)){return}
        foreach($call in $functions[$name].Calls){
            Require (!$call.Banked) "Bank trampoline reachable inside pause: $name"
            Walk-PauseCalls $call.Target
        }
    }
    Walk-PauseCalls 'game_gear_pause_map_show'
    $allowed='^(game_gear_pause_map_show|window_origin|map_tile|passage|cell_pattern|pattern_color|pattern_rows|player_facing|draw_player|frame_rows|draw_rect|draw_focus|load_arrows|load_ui|load_weapon_patterns|draw_window|place_player|corpse_read_row|corpse_pixel|draw_corpses|pan_axis|adjacent_weapon|draw_weapon_slot|draw_weapons|world_get_tile|workshop_map_get_tile|door_instance_find_at|door_state_get|world_sprite_get_count|world_sprite_get|player_get_position_[xy]|camera_get_direction_[xy]|game_gear_input_update|input_pause_requested|SMS_\w+)$'
    foreach($name in $seen.Keys){Require ($name -match $allowed) "Unexpected gameplay/helper reachable from pause: $name"}
    $loader=$functions['load_weapon_patterns']
    Require ($loader.Module -eq 'pause_map' -and $loader.Bank -eq 2 -and $loader.Calls.Count -eq 1 -and $loader.Calls[0].Target -eq 'SMS_VRAMmemcpy' -and !$loader.Calls[0].Banked) 'Precomposed weapon row loader must stay local and call only resident VRAM copy'
    $map=Get-Content "$build/GearRay.map" -Raw
    $nodes=@()
    foreach($name in $seen.Keys|Sort-Object){
        if($functions.ContainsKey($name)){$nodes+=@{Name=$name;Module=$functions[$name].Module;Bank=$functions[$name].Bank;Calls=$functions[$name].Calls}}
        else{
            $symbol=[regex]::Match($map,"(?m)^\s*([0-9A-F]{8})\s+_$name\s")
            Require ($symbol.Success -and [Convert]::ToInt32($symbol.Groups[1].Value,16) -lt 0x4000) "Unresolved/nonresident library call $name"
            $nodes+=@{Name=$name;Module='linked SMSlib/crt0';Bank=0;Address=$symbol.Groups[1].Value}
        }
    }
    $memo=@{}
    function Stack-Bound([string]$name,[string[]]$path=@()){
        Require ($name -notin $path) "Recursive stack path: $name"
        if($memo.ContainsKey($name)){return $memo[$name]}
        # Library arithmetic/VDP leaves use a separate conservative 64-byte
        # allowance, including their internal calls. Not a measured high-water.
        if(!$functions.ContainsKey($name)){return @{Bytes=64;Path=$name}}
        $best=0;$chain=''
        foreach($call in $functions[$name].Calls){
            $child=Stack-Bound $call.Target ($path+@($name))
            $extra=if($call.Banked){7}else{2}
            if($child.Bytes+$extra -gt $best){$best=$child.Bytes+$extra;$chain=$child.Path}
        }
        $answer=@{Bytes=($functions[$name].OwnPushBound+$best);Path=($name+' -> '+$chain)}
        $memo[$name]=$answer;return $answer
    }
    $pauseBound=Stack-Bound 'game_gear_pause_map_show'
    $restoreBound=Stack-Bound 'game_gear_video_restore_gameplay'
    $restoreSeen=@{}
    function Walk-RestoreCalls([string]$name){
        if($restoreSeen.ContainsKey($name)){return};$restoreSeen[$name]=$true
        if($functions.ContainsKey($name)){foreach($call in $functions[$name].Calls){Walk-RestoreCalls $call.Target}}
    }
    Walk-RestoreCalls 'game_gear_video_restore_gameplay'
    $restoreNodes=@()
    foreach($name in $restoreSeen.Keys|Sort-Object){
        if($functions.ContainsKey($name)){$restoreNodes+=@{Name=$name;Module=$functions[$name].Module;Bank=$functions[$name].Bank;Calls=$functions[$name].Calls}}
        else{$restoreNodes+=@{Name=$name;Module='linked runtime/SMSlib';Bank=0}}
    }
    function MapValue([string]$symbol){
        $m=[regex]::Match($map,"(?m)^\s*([0-9A-F]{8})\s+$([regex]::Escape($symbol))\s")
        Require $m.Success "Missing $symbol"
        return [Convert]::ToInt32($m.Groups[1].Value,16)
    }
    $dataEnd=[Math]::Max((MapValue 's__DATA')+(MapValue 'l__DATA'),(MapValue 's__INITIALIZED')+(MapValue 'l__INITIALIZED'))
    $stackGap=0xdff0-$dataEnd
    Require ($pauseBound.Bytes+20 -lt $stackGap -and $restoreBound.Bytes+20 -lt $stackGap) 'Conservative call-chain budget overlaps persistent data'
    $mainAsm=[regex]::Replace($functions['main'].Body,'(?m)^;.*$','')
    Require ($mainAsm -match '(?s)call\s+_game_gear_pause_map_show.*?#_game_gear_video_restore_gameplay\s+call\s+___sdcc_bcall_ehl\s+j[pr]\s+\w+\$.*?call\s+_world_sprites_update') 'Generated main pause gate/continue changed'
    $sources=(Get-ChildItem "$root/game","$root/platform/game_gear" -Filter '*.c'|ForEach-Object{Get-Content $_.FullName -Raw}) -join "`n"
    Require ($sources -notmatch '(?:SMS_setFrameInterruptHandler|SMS_setLineInterruptHandler|GG_setNMIHandler)\s*\(') 'New interrupt callback requires a freeze audit'
    $rom=[IO.File]::ReadAllBytes((Get-ProductionBuildRom $build))
    function LinkAddress([string]$symbol){$m=[regex]::Match($map,"(?m)^\s*([0-9A-F]{8})\s+_+$symbol\s");Require $m.Success "Missing $symbol";return [Convert]::ToInt32($m.Groups[1].Value,16)}
    function WordBytes([int]$value){return ('{0:X2}-{1:X2}' -f ($value-band 255),($value-shr 8))}
    $isr=LinkAddress 'SMS_isr';$callHL=LinkAddress 'sdcc_call_hl'
    # Relocate audited code/data symbols from this link, never opcodes or ports.
    # This also supports the pause-only commit without unrelated RAM changes.
    $expectedIRQ='F5-E5-DB-BF-32-{SMS_VDPFlags}-07-D2-F4-3A-21-{VDPBlank}-36-01-2A-{KeysStatus}-22-{PreviousKeysStatus}-DB-DC-2F-21-{KeysStatus}-77-23-DB-00-F6-7F-2F-77-2A-{SMS_theFrameInterruptHandler}-7C-B5-28-11-C3-F7-3A-2A-{SMS_theLineInterruptHandler}-C5-D5-FD-E5-CD-50-3C-FD-E1-D1-C1-E1-F1-FB-ED-4D-E5-F5-2A-{GG_theNMIHandler}-7C-B5-28-0B-C5-D5-FD-E5-CD-50-3C-FD-E1-D1-C1-F1-E1-ED-45'
    $expectedIRQ=[regex]::Replace($expectedIRQ,'\{(\w+)\}',{
        param($match)
        $address=LinkAddress $match.Groups[1].Value
        Require ($address -ge 0xc000 -and $address -lt $dataEnd) 'IRQ symbol is outside persistent RAM'
        WordBytes $address
    })
    $expectedIRQ=$expectedIRQ.Replace('D2-F4-3A',('D2-'+(WordBytes ($isr+46)))).Replace('C3-F7-3A',('C3-'+(WordBytes ($isr+49)))).Replace('CD-50-3C',('CD-'+(WordBytes $callHL)))
    Require ([BitConverter]::ToString($rom[$isr..($isr+88)]) -eq $expectedIRQ) 'Linked IRQ/NMI changed: re-audit bytecode and hooks'
    @{PauseNodes=$nodes;ResumeNodes=$restoreNodes;PauseConservativeBound=$pauseBound;RestoreConservativeBound=$restoreBound;OuterAndInterruptAllowance=20;StaticToStackGap=$stackGap}|ConvertTo-Json -Depth 12|Set-Content "$build/pause-freeze-callgraph.json"
    Write-Output "- generated pause closure: $($nodes.Count) functions, no simulation/trampolines; linked IRQ/NMI verified"
    Write-Output "- conservative stack bounds before outer/IRQ allowance: pause $($pauseBound.Bytes), restore $($restoreBound.Bytes); gap $stackGap"
}

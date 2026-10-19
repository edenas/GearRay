param([string]$BuildDirectory='build')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
$map=Get-Content (Join-Path $build 'GearRay.map') -Raw
function Symbol([string]$name){$m=[regex]::Match($map,"(?m)^\s*([0-9A-Fa-f]{8})\s+_$name\s+");if(!$m.Success){throw "Missing $name"};[Convert]::ToInt32($m.Groups[1].Value,16)}
$bank1=@('game_gear_prepare_world_sprites','game_gear_hud_weapon_update','game_gear_hud_weapon_changed','zombie_ai_update_all','zombie_shooting_process')
$bank2=@('game_gear_pause_map_show','zombie_corpses_finalize','zombie_corpses_crush_in_door')
foreach($name in $bank1){$a=Symbol $name;if($a -lt 0x14000 -or $a -ge 0x18000){throw "$name left slot-1 page 1"}}
foreach($name in $bank2){$a=Symbol $name;if($a -lt 0x28000 -or $a -ge 0x2C000){throw "$name left permanently mapped slot-2 page 2"}}
. "$PSScriptRoot/production_build_artifacts.ps1"
$asm=(Get-ProductionBuildAssembly $build|ForEach-Object{Get-Content $_.FullName -Raw}) -join "`n"
foreach($name in $bank1+$bank2){if($asm -match "#b_$name"){throw "Obsolete trampoline remains for $name"}}
foreach($name in @('game_gear_startup_logo_show','game_gear_video_present_player_death')){if($asm -notmatch "#b_$name"){throw "Required slot-1 trampoline missing for $name"}}
Write-Output "Bank call topology PASS: $($bank1.Count) direct page-1 hot entries; $($bank2.Count) direct page-2 entries; true slot-1 switches retained."

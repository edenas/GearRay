# Historical optional compile experiment; excluded from Release/validation.
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$out=Join-Path $root 'build/experiments/projection-options'
New-Item -ItemType Directory -Force $out|Out-Null
$sdcc='C:/Program Files/SDCC/bin/sdcc.exe'
$source=Get-Content "$root/platform/game_gear/sprite_projection.c" -Raw
function Compile([string]$name,[string]$text){
  $dir="$root/platform/game_gear"
  $text=[regex]::Replace($text,'(?m)^#include "([^"]+)"',{param($m);$p=[IO.Path]::GetFullPath((Join-Path $dir $m.Groups[1].Value));if(Test-Path $p){'#include "'+$p.Replace('\','/')+'"'}else{$m.Value}})
  $path=Join-Path $out "$name.c";[IO.File]::WriteAllText($path,$text)
  & $sdcc -mz80 -DTARGET_GG "-I$root/game" "-I$root/engine/render" "-I$root/platform/game_gear" "-I$root/build/release/generated" '-ID:/Tools/devkitSMS/SMSlib/src' --peep-file 'D:/Tools/devkitSMS/SMSlib/src/peep-rules.txt' --codeseg BANK1 -c $path -o (Join-Path $out "$name.rel")
  if($LASTEXITCODE){throw "B2 compile failed: $name"}
}
Compile 'scalar_arguments' $source
$pointer=[regex]::Replace($source,'signed int position_x,\r?\n    signed int position_y,\r?\n    signed int direction_x,\r?\n    signed int direction_y,\r?\n    signed int plane_x,\r?\n    signed int plane_y,\r?\n    signed long determinant','const GameGearProjectionContext *context',1)
$m=[regex]::Match($pointer,'(?s)(static void game_gear_project_world_sprite\(.*?)(?=\r?\nunsigned int game_gear_prepare_world_sprites)')
if(!$m.Success){throw 'Cannot isolate B2 projector'}
$function=$m.Groups[1].Value
foreach($field in @('position_x','position_y','direction_x','direction_y','plane_x','plane_y','determinant')){$function=[regex]::Replace($function,"\b$field\b","context->$field")}
$pointer=$pointer.Remove($m.Index,$m.Length).Insert($m.Index,$function)
$pointer=[regex]::Replace($pointer,'(?s)&projected_sprites\[sprite_index\],\r?\n            context\.position_x,.*?context\.determinant\);','&projected_sprites[sprite_index],`n            &context);').Replace('`n',"`n")
Compile 'context_pointer' $pointer
$results=@()
foreach($name in @('context_pointer','scalar_arguments')){
  $rel=Get-Content (Join-Path $out "$name.rel") -Raw;$asm=Get-Content (Join-Path $out "$name.asm") -Raw
  $size=[Convert]::ToInt32(([regex]::Match($rel,'(?m)^A _BANK1 size ([0-9A-F]+)').Groups[1].Value),16)
  $project=[regex]::Match($asm,'(?ms)^; Function game_gear_project_world_sprite\r?\n(.*?)(?=^; Function )').Groups[1].Value
  $prepare=[regex]::Match($asm,'(?ms)^; Function game_gear_prepare_world_sprites\r?\n(.*?)(?=^; Function |\z)').Groups[1].Value
  $results+=[pscustomobject]@{Option=$name;Bank1Bytes=$size;ProjectInstructions=[regex]::Matches($project,'(?m)^\t[a-z]+').Count;PrepareInstructions=[regex]::Matches($prepare,'(?m)^\t[a-z]+').Count;ProjectFrame=([regex]::Match($project,'ld\s+(?:hl|iy), #-(\d+)').Groups[1].Value);PrepareFrame=([regex]::Match($prepare,'ld\s+(?:hl|iy), #-(\d+)').Groups[1].Value)}
}
$results|Format-Table -AutoSize
$results|ConvertTo-Json|Set-Content (Join-Path $out 'results.json')

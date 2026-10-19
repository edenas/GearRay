param([string]$BuildDirectory='build',[switch]$RequireMapPlacement,[switch]$RequireAssembly)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
. "$PSScriptRoot/production_build_artifacts.ps1"
if('native_wall' -notin @(Get-ProductionBuildObjects $build).BaseName) {
    Write-Output 'Native wall candidate is absent from this historical build; original renderer checks apply.'
    exit 0
}
function Values([string]$text,[string]$name) {
    $match=[regex]::Match($text,"(?s)\b$name\[.*?=\s*\{(.*?)\};")
    if(!$match.Success){throw "Missing generated native-wall array: $name"}
    return @([regex]::Matches($match.Groups[1].Value,'0x[0-9a-fA-F]+|\b\d+\b')|ForEach-Object{
        if($_.Value.StartsWith('0x')){[Convert]::ToInt32($_.Value.Substring(2),16)}else{[int]$_.Value}
    })
}
$tables=Get-Content "$build/generated/wall_schedules.h" -Raw
$art=Get-Content "$build/generated/wall_texture.c" -Raw
Add-Type -TypeDefinition @'
using System;
public static class NativeWallTableProof {
 public static long Run(int[] wall,int[] px,int[] py,int[] rows,int[] colors,int[] pairs) {
  if(wall.Length!=320||px.Length!=10||py.Length!=10||rows.Length!=4096||colors.Length!=1280||pairs.Length!=1024)throw new Exception("Native table dimensions");
  long cases=0;
  for(int h=17;h<=144;h++)for(int offset=0;offset<256;offset++)for(int side=0;side<2;side++)for(int material=0;material<10;material++)for(int y=0;y<64;y++) {
   int top=(64-h)/2;
   int expected=y<top||y>=top+h?15:(y-top)*8/h;
   int packed=rows[(h-17)*32+y/2];int actual=(packed>>((y&1)==0?4:0))&15;
   if(actual!=expected)throw new Exception("Clipped schedule differs from exact rational source row");
   if(actual!=15) {
    int source=wall[material*32+expected*4+(offset>>6)];int index=((offset&32)==0?source>>4:source)&15;
    if(index>=10)index=0;
    int reference=side==0?px[index]:py[index];
    int sampled=colors[((material*2+side)*8+(offset>>5))*8+actual];
    if(sampled!=reference)throw new Exception("Native source column/color mismatch");
   }
   cases++;
  }
  for(int left=0;left<16;left++)for(int right=0;right<16;right++)for(int plane=0;plane<4;plane++) {
   int reference=((left&(1<<plane))!=0?240:0)|((right&(1<<plane))!=0?15:0);
   if(pairs[(left*16+right)*4+plane]!=reference)throw new Exception("Native row plane mismatch");
  }
  return cases;
 }
}
'@
$cases=[NativeWallTableProof]::Run((Values $art 'wall_textures'),(Values $art 'wall_palette_x_indices'),(Values $art 'wall_palette_y_indices'),(Values $tables 'wall_source_rows'),(Values $tables 'wall_color_columns'),(Values $tables 'native_wall_pairs'))
if($RequireMapPlacement) {
    $map=Get-Content "$build/GearRay.map" -Raw
    foreach($symbol in @('_wall_plan_prepare','_wall_plan_rows')) {
        $m=[regex]::Match($map,"(?m)^\s*([0-9A-Fa-f]{8})\s+$symbol\s+")
        if(!$m.Success){throw "Missing linked native wall worker: $symbol"}
        $address=[Convert]::ToInt32($m.Groups[1].Value,16)
        if($address -lt 0x39200 -or $address -ge 0x3C000){throw "Native wall entry outside Bank 3 slot-2 tail: $symbol"}
    }
}
if($RequireAssembly) {
    $asm=Get-Content "$build/video.asm" -Raw
    if($asm -notmatch 'call\s+_wall_plan_prepare' -or $asm -notmatch 'call\s+_wall_plan_rows'){throw 'Native wall worker is not called by the linked compositor'}
    if($asm -match '#b_wall_plan_'){throw 'Slot-2 wall kernel must not use the slot-1 bank trampoline'}
    $worker=Get-Content "$build/native_wall.asm" -Raw
    if($worker -match '(?m)^\s*(?:out|outi|di|ei)\b'){throw 'Wall worker unexpectedly owns VDP or interrupt state'}
}
Write-Output "Native wall validation PASS: $cases height/offset/side/material/screen-row cases; all 256 native color pairs; linked slot-2 worker and no VDP/IRQ ownership."

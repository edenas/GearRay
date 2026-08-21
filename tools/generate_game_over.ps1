param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputSource,
    [Parameter(Mandatory=$true)][string]$OutputHeader
)
$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Drawing
$width=150;$height=23;$tileColumns=20;$tileRows=4;$pixelOffsetX=5;$pixelOffsetY=4
$bitmap=[Drawing.Bitmap]::new($InputPath)
try {
 if($bitmap.Width-ne$width-or$bitmap.Height-ne$height){throw 'Game Over image must be exactly 150x23 pixels.'}
 $paletteColors=@('#000000','#ffffff','#bb2200');$indices=New-Object byte[] (160*32)
 for($y=0;$y-lt$height;$y++){for($x=0;$x-lt$width;$x++){$p=$bitmap.GetPixel($x,$y);if($p.A-ne255){throw "Game Over image must be opaque at $x,$y."};$rgb=('#{0:x2}{1:x2}{2:x2}'-f$p.R,$p.G,$p.B);$i=[Array]::IndexOf($paletteColors,$rgb);if($i-lt0){throw "Unexpected Game Over color $rgb at $x,$y."};$indices[($y+$pixelOffsetY)*160+$x+$pixelOffsetX]=$i}}
} finally {$bitmap.Dispose()}
$bytes=[Collections.Generic.List[byte]]::new(2560)
for($ty=0;$ty-lt$tileRows;$ty++){for($tx=0;$tx-lt$tileColumns;$tx++){for($row=0;$row-lt8;$row++){for($plane=0;$plane-lt4;$plane++){$v=0;for($col=0;$col-lt8;$col++){$i=$indices[($ty*8+$row)*160+$tx*8+$col];if($i-band(1-shl$plane)){$v=$v-bor(0x80-shr$col)}};$bytes.Add($v)}}}}
$byteLines=for($i=0;$i-lt$bytes.Count;$i+=16){'    '+(($bytes[$i..($i+15)]|ForEach-Object{'0x{0:x2}'-f$_})-join', ')}
$map=1..80;$mapLines=for($r=0;$r-lt4;$r++){'    '+(($map[($r*20)..($r*20+19)]|ForEach-Object{'0x{0:x4}'-f$_})-join', ')}
$header=@"
#ifndef GEAR_RAY_GENERATED_GAME_OVER_H
#define GEAR_RAY_GENERATED_GAME_OVER_H
#define GAME_OVER_TILE_COLUMNS 20
#define GAME_OVER_TILE_ROWS 4
#define GAME_OVER_TILE_COUNT 80
#define GAME_OVER_TILE_BYTE_COUNT 2560
#define GAME_OVER_TILE_ORIGIN_X 6
#define GAME_OVER_TILE_ORIGIN_Y 10
extern const unsigned char game_over_tiles[GAME_OVER_TILE_BYTE_COUNT];
extern const unsigned int game_over_palette[16];
extern const unsigned int game_over_tilemap[GAME_OVER_TILE_COUNT];
#endif
"@
$source=@"
#include "game_over.h"
const unsigned char game_over_tiles[GAME_OVER_TILE_BYTE_COUNT] = {
$($byteLines-join",`r`n")
};
const unsigned int game_over_palette[16] = {
    0x000, 0xfff, 0x02b, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};
const unsigned int game_over_tilemap[GAME_OVER_TILE_COUNT] = {
$($mapLines-join",`r`n")
};
"@
$dir=Split-Path -Parent $OutputSource;New-Item -ItemType Directory -Force $dir|Out-Null
Set-Content $OutputHeader $header -Encoding Ascii;Set-Content $OutputSource $source -Encoding Ascii

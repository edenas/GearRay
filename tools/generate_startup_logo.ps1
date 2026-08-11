param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputSource,
    [Parameter(Mandatory = $true)][string]$OutputHeader
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$expectedWidth = 96
$expectedHeight = 32
$tileSize = 8
$tileColumns = $expectedWidth / $tileSize
$tileRows = $expectedHeight / $tileSize
$screenTileColumns = 20
$screenTileRows = 18
$screenTileOriginX = 6
$screenTileOriginY = 3
$tileOriginX = $screenTileOriginX +
               ($screenTileColumns - $tileColumns) / 2
$tileOriginY = $screenTileOriginY +
               ($screenTileRows - $tileRows) / 2
$bitmap = [System.Drawing.Bitmap]::new($InputPath)

try {
    if ($bitmap.Width -ne $expectedWidth -or
        $bitmap.Height -ne $expectedHeight) {
        throw "Startup logo must be exactly ${expectedWidth}x${expectedHeight}."
    }

    $colorToIndex = [ordered]@{ '#000000' = 0 }
    $pixelIndices = New-Object byte[] ($expectedWidth * $expectedHeight)
    for ($y = 0; $y -lt $expectedHeight; ++$y) {
        for ($x = 0; $x -lt $expectedWidth; ++$x) {
            $pixel = $bitmap.GetPixel($x, $y)
            if ($pixel.A -ne 255) {
                throw "Startup logo must be fully opaque at ($x,$y)."
            }

            $rgb = ('#{0:x2}{1:x2}{2:x2}' -f
                    $pixel.R, $pixel.G, $pixel.B)
            if (-not $colorToIndex.Contains($rgb)) {
                if ($colorToIndex.Count -ge 16) {
                    throw "Startup logo uses more than 16 colors."
                }
                $colorToIndex[$rgb] = $colorToIndex.Count
            }
            $pixelIndices[$y * $expectedWidth + $x] = $colorToIndex[$rgb]
        }
    }

    $tileBytes = [System.Collections.Generic.List[byte]]::new(
        $tileColumns * $tileRows * 32)
    for ($tileY = 0; $tileY -lt $tileRows; ++$tileY) {
        for ($tileX = 0; $tileX -lt $tileColumns; ++$tileX) {
            for ($row = 0; $row -lt $tileSize; ++$row) {
                for ($plane = 0; $plane -lt 4; ++$plane) {
                    $planeByte = 0
                    for ($column = 0; $column -lt $tileSize; ++$column) {
                        $pixelX = $tileX * $tileSize + $column
                        $pixelY = $tileY * $tileSize + $row
                        $index = $pixelIndices[
                            $pixelY * $expectedWidth + $pixelX]
                        if ($index -band (1 -shl $plane)) {
                            $planeByte = $planeByte -bor (0x80 -shr $column)
                        }
                    }
                    $tileBytes.Add($planeByte)
                }
            }
        }
    }

    $palette = [System.Collections.Generic.List[uint16]]::new(16)
    foreach ($rgb in $colorToIndex.Keys) {
        $red = [Convert]::ToInt32($rgb.Substring(1, 2), 16) -shr 4
        $green = [Convert]::ToInt32($rgb.Substring(3, 2), 16) -shr 4
        $blue = [Convert]::ToInt32($rgb.Substring(5, 2), 16) -shr 4
        $palette.Add([uint16]($red -bor ($green -shl 4) -bor
                              ($blue -shl 8)))
    }
    while ($palette.Count -lt 16) { $palette.Add(0) }
}
finally {
    $bitmap.Dispose()
}

$tileRowsSource = for ($index = 0; $index -lt $tileBytes.Count; $index += 16) {
    "    " + (($tileBytes[$index..($index + 15)] |
        ForEach-Object { "0x{0:x2}" -f $_ }) -join ", ")
}
$paletteSource = "    " + (($palette |
    ForEach-Object { "0x{0:x3}" -f $_ }) -join ", ")
$tileMap = 1..($tileColumns * $tileRows)
$tileMapRows = for ($row = 0; $row -lt $tileRows; ++$row) {
    $offset = $row * $tileColumns
    "    " + (($tileMap[$offset..($offset + $tileColumns - 1)] |
        ForEach-Object { "0x{0:x4}" -f $_ }) -join ", ")
}

$header = @"
#ifndef GEAR_RAY_GENERATED_SEGA_LOGO_H
#define GEAR_RAY_GENERATED_SEGA_LOGO_H

#define SEGA_LOGO_TILE_COLUMNS $tileColumns
#define SEGA_LOGO_TILE_ROWS $tileRows
#define SEGA_LOGO_TILE_ORIGIN_X $tileOriginX
#define SEGA_LOGO_TILE_ORIGIN_Y $tileOriginY
#define SEGA_LOGO_TILE_COUNT $($tileColumns * $tileRows)
#define SEGA_LOGO_TILE_BYTE_COUNT $($tileBytes.Count)

extern const unsigned char sega_logo_tiles[SEGA_LOGO_TILE_BYTE_COUNT];
extern const unsigned int sega_logo_palette[16];
extern const unsigned int sega_logo_tilemap[SEGA_LOGO_TILE_COUNT];

#endif
"@
$source = @"
#include "sega_logo.h"

const unsigned char sega_logo_tiles[SEGA_LOGO_TILE_BYTE_COUNT] = {
$($tileRowsSource -join ",`r`n")
};

const unsigned int sega_logo_palette[16] = {
$paletteSource
};

const unsigned int sega_logo_tilemap[SEGA_LOGO_TILE_COUNT] = {
$($tileMapRows -join ",`r`n")
};
"@

$outputDirectory = Split-Path -Parent $OutputSource
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
Set-Content -LiteralPath $OutputHeader -Value $header -Encoding Ascii
Set-Content -LiteralPath $OutputSource -Value $source -Encoding Ascii

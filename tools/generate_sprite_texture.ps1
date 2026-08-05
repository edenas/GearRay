param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputSource,
    [Parameter(Mandatory = $true)][string]$OutputHeader,
    [Parameter(Mandatory = $true)][string]$Symbol,
    [ValidateSet('WorldSprite', 'HudWeapon')][string]$SpriteKind = 'WorldSprite'
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$expectedSize = if ($SpriteKind -eq 'HudWeapon') { 12 } else { 8 }
$transparentIndex = if ($SpriteKind -eq 'HudWeapon') { 14 } else { 15 }
$bitmap = [System.Drawing.Bitmap]::new($InputPath)
try {
    if ($bitmap.Width -ne $expectedSize -or $bitmap.Height -ne $expectedSize) {
        throw "Sprite must be exactly ${expectedSize}x${expectedSize}."
    }

    $pixelCount = $expectedSize * $expectedSize
    $pixels = [System.Collections.Generic.List[byte]]::new($pixelCount)
    for ($y = 0; $y -lt $expectedSize; ++$y) {
        for ($x = 0; $x -lt $expectedSize; ++$x) {
            $pixel = $bitmap.GetPixel($x, $y)
            if ($pixel.A -eq 0) {
                $pixels.Add($transparentIndex)
                continue
            }
            if ($pixel.A -ne 255) {
                throw "Unexpected partial alpha at ($x,$y): $($pixel.A)."
            }

            $rgb = ('#{0:x2}{1:x2}{2:x2}' -f
                    $pixel.R, $pixel.G, $pixel.B)
            if ($SpriteKind -eq 'HudWeapon') {
                $index = switch ($rgb) {
                    '#000000' { 0; break }
                    '#ad3e00' { 1; break }
                    '#4d4d4d' { 2; break }
                    '#797878' { 3; break }
                    '#b51a00' { 5; break }
                    '#785700' { 6; break }
                    '#ffc4ab' { 11; break }
                    '#ffa57d' { 15; break }
                    '#1a1a1a' { 13; break }
                    '#ffffff' { 12; break }
                    default {
                        throw "Sprite color $rgb at ($x,$y) has no exact BG palette mapping."
                    }
                }
            }
            else {
                $index = switch ($rgb) {
                    '#000000' { 0; break }
                    '#1a1a1a' { 13; break }
                    '#2d2d2d' { 10; break }
                    '#008cb4' { 4; break }
                    '#b51a00' { 5; break }
                    '#53602a' { 7; break }
                    '#006d8f' { 8; break }
                    default {
                        throw "Sprite color $rgb at ($x,$y) has no exact BG palette mapping."
                    }
                }
            }
            $pixels.Add($index)
        }
    }
}
finally {
    $bitmap.Dispose()
}

$packedSourceRowStride = $expectedSize / 2
$packedRowStride = if ($SpriteKind -eq 'HudWeapon') {
    8
}
else {
    $packedSourceRowStride
}
$byteCount = $packedRowStride * $expectedSize
$bytes = [System.Collections.Generic.List[byte]]::new($byteCount)
for ($y = 0; $y -lt $expectedSize; ++$y) {
    $sourceRowOffset = $y * $expectedSize
    for ($x = 0; $x -lt $expectedSize; $x += 2) {
        $bytes.Add(($pixels[$sourceRowOffset + $x] -shl 4) -bor
                   $pixels[$sourceRowOffset + $x + 1])
    }
    for ($padding = $packedSourceRowStride;
         $padding -lt $packedRowStride;
         ++$padding) {
        $bytes.Add(($transparentIndex -shl 4) -bor $transparentIndex)
    }
}

$rows = for ($index = 0; $index -lt $byteCount; $index += $packedRowStride) {
    "    " + (($bytes[$index..($index + $packedRowStride - 1)] |
        ForEach-Object { "0x{0:x2}" -f $_ }) -join ", ")
}

$headerGuard = "GEAR_RAY_GENERATED_" + $Symbol.ToUpperInvariant() + "_H"
$header = @"
#ifndef $headerGuard
#define $headerGuard

#define ${Symbol}_WIDTH $expectedSize
#define ${Symbol}_HEIGHT $expectedSize
#define ${Symbol}_PACKED_ROW_STRIDE $packedRowStride
#define ${Symbol}_TRANSPARENT_INDEX $transparentIndex
#define ${Symbol}_BYTE_COUNT $byteCount

extern const unsigned char $Symbol[${Symbol}_BYTE_COUNT];

#endif
"@

$headerName = Split-Path -Leaf $OutputHeader
$source = @"
#include "$headerName"

const unsigned char $Symbol[${Symbol}_BYTE_COUNT] = {
$($rows -join ",`r`n")
};
"@

$outputDirectory = Split-Path -Parent $OutputSource
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
Set-Content -LiteralPath $OutputHeader -Value $header -Encoding Ascii
Set-Content -LiteralPath $OutputSource -Value $source -Encoding Ascii

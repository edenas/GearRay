param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputSource,
    [Parameter(Mandatory = $true)]
    [string]$OutputHeader
)

$ErrorActionPreference = "Stop"
$textureWidth = 16
$textureHeight = 16
$packedRowStride = $textureWidth / 2
$textureByteCount = $packedRowStride * $textureHeight
$wallColorCount = 7
$nearWallMinimumHeight = 17
$maximumProjectedWallHeight = 144

if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
    throw "Wall texture PNG was not found: $InputPath"
}

Add-Type -AssemblyName System.Drawing

try {
    $bitmap = [System.Drawing.Bitmap]::new([string]$InputPath)
}
catch {
    throw "Wall texture PNG is not readable: $InputPath"
}

function Convert-ToGameGearChannel {
    param([int]$Channel)
    return [int][Math]::Floor(($Channel * 15 + 127) / 255)
}

try {
    if ($bitmap.Width -ne $textureWidth -or
        $bitmap.Height -ne $textureHeight) {
        throw "Wall texture must be exactly ${textureWidth}x${textureHeight}; found $($bitmap.Width)x$($bitmap.Height)."
    }

    $quantizedPixels = [System.Collections.Generic.List[object]]::new($textureWidth * $textureHeight)
    $colorCounts = @{}

    for ($textureY = 0; $textureY -lt $textureHeight; ++$textureY) {
        for ($textureX = 0; $textureX -lt $textureWidth; ++$textureX) {
            $pixel = $bitmap.GetPixel($textureX, $textureY)
            $red = Convert-ToGameGearChannel $pixel.R
            $green = Convert-ToGameGearChannel $pixel.G
            $blue = Convert-ToGameGearChannel $pixel.B
            $packedColor = $red -bor ($green -shl 4) -bor ($blue -shl 8)
            $quantizedPixels.Add($packedColor)

            if ($colorCounts.ContainsKey($packedColor)) {
                $colorCounts[$packedColor]++
            }
            else {
                $colorCounts[$packedColor] = 1
            }
        }
    }
}
finally {
    $bitmap.Dispose()
}

$colorRecords = @(
    $colorCounts.GetEnumerator() |
        Sort-Object Name |
        ForEach-Object {
            $packed = [int]$_.Key
            [pscustomobject]@{
                R = $packed -band 15
                G = ($packed -shr 4) -band 15
                B = ($packed -shr 8) -band 15
                Count = [int]$_.Value
            }
        }
)

$palette = [System.Collections.Generic.List[object]]::new($wallColorCount)
$neutralTargets = @(1, 4, 8, 12)
foreach ($target in $neutralTargets) {
    $neutral = $colorRecords |
        Where-Object {
            ([Math]::Max($_.R, [Math]::Max($_.G, $_.B)) -
             [Math]::Min($_.R, [Math]::Min($_.G, $_.B))) -le 1
        } |
        Sort-Object @{ Expression = {
            ($_.R - $target) * ($_.R - $target) +
            ($_.G - $target) * ($_.G - $target) +
            ($_.B - $target) * ($_.B - $target)
        } }, @{ Expression = 'Count'; Descending = $true }, R, G, B |
        Select-Object -First 1
    $palette.Add([pscustomobject]@{ R = $neutral.R; G = $neutral.G; B = $neutral.B })
}

$blue = $colorRecords |
    Sort-Object @{ Expression = { $_.B - [Math]::Max($_.R, $_.G) }; Descending = $true },
                @{ Expression = 'Count'; Descending = $true }, R, G, B |
    Select-Object -First 1
$warm = $colorRecords |
    Sort-Object @{ Expression = { $_.R - [Math]::Max($_.G, $_.B) }; Descending = $true },
                @{ Expression = 'Count'; Descending = $true }, R, G, B |
    Select-Object -First 1
$green = $colorRecords |
    Sort-Object @{ Expression = { $_.G - [Math]::Max($_.R, $_.B) }; Descending = $true },
                @{ Expression = 'Count'; Descending = $true }, R, G, B |
    Select-Object -First 1

$palette.Add([pscustomobject]@{ R = $blue.R; G = $blue.G; B = $blue.B })
$palette.Add([pscustomobject]@{ R = $warm.R; G = $warm.G; B = $warm.B })
$palette.Add([pscustomobject]@{ R = $green.R; G = $green.G; B = $green.B })

$indexedPixels = [System.Collections.Generic.List[byte]]::new($textureWidth * $textureHeight)
foreach ($packedPixel in $quantizedPixels) {
    $red = $packedPixel -band 15
    $green = ($packedPixel -shr 4) -band 15
    $blue = ($packedPixel -shr 8) -band 15
    $bestIndex = 0
    $bestDistance = 2147483647

    for ($paletteIndex = 0; $paletteIndex -lt $palette.Count; ++$paletteIndex) {
        $redDifference = $red - $palette[$paletteIndex].R
        $greenDifference = $green - $palette[$paletteIndex].G
        $blueDifference = $blue - $palette[$paletteIndex].B
        $distance = $redDifference * $redDifference +
                    $greenDifference * $greenDifference +
                    $blueDifference * $blueDifference

        if ($distance -lt $bestDistance) {
            $bestDistance = $distance
            $bestIndex = $paletteIndex
        }
    }

    $indexedPixels.Add($bestIndex)
}

$textureBytes = [System.Collections.Generic.List[byte]]::new($textureByteCount)
for ($index = 0; $index -lt $indexedPixels.Count; $index += 2) {
    $textureBytes.Add(($indexedPixels[$index] -shl 4) -bor
                      $indexedPixels[$index + 1])
}

$textureSteps = [System.Collections.Generic.List[int]]::new(
    $maximumProjectedWallHeight - $nearWallMinimumHeight + 1)
$textureStepRemainders = [System.Collections.Generic.List[byte]]::new(
    $maximumProjectedWallHeight - $nearWallMinimumHeight + 1)
for ($projectedHeight = $nearWallMinimumHeight;
     $projectedHeight -le $maximumProjectedWallHeight;
     ++$projectedHeight) {
    $textureStep = [Math]::Floor(
        ($textureHeight * 256) / $projectedHeight)
    $textureSteps.Add($textureStep)
    $textureStepRemainders.Add(
        $textureHeight * 256 - $textureStep * $projectedHeight)
}

$paletteColors = [System.Collections.Generic.List[int]]::new(14)
foreach ($color in $palette) {
    $paletteColors.Add($color.R -bor ($color.G -shl 4) -bor
                       ($color.B -shl 8))
}

foreach ($color in $palette) {
    $darkRed = [Math]::Max(1, $color.R - 2)
    $darkGreen = [Math]::Max(1, $color.G - 2)
    $darkBlue = [Math]::Max(1, $color.B - 2)
    $paletteColors.Add($darkRed -bor ($darkGreen -shl 4) -bor
                       ($darkBlue -shl 8))
}

$headerText = @"
#ifndef GEAR_RAY_GENERATED_WALL_TEXTURE_H
#define GEAR_RAY_GENERATED_WALL_TEXTURE_H

#define WALL_TEXTURE_WIDTH $textureWidth
#define WALL_TEXTURE_HEIGHT $textureHeight
#define WALL_TEXTURE_PACKED_ROW_STRIDE $packedRowStride
#define WALL_TEXTURE_PACKED_ROW_SHIFT 3
#define WALL_TEXTURE_COLOR_COUNT 7
#define WALL_TEXTURE_BYTE_COUNT $textureByteCount
#define WALL_TEXTURE_SAMPLER_MINIMUM_HEIGHT $nearWallMinimumHeight
#define WALL_TEXTURE_SAMPLER_HEIGHT_COUNT $($maximumProjectedWallHeight - $nearWallMinimumHeight + 1)
#define WALL_PALETTE_COLOR_COUNT 14

extern const unsigned char wall_texture[WALL_TEXTURE_BYTE_COUNT];
extern const unsigned int wall_texture_steps[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT];
extern const unsigned char wall_texture_step_remainders[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT];
extern const unsigned int wall_palette_colors[WALL_PALETTE_COLOR_COUNT];

#endif
"@

$sourceLines = [System.Collections.Generic.List[string]]::new()
$sourceLines.Add('#include "wall_texture.h"')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_texture[WALL_TEXTURE_BYTE_COUNT] = {')
for ($offset = 0; $offset -lt $textureBytes.Count; $offset += 8) {
    $values = @()
    for ($index = 0; $index -lt 8; ++$index) {
        $values += ('0x{0:x2}' -f $textureBytes[$offset + $index])
    }
    $suffix = ','
    if ($offset + 8 -eq $textureBytes.Count) { $suffix = '' }
    $sourceLines.Add('    ' + ($values -join ', ') + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned int wall_texture_steps[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT] = {')
for ($offset = 0; $offset -lt $textureSteps.Count; $offset += 8) {
    $values = @()
    for ($index = 0; $index -lt 8; ++$index) {
        $values += ('0x{0:x4}' -f $textureSteps[$offset + $index])
    }
    $suffix = if ($offset + 8 -eq $textureSteps.Count) { '' } else { ',' }
    $sourceLines.Add('    ' + ($values -join ', ') + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_texture_step_remainders[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT] = {')
for ($offset = 0; $offset -lt $textureStepRemainders.Count; $offset += 8) {
    $values = @()
    for ($index = 0; $index -lt 8; ++$index) {
        $values += ('0x{0:x2}' -f $textureStepRemainders[$offset + $index])
    }
    $suffix = if ($offset + 8 -eq $textureStepRemainders.Count) { '' } else { ',' }
    $sourceLines.Add('    ' + ($values -join ', ') + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned int wall_palette_colors[WALL_PALETTE_COLOR_COUNT] = {')
$sourceLines.Add('    ' + (($paletteColors | ForEach-Object { '0x{0:x3}' -f $_ }) -join ', '))
$sourceLines.Add('};')

$utf8WithoutBom = [System.Text.UTF8Encoding]::new($false)
$sourceText = ($sourceLines -join "`n") + "`n"
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputSource)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputHeader)) | Out-Null
[System.IO.File]::WriteAllText($OutputSource, $sourceText, $utf8WithoutBom)
[System.IO.File]::WriteAllText($OutputHeader, $headerText.Replace("`r`n", "`n"), $utf8WithoutBom)

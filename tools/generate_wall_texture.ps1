param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$BloodInputPath,
    [Parameter(Mandatory = $true)][string]$DoorInputPath,
    [Parameter(Mandatory = $true)][string]$RedDoorInputPath,
    [Parameter(Mandatory = $true)][string]$SwitchWaitingFrame1InputPath,
    [Parameter(Mandatory = $true)][string]$SwitchWaitingFrame2InputPath,
    [Parameter(Mandatory = $true)][string]$SwitchActivatedFrame1InputPath,
    [Parameter(Mandatory = $true)][string]$SwitchActivatedFrame2InputPath,
    [Parameter(Mandatory = $true)][string]$OutputSource,
    [Parameter(Mandatory = $true)][string]$OutputHeader
)

$ErrorActionPreference = "Stop"
$textureWidth = 8
$textureHeight = 8
$packedRowStride = 4
$textureByteCount = 32
$nearWallMinimumHeight = 17
$maximumProjectedWallHeight = 144
Add-Type -AssemblyName System.Drawing

function Get-SourcePixels {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Description PNG was not found: $Path"
    }
    try { $bitmap = [System.Drawing.Bitmap]::new($Path) }
    catch { throw "$Description PNG is not readable: $Path" }
    try {
        if ($bitmap.Width -ne 8 -or $bitmap.Height -ne 8) {
            throw "$Description must be exactly 8x8; found $($bitmap.Width)x$($bitmap.Height)."
        }
        $pixels = [System.Collections.Generic.List[object]]::new(64)
        for ($y = 0; $y -lt 8; ++$y) {
            for ($x = 0; $x -lt 8; ++$x) {
                $pixel = $bitmap.GetPixel($x, $y)
                if ($pixel.A -ne 255) {
                    throw "Unexpected non-opaque $Description pixel at ($x,$y): alpha $($pixel.A)."
                }
                $pixels.Add([pscustomobject]@{
                    R = [int]$pixel.R; G = [int]$pixel.G; B = [int]$pixel.B
                })
            }
        }
        return ,$pixels
    }
    finally { $bitmap.Dispose() }
}

function Get-Rgb {
    param($Pixel)
    return ('#{0:x2}{1:x2}{2:x2}' -f $Pixel.R, $Pixel.G, $Pixel.B)
}

function Assert-KnownColors {
    param($Pixels, [string[]]$KnownColors, [string]$Description)
    for ($index = 0; $index -lt $Pixels.Count; ++$index) {
        $rgb = Get-Rgb $Pixels[$index]
        if ($KnownColors -notcontains $rgb) {
            $x = $index % 8
            $y = [Math]::Floor($index / 8)
            throw "Unexpected $Description source color at ($x,$y): RGB $rgb."
        }
    }
}

function Convert-EnvironmentToPalette {
    param($Pixels, [string]$Description)
    $result = [System.Collections.Generic.List[byte]]::new(64)
    foreach ($pixel in $Pixels) {
        $rgb = Get-Rgb $pixel
        $index = switch ($rgb) {
            '#000000' { 0; break }
            '#000009' { 0; break }
            '#4d4d4d' { 1; break }
            '#797878' { 2; break }
            '#53602a' { 6; break }
            '#785700' { 5; break }
            '#b51a00' { 4; break }
            default { throw "Unexpected $Description source color: RGB $rgb." }
        }
        $result.Add($index)
    }
    return ,$result
}

function Convert-SwitchToPalette {
    param($Pixels, [string]$Description)
    $result = [System.Collections.Generic.List[byte]]::new(64)
    foreach ($pixel in $Pixels) {
        $rgb = Get-Rgb $pixel
        $index = switch ($rgb) {
            '#000000' { 0; break }
            '#53602a' { 6; break }
            '#b51a00' { 4; break }
            '#008cb4' { 3; break }
            '#006d8f' { 7; break }
            '#ffffff' { 8; break }
            '#669c35' { 9; break }
            default { throw "Unexpected $Description source color: RGB $rgb." }
        }
        $result.Add($index)
    }
    return ,$result
}

function Convert-ToPackedTexture {
    param($Pixels)
    $result = [System.Collections.Generic.List[byte]]::new(32)
    for ($index = 0; $index -lt 64; $index += 2) {
        $result.Add(($Pixels[$index] -shl 4) -bor $Pixels[$index + 1])
    }
    return ,$result
}

$wallPixels = Get-SourcePixels $InputPath 'Concrete wall texture'
$bloodWallPixels = Get-SourcePixels $BloodInputPath 'Blood concrete wall texture'
$doorPixels = Get-SourcePixels $DoorInputPath 'Yellow door texture'
$redDoorPixels = Get-SourcePixels $RedDoorInputPath 'Red door texture'
$switchWaiting1Pixels = Get-SourcePixels $SwitchWaitingFrame1InputPath 'Switch waiting frame 1 texture'
$switchWaiting2Pixels = Get-SourcePixels $SwitchWaitingFrame2InputPath 'Switch waiting frame 2 texture'
$switchActivated1Pixels = Get-SourcePixels $SwitchActivatedFrame1InputPath 'Switch activated frame 1 texture'
$switchActivated2Pixels = Get-SourcePixels $SwitchActivatedFrame2InputPath 'Switch activated frame 2 texture'

$wallColors = @('#4d4d4d', '#53602a', '#797878')
$bloodWallColors = @('#4d4d4d', '#53602a', '#797878', '#b51a00')
$yellowDoorColors = @('#000000', '#000009', '#4d4d4d', '#53602a', '#785700')
$redDoorColors = @('#000000', '#000009', '#4d4d4d', '#53602a', '#b51a00')
$waitingSwitchColors = @('#000000', '#53602a', '#b51a00',
                         '#008cb4', '#006d8f', '#ffffff')
$activatedSwitchColors = @('#000000', '#53602a', '#669c35',
                           '#008cb4', '#006d8f', '#ffffff')
Assert-KnownColors $wallPixels $wallColors 'concrete wall'
Assert-KnownColors $bloodWallPixels $bloodWallColors 'blood concrete wall'
Assert-KnownColors $doorPixels $yellowDoorColors 'yellow door'
Assert-KnownColors $redDoorPixels $redDoorColors 'red door'
Assert-KnownColors $switchWaiting1Pixels $waitingSwitchColors 'switch waiting frame 1'
Assert-KnownColors $switchWaiting2Pixels $waitingSwitchColors 'switch waiting frame 2'
Assert-KnownColors $switchActivated1Pixels $activatedSwitchColors 'switch activated frame 1'
Assert-KnownColors $switchActivated2Pixels $activatedSwitchColors 'switch activated frame 2'

$textures = @(
    # Texture IDs 1..4: concrete materials and semantic placeholders.
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $wallPixels 'concrete wall')),
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $bloodWallPixels 'blood concrete wall')),
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $wallPixels 'concrete wall')),
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $wallPixels 'concrete wall')),
    # Texture IDs 5..6: yellow and red doors.
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $doorPixels 'yellow door')),
    (Convert-ToPackedTexture (Convert-EnvironmentToPalette $redDoorPixels 'red door')),
    # Texture IDs 7..10: waiting and activated switch animation frames.
    (Convert-ToPackedTexture (Convert-SwitchToPalette $switchWaiting1Pixels 'switch waiting frame 1')),
    (Convert-ToPackedTexture (Convert-SwitchToPalette $switchWaiting2Pixels 'switch waiting frame 2')),
    (Convert-ToPackedTexture (Convert-SwitchToPalette $switchActivated1Pixels 'switch activated frame 1')),
    (Convert-ToPackedTexture (Convert-SwitchToPalette $switchActivated2Pixels 'switch activated frame 2'))
)

$textureSteps = [System.Collections.Generic.List[int]]::new(128)
$textureStepRemainders = [System.Collections.Generic.List[byte]]::new(128)
for ($height = $nearWallMinimumHeight; $height -le $maximumProjectedWallHeight; ++$height) {
    $step = [Math]::Floor((8 * 256) / $height)
    $textureSteps.Add($step)
    $textureStepRemainders.Add(8 * 256 - $step * $height)
}

$paletteColors = @(
    0x555, 0x777, 0xb80, 0x02b, 0x057, 0x265, 0x860, 0x566,
    0x333, 0x961, 0x119, 0x396, 0x143, 0x641
)
$paletteXIndices = @(0, 2, 3, 4, 5, 6, 7, 8, 1, 13)
$paletteYIndices = @(0, 10, 2, 11, 12, 6, 14, 15, 1, 13)

$headerText = @"
#ifndef GEAR_RAY_GENERATED_WALL_TEXTURE_H
#define GEAR_RAY_GENERATED_WALL_TEXTURE_H

#define WALL_TEXTURE_WIDTH 8
#define WALL_TEXTURE_HEIGHT 8
#define WALL_TEXTURE_PACKED_ROW_STRIDE 4
#define WALL_TEXTURE_PACKED_ROW_SHIFT 2
#define WALL_TEXTURE_COLOR_COUNT 10
#define WALL_TEXTURE_BYTE_COUNT 32
#define WALL_TEXTURE_COUNT 10
#define WALL_TEXTURE_SAMPLER_MINIMUM_HEIGHT 17
#define WALL_TEXTURE_SAMPLER_HEIGHT_COUNT 128
#define WALL_PALETTE_COLOR_COUNT 14

extern const unsigned char wall_textures[WALL_TEXTURE_COUNT][WALL_TEXTURE_BYTE_COUNT];
extern const unsigned int wall_texture_steps[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT];
extern const unsigned char wall_texture_step_remainders[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT];
extern const unsigned int wall_palette_colors[WALL_PALETTE_COLOR_COUNT];
extern const unsigned char wall_palette_x_indices[WALL_TEXTURE_COLOR_COUNT];
extern const unsigned char wall_palette_y_indices[WALL_TEXTURE_COLOR_COUNT];

#endif
"@

$sourceLines = [System.Collections.Generic.List[string]]::new()
$sourceLines.Add('#include "wall_texture.h"')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_textures[WALL_TEXTURE_COUNT][WALL_TEXTURE_BYTE_COUNT] = {')
for ($textureIndex = 0; $textureIndex -lt 10; ++$textureIndex) {
    $sourceLines.Add('    {')
    $bytes = $textures[$textureIndex]
    for ($offset = 0; $offset -lt 32; $offset += 4) {
        $values = @()
        for ($index = 0; $index -lt 4; ++$index) {
            $values += ('0x{0:x2}' -f $bytes[$offset + $index])
        }
        $suffix = if ($offset -eq 28) { '' } else { ',' }
        $sourceLines.Add('        ' + ($values -join ', ') + $suffix)
    }
    $suffix = if ($textureIndex -eq 9) { '' } else { ',' }
    $sourceLines.Add('    }' + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned int wall_texture_steps[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT] = {')
for ($offset = 0; $offset -lt 128; $offset += 8) {
    $values = for ($index = 0; $index -lt 8; ++$index) {
        '0x{0:x4}' -f $textureSteps[$offset + $index]
    }
    $suffix = if ($offset -eq 120) { '' } else { ',' }
    $sourceLines.Add('    ' + ($values -join ', ') + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_texture_step_remainders[WALL_TEXTURE_SAMPLER_HEIGHT_COUNT] = {')
for ($offset = 0; $offset -lt 128; $offset += 8) {
    $values = for ($index = 0; $index -lt 8; ++$index) {
        '0x{0:x2}' -f $textureStepRemainders[$offset + $index]
    }
    $suffix = if ($offset -eq 120) { '' } else { ',' }
    $sourceLines.Add('    ' + ($values -join ', ') + $suffix)
}
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned int wall_palette_colors[WALL_PALETTE_COLOR_COUNT] = {')
$sourceLines.Add('    ' + (($paletteColors | ForEach-Object { '0x{0:x3}' -f $_ }) -join ', '))
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_palette_x_indices[WALL_TEXTURE_COLOR_COUNT] = {')
$sourceLines.Add('    ' + (($paletteXIndices | ForEach-Object { $_.ToString() }) -join ', '))
$sourceLines.Add('};')
$sourceLines.Add('')
$sourceLines.Add('const unsigned char wall_palette_y_indices[WALL_TEXTURE_COLOR_COUNT] = {')
$sourceLines.Add('    ' + (($paletteYIndices | ForEach-Object { $_.ToString() }) -join ', '))
$sourceLines.Add('};')

$utf8WithoutBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputSource)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputHeader)) | Out-Null
[System.IO.File]::WriteAllText($OutputSource, ($sourceLines -join "`n") + "`n", $utf8WithoutBom)
[System.IO.File]::WriteAllText($OutputHeader, $headerText.Replace("`r`n", "`n"), $utf8WithoutBom)

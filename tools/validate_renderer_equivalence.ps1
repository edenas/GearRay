param(
    [string]$BuildDirectory = "build"
)

$ErrorActionPreference = "Stop"
$videoPath = Join-Path $PSScriptRoot "..\platform\game_gear\video.c"
$texturePath = Join-Path $PSScriptRoot "..\$BuildDirectory\generated\wall_texture.c"
$textureHeaderPath = Join-Path $PSScriptRoot "..\$BuildDirectory\generated\wall_texture.h"
$video = Get-Content -Raw -LiteralPath $videoPath
$texture = Get-Content -Raw -LiteralPath $texturePath
$textureHeader = Get-Content -Raw -LiteralPath $textureHeaderPath

function Get-HexArray {
    param([string]$Source, [string]$Name)
    $match = [regex]::Match(
        $Source,
        "(?:static )?const unsigned (?:char|int) $Name\[[\s\S]*?= \{(?<values>[\s\S]*?)\n\};")
    if (-not $match.Success) { throw "Array not found: $Name" }
    return @(
        [regex]::Matches($match.Groups['values'].Value, '0x[0-9a-fA-F]+') |
            ForEach-Object { [Convert]::ToInt32($_.Value, 16) }
    )
}

function Get-IntegerArray {
    param([string]$Source, [string]$Name)
    $match = [regex]::Match(
        $Source,
        "(?:static )?const unsigned (?:char|int) $Name\[[\s\S]*?= \{(?<values>[\s\S]*?)\n\};")
    if (-not $match.Success) { throw "Array not found: $Name" }
    return @(
        [regex]::Matches($match.Groups['values'].Value, '0x[0-9a-fA-F]+|\b\d+\b') |
            ForEach-Object {
                if ($_.Value.StartsWith('0x')) {
                    [Convert]::ToInt32($_.Value, 16)
                }
                else {
                    [Convert]::ToInt32($_.Value, 10)
                }
            }
    )
}

function Decode-HalfRow {
    param([int[]]$Bytes, [int]$Offset, [bool]$Right)
    $pixels = @()
    for ($x = 0; $x -lt 4; ++$x) {
        $index = 0
        $bit = if ($Right) { 3 - $x } else { 7 - $x }
        for ($plane = 0; $plane -lt 4; ++$plane) {
            if (($Bytes[$Offset + $plane] -band (1 -shl $bit)) -ne 0) {
                $index = $index -bor (1 -shl $plane)
            }
        }
        $pixels += $index
    }
    return $pixels
}

function Test-EqualBytes {
    param([int[]]$Expected, [int[]]$Actual, [string]$Context)
    if ($Expected.Count -ne $Actual.Count) { throw "$Context length mismatch" }
    for ($index = 0; $index -lt $Expected.Count; ++$index) {
        if ($Expected[$index] -ne $Actual[$index]) {
            throw "$Context byte ${index}: expected $($Expected[$index]), got $($Actual[$index])"
        }
    }
}

$leftLod1X = @(Get-HexArray $video 'left_lod1_x_rows')
$rightLod1X = @(Get-HexArray $video 'right_lod1_x_rows')
$leftLod1Y = @(Get-HexArray $video 'left_lod1_y_rows')
$rightLod1Y = @(Get-HexArray $video 'right_lod1_y_rows')
$leftLod2 = @(Get-HexArray $video 'left_lod2_rows')
$rightLod2 = @(Get-HexArray $video 'right_lod2_rows')
$steps = @(Get-HexArray $texture 'wall_texture_steps')
$remainders = @(Get-HexArray $texture 'wall_texture_step_remainders')
$wallTextures = @(Get-HexArray $texture 'wall_textures')
$paletteColors = @(Get-HexArray $texture 'wall_palette_colors')
$paletteXIndices = @(Get-IntegerArray $texture 'wall_palette_x_indices')
$paletteYIndices = @(Get-IntegerArray $texture 'wall_palette_y_indices')

if ($textureHeader -notmatch '#define WALL_TEXTURE_COUNT 10' -or
    $textureHeader -notmatch '#define WALL_TEXTURE_COLOR_COUNT 10') {
    throw "Generated wall texture count contract mismatch"
}
Test-EqualBytes @(0x555, 0x777, 0xb80, 0x02b, 0x057, 0x265, 0x860,
                  0x566, 0x333, 0x961, 0x119, 0x396, 0x143, 0x641) `
                $paletteColors "wall palette"
Test-EqualBytes @(0, 2, 3, 4, 5, 6, 7, 8, 1, 13) `
                $paletteXIndices "X palette lookup"
Test-EqualBytes @(0, 10, 2, 11, 12, 6, 14, 15, 1, 13) `
                $paletteYIndices "Y palette lookup"
if ($wallTextures.Count -ne (10 * 32)) {
    throw "Expected ten 32-byte wall textures; got $($wallTextures.Count) bytes"
}

for ($textureId = 7; $textureId -le 10; ++$textureId) {
    $textureOffset = ($textureId - 1) * 32
    $indices = @()
    for ($byteIndex = 0; $byteIndex -lt 32; ++$byteIndex) {
        $packed = $wallTextures[$textureOffset + $byteIndex]
        $indices += ($packed -shr 4) -band 15
        $indices += $packed -band 15
    }

    $redCount = @($indices | Where-Object { $_ -eq 4 }).Count
    $greenCount = @($indices | Where-Object { $_ -eq 9 }).Count
    if ($textureId -le 8) {
        if ($redCount -eq 0 -or $greenCount -ne 0) {
            throw "Switch OFF texture ID $textureId is not red-only"
        }
    }
    elseif ($greenCount -eq 0 -or $redCount -ne 0) {
        throw "Switch ON texture ID $textureId is not green-only"
    }
}

# LOD1 must remain neutral under the current global palette layout.
foreach ($entry in @(
    @('left_lod1_x_rows', $leftLod1X, $false, @(2, 9)),
    @('right_lod1_x_rows', $rightLod1X, $true, @(2, 9)),
    @('left_lod1_y_rows', $leftLod1Y, $false, @(2, 10)),
    @('right_lod1_y_rows', $rightLod1Y, $true, @(2, 10))
)) {
    $name = $entry[0]
    $bytes = [int[]]$entry[1]
    $right = [bool]$entry[2]
    $allowed = [int[]]$entry[3]
    for ($row = 0; $row -lt 8; ++$row) {
        foreach ($pixel in @(Decode-HalfRow $bytes ($row * 4) $right)) {
            if ($pixel -notin $allowed) {
                throw "$name invalid index $pixel"
            }
        }
    }
}

# LOD2 preserves the reference renderer's ordered black/dark-grey/mid-grey mix.
foreach ($entry in @(
    @('left_lod2_rows', $leftLod2, $false),
    @('right_lod2_rows', $rightLod2, $true)
)) {
    $name = $entry[0]
    $bytes = [int[]]$entry[1]
    $right = [bool]$entry[2]
    for ($phase = 0; $phase -lt 2; ++$phase) {
        $allPixels = @()
        for ($row = 0; $row -lt 8; ++$row) {
            $pixels = @(Decode-HalfRow $bytes ($phase * 32 + $row * 4) $right)
            if (@($pixels | Where-Object { $_ -eq 0 }).Count -gt 1) {
                throw "$name phase $phase row $row has multiple background pixels"
            }
            if (@($pixels | Where-Object { $_ -ne 0 }).Count -lt 3) {
                throw "$name phase $phase row $row breaks the silhouette"
            }
            foreach ($pixel in $pixels) {
                if ($pixel -notin @(0, 2, 10)) { throw "$name invalid index $pixel" }
            }
            $allPixels += $pixels
        }
        $counts = @(
            @($allPixels | Where-Object { $_ -eq 0 }).Count,
            @($allPixels | Where-Object { $_ -eq 2 }).Count,
            @($allPixels | Where-Object { $_ -eq 10 }).Count
        )
        Test-EqualBytes @(4, 8, 20) $counts "$name phase $phase distribution"
    }
}

# Every oriented hit offset maps to the native 8-pixel column, byte and nibble.
for ($hitOffset = 0; $hitOffset -lt 256; ++$hitOffset) {
    $textureX = $hitOffset -shr 5
    $byteX = $hitOffset -shr 6
    $highNibble = ($hitOffset -band 0x20) -eq 0
    if ($textureX -ne [int][Math]::Floor($hitOffset / 32) -or
        $byteX -ne [int][Math]::Floor($textureX / 2) -or
        $highNibble -ne (($textureX -band 1) -eq 0)) {
        throw "Horizontal mapping mismatch at hit offset $hitOffset"
    }
}

# Exact carried-remainder sampling for all logical heights. Generated ROM tables
# cover the engine-reachable textured range 17..144.
for ($height = 1; $height -le 255; ++$height) {
    $step = [int][Math]::Floor(2048 / $height)
    $remainder = 2048 - $step * $height
    if ($height -ge 17 -and $height -le 144) {
        $tableIndex = $height - 17
        if ($steps[$tableIndex] -ne $step -or
            $remainders[$tableIndex] -ne $remainder) {
            throw "Sampler table mismatch at height $height"
        }
    }
    $position = 0
    $remainderPosition = 0
    for ($pixel = 0; $pixel -lt $height; ++$pixel) {
        $actualRow = $position -shr 8
        $expectedRow = [int][Math]::Floor(($pixel * 8) / $height)
        if ($actualRow -ne $expectedRow) {
            throw "Vertical mapping mismatch at height $height pixel $pixel"
        }
        $position += $step
        $remainderPosition += $remainder
        if ($remainderPosition -ge $height) {
            ++$position
            $remainderPosition -= $height
        }
    }
}

# The optimized byte bounds are equivalent to the original signed expression
# for the only path that reads them: centred flat walls with heights 1..16.
for ($height = 1; $height -le 16; ++$height) {
    $top = [int][Math]::Truncate((64 - $height) / 2)
    $bottom = $top + $height
    for ($screenY = 0; $screenY -lt 64; ++$screenY) {
        $reference = $screenY -ge $top -and $screenY -lt ($top + $height)
        $optimized = $screenY -ge ([byte]$top) -and $screenY -lt ([byte]$bottom)
        if ($reference -ne $optimized) {
            throw "Flat bound mismatch at height $height screen Y $screenY"
        }
    }
}

# Exhaustive native flat output for all left/right heights, sides, phases and
# viewport tile rows. This covers outside rows and 8/9 and 16/17 selection.
for ($leftHeight = 0; $leftHeight -le 17; ++$leftHeight) {
    for ($rightHeight = 0; $rightHeight -le 17; ++$rightHeight) {
        foreach ($leftSide in 0, 1) {
            foreach ($rightSide in 0, 1) {
                for ($phase = 0; $phase -lt 2; ++$phase) {
                    for ($tileY = 0; $tileY -lt 64; $tileY += 8) {
                        $referenceTile = @()
                        $optimizedTile = @()
                        for ($row = 0; $row -lt 8; ++$row) {
                            $screenY = $tileY + $row
                            $combinedReference = @(0, 0, 0, 0)
                            $combinedOptimized = @(0, 0, 0, 0)
                            foreach ($half in 0, 1) {
                                $height = if ($half -eq 0) { $leftHeight } else { $rightHeight }
                                $side = if ($half -eq 0) { $leftSide } else { $rightSide }
                                $top = [int][Math]::Truncate((64 - $height) / 2)
                                $visibleReference = $height -gt 0 -and $screenY -ge $top -and $screenY -lt ($top + $height)
                                $visibleOptimized = $height -gt 0 -and $screenY -ge ([byte]$top) -and $screenY -lt ([byte]($top + $height))
                                if ($visibleReference -ne $visibleOptimized) { throw "Native visibility mismatch" }
                                if ($height -le 8) {
                                    $table = if ($half -eq 0) { $leftLod2 } else { $rightLod2 }
                                    $offset = $phase * 32 + $row * 4
                                }
                                elseif ($height -le 16) {
                                    if ($half -eq 0) {
                                        $table = if ($side -eq 0) { $leftLod1X } else { $leftLod1Y }
                                    }
                                    else {
                                        $table = if ($side -eq 0) { $rightLod1X } else { $rightLod1Y }
                                    }
                                    $offset = $row * 4
                                }
                                else { continue }
                                if ($visibleReference) {
                                    for ($plane = 0; $plane -lt 4; ++$plane) {
                                        $combinedReference[$plane] = $combinedReference[$plane] -bor $table[$offset + $plane]
                                        $combinedOptimized[$plane] = $combinedOptimized[$plane] -bor $table[$offset + $plane]
                                    }
                                }
                            }
                            $referenceTile += $combinedReference
                            $optimizedTile += $combinedOptimized
                        }
                        Test-EqualBytes $referenceTile $optimizedTile "native flat tile"
                    }
                }
            }
        }
    }
}

# The cache is an exact seven-field signature. Model the runtime comparison and
# prove that every renderer-relevant field transition invalidates it, including
# both texture IDs, both LOD boundaries, and both wall-side flags. The fixed
# tile-column phase owner is not mutable signature state.
function Test-WallColumnUnchanged {
    param([int[]]$Previous, [int[]]$Candidate)

    if (($Previous[6] -band 0x80) -eq 0) {
        return $false
    }

    return $Previous[0] -eq $Candidate[0] -and
           $Previous[1] -eq $Candidate[1] -and
           $Previous[2] -eq $Candidate[2] -and
           $Previous[3] -eq $Candidate[3] -and
           $Previous[4] -eq $Candidate[4] -and
           $Previous[5] -eq $Candidate[5] -and
           ($Previous[6] -band 0x03) -eq ($Candidate[6] -band 0x03)
}

$boundaryHeights = @(0, 1, 7, 8, 9, 15, 16, 17, 32, 64, 127, 144, 255)
foreach ($leftHeight in $boundaryHeights) {
    foreach ($rightHeight in $boundaryHeights) {
        foreach ($leftOffset in @(0, 31, 32, 127, 255)) {
            foreach ($rightOffset in @(0, 31, 32, 127, 255)) {
                foreach ($sideFlags in @(0, 1, 2, 3)) {
                    $signature = @(
                        $leftHeight, $rightHeight,
                        $leftOffset, $rightOffset,
                        1, 1,
                        (0x80 -bor $sideFlags)
                    )
                    if (-not (Test-WallColumnUnchanged $signature $signature)) {
                        throw "Identical valid dirty signature was rejected"
                    }

                    for ($field = 0; $field -lt 6; ++$field) {
                        $changed = [int[]]$signature.Clone()
                        $changed[$field] = ($changed[$field] + 1) -band 0xFF
                        if (Test-WallColumnUnchanged $signature $changed) {
                            throw "Dirty signature failed to observe field $field"
                        }
                    }

                    $changedSide = [int[]]$signature.Clone()
                    $changedSide[6] = $changedSide[6] -bxor 1
                    if (Test-WallColumnUnchanged $signature $changedSide) {
                        throw "Dirty signature failed to observe left wall-side flag"
                    }

                    $changedSide[6] = $signature[6] -bxor 2
                    if (Test-WallColumnUnchanged $signature $changedSide) {
                        throw "Dirty signature failed to observe right wall-side flag"
                    }

                    $invalid = [int[]]$signature.Clone()
                    $invalid[6] = $invalid[6] -band 0x03
                    if (Test-WallColumnUnchanged $invalid $signature) {
                        throw "Dirty signature accepted an invalid cached column"
                    }
                }
            }
        }
    }
}

# Switch animation and activation must independently invalidate either half.
foreach ($transition in @(
    @(7, 8, 'OFF frame 1 to 2'),
    @(9, 10, 'ON frame 1 to 2'),
    @(7, 9, 'OFF to ON frame 1'),
    @(8, 10, 'OFF to ON frame 2')
)) {
    $before = [int[]]@(64, 64, 32, 32, $transition[0], 1, 0x80)
    $after = [int[]]$before.Clone()
    $after[4] = $transition[1]
    if (Test-WallColumnUnchanged $before $after) {
        throw "Left switch texture transition remained cached: $($transition[2])"
    }

    $before[4] = 1
    $before[5] = $transition[0]
    $after = [int[]]$before.Clone()
    $after[5] = $transition[1]
    if (Test-WallColumnUnchanged $before $after) {
        throw "Right switch texture transition remained cached: $($transition[2])"
    }
}

Write-Output "Renderer equivalence PASS"
Write-Output "- Candidate C rows/phases/halves and native combinations"
Write-Output "- hit offsets 0..255"
Write-Output "- vertical sampling heights 1..255; ROM tables 17..144"
Write-Output "- flat bounds and native tiles across LOD boundaries/clipping"
Write-Output "- exact seven-field dirty signature, texture transitions and boundaries"

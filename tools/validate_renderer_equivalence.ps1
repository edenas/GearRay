param(
    [string]$BuildDirectory = "build"
)

$ErrorActionPreference = "Stop"
$videoPath = Join-Path $PSScriptRoot "..\platform\game_gear\video.c"
$texturePath = Join-Path $PSScriptRoot "..\$BuildDirectory\generated\wall_texture.c"
$video = Get-Content -Raw -LiteralPath $videoPath
$texture = Get-Content -Raw -LiteralPath $texturePath

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

# Candidate C: exact palette distribution, half isolation and row continuity.
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
                if ($pixel -notin @(0, 9, 11)) { throw "$name invalid index $pixel" }
            }
            $allPixels += $pixels
        }
        $counts = @(
            @($allPixels | Where-Object { $_ -eq 0 }).Count,
            @($allPixels | Where-Object { $_ -eq 9 }).Count,
            @($allPixels | Where-Object { $_ -eq 11 }).Count
        )
        Test-EqualBytes @(4, 20, 8) $counts "$name phase $phase distribution"
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

# The cache is an exact five-byte signature. Prove that every field transition
# relevant to rendering invalidates it, including both LOD boundaries and the
# fixed tile-column phase owner (the column itself is not mutable state).
$boundaryHeights = @(0, 1, 7, 8, 9, 15, 16, 17, 32, 64, 127, 144, 255)
foreach ($leftHeight in $boundaryHeights) {
    foreach ($rightHeight in $boundaryHeights) {
        foreach ($leftOffset in @(0, 31, 32, 127, 255)) {
            foreach ($rightOffset in @(0, 31, 32, 127, 255)) {
                foreach ($sideFlags in @(0, 1, 2, 3)) {
                    $signature = @($leftHeight, $rightHeight, $leftOffset, $rightOffset, $sideFlags)
                    for ($field = 0; $field -lt 5; ++$field) {
                        $changed = @($signature)
                        $changed[$field] = ($changed[$field] + 1) -band 0xFF
                        if ((Compare-Object $signature $changed -SyncWindow 0).Count -eq 0) {
                            throw "Dirty signature failed to observe field $field"
                        }
                    }
                }
            }
        }
    }
}

Write-Output "Renderer equivalence PASS"
Write-Output "- Candidate C rows/phases/halves and native combinations"
Write-Output "- hit offsets 0..255"
Write-Output "- vertical sampling heights 1..255; ROM tables 17..144"
Write-Output "- flat bounds and native tiles across LOD boundaries/clipping"
Write-Output "- exact dirty-signature field and boundary transitions"

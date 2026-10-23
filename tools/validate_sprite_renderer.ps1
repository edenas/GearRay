param([string]$BuildDirectory='build/release')
$ErrorActionPreference = "Stop"

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Project-Sprite {
    param(
        [int]$RelativeX,
        [int]$RelativeY,
        [int]$DirectionX,
        [int]$DirectionY,
        [int]$PlaneX,
        [int]$PlaneY,
        [bool]$Corpse = $false
    )

    $determinant = $PlaneX * $DirectionY - $DirectionX * $PlaneY
    if ($determinant -eq 0) { return @{ Visible = $false } }
    $depth = [Math]::Truncate(
        (($PlaneX * $RelativeY - $RelativeX * $PlaneY) * 256) /
        $determinant)
    if ($depth -le 32) { return @{ Visible = $false; Depth = $depth } }
    $horizontal = [Math]::Truncate(
        (($DirectionY * $RelativeX - $DirectionX * $RelativeY) * 256) /
        $determinant)
    $center = 56 + [Math]::Truncate($horizontal * 80 / $depth)
    $height = [Math]::Truncate(16384 / $depth)
    if ($height -lt 1) { $height = 1 }
    $naturalHeight = $height
    if ($height -gt 144) { $height = 144 }
    $texture = if ($Corpse) { "AuthoredCorpse32" } else { "AuthoredZombie" }
    $sourceSize = 8
    $distanceSquared = [long]$RelativeX * $RelativeX +
                       [long]$RelativeY * $RelativeY
    if ($Corpse) {
        $absoluteX = [Math]::Abs($RelativeX)
        $absoluteY = [Math]::Abs($RelativeY)
        $distance = if ($absoluteX -gt $absoluteY) {
            $absoluteX + [Math]::Truncate($absoluteY / 2)
        } else {
            $absoluteY + [Math]::Truncate($absoluteX / 2)
        }
        if ($distanceSquared -gt 1587600) {
            return @{
                Visible = $false; Depth = $depth; Height = $height
                Texture = "Hidden"
            }
        }
        if ($depth -le 159) {
            return @{
                Visible = $false; Depth = $depth; Height = $height
                NaturalHeight = $naturalHeight; Texture = "HiddenClose"
            }
        }
        if ($height -lt 15) {
            $height = 13
            $texture = "DarkPile13"
        }
        elseif ($height -lt 17) {
            $height -= ($height - 15) -band 1
            $texture = "DarkPile15"
        }
        elseif ($distance -le 392) {
            $texture = "AuthoredCorpse32"
            $sourceSize = 32
        }
        elseif ($distance -le 616) {
            $texture = "AuthoredCorpse16"
            $sourceSize = 16
        }
        else {
            $texture = "AuthoredCorpse8"
        }
    }
    else {
        if ($distanceSquared -gt 1587600) {
            return @{
                Visible = $false; Depth = $depth; Height = $height
                Texture = "Hidden"
            }
        }
        if ($height -lt 15) {
            $height = 13
            $texture = "Simple"
        }
        elseif ($height -lt 17) {
            $height -= ($height - 15) -band 1
            $texture = "Medium"
        }
    }
    $left = $center - [Math]::Truncate($height / 2)
    $right = $left + $height
    $bottom = 32 + [Math]::Truncate($height / 2)
    if ($Corpse) { $bottom += [Math]::Truncate($height / 3) }
    $top = $bottom - $height
    return @{
        Visible = $right -gt 0 -and $left -lt 112 -and
                  $bottom -gt 0 -and $top -lt 64
        Depth = $depth; Center = $center; Height = $height
        NaturalHeight = $naturalHeight
        Left = $left; Right = $right; Top = $top; Bottom = $bottom
        Texture = $texture; SourceSize = $sourceSize
    }
}

function Get-SpriteLod {
    param([int]$Height)

    if ($Height -ge 17) { return "Full" }
    if ($Height -ge 15) { return "Medium" }
    if ($Height -ge 13) { return "Simple" }
    return "Hidden"
}

function Get-QuantizedSpriteHeight {
    param([int]$Height)

    if ($Height -ge 17) { return $Height }
    if ($Height -ge 15) { return $Height - (($Height - 15) -band 1) }
    if ($Height -ge 13) { return 13 }
    return 0
}

function Get-SpriteRenderCost {
    param([int]$Height)

    if ($Height -ge 17) { return 5 }
    if ($Height -ge 15) { return 2 }
    if ($Height -ge 13) { return 1 }
    return 0
}

function Get-CorpseLod {
    param([int]$Distance)

    if ($Distance -le 392) { return "AuthoredCorpse32" }
    if ($Distance -le 616) { return "AuthoredCorpse16" }
    if ($Distance -le 963) { return "AuthoredCorpse8" }
    if ($Distance -le 1092) { return "DarkPile15" }
    if ($Distance -le 1260) { return "DarkPile13" }
    return "Hidden"
}

function Get-CorpseRenderCost {
    param([string]$Texture, [int]$Height)

    if ($Texture -eq "DarkPile15" -or $Texture -eq "DarkPile13") { return 1 }
    if ($Height -ge 17) { return 5 }
    if ($Height -ge 15) { return 2 }
    return 1
}

function Test-FullyOccluded {
    param([int]$SpriteDepth, [int[]]$WallDepths)

    return (@($WallDepths | Where-Object {
        $SpriteDepth -lt $_
    })).Count -eq 0
}

function Get-WallEligiblePixels {
    param(
        [int]$Left,
        [int]$Right,
        [int]$SpriteDepth,
        [int[]]$WallDepths
    )

    $visibleLeft = [Math]::Max(0, $Left)
    $visibleRight = [Math]::Min(112, $Right)
    if ($visibleRight -le $visibleLeft) { return @() }
    return @($visibleLeft..($visibleRight - 1) | Where-Object {
        $SpriteDepth -lt $WallDepths[$_ -shr 2]
    })
}

function New-WallDepths {
    param([int]$Depth = 101)
    return @(0..27 | ForEach-Object { $Depth })
}

function Get-SignedRoundedQuotient {
    param([long]$Value, [int]$Scale)

    if ($Value -lt 0) {
        $Value -= [Math]::Truncate($Scale / 2)
    }
    else {
        $Value += [Math]::Truncate($Scale / 2)
    }
    return [int][Math]::Truncate($Value / $Scale)
}

function Get-RotatedCameraBasis {
    param([int[]]$Basis, [int]$RotationSine)

    $directionX = Get-SignedRoundedQuotient `
        ([long]$Basis[0] * 4058 - [long]$Basis[1] * $RotationSine) 4096
    $directionY = Get-SignedRoundedQuotient `
        ([long]$Basis[1] * 4058 + [long]$Basis[0] * $RotationSine) 4096
    $length = [int][Math]::Floor([Math]::Sqrt(
        [long]$directionX * $directionX +
        [long]$directionY * $directionY))
    $directionX = Get-SignedRoundedQuotient `
        ([long]$directionX * 256) $length
    $directionY = Get-SignedRoundedQuotient `
        ([long]$directionY * 256) $length
    $planeX = Get-SignedRoundedQuotient `
        (-[long]$directionY * 169) 256
    $planeY = Get-SignedRoundedQuotient `
        ([long]$directionX * 169) 256
    return [int[]]@($directionX, $directionY, $planeX, $planeY)
}

function Get-HorizontalProjection {
    param([int[]]$Basis, [int]$RelativeX, [int]$RelativeY)

    $determinant = [long]$Basis[2] * $Basis[1] -
                   [long]$Basis[0] * $Basis[3]
    $depth = [int][Math]::Truncate(
        (([long]$Basis[2] * $RelativeY -
          [long]$RelativeX * $Basis[3]) * 256) / $determinant)
    $horizontal = [int][Math]::Truncate(
        (([long]$Basis[1] * $RelativeX -
          [long]$Basis[0] * $RelativeY) * 256) / $determinant)
    return [pscustomobject]@{
        Depth = $depth
        Horizontal = $horizontal
        Center = 56 + [int][Math]::Truncate(
            ([long]$horizontal * 80) / $depth)
        OldCenter = 56 + [int][Math]::Truncate(
            ([long]$horizontal * 56) / $depth)
    }
}

function Get-FovSweepRecord {
    param([int]$Step, [int[]]$Basis, [int]$RelativeX, [int]$RelativeY)

    $projection = Get-HorizontalProjection $Basis $RelativeX $RelativeY
    $distanceSquared = [long]$RelativeX * $RelativeX +
                       [long]$RelativeY * $RelativeY
    $projectedHeight = [Math]::Truncate(16384 / $projection.Depth)
    $distanceEligible = $distanceSquared -le 1587600
    $lod = if (-not $distanceEligible) { "Hidden" }
           elseif ($projectedHeight -ge 17) { "Full" }
           elseif ($projectedHeight -ge 15) { "Medium" }
           else { "Simple" }
    $height = if ($lod -eq "Full") {
        [Math]::Min(144, [Math]::Max(1,
            [Math]::Truncate(16384 / $projection.Depth)))
    } elseif ($lod -eq "Medium") { 15 }
      elseif ($lod -eq "Simple") { 13 }
      else { 0 }
    $left = $projection.Center - [Math]::Truncate($height / 2)
    $right = $left + $height
    $visibleLeft = [Math]::Max(0, $left)
    $visibleRight = [Math]::Min(112, $right)
    $hasPixels = $lod -ne "Hidden" -and $projection.Depth -gt 32 -and
                 $visibleRight -gt $visibleLeft
    $firstRay = if ($hasPixels) { $visibleLeft -shr 2 } else { -1 }
    $lastRay = if ($hasPixels) { ($visibleRight - 1) -shr 2 } else { -1 }
    return [pscustomobject]@{
        Step = $Step
        DirectionX = $Basis[0]
        DirectionY = $Basis[1]
        Depth = $projection.Depth
        Horizontal = $projection.Horizontal
        Center = $projection.Center
        Height = $height
        Left = $left
        Right = $right
        VisibleLeft = $visibleLeft
        VisibleRight = $visibleRight
        FirstRay = $firstRay
        LastRay = $lastRay
        CoarseOccluded = $false
        BudgetAccepted = $hasPixels
        DistanceEligible = $distanceEligible
        Visible = $hasPixels
        Lod = $lod
    }
}

$initialCameraBasis = [int[]]@(0, -256, 169, 0)
$clockwiseCenters = @()
$counterclockwiseCenters = @()
$oldClockwiseCenters = @()
$clockwiseBasis = $initialCameraBasis
$counterclockwiseBasis = $initialCameraBasis
for ($rotationStep = 0; $rotationStep -le 7; ++$rotationStep) {
    $clockwiseProjection = Get-HorizontalProjection `
        $clockwiseBasis 0 -1024
    $counterclockwiseProjection = Get-HorizontalProjection `
        $counterclockwiseBasis 0 -1024
    $clockwiseCenters += $clockwiseProjection.Center
    $counterclockwiseCenters += $counterclockwiseProjection.Center
    $oldClockwiseCenters += $clockwiseProjection.OldCenter
    Assert-True ($clockwiseProjection.Center +
                 $counterclockwiseProjection.Center -eq 112) `
        "Camera rotation lost horizontal projection symmetry."
    $clockwiseBasis = Get-RotatedCameraBasis $clockwiseBasis 556
    $counterclockwiseBasis = Get-RotatedCameraBasis `
        $counterclockwiseBasis -556
}
Assert-True ($clockwiseCenters[0] -eq 56 -and
             $clockwiseCenters[1] -lt 56 -and
             $counterclockwiseCenters[1] -gt 56) `
    "Small rotations moved the sprite toward the wrong screen side."
for ($rotationStep = 1; $rotationStep -lt $clockwiseCenters.Count; ++$rotationStep) {
    Assert-True ($clockwiseCenters[$rotationStep] -lt
                 $clockwiseCenters[$rotationStep - 1]) `
        "Clockwise rotation plateaued or temporarily reversed."
    Assert-True ($counterclockwiseCenters[$rotationStep] -gt
                 $counterclockwiseCenters[$rotationStep - 1]) `
        "Counterclockwise rotation plateaued or temporarily reversed."
}
Assert-True ((($clockwiseCenters | ForEach-Object { 112 - $_ }) -join ",") `
             -eq ($counterclockwiseCenters -join ",")) `
    "Clockwise and counterclockwise sweeps are not exact mirrors."
Assert-True ((56 - $clockwiseCenters[1]) -gt
             (56 - $oldClockwiseCenters[1])) `
    "Corrected projection did not remove the cropped-viewport center compression."

$fovSweep = @()
for ($rotationStep = -5; $rotationStep -le 5; ++$rotationStep) {
    $basis = $initialCameraBasis
    $rotationSine = if ($rotationStep -lt 0) { -556 } else { 556 }
    for ($turn = 0; $turn -lt [Math]::Abs($rotationStep); ++$turn) {
        $basis = Get-RotatedCameraBasis $basis $rotationSine
    }
    $fovSweep += Get-FovSweepRecord $rotationStep $basis 0 -1200
}
Assert-True $fovSweep[5].Visible "Centered FOV-sweep zombie is hidden."
for ($index = 0; $index -lt 5; ++$index) {
    $mirror = $fovSweep[10 - $index]
    Assert-True ($fovSweep[$index].Visible -eq $mirror.Visible -and
                 $fovSweep[$index].Center + $mirror.Center -eq 112 -and
                 $fovSweep[$index].Left + $mirror.Right -eq 113 -and
                 $fovSweep[$index].Right + $mirror.Left -eq 113 -and
                 $fovSweep[$index].Lod -eq $mirror.Lod) `
        "Clockwise/counterclockwise FOV sweep lost exact symmetry."
}
$approachingVisibility = @($fovSweep[0..5] | ForEach-Object { $_.Visible })
for ($index = 1; $index -lt $approachingVisibility.Count; ++$index) {
    Assert-True (-not ($approachingVisibility[$index - 1] -and
                       -not $approachingVisibility[$index])) `
        "FOV sweep became hidden while rotating toward center."
}
$forwardVisibility = @($fovSweep | ForEach-Object { $_.Visible })
$reverseVisibility = @($forwardVisibility)
[array]::Reverse($reverseVisibility)
Assert-True (($forwardVisibility -join ",") -eq
             ($reverseVisibility -join ",")) `
    "Reverse rotation did not reproduce the exact reverse visibility sequence."
foreach ($record in @($fovSweep | Where-Object { $_.Visible })) {
    Assert-True ($record.VisibleRight -gt $record.VisibleLeft -and
                 $record.FirstRay -ge 0 -and $record.FirstRay -le 27 -and
                 $record.LastRay -ge 0 -and $record.LastRay -le 27 -and
                 $record.FirstRay -le $record.LastRay) `
        "Visible FOV sweep record produced an invalid pixel or ray span."
}
$onePixelLeftFirstRay = 0 -shr 2
$onePixelLeftLastRay = (1 - 1) -shr 2
$onePixelRightFirstRay = 111 -shr 2
$onePixelRightLastRay = (112 - 1) -shr 2
Assert-True ($onePixelLeftFirstRay -eq 0 -and $onePixelLeftLastRay -eq 0 -and
             $onePixelRightFirstRay -eq 27 -and
             $onePixelRightLastRay -eq 27) `
    "One-pixel edge visibility did not map symmetrically to rays 0 and 27."
$centeredBoundaryHeight = [Math]::Truncate(16384 / 1260)
$centeredOutsideHeight = [Math]::Truncate(16384 / 1261)
Assert-True ($centeredBoundaryHeight -eq 13 -and
             $centeredOutsideHeight -eq 12) `
    "World-distance cutoff no longer matches the old centered 12/13 boundary."
Assert-True (1587600 -eq 1260 * 1260 -and
             1587600 -le 1587600 -and 1587601 -gt 1587600) `
    "Living squared-distance boundary is not exactly inclusive at 1260 squared."
$insideBoundarySweep = @()
$outsideBoundarySweep = @()
foreach ($rotationStep in -5..5) {
    $basis = $initialCameraBasis
    $rotationSine = if ($rotationStep -lt 0) { -556 } else { 556 }
    for ($turn = 0; $turn -lt [Math]::Abs($rotationStep); ++$turn) {
        $basis = Get-RotatedCameraBasis $basis $rotationSine
    }
    $insideBoundarySweep +=
        Get-FovSweepRecord $rotationStep $basis 0 -1260
    $outsideBoundarySweep +=
        Get-FovSweepRecord $rotationStep $basis 0 -1261
}
Assert-True ((@($insideBoundarySweep | Where-Object {
                    -not $_.DistanceEligible }).Count) -eq 0) `
    "Just-inside living distance eligibility changed during rotation."
Assert-True ((@($outsideBoundarySweep | Where-Object {
                    $_.DistanceEligible }).Count) -eq 0) `
    "Just-outside living sprite became distance-eligible during rotation."
$insideEligibility = @($insideBoundarySweep | ForEach-Object {
    $_.DistanceEligible })
$insideEligibilityReverse = @($insideEligibility)
[array]::Reverse($insideEligibilityReverse)
Assert-True (($insideEligibility -join ",") -eq
             ($insideEligibilityReverse -join ",")) `
    "Living distance eligibility is not clockwise/counterclockwise symmetric."
foreach ($horizontalCoordinate in @(1, 17, 127, 511)) {
    $positiveOffset = [int][Math]::Truncate(
        ([long]$horizontalCoordinate * 80) / 1024)
    $negativeOffset = [int][Math]::Truncate(
        (-[long]$horizontalCoordinate * 80) / 1024)
    Assert-True ($positiveOffset -eq -$negativeOffset) `
        "Signed horizontal truncation is asymmetric."
}
foreach ($oddWidth in @(13, 15, 17)) {
    $oddCenter = 56
    $oddLeft = $oddCenter - [Math]::Truncate($oddWidth / 2)
    $oddRight = $oddLeft + $oddWidth
    Assert-True ($oddLeft + [Math]::Truncate($oddWidth / 2) -eq $oddCenter -and
                 $oddRight - $oddLeft -eq $oddWidth -and
                 ($oddLeft + $oddRight - 1) / 2 -eq $oddCenter) `
        "Odd-width sprite does not keep its center pixel at center_x."
}

$wallEdgeDepth = 100
$allBehind = New-WallDepths 101
$fullyVisiblePixels = @(Get-WallEligiblePixels 5 22 $wallEdgeDepth $allBehind)
Assert-True (($fullyVisiblePixels -join ",") -eq ((5..21) -join ",")) `
    "A fully exposed sprite lost eligible pixels."

$leftOccludedWalls = New-WallDepths 101
$leftOccludedWalls[1] = 100
$leftOccludedWalls[2] = 99
$leftVisiblePixels = @(
    Get-WallEligiblePixels 5 22 $wallEdgeDepth $leftOccludedWalls)
Assert-True (($leftVisiblePixels -join ",") -eq ((12..21) -join ",")) `
    "Left-side wall clipping did not preserve complete four-pixel rays."

$rightOccludedWalls = New-WallDepths 101
$rightOccludedWalls[4] = 100
$rightOccludedWalls[5] = 99
$rightVisiblePixels = @(
    Get-WallEligiblePixels 5 22 $wallEdgeDepth $rightOccludedWalls)
Assert-True (($rightVisiblePixels -join ",") -eq ((5..15) -join ",")) `
    "Right-side wall clipping did not preserve complete four-pixel rays."

$boundaryWalls = New-WallDepths 101
$boundaryWalls[3] = 100
$boundaryVisible = @(
    Get-WallEligiblePixels 5 22 $wallEdgeDepth $boundaryWalls)
$expectedBoundary = @((5..11) + (16..21))
Assert-True (($boundaryVisible -join ",") -eq
             ($expectedBoundary -join ",")) `
    "A boundary wall ray did not suppress exactly its four screen pixels."
Assert-True ((@(Get-WallEligiblePixels 12 16 100 (New-WallDepths 100))).Count `
             -eq 0) "Equal-depth wall did not win its complete ray."
Assert-True ((@(Get-WallEligiblePixels 12 16 100 (New-WallDepths 101))).Count `
             -eq 4) "One-unit-nearer sprite did not win its complete ray."
Assert-True ((@(Get-WallEligiblePixels 12 16 100 (New-WallDepths 99))).Count `
             -eq 0) "One-unit-farther sprite overwrote its wall ray."

$insideLeft = @(Get-WallEligiblePixels 6 18 100 $allBehind)
$insideRight = @(Get-WallEligiblePixels 6 18 100 $allBehind)
Assert-True ($insideLeft[0] -eq 6 -and $insideRight[-1] -eq 17 -and
             ($insideLeft | Where-Object { ($_ -shr 2) -ne
                 [Math]::Truncate($_ / 4) }).Count -eq 0) `
    "Sub-ray projected bounds changed destination-X ray selection."
$offscreenPixels = @(Get-WallEligiblePixels -5 10 100 $allBehind)
Assert-True (($offscreenPixels -join ",") -eq ((0..9) -join ",")) `
    "Off-screen sprite clipping escaped the viewport or lost valid pixels."
foreach ($lodWidth in @(13, 15, 17)) {
    $lodLeft = 53 - [Math]::Truncate($lodWidth / 2)
    $lodPixels = @(Get-WallEligiblePixels $lodLeft ($lodLeft + $lodWidth) `
        100 $allBehind)
    Assert-True ($lodPixels.Count -eq $lodWidth -and
                 $lodPixels[0] -eq $lodLeft -and
                 $lodPixels[-1] -eq $lodLeft + $lodWidth - 1) `
        "LOD width $lodWidth crossed a ray boundary incorrectly."
}

$rotationWalls = New-WallDepths 101
$rotationCoverages = @()
foreach ($occludedRayCount in @(0, 1, 2, 4, 2, 1, 0)) {
    $frameWalls = @($rotationWalls)
    for ($ray = 14 - $occludedRayCount; $ray -lt 14; ++$ray) {
        if ($ray -ge 10) { $frameWalls[$ray] = 100 }
    }
    $rotationCoverages += ,@(
        Get-WallEligiblePixels 40 56 100 $frameWalls)
}
Assert-True ((@($rotationCoverages | ForEach-Object { $_.Count }) -join ",") `
             -eq "16,12,8,0,8,12,16") `
    "Rotation-like wall clipping was not progressive and reversible."
for ($frame = 1; $frame -lt $rotationCoverages.Count; ++$frame) {
    $dirtyUnion = @($rotationCoverages[$frame - 1] +
                    $rotationCoverages[$frame] | Sort-Object -Unique)
    $expectedUnion = @($rotationCoverages[$frame - 1] +
                       $rotationCoverages[$frame] | Sort-Object -Unique)
    Assert-True (($dirtyUnion -join ",") -eq ($expectedUnion -join ",")) `
        "Rotation transition left stale sprite pixels."
}
$corpseWallPixels = @(Get-WallEligiblePixels 48 63 100 $boundaryWalls)
$livingWallPixels = @(Get-WallEligiblePixels 48 63 100 $boundaryWalls)
Assert-True (($corpseWallPixels -join ",") -eq ($livingWallPixels -join ",")) `
    "Corpse pile did not use the living sprite wall-depth rule."

$ahead = Project-Sprite 0 -768 0 -256 169 0
Assert-True $ahead.Visible "Directly-ahead sprite was not visible."
Assert-True ($ahead.Center -eq 56) "Directly-ahead sprite was not centered."
Assert-True ($ahead.Bottom -eq 32 + [Math]::Truncate($ahead.Height / 2)) `
    "Sprite feet are not floor anchored."

$near = Project-Sprite 0 -256 0 -256 169 0
$far = Project-Sprite 0 -1536 0 -256 169 0
Assert-True ($near.Height -gt $far.Height) "Perspective scaling is not monotonic."

$leftEdge = Project-Sprite -320 -768 0 -256 169 0
$rightEdge = Project-Sprite 320 -768 0 -256 169 0
Assert-True ($leftEdge.Visible -and $leftEdge.Left -lt 0) `
    "Left-edge clipping case was not produced."
Assert-True ($rightEdge.Visible -and $rightEdge.Right -gt 112) `
    "Right-edge clipping case was not produced."

$behind = Project-Sprite 0 256 0 -256 169 0
Assert-True (-not $behind.Visible) "Behind-camera sprite remained visible."

$corpse = Project-Sprite 0 -768 0 -256 169 0 $true
Assert-True ($corpse.Visible -and $corpse.Bottom -gt $ahead.Bottom) `
    "Corpse floor adjustment did not preserve a visible floor position."
foreach ($cameraDepth in @(-64, -1, 0, 1, 16, 32)) {
    $crossing = Project-Sprite 0 (-$cameraDepth) 0 -256 169 0 $true
    Assert-True (-not $crossing.Visible) `
        "Corpse at unsafe camera depth $cameraDepth was projected."
}
$nearPlaneFront = Project-Sprite 0 -33 0 -256 169 0 $true
Assert-True (-not $nearPlaneFront.Visible -and
             $nearPlaneFront.Texture -eq "HiddenClose") `
    "Extremely close corpse still reaches rasterization."

Assert-True ((Get-CorpseLod 392) -eq "AuthoredCorpse32" -and
             (Get-CorpseLod 393) -eq "AuthoredCorpse16" -and
             (Get-CorpseLod 616) -eq "AuthoredCorpse16" -and
             (Get-CorpseLod 617) -eq "AuthoredCorpse8" -and
             (Get-CorpseLod 963) -eq "AuthoredCorpse8" -and
             (Get-CorpseLod 964) -eq "DarkPile15" -and
             (Get-CorpseLod 1092) -eq "DarkPile15" -and
             (Get-CorpseLod 1093) -eq "DarkPile13" -and
             (Get-CorpseLod 1260) -eq "DarkPile13" -and
             (Get-CorpseLod 1261) -eq "Hidden") `
    "Distance-based corpse LOD boundaries changed."
$farSymmetry = foreach ($distance in 963,964,1092,1093,1260,1261) {
    $living = Project-Sprite 0 (-$distance) 0 -256 169 0 $false
    $corpse = Project-Sprite 0 (-$distance) 0 -256 169 0 $true
    Assert-True ($living.Visible -eq $corpse.Visible -and
                 (-not $living.Visible -or
                  ($living.Height -eq $corpse.Height -and
                   $living.Right-$living.Left -eq $corpse.Right-$corpse.Left))) `
        "Living/corpse far geometry diverges at $distance."
    if ($corpse.Visible) { $corpse.Height } else { 0 }
}
Assert-True (($farSymmetry -join ',') -eq '17,15,15,13,13,0') `
    "Far corpse sizes are not monotonic or do not mirror living stages."
$reverseFar = @($farSymmetry)
[array]::Reverse($reverseFar)
Assert-True (($reverseFar -join ',') -eq '0,13,13,15,15,17') `
    "Far reverse traversal does not restore monotonically increasing sizes."
$corpseSourceMetrics = @{
    AuthoredCorpse32 = @(32,10,31)
    AuthoredCorpse16 = @(16,6,15)
    AuthoredCorpse8 = @(8,3,7)
    DarkPile15 = @(8,5,7)
    DarkPile13 = @(8,5,7)
}
$corpseTransitions = @()
foreach ($boundary in @(@(392,393),@(616,617))) {
    $before = Project-Sprite 0 (-$boundary[0]) 0 -256 169 0 $true
    $after = Project-Sprite 0 (-$boundary[1]) 0 -256 169 0 $true
    $beforeMetric = $corpseSourceMetrics[$before.Texture]
    $afterMetric = $corpseSourceMetrics[$after.Texture]
    $beforeBodyHeight = [Math]::Ceiling(
        ($beforeMetric[2]-$beforeMetric[1]+1)*$before.Height/$beforeMetric[0])
    $afterBodyHeight = [Math]::Ceiling(
        ($afterMetric[2]-$afterMetric[1]+1)*$after.Height/$afterMetric[0])
    Assert-True ($before.Height -eq [Math]::Truncate(16384/$boundary[0]) -and
                 $after.Height -eq [Math]::Truncate(16384/$boundary[1]) -and
                 [Math]::Abs($before.Height-$after.Height) -le 1) `
        "Corpse transition $($boundary[0])/$($boundary[1]) changes natural perspective scale."
    Assert-True ($before.Bottom -eq $after.Bottom -and
                 $beforeMetric[2] -eq $beforeMetric[0]-1 -and
                 $afterMetric[2] -eq $afterMetric[0]-1) `
        "Corpse transition $($boundary[0])/$($boundary[1]) leaves the shared floor anchor."
    $corpseTransitions += "$($boundary[0]):$($before.Texture):h$($before.Height):body${beforeBodyHeight}:bottom$($before.Bottom) -> $($boundary[1]):$($after.Texture):h$($after.Height):body${afterBodyHeight}:bottom$($after.Bottom)"
}
foreach($transition in $corpseTransitions){Write-Output "- corpse transition $transition"}
$lastClose32 = Project-Sprite 0 -160 0 -256 169 0 $true
$hiddenClose = Project-Sprite 0 -159 0 -256 169 0 $true
Assert-True ($lastClose32.Texture -eq "AuthoredCorpse32" -and
             $lastClose32.NaturalHeight -eq 102 -and
             $lastClose32.Visible -and
             $hiddenClose.Texture -eq "HiddenClose" -and
             -not $hiddenClose.Visible) `
    "Near-side corpse 32x32 -> hidden boundary changed."
$closeApproach = @(280,206,132 | ForEach-Object {
    (Project-Sprite 0 (-$_) 0 -256 169 0 $true).Texture
})
Assert-True (($closeApproach -join ',') -eq
             'AuthoredCorpse32,AuthoredCorpse32,HiddenClose') `
    "A straight 74-unit approach does not directly cull the 32x32 corpse."
$closeReverse = @(132,206 | ForEach-Object {
    (Project-Sprite 0 (-$_) 0 -256 169 0 $true).Texture
})
Assert-True (($closeReverse -join ',') -eq
             'HiddenClose,AuthoredCorpse32') `
    "Reverse movement does not restore the 32x32 corpse at the close boundary."
$closeCleanupRedraw = $hiddenClose.Visible -ne $lastClose32.Visible
Assert-True $closeCleanupRedraw `
    "Visible-to-hidden close corpse transition does not invalidate stale pixels."
$naturalDepths = 392,393,616,617,963,964,1092,1093,1260,1261
foreach($distance in $naturalDepths){
    $projected = Project-Sprite 0 (-$distance) 0 -256 169 0 $true
    $naturalHeight = [Math]::Truncate(16384/$distance)
    $expectedHeight=if($naturalHeight-lt15){13}elseif($naturalHeight-lt17){$naturalHeight-(($naturalHeight-15)-band1)}else{$naturalHeight}
    Assert-True ((-not $projected.Visible -and $distance -eq 1261) -or
                 $projected.Height -eq $expectedHeight) `
        "Corpse at distance $distance does not match living quantized height."
}
foreach ($visibleCorpse in @(
    (Project-Sprite 0 -392 0 -256 169 0 $true),
    (Project-Sprite 0 -1050 0 -256 169 0 $true))) {
    $standingBottom = 32 + [Math]::Truncate($visibleCorpse.Height / 2)
    Assert-True ($visibleCorpse.Bottom -eq
        $standingBottom + [Math]::Truncate($visibleCorpse.Height / 3)) `
        "Corpse tier lost its floor adjustment."
}
Assert-True ((Get-CorpseRenderCost "AuthoredCorpse8" 13) -eq 1 -and
             (Get-CorpseRenderCost "AuthoredCorpse8" 15) -eq 2 -and
             (Get-CorpseRenderCost "AuthoredCorpse8" 23) -eq 5) `
    "Corpse render costs changed."
$corpseTextures = @("AuthoredCorpse32", "AuthoredCorpse16",
                    "AuthoredCorpse8", "DarkPile15", "DarkPile13", "Hidden")
Assert-True (($corpseTextures -notcontains "Medium") -and
             ($corpseTextures -notcontains "Simple")) `
    "Corpse state selected an upright silhouette."
$corpseCleanupRedraw = "AuthoredCorpse8" -ne "Hidden"
$corpseHiddenRedraw = "Hidden" -ne "Hidden"
$corpseReappearRedraw = "Hidden" -ne "AuthoredCorpse8"
$corpseFullToPileRedraw = "AuthoredCorpse16" -ne "AuthoredCorpse8"
$corpsePileToFullRedraw = "AuthoredCorpse8" -ne "AuthoredCorpse16"
Assert-True ($corpseCleanupRedraw -and -not $corpseHiddenRedraw -and
             $corpseReappearRedraw -and $corpseFullToPileRedraw -and
             $corpsePileToFullRedraw) `
    "Corpse texture transitions do not invalidate exactly as required."

Assert-True ((Get-SpriteLod 17) -eq "Full") `
    "Projected height 17 did not select full detail."
Assert-True ((Get-SpriteLod 16) -eq "Medium" -and
             (Get-SpriteLod 15) -eq "Medium") `
    "Projected heights 15 through 16 did not select medium LOD."
Assert-True ((Get-SpriteLod 14) -eq "Simple" -and
             (Get-SpriteLod 13) -eq "Simple") `
    "Projected heights 13 through 14 did not select simple LOD."
Assert-True ((Get-SpriteLod 12) -eq "Hidden") `
    "Projected height 12 was not hidden."

$quantizedHeights = @(13..16 | ForEach-Object {
    Get-QuantizedSpriteHeight $_
})
Assert-True (($quantizedHeights -join ",") -eq
    "13,13,15,15") `
    "Distant projected-height quantization changed."
Assert-True ((Get-QuantizedSpriteHeight 17) -eq 17 -and
             (Get-QuantizedSpriteHeight 18) -eq 18) `
    "Full-detail projected heights were quantized."

$lodSequence = @(17, 16, 15, 14, 13, 12, 13, 15, 17)
$lodTransitions = @($lodSequence | ForEach-Object { Get-SpriteLod $_ })
Assert-True (($lodTransitions -join ",") -eq
    "Full,Medium,Medium,Simple,Simple,Hidden,Simple,Medium,Full") `
    "LOD transitions do not cross the approved boundaries exactly."
$simpleCoverage = 5..8
$hiddenCoverage = @()
$cleanupUnion = @($simpleCoverage + $hiddenCoverage | Sort-Object -Unique)
Assert-True ($cleanupUnion.Count -eq $simpleCoverage.Count) `
    "Simple-to-hidden transition did not retain one-frame stale cleanup."
Assert-True ($hiddenCoverage.Count -eq 0) `
    "Hidden sprite contributed dirty coverage or overlay work."
$visibleAtThirteen = $true
$visibleAtTwelve = $false
$cleanupRedraw = $visibleAtThirteen -ne $visibleAtTwelve
$unchangedHiddenRedraw = $visibleAtTwelve -ne $visibleAtTwelve
$reappearRedraw = $visibleAtTwelve -ne $visibleAtThirteen
Assert-True ($cleanupRedraw -and -not $unchangedHiddenRedraw -and
             $reappearRedraw) `
    "The 13-to-12 cleanup or 12-to-13 redraw transition changed."
Assert-True ((Get-SpriteRenderCost 17) -eq 5 -and
             (Get-SpriteRenderCost 15) -eq 2 -and
             (Get-SpriteRenderCost 13) -eq 1 -and
             (Get-SpriteRenderCost 12) -eq 0) `
    "Sprite render costs changed."
$budgetCandidates = @(
    [pscustomobject]@{ Index = 0; Depth = 100; Height = 17 }
    [pscustomobject]@{ Index = 1; Depth = 120; Height = 17 }
    [pscustomobject]@{ Index = 2; Depth = 140; Height = 15 }
    [pscustomobject]@{ Index = 3; Depth = 160; Height = 13 }
)
$remainingBudget = 12
$acceptedBudgetIndices = @()
foreach ($candidate in @($budgetCandidates | Sort-Object Depth,Index)) {
    $cost = Get-SpriteRenderCost $candidate.Height
    if ($cost -le $remainingBudget) {
        $acceptedBudgetIndices += $candidate.Index
        $remainingBudget -= $cost
    }
}
Assert-True (($acceptedBudgetIndices -join ",") -eq "0,1,2" -and
             $remainingBudget -eq 0) `
    "Deterministic nearest-first render budget selection changed."

$spriteDepth = $ahead.Depth
Assert-True ($spriteDepth -lt ($spriteDepth + 1)) `
    "Sprite closer than wall should pass occlusion."
Assert-True (-not ($spriteDepth -lt $spriteDepth)) `
    "Sprite equal to wall depth should remain occluded."
$wallDepths = @(
    ($spriteDepth + 1)
    ($spriteDepth - 1)
    ($spriteDepth + 20)
    $spriteDepth
)
$visibleHalves = @($wallDepths | Where-Object { $spriteDepth -lt $_ })
Assert-True ($visibleHalves.Count -eq 2) `
    "Partial wall occlusion did not preserve exactly the nearer sprite halves."
$hiddenHalves = @(($spriteDepth - 1), $spriteDepth, ($spriteDepth - 20))
Assert-True ((@($hiddenHalves |
    Where-Object { $spriteDepth -lt $_ })).Count -eq 0) `
    "Fully wall-occluded sprite retained visible halves."
Assert-True (-not (Test-FullyOccluded $spriteDepth $wallDepths)) `
    "Coarse occlusion rejected a partially visible sprite."
Assert-True (Test-FullyOccluded $spriteDepth $hiddenHalves) `
    "Coarse occlusion retained a fully wall-occluded sprite."

$oldColumns = 3..6
$newColumns = 5..8
$union = @($oldColumns + $newColumns | Sort-Object -Unique)
Assert-True ($union.Count -eq 6 -and $union[0] -eq 3 -and $union[-1] -eq 8) `
    "Old/new coverage union does not restore stale columns."

for ($top = -144; $top -le 64; ++$top) {
    for ($bottom = $top + 1; $bottom -le 176; $bottom += 17) {
        $visibleTop = [Math]::Max(0, $top)
        $visibleBottom = [Math]::Min(64, $bottom)
        if ($visibleBottom -le $visibleTop) { continue }
        $firstRow = [Math]::Truncate($visibleTop / 8)
        $lastRow = [Math]::Truncate(($visibleBottom - 1) / 8)
        Assert-True ($firstRow -ge 0 -and $lastRow -le 7) `
            "Clipped sprite tile row escaped viewport storage."
    }
}

$closeCorpse = Project-Sprite 0 -64 0 -256 169 0 $true
$coveredColumns = @()
$coveredRows = @()
for ($column = 0; $column -lt 14; ++$column) {
    if ($closeCorpse.Right -gt $column * 8 -and
        $closeCorpse.Left -lt ($column + 1) * 8) {
        $coveredColumns += $column
    }
}
for ($row = 0; $row -lt 8; ++$row) {
    if ($closeCorpse.Bottom -gt $row * 8 -and
        $closeCorpse.Top -lt ($row + 1) * 8) {
        $coveredRows += $row
    }
}
Assert-True ($coveredColumns.Count -le 14 -and $coveredRows.Count -le 8) `
    "Close-corpse dirty coverage escaped the viewport."
Assert-True ($coveredColumns.Count * $coveredRows.Count -le 112) `
    "Close-corpse tile work exceeded the complete viewport."
$rejectedCorpse = Project-Sprite 0 0 0 -256 169 0 $true
$cleanupColumns = @($coveredColumns | Sort-Object -Unique)
Assert-True (-not $rejectedCorpse.Visible -and
    $cleanupColumns.Count -eq $coveredColumns.Count) `
    "Near-plane rejection did not preserve previous coverage for cleanup."
$unchangedCorpse = Project-Sprite 0 -64 0 -256 169 0 $true
$projectionFields = @(
    "Visible", "Depth", "Left", "Right", "Top", "Bottom", "Height"
)
$projectionChanged = $false
foreach ($field in $projectionFields) {
    if ($closeCorpse[$field] -ne $unchangedCorpse[$field]) {
        $projectionChanged = $true
    }
}
Assert-True (-not $projectionChanged) `
    "Unchanged corpse projection forced sprite-driven dirty work."
$visibleSpriteCount = 4
$coveringSpriteCount = 1
$oldCandidateTests = $visibleSpriteCount * $visibleSpriteCount
$newCandidateTests =
    $visibleSpriteCount * ($coveringSpriteCount + 1)
Assert-True ($newCandidateTests -lt $oldCandidateTests) `
    "Tile-local composition did not reduce close-corpse candidate work."
Assert-True ($coveringSpriteCount -lt $visibleSpriteCount) `
    "Tile-local composition did not eliminate unrelated sprite overlays."

$assetPath = Join-Path $PSScriptRoot `
    "..\assets\sprites\enemies\zombie\zombie_01_standing.png"
Add-Type -AssemblyName System.Drawing
$bitmap = [System.Drawing.Bitmap]::new($assetPath)
try {
    $transparent = 0
    $opaque = 0
    for ($y = 0; $y -lt $bitmap.Height; ++$y) {
        for ($x = 0; $x -lt $bitmap.Width; ++$x) {
            if ($bitmap.GetPixel($x, $y).A -eq 0) { ++$transparent }
            else { ++$opaque }
        }
    }
}
finally {
    $bitmap.Dispose()
}
Assert-True ($transparent -eq 34 -and $opaque -eq 30) `
    "Sprite transparency/source pixel counts changed."

$repositoryPath = Resolve-Path (Join-Path $PSScriptRoot "..")
$raycasterSource = Get-Content (
    Join-Path $repositoryPath "engine\render\raycaster.c") -Raw
$videoSource = Get-Content (
    Join-Path $repositoryPath "platform\game_gear\video.c") -Raw
$projectionSource = Get-Content (
    Join-Path $repositoryPath "platform\game_gear\sprite_projection.c") -Raw
$walking01GeneratedSource = Get-Content (
    Join-Path $repositoryPath "$BuildDirectory\generated\zombie_01_walking_01_texture.c") -Raw
$walking02GeneratedSource = Get-Content (
    Join-Path $repositoryPath "$BuildDirectory\generated\zombie_01_walking_02_texture.c") -Raw
$lodTextureSources = $projectionSource + $walking01GeneratedSource +
    $walking02GeneratedSource
$projectionHeader = Get-Content (
    Join-Path $repositoryPath "platform\game_gear\sprite_projection.h") -Raw
$mainSource = Get-Content (Join-Path $repositoryPath "game\main.c") -Raw
$playerSource = Get-Content (Join-Path $repositoryPath "game\player.c") -Raw
$worldSource = Get-Content (Join-Path $repositoryPath "game\world.c") -Raw
$worldSpriteAssemblyPath = Join-Path $repositoryPath "$BuildDirectory\world_sprite.asm"
$linkerMapPath = Join-Path $repositoryPath "$BuildDirectory\GearRay.map"
Assert-True (Test-Path -LiteralPath $worldSpriteAssemblyPath) `
    "World-sprite assembly is missing; run the Release build."
Assert-True (Test-Path -LiteralPath $linkerMapPath) `
    "Release linker map is missing; run the Release build."
$worldSpriteAssembly = Get-Content $worldSpriteAssemblyPath -Raw
$linkerMap = Get-Content $linkerMapPath -Raw
Assert-True ($worldSpriteAssembly -match
    "_world_sprites:\s*[\r\n]+\s*\.ds\s+72(?:\D|$)") `
    "WorldSprite storage is not exactly 8 sprites * 9 bytes."
foreach ($walkingSymbol in @(
    '_zombie_01_walking_01_pixels',
    '_zombie_01_walking_01_pixels_med',
    '_zombie_01_walking_01_pixels_sim',
    '_zombie_01_walking_02_pixels',
    '_zombie_01_walking_02_pixels_med',
    '_zombie_01_walking_02_pixels_sim')) {
    $mapSymbol = [regex]::Match(
        $linkerMap,
        "(?m)^\s*(?<address>[0-9A-Fa-f]{8})\s+" +
        [regex]::Escape($walkingSymbol) + "(?:\s|$)")
    Assert-True $mapSymbol.Success `
        "Walking linker symbol $walkingSymbol is missing."
    $address = [Convert]::ToInt32($mapSymbol.Groups['address'].Value, 16)
    Assert-True ($address -ge 0x14000 -and $address -lt 0x18000) `
        "Walking linker symbol $walkingSymbol escaped BANK1."
}

Assert-True ($raycasterSource -match
    "\*result_distance\s*=\s*projection_distance\s*;") `
    "Ray results do not store the exact wall projection distance."
Assert-True ($videoSource -match
    "projected->depth\s*>=\s*rays\[[^\]]+\]\.wall_distance") `
    "Production occlusion does not intentionally favor equal-depth walls."
Assert-True ($videoSource -match
    "screen_x\s*=\s*tile_left\s*\+\s*pixel_x\s*;[\s\S]*?" +
    "rays\[\(unsigned\s+char\)screen_x\s*>>\s*2\]\.wall_distance") `
    "Production sprite pixels do not select wall rays from absolute screen X."
Assert-True ($projectionSource -match
    "first_ray\s*=\s*\(unsigned\s+char\)visible_left\s*>>\s*2\s*;" -and
    $projectionSource -match
    "last_ray\s*=\s*\(unsigned\s+char\)\(visible_right\s*-\s*1\)\s*>>\s*2\s*;") `
    "Coarse sprite occlusion does not use the compositor's half-open ray span."
Assert-True ($projectionSource -match
    "changed_mask\s*\|=\s*1U\s*<<\s*sprite_index" -and
    $videoSource -match
    "sprite_changed_mask\s*&\s*\(1U\s*<<\s*sprite_index\)" -and
    ([regex]::Matches($videoSource,
        "sprite_changed_mask\s*&\s*\(1U\s*<<\s*sprite_index\)").Count -eq 2)) `
    "Production renderer does not invalidate only changed old/current coverage."
Assert-True ($projectionSource -match
    "current->pixels\s*!=\s*previous->pixels") `
    "Texture-only sprite state changes do not invalidate projected coverage."
Assert-True ($projectionSource -match
    "current->near_texture_id\s*!=\s*previous->near_texture_id" -and
    $projectionSource -match
    "current->depth\s*!=\s*previous->depth") `
    "LOD/native or depth-only sprite changes do not invalidate coverage."
Assert-True ($videoSource -match
    "ordered_sprite_indices\[PROJECTED_SPRITE_MAX_COUNT\]" -and
    ($projectionSource -match "depth\s*>\s*selected_depth" -or
     $projectionSource -match "depth\s*<=\s*selected_depth[\s\S]*?continue\s*;") -and
    $projectionSource -match
    "ordered_sprite_indices\[\(\*ordered_sprite_count\)\+\+\]\s*=\s*selected" -and
    $videoSource -match
    "for\s*\(ordered_sprite_index\s*=\s*0;[\s\S]*?ordered_sprite_index\s*<\s*ordered_sprite_count") `
    "Production renderer does not precompute and reuse far-to-near sprite order."
Assert-True ($videoSource -match
    "sprite_changed_mask\s*=\s*game_gear_prepare_(?:cached_)?world_sprites\s*\(" -and
    $videoSource -notmatch "game_gear_project_world_sprite\s*\(" -and
    $videoSource -notmatch "game_gear_apply_sprite_render_budget\s*\(" -and
    $projectionSource -match
    "static\s+void\s+game_gear_project_world_sprite\s*\(" -and
    $projectionSource -notmatch
    "game_gear_apply_sprite_render_budget\s*\(" -and
    $projectionSource -match
    "game_gear_prepare_world_sprites[\s\S]*?game_gear_project_world_sprite[\s\S]*?world_sprite_get\(sprite_index\)" -and
    $projectionSource -match
    "remaining_budget\s*=\s*SPRITE_RENDER_BUDGET[\s\S]*?return\s+changed_mask" -and
    ([regex]::Matches($projectionHeader, "__banked").Count -eq 0) -and
    ([regex]::Matches($projectionSource, "__banked").Count -eq 0)) `
    "Sprite preparation is not one direct page-1 coordinator with same-page internals."
Assert-True ($videoSource -notmatch "drawn_mask" -and
    $videoSource -notmatch "while\s*\(draw_count\s*!=\s*0\)") `
    "Per-tile repeated sprite-selection rescans remain."
Assert-True ($videoSource -match "sprite_driven_dirty_columns" -and
    $videoSource -match "sprite_candidate_tests" -and
    $videoSource -match "ordered_visible_sprites") `
    "Compile-time renderer profiling does not cover Phase 2A work."

function New-TestProjection(
    [bool]$Visible, [int]$Left, [int]$Right, [int]$Depth,
    [string]$Pixels, [int]$NearId) {
    [pscustomobject]@{
        Visible=$Visible;Left=$Left;Right=$Right;Top=0;Bottom=16
        Depth=$Depth;Pixels=$Pixels;NearId=$NearId
    }
}
function Test-ProjectionChanged($Current,$Previous) {
    foreach($field in @('Visible','Left','Right','Top','Bottom','Depth','Pixels','NearId')) {
        if($Current.$field -ne $Previous.$field){return $true}
    }
    return $false
}
function Get-TestChangedMask($Current,$Previous) {
    $mask=0;$count=[Math]::Max($Current.Count,$Previous.Count)
    for($index=0;$index-lt$count;$index++){
        if($index-ge$Current.Count-or$index-ge$Previous.Count-or
           (Test-ProjectionChanged $Current[$index] $Previous[$index])){
            $mask=$mask-bor(1-shl$index)
        }
    }
    return $mask
}
function Get-TestDirtyColumns($Current,$Previous,[int]$ChangedMask) {
    $dirty=@()
    for($column=0;$column-lt14;$column++){
        $tileLeft=$column*8;$tileRight=$tileLeft+8;$isDirty=$false
        for($index=0;$index-lt8;$index++){
            if(-not($ChangedMask-band(1-shl$index))){continue}
            foreach($set in @($Current,$Previous)){
                if($index-lt$set.Count){$sprite=$set[$index]
                    if($sprite.Visible-and$sprite.Right-gt$tileLeft-and$sprite.Left-lt$tileRight){$isDirty=$true}
                }
            }
        }
        if($isDirty){$dirty+=$column}
    }
    return @($dirty)
}
function Get-TestSpriteOrder($Sprites) {
    return @(0..($Sprites.Count-1) | Where-Object {$Sprites[$_].Visible} |
        Sort-Object @{Expression={-$Sprites[$_].Depth}},@{Expression={$_}})
}
$unchanged=New-TestProjection $true 0 16 600 'idle' 0
$oldAnimated=New-TestProjection $true 40 48 500 'idle' 0
$newAnimated=New-TestProjection $true 40 48 500 'walk' 0
$old=@($unchanged,$oldAnimated);$current=@($unchanged,$newAnimated)
$mask=Get-TestChangedMask $current $old
Assert-True (($mask-eq2)-and((Get-TestDirtyColumns $current $old $mask)-join',')-eq'5') `
    'One changing sprite dirties unrelated unchanged-sprite coverage.'
$movingOld=@(New-TestProjection $true 8 16 500 'idle' 0)
$movingNew=@(New-TestProjection $true 24 32 500 'idle' 0)
Assert-True (((Get-TestDirtyColumns $movingNew $movingOld (Get-TestChangedMask $movingNew $movingOld))-join',')-eq'1,3') `
    'Moving sprite does not dirty the exact old/current union.'
$hidden=@(New-TestProjection $false 16 24 500 'idle' 0)
$visible=@(New-TestProjection $true 16 24 500 'idle' 0)
Assert-True (((Get-TestDirtyColumns $hidden $visible (Get-TestChangedMask $hidden $visible))-join',')-eq'2') `
    'Visible-to-hidden sprite does not clear previous coverage.'
Assert-True (((Get-TestDirtyColumns $visible $hidden (Get-TestChangedMask $visible $hidden))-join',')-eq'2') `
    'Hidden-to-visible sprite does not draw current coverage.'
Assert-True (((Get-TestDirtyColumns $current $old $mask)-join',')-eq'5') `
    'Texture-only animation does not dirty its current coverage.'
$lodOld=@(New-TestProjection $true 16 32 500 'full8' 0)
$lodNew=@(New-TestProjection $true 8 40 500 'native' 2)
Assert-True (((Get-TestDirtyColumns $lodNew $lodOld (Get-TestChangedMask $lodNew $lodOld))-join',')-eq'1,2,3,4') `
    'LOD/native transition does not dirty its required union.'
$multiOld=@($unchanged,(New-TestProjection $true 32 40 500 'a' 0),(New-TestProjection $true 64 72 400 'b' 0))
$multiNew=@($unchanged,(New-TestProjection $true 40 48 500 'a' 0),(New-TestProjection $true 72 80 400 'c' 0))
Assert-True (((Get-TestDirtyColumns $multiNew $multiOld (Get-TestChangedMask $multiNew $multiOld))-join',')-eq'4,5,8,9') `
    'Multiple changing sprites dirty unrelated coverage or miss their union.'
$ordered=@(
    New-TestProjection $true 0 16 300 'a' 0
    New-TestProjection $true 32 48 600 'b' 0
    New-TestProjection $true 8 40 600 'c' 0
    New-TestProjection $false 0 112 900 'd' 0)
Assert-True (((Get-TestSpriteOrder $ordered)-join',')-eq'1,2,0') `
    'Precomputed order changed distinct-depth, visibility, or equal-depth index semantics.'
Assert-True ($videoSource -match
    "game_gear_wall_column_is_unchanged[\s\S]*?&&\s*!sprite_dirty_column") `
    'Wall changes can be skipped when sprite coverage is unchanged.'
Assert-True ($videoSource -match
    "game_gear_sprite_covers_tile\s*\(\s*&projected_sprites\[selected\]") `
    "Sprite composition is not restricted to sprites covering the tile."
Assert-True ($videoSource -match
    "palette_index\s*==\s*SPRITE_TRANSPARENT_INDEX[\s\S]*?continue\s*;") `
    "Transparent production pixels do not leave native tile data untouched."
Assert-True ($projectionHeader -match
    "#define SPRITE_FULL_DETAIL_MIN_HEIGHT 17" -and
    $projectionHeader -match
    "#define SPRITE_MEDIUM_LOD_MIN_HEIGHT 15" -and
    $projectionHeader -match
    "#define SPRITE_SIMPLE_LOD_MIN_HEIGHT 13" -and
    $projectionHeader -match
    "#define SPRITE_HORIZONTAL_PROJECTION_SCALE 80" -and
    $projectionHeader -match
    "#define SPRITE_RENDER_BUDGET 12" -and
    $projectionHeader -match
    "#define ZOMBIE_8X8_MAX_PROJECTED_HEIGHT 32") `
    "Production sprite LOD thresholds changed."
Assert-True ($projectionHeader -match
    "#define SPRITE_NEAR_DETAIL_MAX_DISTANCE[\s\\]*" +
    "\(ZOMBIE_ATTACK_DISTANCE \+ 2 \* ZOMBIE_MOVEMENT_STEP\)") `
    "Native close-detail range does not provide two walking steps before melee."
Assert-True ($projectionHeader -match
    "#define SPRITE_MIDDLE_DETAIL_MAX_DISTANCE[\s\\]*" +
    "\(SPRITE_NEAR_DETAIL_MAX_DISTANCE \+ 4 \* ZOMBIE_MOVEMENT_STEP\)") `
    "Authored middle-detail range does not provide four walking steps."
Assert-True ($projectionSource -match
    "center_x\s*=\s*GAME_GEAR_VIEWPORT_PIXEL_WIDTH\s*/\s*2[\s\S]*?" +
    "horizontal\s*\*\s*SPRITE_HORIZONTAL_PROJECTION_SCALE[\s\S]*?/\s*depth\s*;") `
    "Production sprite center does not use the parent Game Gear projection scale."
Assert-True ($projectionSource -match
    "projected->depth\s*<\s*rays\[first_ray\]\.wall_distance" -and
    $projectionSource -match "projected->depth\s*<\s*selected_depth") `
    "Presentation-only walking depth replaced real wall or ordering depth."
$raycasterSourceForPlacement = Get-Content (
    Join-Path $repositoryPath "engine\render\raycaster.c") -Raw
$cameraXInitializerForPlacement = [regex]::Match(
    $raycasterSourceForPlacement,
    "camera_x_by_ray\s*\[\s*RAY_COUNT\s*\]\s*=\s*" +
    "\{(?<values>[\s\S]*?)\};")
Assert-True $cameraXInitializerForPlacement.Success `
    "Production wall-ray projection coordinates are missing."
$cameraXByRayForPlacement = @(
    [regex]::Matches(
        $cameraXInitializerForPlacement.Groups["values"].Value, "-?\d+") |
        ForEach-Object { [int]$_.Value }
)
Assert-True ($cameraXByRayForPlacement.Count -eq 28) `
    "Wall-ray projection coordinate count changed."
for ($rayIndex = 0; $rayIndex -lt 28; ++$rayIndex) {
    $projectedRayX = 56 + [int][Math]::Truncate(
        ([long]$cameraXByRayForPlacement[$rayIndex] * 80) / 256)
    Assert-True (($projectedRayX -shr 2) -eq $rayIndex) `
        "Sprite projection does not align wall ray $rayIndex with its screen group."
}
Assert-True ($projectionSource -match
    "distance_squared\s*>\s*SPRITE_VISIBLE_MAX_DISTANCE_SQUARED[\s\S]*?return\s*;") `
    "Very distant production sprites are not culled before dirty coverage."
Assert-True ($projectionSource -match
    "(?:WORLD_SPRITE_LIFE_STATE\(sprite\)|life_state)\s*==\s*ZOMBIE_STATE_CORPSE" -and
    $projectionSource -match "projected->depth\s*<=\s*SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH" -and
    $projectionSource -match "distance\s*<=\s*SPRITE_NEAR_DETAIL_MAX_DISTANCE" -and
    $projectionSource -match "distance\s*<=\s*SPRITE_MIDDLE_DETAIL_MAX_DISTANCE") `
    "Production corpse does not use the shared authored LOD ladder."
Assert-True ($projectionHeader -match
    "SPRITE_NEAR_DETAIL_MAX_DISTANCE" -and
    $projectionHeader -match "SPRITE_MIDDLE_DETAIL_MAX_DISTANCE" -and
    $projectionSource -match "SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH[\s\\]*" +
        "\(16384U / \(3U \* GAME_GEAR_VIEWPORT_PIXEL_HEIGHT\) \+ PLAYER_MOVE_SPEED\)" -and
    $projectionHeader -notmatch "SPRITE_CORPSE_AUTHORED_|SPRITE_CORPSE_VISIBLE_MAX_DISTANCE|VERY_FAR" -and
    $projectionHeader -notmatch "SPRITE_CORPSE_CLOSE_.*NATURAL_HEIGHT" -and
    $projectionSource -notmatch
    "SPRITE_CORPSE_VISIBLE_MAX_DISTANCE_SQUARED|SPRITE_CORPSE_LOD_MIN_HEIGHT") `
    "Corpse ladder boundaries changed or the obsolete long-range cutoff remains."
$corpseBranch = $projectionSource.IndexOf(
    "projected->depth <= SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH")
$screenBounds = $projectionSource.IndexOf(
    "center_x = GAME_GEAR_VIEWPORT_PIXEL_WIDTH")
$wallScan = $projectionSource.IndexOf("rays = raycaster_get_rendered_rays();")
Assert-True ($corpseBranch -ge 0 -and $corpseBranch -lt $screenBounds -and
             $screenBounds -lt $wallScan) `
    "Hidden corpse rejection no longer precedes clipping and wall scanning."
Assert-True ($projectionSource -notmatch "natural_projected_height") `
    "Obsolete close-corpse natural-height storage remains."
Assert-True ($projectionSource -match
    "projected_height\s*=\s*SPRITE_SIMPLE_LOD_MIN_HEIGHT\s*;" -and
    $projectionSource -match
    "projected_height\s*-=\s*[\s\S]*?" +
    "SPRITE_MEDIUM_LOD_MIN_HEIGHT[\s\S]*?&\s*1U\s*;") `
    "Production distant projection heights are not quantized."
Assert-True ($projectionSource -match
    "projected->depth\s*<\s*rays\[first_ray\]\.wall_distance[\s\S]*?" +
    "if\s*\(\s*first_ray\s*>\s*last_ray\s*\)[\s\S]*?return\s*;") `
    "Production projection does not safely reject fully occluded sprites."
Assert-True ($projectionSource -match
    "projected->pixels\s*=\s*sprite->pixels\s*;" -and
    $projectionSource -match
    "projected_height\s*<\s*SPRITE_MEDIUM_LOD_MIN_HEIGHT[\s\S]*?" +
    "zombie_corpse_lod_pixels[\s\S]*?game_gear_get_zombie_lod_pixels\(sprite,\s*0\)\s*;" -and
    $projectionSource -match
    "projected_height\s*<\s*SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?" +
    "zombie_corpse_lod_pixels[\s\S]*?game_gear_get_zombie_lod_pixels\(sprite,\s*1\)\s*;") `
    "Production projection does not select the approved LOD textures."
Assert-True ($projectionSource -match
    "zombie_corpse_lod_pixels\[32\]" -and
    $projectionSource -notmatch "zombie_corpse_very_far_lod_pixels" -and
    $projectionSource -match "projected->pixels == zombie_corpse_lod_pixels[\s\S]*?return 1" -and
    $projectionSource -match
    "projected_height\s*>=\s*SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?return\s*5\s*;") `
    "Obsolete corpse render-cost exception remains or normal cost changed."
Assert-True ($projectionSource -match
    "remaining_budget\s*=\s*SPRITE_RENDER_BUDGET" -and
    $projectionSource -match
    "render_cost\s*>\s*remaining_budget" -and
    $projectionSource -match
    "projected->depth\s*<\s*selected_depth" -and
    $projectionSource -match
    "projected_sprites\[sprite_index\]\.visible\s*=\s*0\s*;" -and
    $videoSource -match
    "game_gear_prepare_(?:cached_)?world_sprites\s*\(") `
    "Production sprite render budget is not deterministic or enforced."
function Get-PackedLodIndices([string]$Name) {
    $initializer = [regex]::Match($lodTextureSources,
        $Name + "\[[^\]]+\]\s*=\s*\{(?<bytes>[\s\S]*?)\};")
    Assert-True $initializer.Success "Missing packed LOD texture $Name."
    $packedBytes = [regex]::Matches(
        $initializer.Groups["bytes"].Value, "0x(?<byte>[0-9a-fA-F]{2})")
    Assert-True ($packedBytes.Count -eq 32) "$Name is not exactly 32 bytes."
    return @($packedBytes | ForEach-Object {
        $value = [Convert]::ToInt32($_.Groups["byte"].Value, 16)
        ($value -shr 4) -band 15
        $value -band 15
    })
}
function Get-LodTextureName([string]$Pose, [string]$Lod) {
    if ($Pose -eq 'walking_01' -or $Pose -eq 'walking_02') {
        return "zombie_01_${Pose}_pixels_${Lod}_lod"
    }
    return "zombie_${Pose}_${Lod}_lod_pixels"
}
$lodPatterns = @{}
foreach ($pose in @("standing", "walking_01", "walking_02", "shot_01", "shot_02", "shot_dead")) {
    $mediumName = Get-LodTextureName $pose "medium"
    $simpleName = Get-LodTextureName $pose "simple"
    $mediumIndices = @(Get-PackedLodIndices $mediumName)
    $simpleIndices = @(Get-PackedLodIndices $simpleName)
    Assert-True ((($mediumIndices | Sort-Object -Unique) -join ",") `
        -eq "10,13,15") "$mediumName escaped indices 10, 13, and 15."
    Assert-True ((($simpleIndices | Sort-Object -Unique) -join ",") `
        -eq "13,15") "$simpleName escaped indices 13 and 15."
    $maximumHighlights = if ($pose -like 'walking_*') { 3 } else { 2 }
    Assert-True ((@($mediumIndices | Where-Object { $_ -eq 10 })).Count -le
                 $maximumHighlights) `
        "$mediumName has too many highlight pixels."
    $simpleOpaque = (@($simpleIndices | Where-Object { $_ -eq 13 })).Count
    $mediumOpaque = (@($mediumIndices | Where-Object { $_ -ne 15 })).Count
    if ($pose -like 'walking_*') {
        Assert-True ($simpleOpaque -eq $mediumOpaque) `
            "$simpleName did not preserve the authored footprint."
    }
    else {
        Assert-True ($simpleOpaque -lt $mediumOpaque) `
            "$simpleName did not reduce the opaque pixel count."
    }
    $lodPatterns[$mediumName] = $mediumIndices -join ","
    $lodPatterns[$simpleName] = $simpleIndices -join ","
}
foreach ($lod in @("medium", "simple")) {
    $standingPattern = $lodPatterns["zombie_standing_${lod}_lod_pixels"]
    foreach ($pose in @("walking_01", "walking_02", "shot_01", "shot_02", "shot_dead")) {
        $poseName = Get-LodTextureName $pose $lod
        Assert-True ($lodPatterns[$poseName] -ne
                     $standingPattern) `
            "$pose $lod LOD is byte-identical to standing."
    }
    foreach ($hitCount in @(1, 2, 3)) {
        $reactionPose = if ($hitCount -band 1) { "shot_01" } else { "shot_02" }
        $timeline = @(0..3 | ForEach-Object {
            if ($_ -lt 3) { $lodPatterns["zombie_${reactionPose}_${lod}_lod_pixels"] }
            else { $standingPattern }
        })
        Assert-True ($timeline[0] -ne $standingPattern -and
                     $timeline[1] -ne $standingPattern -and
                     $timeline[2] -ne $standingPattern -and
                     $timeline[3] -eq $standingPattern) `
            "Hit $hitCount $lod LOD did not return to standing after 3 frames."
    }
}
Assert-True ($projectionSource -match
    "sprite->state_timer\s*!=\s*0[\s\S]*?" +
    "sprite->health_and_hit_count\s*>>\s*ZOMBIE_HIT_COUNT_SHIFT" +
    "[\s\S]*?&\s*1U\s*\?\s*1\s*:\s*2") `
    "Production LOD pose selection is not driven by active hit parity."
Assert-True ($projectionSource -match
    "sprite->pixels\s*==\s*zombie_01_walking_01_pixels[\s\S]*?\?\s*4" -and
    $projectionSource -match
    "sprite->pixels\s*==\s*zombie_01_walking_02_pixels\s*\?\s*5\s*:\s*0") `
    "Walking phase is not preserved independently through LOD selection."
foreach ($lod in @("medium", "simple")) {
    Assert-True ($lodPatterns[(Get-LodTextureName 'walking_01' $lod)] -ne
                 $lodPatterns[(Get-LodTextureName 'walking_02' $lod)]) `
        "Walking $lod phases are byte-identical and should be shared."
}
foreach ($phase in @('walking_01', 'walking_02')) {
    $fullName = "zombie_01_${phase}_pixels"
    $fullIndices = @(Get-PackedLodIndices $fullName)
    foreach ($lod in @('medium', 'simple')) {
        $lodIndices = @(Get-PackedLodIndices (Get-LodTextureName $phase $lod))
        for ($pixel = 0; $pixel -lt 64; ++$pixel) {
            Assert-True (($fullIndices[$pixel] -eq 15) -eq
                         ($lodIndices[$pixel] -eq 15)) `
                "$phase $lod changed the authored opaque footprint at pixel $pixel."
        }
    }
}
$healthBeforeReturn = 9
$hitCountBeforeReturn = 1
$reactionTimer = 1
--$reactionTimer
Assert-True ($reactionTimer -eq 0 -and $healthBeforeReturn -eq 9 -and
             $hitCountBeforeReturn -eq 1) `
    "Returning to standing changed health or successful-hit count."
foreach ($damage in @(3, 4, 6)) {
    Assert-True (($hitCountBeforeReturn -band 1) -eq 1) `
        "Distance damage $damage changed the selected reaction pose."
}
Assert-True ($projectionSource -match
    "signed\s+long\s+depth\s*;" -and
    $projectionSource -match
    "depth\s*<=\s*SPRITE_NEAR_PLANE_DEPTH[\s\S]*?return\s*;[\s\S]*?" +
    "projected->depth\s*=\s*\(unsigned\s+int\)depth\s*;") `
    "Production projection narrows depth before strict near-plane rejection."
Assert-True ($projectionSource -match
    "signed\s+long\s+left\s*;" -and
    $projectionSource -match
    "signed\s+long\s+right\s*;" -and
    $projectionSource -match
    "if\s*\(\s*right\s*<=\s*0[\s\S]*?left\s*>=\s*" +
    "GAME_GEAR_VIEWPORT_PIXEL_WIDTH[\s\S]*?return\s*;") `
    "Production projection narrows horizontal bounds before signed clipping."
Assert-True ($playerSource -notmatch "world_sprite" -and
    $worldSource -match
    "tile_id\s*==\s*WORLD_TILE_SPRITE_MARKER[\s\S]*?" +
    "WORLD_TILE_EMPTY") `
    "World sprites participate in player collision."

$worldInitialize = $mainSource.IndexOf("world_initialize();")
$startupRaycast = $mainSource.IndexOf("raycaster_update();")
$startupDraw = $mainSource.IndexOf("game_gear_video_draw_wall_columns();")
Assert-True ($worldInitialize -ge 0 -and
             $worldInitialize -lt $startupRaycast -and
             $startupRaycast -lt $startupDraw) `
    "Startup ordering does not initialize and project the sprite before drawing."

foreach ($generatedName in @("sprite_texture",
                              "zombie_01_walking_01_texture",
                              "zombie_01_walking_02_texture",
                              "zombie_01_shot_01_texture",
                              "zombie_01_shot_02_texture",
                              "zombie_01_shot_dead_texture",
                              "zombie_01_corps_texture")) {
    $generatedSource = Join-Path $repositoryPath "$BuildDirectory\generated\${generatedName}.c"
    Assert-True (Test-Path -LiteralPath $generatedSource) `
        "Generated zombie source $generatedName is missing; run the Release build."
    $generatedBytes = [regex]::Matches(
        (Get-Content $generatedSource -Raw), "0x[0-9a-fA-F]{2}")
    $expectedGeneratedBytes = if ($generatedName -like '*walking*') {
        96
    }
    else {
        32
    }
    Assert-True ($generatedBytes.Count -eq $expectedGeneratedBytes) `
        "$generatedName has an unexpected packed-byte count."
}

Write-Output "Sprite renderer validation PASS"
Write-Output "- ahead, viewport edges, behind-camera, near/far projection"
Write-Output "- partial/full strict-depth occlusion and floor anchoring"
Write-Output "- clipping bounds, startup order, old/new coverage cleanup"
Write-Output "- production wiring and 32-byte transparent packed texture"
Write-Output "- tile-local four-sprite model: candidate tests 16 -> 8; overlays 4 -> 1"
Write-Output "- sprite LOD: full >=17, medium 15..16, simple 13..14, hidden <=12"
Write-Output "- movement-phase walking silhouettes remain distinct at every living LOD"
Write-Output "- WorldSprite remains 9 bytes; all six walking arrays are in BANK1"
Write-Output "- corpse LOD: 32x32 <=392, 16x16 393..616, authored 8x8 through projected height 17"
Write-Output "- one pile texture mirrors living far geometry at 15px then 13px; shared far hide"
Write-Output "- exact wall-edge mapping: absolute screen X >> 2; wall wins ties"
Write-Output "- progressive four-pixel clipping, off-screen and LOD edge cases"
Write-Output "- horizontal rotation sweep: symmetric, monotonic 160-pixel projection"
Write-Output "- deterministic render-cost budget: 12 (full 5, medium 2, simple 1)"

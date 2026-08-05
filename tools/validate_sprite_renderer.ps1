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
    if ($height -gt 144) { $height = 144 }
    $texture = if ($Corpse) { "AuthoredCorpse" } else { "AuthoredZombie" }
    if ($Corpse) {
        if ($height -lt 15) {
            return @{
                Visible = $false; Depth = $depth; Height = $height
                Texture = "Hidden"
            }
        }
        if ($height -lt 17) {
            $height = 15
            $texture = "CorpsePile"
        }
    }
    else {
        if ($height -lt 13) {
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
        Left = $left; Right = $right; Top = $top; Bottom = $bottom
        Texture = $texture
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
    param([int]$Height)

    if ($Height -ge 17) { return "FullCorpse" }
    if ($Height -ge 15) { return "CorpsePile" }
    return "Hidden"
}

function Get-CorpseRenderCost {
    param([int]$Height)

    if ($Height -ge 17) { return 5 }
    if ($Height -ge 15) { return 1 }
    return 0
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
Assert-True $nearPlaneFront.Visible `
    "Corpse immediately beyond the near plane was hidden."

Assert-True ((Get-CorpseLod 14) -eq "Hidden" -and
             (Get-CorpseLod 15) -eq "CorpsePile" -and
             (Get-CorpseLod 16) -eq "CorpsePile" -and
             (Get-CorpseLod 17) -eq "FullCorpse") `
    "Corpse LOD boundaries changed."
$corpsePileAt15 = Project-Sprite 0 (-[Math]::Truncate(16384 / 15)) `
    0 -256 169 0 $true
$corpsePileAt16 = Project-Sprite 0 (-[Math]::Truncate(16384 / 16)) `
    0 -256 169 0 $true
$fullCorpseAt17 = Project-Sprite 0 (-[Math]::Truncate(16384 / 17)) `
    0 -256 169 0 $true
Assert-True ($corpsePileAt15.Visible -and $corpsePileAt16.Visible -and
             $corpsePileAt15.Height -eq 15 -and
             $corpsePileAt16.Height -eq 15 -and
             $corpsePileAt15.Texture -eq "CorpsePile" -and
             $corpsePileAt16.Texture -eq "CorpsePile") `
    "Corpse-pile tier was not quantized to height 15."
Assert-True ($fullCorpseAt17.Visible -and
             $fullCorpseAt17.Height -eq 17 -and
             $fullCorpseAt17.Texture -eq "AuthoredCorpse") `
    "Full corpse tier did not preserve authored texture and height."
foreach ($visibleCorpse in @($corpsePileAt15, $fullCorpseAt17)) {
    $standingBottom = 32 + [Math]::Truncate($visibleCorpse.Height / 2)
    Assert-True ($visibleCorpse.Bottom -eq
        $standingBottom + [Math]::Truncate($visibleCorpse.Height / 3)) `
        "Corpse tier lost its floor adjustment."
}
Assert-True ((Get-CorpseRenderCost 14) -eq 0 -and
             (Get-CorpseRenderCost 15) -eq 1 -and
             (Get-CorpseRenderCost 16) -eq 1 -and
             (Get-CorpseRenderCost 17) -eq 5) `
    "Corpse render costs changed."
$corpseTextures = @("AuthoredCorpse", "CorpsePile", "Hidden")
Assert-True (($corpseTextures -notcontains "Medium") -and
             ($corpseTextures -notcontains "Simple")) `
    "Corpse state selected an upright silhouette."
$corpseCleanupRedraw = "CorpsePile" -ne "Hidden"
$corpseHiddenRedraw = "Hidden" -ne "Hidden"
$corpseReappearRedraw = "Hidden" -ne "CorpsePile"
$corpseFullToPileRedraw = "AuthoredCorpse" -ne "CorpsePile"
$corpsePileToFullRedraw = "CorpsePile" -ne "AuthoredCorpse"
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
$projectionHeader = Get-Content (
    Join-Path $repositoryPath "platform\game_gear\sprite_projection.h") -Raw
$mainSource = Get-Content (Join-Path $repositoryPath "game\main.c") -Raw
$playerSource = Get-Content (Join-Path $repositoryPath "game\player.c") -Raw
$worldSource = Get-Content (Join-Path $repositoryPath "game\world.c") -Raw

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
Assert-True ($videoSource -match
    "current_sprite_column\s*\|\|\s*previous_sprite_column") `
    "Production renderer does not invalidate old/current coverage union."
Assert-True ($projectionSource -match
    "current->pixels\s*!=\s*previous->pixels") `
    "Texture-only sprite state changes do not invalidate projected coverage."
Assert-True ($videoSource -match
    "game_gear_sprite_covers_tile\s*\(\s*&projected_sprites\[sprite_index\]") `
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
    "#define SPRITE_CORPSE_LOD_MIN_HEIGHT 15" -and
    $projectionHeader -match
    "#define SPRITE_HORIZONTAL_PROJECTION_SCALE 80" -and
    $projectionHeader -match
    "#define SPRITE_RENDER_BUDGET 12") `
    "Production sprite LOD thresholds changed."
Assert-True ($projectionSource -match
    "center_x\s*=\s*GAME_GEAR_VIEWPORT_PIXEL_WIDTH\s*/\s*2[\s\S]*?" +
    "horizontal\s*\*\s*SPRITE_HORIZONTAL_PROJECTION_SCALE[\s\S]*?/\s*depth\s*;") `
    "Production sprite center does not use the parent Game Gear projection scale."
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
    "projected_height\s*<\s*SPRITE_SIMPLE_LOD_MIN_HEIGHT[\s\S]*?return\s*;") `
    "Very distant production sprites are not culled before dirty coverage."
Assert-True ($projectionSource -match
    "sprite->state\s*==\s*ZOMBIE_STATE_CORPSE[\s\S]*?" +
    "projected_height\s*<\s*SPRITE_CORPSE_LOD_MIN_HEIGHT[\s\S]*?" +
    "return\s*;[\s\S]*?projected_height\s*=\s*" +
    "SPRITE_CORPSE_LOD_MIN_HEIGHT[\s\S]*?" +
    "projected->pixels\s*=\s*zombie_corpse_lod_pixels\s*;") `
    "Production corpse LOD selection is not state-specific."
$corpseBranch = $projectionSource.IndexOf(
    "if (sprite->state == ZOMBIE_STATE_CORPSE)")
$screenBounds = $projectionSource.IndexOf(
    "center_x = GAME_GEAR_VIEWPORT_PIXEL_WIDTH")
$wallScan = $projectionSource.IndexOf("rays = raycaster_get_rendered_rays();")
Assert-True ($corpseBranch -ge 0 -and $corpseBranch -lt $screenBounds -and
             $screenBounds -lt $wallScan) `
    "Hidden corpse rejection no longer precedes clipping and wall scanning."
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
    "projected_height\s*<\s*SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?" +
    "projected->pixels\s*=\s*zombie_corpse_lod_pixels\s*;[\s\S]*?" +
    "else\s*\{" -and
    $projectionSource -match
    "projected_height\s*<\s*SPRITE_MEDIUM_LOD_MIN_HEIGHT[\s\S]*?" +
    "projected->pixels\s*=\s*game_gear_get_zombie_lod_pixels\(sprite,\s*0\)\s*;" -and
    $projectionSource -match
    "projected_height\s*<\s*SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?" +
    "projected->pixels\s*=\s*game_gear_get_zombie_lod_pixels\(sprite,\s*1\)\s*;") `
    "Production projection does not select the approved LOD textures."
Assert-True ($projectionSource -match
    "projected->pixels\s*==\s*zombie_corpse_lod_pixels[\s\S]*?return\s*1\s*;" -and
    $projectionSource -match
    "projected_height\s*>=\s*SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?return\s*5\s*;") `
    "Production corpse render cost is not LOD-specific."
Assert-True ($projectionSource -match
    "remaining_budget\s*=\s*SPRITE_RENDER_BUDGET" -and
    $projectionSource -match
    "render_cost\s*>\s*remaining_budget" -and
    $projectionSource -match
    "projected->depth\s*<\s*selected_depth" -and
    $projectionSource -match
    "projected_sprites\[sprite_index\]\.visible\s*=\s*0\s*;" -and
    $videoSource -match
    "game_gear_apply_sprite_render_budget\s*\(") `
    "Production sprite render budget is not deterministic or enforced."
$corpseInitializer = [regex]::Match(
    $projectionSource,
    "zombie_corpse_lod_pixels\[32\]\s*=\s*\{(?<bytes>[\s\S]*?)\};")
Assert-True ($corpseInitializer.Success) `
    "Packed sprite LOD textures are missing."
function Get-PackedLodIndices([string]$Name) {
    $initializer = [regex]::Match($projectionSource,
        $Name + "\[32\]\s*=\s*\{(?<bytes>[\s\S]*?)\};")
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
$lodPatterns = @{}
foreach ($pose in @("standing", "shot_01", "shot_02", "shot_dead")) {
    $mediumName = "zombie_${pose}_medium_lod_pixels"
    $simpleName = "zombie_${pose}_simple_lod_pixels"
    $mediumIndices = @(Get-PackedLodIndices $mediumName)
    $simpleIndices = @(Get-PackedLodIndices $simpleName)
    Assert-True ((($mediumIndices | Sort-Object -Unique) -join ",") `
        -eq "10,13,15") "$mediumName escaped indices 10, 13, and 15."
    Assert-True ((($simpleIndices | Sort-Object -Unique) -join ",") `
        -eq "13,15") "$simpleName escaped indices 13 and 15."
    Assert-True ((@($mediumIndices | Where-Object { $_ -eq 10 })).Count -le 2) `
        "$mediumName has too many highlight pixels."
    Assert-True ((@($simpleIndices | Where-Object { $_ -eq 13 })).Count -lt
                 (@($mediumIndices | Where-Object { $_ -ne 15 })).Count) `
        "$simpleName did not reduce the opaque pixel count."
    $lodPatterns[$mediumName] = $mediumIndices -join ","
    $lodPatterns[$simpleName] = $simpleIndices -join ","
}
foreach ($lod in @("medium", "simple")) {
    $standingPattern = $lodPatterns["zombie_standing_${lod}_lod_pixels"]
    foreach ($pose in @("shot_01", "shot_02", "shot_dead")) {
        Assert-True ($lodPatterns["zombie_${pose}_${lod}_lod_pixels"] -ne
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
    "[\s\S]*?&\s*1U\s*\?\s*1\s*:\s*2[\s\S]*?:\s*0") `
    "Production LOD pose selection is not driven by active hit parity."
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
$corpseIndices = @(
    [regex]::Matches($corpseInitializer.Groups["bytes"].Value,
                     "0x(?<byte>[0-9a-fA-F]{2})") |
        ForEach-Object {
            $value = [Convert]::ToInt32($_.Groups["byte"].Value, 16)
            ($value -shr 4) -band 15
            $value -band 15
        }
)
Assert-True ($corpseIndices.Count -eq 64 -and
             (($corpseIndices | Sort-Object -Unique) -join ",") -eq "13,15") `
    "Corpse-pile texture escaped indices 13 and 15."
Assert-True ((@($corpseIndices | Where-Object { $_ -eq 13 })).Count -eq 18) `
    "Corpse-pile opaque-pixel count changed."
$corpseRowCounts = @(0..7 | ForEach-Object {
    $row = $_
    @($corpseIndices[($row * 8)..($row * 8 + 7)] |
        Where-Object { $_ -eq 13 }).Count
})
Assert-True (($corpseRowCounts -join ",") -eq "0,0,0,0,0,4,6,8") `
    "Corpse-pile texture is not a horizontal ground-level body shape."
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

foreach ($generatedName in @("sprite_texture", "zombie_01_shot_01_texture",
                              "zombie_01_shot_02_texture",
                              "zombie_01_shot_dead_texture",
                              "zombie_01_corps_texture")) {
    $generatedSource = Join-Path $repositoryPath "build\generated\${generatedName}.c"
    Assert-True (Test-Path -LiteralPath $generatedSource) `
        "Generated zombie source $generatedName is missing; run the Release build."
    $generatedBytes = [regex]::Matches(
        (Get-Content $generatedSource -Raw), "0x[0-9a-fA-F]{2}")
    Assert-True ($generatedBytes.Count -eq 32) `
        "$generatedName is not exactly 32 packed bytes."
}

Write-Output "Sprite renderer validation PASS"
Write-Output "- ahead, viewport edges, behind-camera, near/far projection"
Write-Output "- partial/full strict-depth occlusion and floor anchoring"
Write-Output "- clipping bounds, startup order, old/new coverage cleanup"
Write-Output "- production wiring and 32-byte transparent packed texture"
Write-Output "- tile-local four-sprite model: candidate tests 16 -> 8; overlays 4 -> 1"
Write-Output "- sprite LOD: full >=17, medium 15..16, simple 13..14, hidden <=12"
Write-Output "- corpse LOD: full >=17, dark pile 15..16, hidden <=14"
Write-Output "- corpse pile: 18 opaque pixels; palette indices 13 and 15"
Write-Output "- exact wall-edge mapping: absolute screen X >> 2; wall wins ties"
Write-Output "- progressive four-pixel clipping, off-screen and LOD edge cases"
Write-Output "- horizontal rotation sweep: symmetric, monotonic 160-pixel projection"
Write-Output "- deterministic render-cost budget: 12 (full 5, medium 2, simple 1)"

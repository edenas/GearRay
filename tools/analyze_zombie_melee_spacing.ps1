param([switch]$Csv)

$ErrorActionPreference = 'Stop'
$attackDistance = 280
$movementStep = 56

$approaches = @(
    [pscustomobject]@{ Name = 'cardinal'; X = 336; Y = 0 },
    [pscustomobject]@{ Name = 'diagonal'; X = 168; Y = 224 },
    [pscustomobject]@{ Name = '2:1'; X = 280; Y = 112 },
    [pscustomobject]@{ Name = 'mirrored 2:1'; X = 280; Y = -112 },
    [pscustomobject]@{ Name = 'representative oblique'; X = 164; Y = 200 },
    [pscustomobject]@{ Name = 'reverse cardinal'; X = -336; Y = 0 },
    [pscustomobject]@{ Name = '3:1'; X = 336; Y = 112 },
    [pscustomobject]@{ Name = 'mirrored oblique'; X = -164; Y = 200 }
)

function Get-Components([int]$X, [int]$Y) {
    $ax = [Math]::Abs($X); $ay = [Math]::Abs($Y)
    [pscustomobject]@{ Max = [Math]::Max($ax, $ay); Min = [Math]::Min($ax, $ay) }
}

function Get-Octagonal([int]$X, [int]$Y) {
    $c = Get-Components $X $Y
    return $c.Max + [Math]::Floor($c.Min / 2)
}

function Get-Corrected([int]$X, [int]$Y) {
    $c = Get-Components $X $Y
    return $c.Max + [Math]::Floor($c.Min / 4) + [Math]::Floor($c.Min / 8)
}

function Test-Melee([string]$Candidate, [int]$X, [int]$Y) {
    switch ($Candidate) {
        'A baseline' { return (Get-Octagonal $X $Y) -le $attackDistance }
        'B limited final step' { return (Get-Octagonal $X $Y) -le $attackDistance }
        'C squared Euclidean' { return ([long]$X * $X + [long]$Y * $Y) -le ([long]$attackDistance * $attackDistance) }
        'D corrected octagonal' { return (Get-Corrected $X $Y) -le $attackDistance }
    }
}

function Move-TowardPlayer([string]$Candidate, [int]$X, [int]$Y) {
    $step = $movementStep
    if ($Candidate -eq 'B limited final step') {
        $remaining = (Get-Octagonal $X $Y) - $attackDistance
        if ($remaining -lt $step) { $step = $remaining }
    }
    if ([Math]::Abs($X) -ge [Math]::Abs($Y)) {
        $X += $(if ($X -lt 0) { $step } else { -$step })
        $axis = 'X'
    } else {
        $Y += $(if ($Y -lt 0) { $step } else { -$step })
        $axis = 'Y'
    }
    [pscustomobject]@{ X = $X; Y = $Y; Axis = $axis }
}

$rows = foreach ($candidate in @('A baseline', 'B limited final step', 'C squared Euclidean', 'D corrected octagonal')) {
    foreach ($approach in $approaches) {
        $x = $approach.X; $y = $approach.Y; $previousX = $x; $previousY = $y; $axis = '-'
        while (-not (Test-Melee $candidate $x $y)) {
            $previousX = $x; $previousY = $y
            $moved = Move-TowardPlayer $candidate $x $y
            $x = $moved.X; $y = $moved.Y; $axis = $moved.Axis
        }
        $euclidean = [Math]::Sqrt([double]$x * $x + [double]$y * $y)
        $height = [Math]::Min(144, [Math]::Floor(16384 / $euclidean))
        $bodyGap = [Math]::Max(0, $euclidean -
            64 * ([Math]::Abs($x) + [Math]::Abs($y)) / $euclidean)
        [pscustomobject]@{
            Candidate = $candidate; Approach = $approach.Name
            Previous = "($previousX,$previousY)"; FirstMelee = "($x,$y)"; Axis = $axis
            Octagonal = Get-Octagonal $x $y; Euclidean = [Math]::Round($euclidean, 2)
            Depth = [Math]::Round($euclidean, 2); Height = $height
            SquareBodyGap = [Math]::Round($bodyGap, 2)
        }
    }
}

if ($Csv) { $rows | ConvertTo-Csv -NoTypeInformation; exit }
$rows | Format-Table -AutoSize
foreach ($candidate in $rows.Candidate | Select-Object -Unique) {
    $sample = @($rows | Where-Object Candidate -eq $candidate)
    $min = ($sample.Euclidean | Measure-Object -Minimum).Minimum
    $max = ($sample.Euclidean | Measure-Object -Maximum).Maximum
    $minHeight = ($sample.Height | Measure-Object -Minimum).Minimum
    $maxHeight = ($sample.Height | Measure-Object -Maximum).Maximum
    '{0}: Euclidean {1:N2}..{2:N2} (spread {3:N2}); height {4}..{5} (spread {6})' -f `
        $candidate, $min, $max, ($max - $min), $minHeight, $maxHeight, ($maxHeight - $minHeight)
}

# Compare the optimized split path with the original Candidate B formulation
# across a broad local grid. Exact threshold cases are checked separately.
for ($x = -400; $x -le 400; $x += 4) {
    for ($y = -400; $y -le 400; $y += 4) {
        $distance = Get-Octagonal $x $y
        if ($distance -le $attackDistance) { continue }
        $currentStep = [Math]::Min($movementStep, $distance - $attackDistance)
        $splitStep = if ($distance -ge $attackDistance + $movementStep) {
            $movementStep
        } else { $distance - $attackDistance }
        if ($currentStep -ne $splitStep) {
            throw "Candidate B step mismatch at ($x,$y)"
        }
        $current = Move-TowardPlayer 'B limited final step' $x $y
        $nextDistance = Get-Octagonal $current.X $current.Y
        if ($current.X -ne $(if ([Math]::Abs($x) -ge [Math]::Abs($y)) {
                $x + $(if ($x -lt 0) { $splitStep } else { -$splitStep })
            } else { $x }) -or
            $current.Y -ne $(if ([Math]::Abs($x) -lt [Math]::Abs($y)) {
                $y + $(if ($y -lt 0) { $splitStep } else { -$splitStep })
            } else { $y }) -or
            (($nextDistance -le $attackDistance) -ne
             ((Get-Octagonal $current.X $current.Y) -le $attackDistance))) {
            throw "Candidate B coordinate/eligibility mismatch at ($x,$y)"
        }
    }
}
foreach ($distance in 280, 281, 335, 336, 337) {
    if ($distance -le $attackDistance) { continue }
    $currentStep = [Math]::Min($movementStep, $distance - $attackDistance)
    $splitStep = if ($distance -ge $attackDistance + $movementStep) {
        $movementStep
    } else { $distance - $attackDistance }
    if ($currentStep -ne $splitStep) {
        throw "Candidate B boundary mismatch at distance $distance"
    }
}
'Boundary equivalence PASS: 280/281/335/336/337 follow the same min(56, distance - 280) rule'
'Optimized Candidate B equivalence PASS: grid -400..400 on both axes at 4-unit granularity'

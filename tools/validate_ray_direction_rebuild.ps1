$ErrorActionPreference = "Stop"

function Get-RequiredMatch {
    param(
        [string]$Text,
        [string]$Pattern,
        [string]$Description
    )

    $match = [regex]::Match($Text, $Pattern)
    if (-not $match.Success) {
        throw "Could not extract $Description from production source."
    }

    return $match
}

function Get-ProductionDefine {
    param([string]$Text, [string]$Name)

    return [int](Get-RequiredMatch `
        $Text `
        "(?m)^\s*#define\s+$Name\s+(\d+)\s*$" `
        $Name).Groups[1].Value
}

$cameraSource = Get-Content (Join-Path $PSScriptRoot "..\game\camera.c") -Raw
$raycasterSource = Get-Content (
    Join-Path $PSScriptRoot "..\engine\render\raycaster.c") -Raw
$raycasterHeader = Get-Content (
    Join-Path $PSScriptRoot "..\engine\render\raycaster.h") -Raw

$rotationCosine = Get-ProductionDefine $cameraSource "ROTATION_COSINE"
$rotationSine = Get-ProductionDefine $cameraSource "ROTATION_SINE"
$rotationScale = Get-ProductionDefine $cameraSource "ROTATION_SCALE"
$directionLength = Get-ProductionDefine $cameraSource "DIRECTION_LENGTH"
$cameraPlaneLength = Get-ProductionDefine $cameraSource "CAMERA_PLANE_LENGTH"
$rayCount = Get-ProductionDefine $raycasterHeader "RAYCASTER_RAY_COUNT"

$cameraXInitializer = (Get-RequiredMatch `
    $raycasterSource `
    "static\s+const\s+signed\s+int\s+camera_x_by_ray\s*\[\s*RAY_COUNT\s*\]\s*=\s*\{(?<values>[\s\S]*?)\};" `
    "camera_x_by_ray[]").Groups["values"].Value
$cameraXByRay = @(
    [regex]::Matches($cameraXInitializer, "-?\d+") |
        ForEach-Object { [int]$_.Value }
)

$cameraInitializeBody = (Get-RequiredMatch `
    $cameraSource `
    "void\s+camera_initialize\s*\(\s*void\s*\)\s*\{(?<body>[\s\S]*?)\}" `
    "camera_initialize()").Groups["body"].Value
$initialDirectionXSign = if ((Get-RequiredMatch `
    $cameraInitializeBody `
    "direction_x\s*=\s*(?<sign>-?)DIRECTION_LENGTH\s*;" `
    "initial direction X").Groups["sign"].Value -eq "-") { -1 } else { 1 }
$initialDirectionY = [int](Get-RequiredMatch `
    $cameraInitializeBody `
    "direction_y\s*=\s*(-?\d+)\s*;" `
    "initial direction Y").Groups[1].Value
$initialPlaneX = [int](Get-RequiredMatch `
    $cameraInitializeBody `
    "plane_x\s*=\s*(-?\d+)\s*;" `
    "initial camera plane X").Groups[1].Value
$initialPlaneYSign = if ((Get-RequiredMatch `
    $cameraInitializeBody `
    "plane_y\s*=\s*(?<sign>-?)CAMERA_PLANE_LENGTH\s*;" `
    "initial camera plane Y").Groups["sign"].Value -eq "-") { -1 } else { 1 }

# These assertions intentionally freeze the approved gameplay/render baseline.
if ($rotationCosine -ne 4058 -or $rotationSine -ne 556 -or
    $rotationScale -ne 4096 -or $directionLength -ne 256 -or
    $cameraPlaneLength -ne 169 -or $rayCount -ne 28) {
    throw "Production camera/ray constants no longer match the approved baseline."
}
if ($cameraXByRay.Count -ne $rayCount) {
    throw "camera_x_by_ray[] has $($cameraXByRay.Count) values; RAY_COUNT is $rayCount."
}

function Get-RoundedQuotient {
    param([long]$Value, [int]$Scale)

    if ($Value -lt 0) {
        $Value -= [int]($Scale / 2)
    } else {
        $Value += [int]($Scale / 2)
    }

    return [int][Math]::Truncate($Value / $Scale)
}

function Get-TruncatedQuotient {
    param([long]$Value, [int]$Scale)
    return [int][Math]::Truncate($Value / $Scale)
}

function Get-RotatedBasis {
    param([int[]]$Basis, [int]$Sine)

    $oldX = $Basis[0]
    $oldY = $Basis[1]
    $directionX = Get-RoundedQuotient `
        ([long]$oldX * $rotationCosine - [long]$oldY * $Sine) `
        $rotationScale
    $directionY = Get-RoundedQuotient `
        ([long]$oldY * $rotationCosine + [long]$oldX * $Sine) `
        $rotationScale
    $length = [int][Math]::Floor([Math]::Sqrt(
        [long]$directionX * $directionX +
        [long]$directionY * $directionY))

    if ($length -ne 0) {
        $directionX = Get-RoundedQuotient `
            ([long]$directionX * $directionLength) $length
        $directionY = Get-RoundedQuotient `
            ([long]$directionY * $directionLength) $length
    }

    $planeX = Get-RoundedQuotient `
        ([long]$directionY * $cameraPlaneLength) $directionLength
    $planeY = Get-RoundedQuotient `
        (-[long]$directionX * $cameraPlaneLength) $directionLength

    return [int[]]@($directionX, $directionY, $planeX, $planeY)
}

function Test-Basis {
    param([int[]]$Basis)

    foreach ($cameraX in $cameraXByRay) {
        foreach ($planeComponent in @($Basis[2], $Basis[3])) {
            $wideProduct = [long]$planeComponent * $cameraX
            if ($wideProduct -lt [int16]::MinValue -or
                $wideProduct -gt [int16]::MaxValue) {
                throw "Reachable product exceeds signed 16-bit range: $wideProduct"
            }

            $wideResult = Get-TruncatedQuotient $wideProduct 256
            $narrowProduct = [int16]$wideProduct
            $narrowResult = Get-TruncatedQuotient $narrowProduct 256
            if ($wideResult -ne $narrowResult) {
                throw "Ray-direction mismatch for basis $($Basis -join ',') and camera X $cameraX"
            }
        }
    }
}

$initialBasis = [int[]]@(
    ($initialDirectionXSign * $directionLength),
    $initialDirectionY,
    $initialPlaneX,
    ($initialPlaneYSign * $cameraPlaneLength)
)
$pending = [System.Collections.Generic.Queue[int[]]]::new()
$pending.Enqueue($initialBasis)
$visited = @{}
$maximumAbsoluteProduct = 0

while ($pending.Count -ne 0) {
    $basis = $pending.Dequeue()
    $key = $basis -join ","
    if ($visited.ContainsKey($key)) {
        continue
    }

    $visited[$key] = $true
    Test-Basis $basis

    foreach ($cameraX in $cameraXByRay) {
        foreach ($planeComponent in @($basis[2], $basis[3])) {
            $absoluteProduct = [Math]::Abs([long]$planeComponent * $cameraX)
            if ($absoluteProduct -gt $maximumAbsoluteProduct) {
                $maximumAbsoluteProduct = $absoluteProduct
            }
        }
    }

    $pending.Enqueue((Get-RotatedBasis $basis $rotationSine))
    $pending.Enqueue((Get-RotatedBasis $basis (-$rotationSine)))
}

Write-Output "Ray-direction rebuild equivalence PASS"
Write-Output "- reachable camera bases: $($visited.Count)"
Write-Output "- rays per basis: $($cameraXByRay.Count)"
Write-Output "- compared components: $($visited.Count * $cameraXByRay.Count * 2)"
Write-Output "- maximum absolute product: $maximumAbsoluteProduct"

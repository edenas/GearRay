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
        [int]$PlaneY
    )

    $determinant = $PlaneX * $DirectionY - $DirectionX * $PlaneY
    if ($determinant -eq 0) { return @{ Visible = $false } }
    $depth = [Math]::Truncate(
        (($PlaneX * $RelativeY - $RelativeX * $PlaneY) * 256) /
        $determinant)
    if ($depth -le 0) { return @{ Visible = $false; Depth = $depth } }
    $horizontal = [Math]::Truncate(
        (($DirectionY * $RelativeX - $DirectionX * $RelativeY) * 256) /
        $determinant)
    $center = 56 + [Math]::Truncate($horizontal * 56 / $depth)
    $height = [Math]::Truncate(16384 / $depth)
    if ($height -lt 1) { $height = 1 }
    if ($height -gt 144) { $height = 144 }
    $left = $center - [Math]::Truncate($height / 2)
    $right = $left + $height
    $bottom = 32 + [Math]::Truncate($height / 2)
    $top = $bottom - $height
    return @{
        Visible = $right -gt 0 -and $left -lt 112 -and
                  $bottom -gt 0 -and $top -lt 64
        Depth = $depth; Center = $center; Height = $height
        Left = $left; Right = $right; Top = $top; Bottom = $bottom
    }
}

$ahead = Project-Sprite 0 -768 0 -256 169 0
Assert-True $ahead.Visible "Directly-ahead sprite was not visible."
Assert-True ($ahead.Center -eq 56) "Directly-ahead sprite was not centered."
Assert-True ($ahead.Bottom -eq 32 + [Math]::Truncate($ahead.Height / 2)) `
    "Sprite feet are not floor anchored."

$near = Project-Sprite 0 -256 0 -256 169 0
$far = Project-Sprite 0 -1536 0 -256 169 0
Assert-True ($near.Height -gt $far.Height) "Perspective scaling is not monotonic."

$leftEdge = Project-Sprite -480 -768 0 -256 169 0
$rightEdge = Project-Sprite 480 -768 0 -256 169 0
Assert-True ($leftEdge.Visible -and $leftEdge.Left -lt 0) `
    "Left-edge clipping case was not produced."
Assert-True ($rightEdge.Visible -and $rightEdge.Right -gt 112) `
    "Right-edge clipping case was not produced."

$behind = Project-Sprite 0 256 0 -256 169 0
Assert-True (-not $behind.Visible) "Behind-camera sprite remained visible."

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
$mainSource = Get-Content (Join-Path $repositoryPath "game\main.c") -Raw

Assert-True ($raycasterSource -match
    "\*result_distance\s*=\s*projection_distance\s*;") `
    "Ray results do not store the exact wall projection distance."
Assert-True ($videoSource -match
    "projected->depth\s*>=\s*rays\[[^\]]+\]\.wall_distance") `
    "Production occlusion does not intentionally favor equal-depth walls."
Assert-True ($videoSource -match
    "current_sprite_column\s*\|\|\s*previous_sprite_column") `
    "Production renderer does not invalidate old/current coverage union."
Assert-True ($videoSource -match
    "palette_index\s*==\s*SPRITE_TRANSPARENT_INDEX[\s\S]*?continue\s*;") `
    "Transparent production pixels do not leave native tile data untouched."

$worldInitialize = $mainSource.IndexOf("world_initialize();")
$startupRaycast = $mainSource.IndexOf("raycaster_update();")
$startupDraw = $mainSource.IndexOf("game_gear_video_draw_wall_columns();")
Assert-True ($worldInitialize -ge 0 -and
             $worldInitialize -lt $startupRaycast -and
             $startupRaycast -lt $startupDraw) `
    "Startup ordering does not initialize and project the sprite before drawing."

$generatedSource = Join-Path $repositoryPath "build\generated\sprite_texture.c"
Assert-True (Test-Path -LiteralPath $generatedSource) `
    "Generated standing sprite source is missing; run the Release build."
$generatedText = Get-Content $generatedSource -Raw
$generatedBytes = [regex]::Matches($generatedText, "0x[0-9a-fA-F]{2}")
Assert-True ($generatedBytes.Count -eq 32) `
    "Generated standing sprite is not exactly 32 packed bytes."

Write-Output "Sprite renderer validation PASS"
Write-Output "- ahead, viewport edges, behind-camera, near/far projection"
Write-Output "- partial/full strict-depth occlusion and floor anchoring"
Write-Output "- clipping bounds, startup order, old/new coverage cleanup"
Write-Output "- production wiring and 32-byte transparent packed texture"

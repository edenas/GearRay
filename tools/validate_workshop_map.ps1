$ErrorActionPreference = "Stop"

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "$Message (expected $Expected, got $Actual)"
    }
}

function Get-Define {
    param([string]$Source, [string]$Name)
    $match = [regex]::Match(
        $Source,
        "(?m)^\s*#define\s+$Name\s+(?<value>\d+)\s*$")
    if (-not $match.Success) {
        throw "Could not extract $Name."
    }
    return [int]$match.Groups["value"].Value
}

$repositoryPath = Resolve-Path (Join-Path $PSScriptRoot "..")
$gamePath = Join-Path $repositoryPath "game"
$mapHeader = Get-Content (Join-Path $gamePath "workshop_map.h") -Raw
$mapSource = Get-Content (Join-Path $gamePath "workshop_map.c") -Raw
$worldHeader = Get-Content (Join-Path $gamePath "world.h") -Raw
$worldSource = Get-Content (Join-Path $gamePath "world.c") -Raw
$doorHeader = Get-Content (Join-Path $gamePath "door_instances.h") -Raw
$doorSource = Get-Content (Join-Path $gamePath "door_instances.c") -Raw
$switchHeader = Get-Content (Join-Path $gamePath "red_door_switch.h") -Raw
$switchSource = Get-Content (Join-Path $gamePath "red_door_switch.c") -Raw
$textureGenerator = Get-Content (
    Join-Path $PSScriptRoot "generate_wall_texture.ps1") -Raw

$width = Get-Define $mapHeader "WORKSHOP_MAP_WIDTH"
$height = Get-Define $mapHeader "WORKSHOP_MAP_HEIGHT"
$spawnX = Get-Define $mapSource "WORKSHOP_SPAWN_X"
$spawnY = Get-Define $mapSource "WORKSHOP_SPAWN_Y"
$voidTileId = Get-Define $worldHeader "WORLD_TILE_VOID"
$switchTileId = Get-Define $worldHeader "WORLD_TILE_RED_DOOR_SWITCH"

Assert-Equal 13 $width "Workshop width"
Assert-Equal 13 $height "Workshop height"
foreach ($tileContract in @{
    WORLD_TILE_EMPTY = 0
    WORLD_TILE_STONE = 1
    WORLD_TILE_CONCRETE_BLOOD = 2
    WORLD_TILE_BRICK = 3
    WORLD_TILE_METAL = 4
    WORLD_TILE_DOOR = 5
    WORLD_TILE_RED_DOOR = 6
    WORLD_TILE_RED_DOOR_SWITCH = 7
    WORLD_TILE_VOID = 8
    WORLD_TILE_SPRITE_MARKER = 9
}.GetEnumerator()) {
    Assert-Equal $tileContract.Value `
        (Get-Define $worldHeader $tileContract.Key) `
        $tileContract.Key
}
if ($voidTileId -le $switchTileId) {
    throw "VOID must not displace an authored texture tile ID."
}

foreach ($alias in @{
    X = "WORLD_TILE_VOID"
    E = "WORLD_TILE_EMPTY"
    S = "WORLD_TILE_STONE"
    B = "WORLD_TILE_CONCRETE_BLOOD"
    D = "WORLD_TILE_DOOR"
    R = "WORLD_TILE_RED_DOOR"
    W = "WORLD_TILE_RED_DOOR_SWITCH"
    Z = "WORLD_TILE_SPRITE_MARKER"
}.GetEnumerator()) {
    if ($mapSource -notmatch
        "(?m)^\s*#define\s+$($alias.Key)\s+$($alias.Value)\s*$") {
        throw "Map alias $($alias.Key) does not map to $($alias.Value)."
    }
}

$initializer = [regex]::Match(
    $mapSource,
    "static\s+const\s+unsigned\s+char\s+workshop_map\s*\[[^\]]+\]\s*\[[^\]]+\]\s*=\s*\{(?<rows>[\s\S]*?)\n\};")
if (-not $initializer.Success) {
    throw "Could not extract workshop_map initializer."
}

$rowMatches = [regex]::Matches(
    $initializer.Groups["rows"].Value,
    "\{(?<tiles>[^{}]+)\}")
Assert-Equal $height $rowMatches.Count "Workshop row count"

$map = [System.Collections.Generic.List[object]]::new()
foreach ($rowMatch in $rowMatches) {
    $tiles = @(
        $rowMatch.Groups["tiles"].Value.Split(",") |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ -ne "" }
    )
    Assert-Equal $width $tiles.Count "Workshop row width"
    foreach ($tile in $tiles) {
        if ($tile -notin @("X", "E", "S", "B", "D", "R", "W", "Z")) {
            throw "Unknown workshop tile symbol: $tile"
        }
    }
    $map.Add([string[]]$tiles)
}

$approvedRows = @(
    "XXXXXSBSXXXXX",
    "XXXXXSZSXXXXX",
    "XXXXXBRSXXXXX",
    "XXXXSEEESXXXX",
    "XSBSSSDSSSBSX",
    "XSEEEEEEEEESX",
    "BZEEEEEEEEEES",
    "XSEEEEEEEEESX",
    "XSBSSBDSSSSSX",
    "XXXXSEEESXXXX",
    "XXXXSEEEBXXXX",
    "XXXXSZEZSXXXX",
    "XXXXSBWSSXXXX"
)
for ($y = 0; $y -lt $height; ++$y) {
    Assert-Equal $approvedRows[$y] ($map[$y] -join "") "Approved map row $y"
}

$spriteMarkers = @()
for ($y = 0; $y -lt $height; ++$y) {
    for ($x = 0; $x -lt $width; ++$x) {
        if ($map[$y][$x] -eq "Z") {
            $spriteMarkers += ,@($x, $y)
        }
    }
}
$expectedSpriteMarkers = @(
    @(6, 1),
    @(1, 6),
    @(5, 11),
    @(7, 11)
)
Assert-Equal $expectedSpriteMarkers.Count $spriteMarkers.Count `
    "Static sprite marker count"
for ($index = 0; $index -lt $expectedSpriteMarkers.Count; ++$index) {
    Assert-Equal $expectedSpriteMarkers[$index][0] $spriteMarkers[$index][0] `
        "Static sprite marker $index X"
    Assert-Equal $expectedSpriteMarkers[$index][1] $spriteMarkers[$index][1] `
        "Static sprite marker $index Y"
}

function Get-Tile {
    param([int]$X, [int]$Y)
    if ($X -lt 0 -or $Y -lt 0 -or $X -ge $width -or $Y -ge $height) {
        return $null
    }
    return $map[$Y][$X]
}

if ($spawnX -lt 0 -or $spawnY -lt 0 -or
    $spawnX -ge $width -or $spawnY -ge $height) {
    throw "Spawn is outside the workshop."
}
Assert-Equal "E" (Get-Tile $spawnX $spawnY) "Spawn tile"
Assert-Equal 6 $spawnX "Canonical spawn X"
Assert-Equal 7 $spawnY "Canonical spawn Y"
Assert-Equal "E" (Get-Tile $spawnX ($spawnY - 1)) "North-facing spawn opening"

$doorCount = Get-Define $doorHeader "DOOR_INSTANCE_COUNT"
$doorInitializer = [regex]::Match(
    $doorSource,
    "door_instances\s*\[[^\]]+\]\s*=\s*\{(?<entries>[\s\S]*?)\};")
if (-not $doorInitializer.Success) {
    throw "Could not extract door_instances initializer."
}
$doorMatches = [regex]::Matches(
    $doorInitializer.Groups["entries"].Value,
    "\{\s*(?<x>\d+)\s*,\s*(?<y>\d+)\s*\}")
Assert-Equal $doorCount $doorMatches.Count "Door instance count"

$registeredDoors = @()
foreach ($doorMatch in $doorMatches) {
    $registeredDoors += ,@(
        [int]$doorMatch.Groups["x"].Value,
        [int]$doorMatch.Groups["y"].Value
    )
}
$expectedDoors = @(@(6, 4, "D"), @(6, 2, "R"), @(6, 8, "D"))
for ($index = 0; $index -lt $expectedDoors.Count; ++$index) {
    Assert-Equal $expectedDoors[$index][0] $registeredDoors[$index][0] `
        "Door $index X"
    Assert-Equal $expectedDoors[$index][1] $registeredDoors[$index][1] `
        "Door $index Y"
    Assert-Equal $expectedDoors[$index][2] `
        (Get-Tile $registeredDoors[$index][0] $registeredDoors[$index][1]) `
        "Door $index map tile"
}

for ($y = 0; $y -lt $height; ++$y) {
    for ($x = 0; $x -lt $width; ++$x) {
        $tile = Get-Tile $x $y
        if ($tile -in @("D", "R")) {
            $matches = @(
                $registeredDoors |
                    Where-Object { $_[0] -eq $x -and $_[1] -eq $y }
            )
            Assert-Equal 1 $matches.Count "Registered door at ($x,$y)"
        }
    }
}

$switchX = Get-Define $switchHeader "RED_DOOR_SWITCH_MAP_X"
$switchY = Get-Define $switchHeader "RED_DOOR_SWITCH_MAP_Y"
Assert-Equal 6 $switchX "Switch X"
Assert-Equal 12 $switchY "Switch Y"
Assert-Equal "W" (Get-Tile $switchX $switchY) "Registered switch map tile"
if ($doorHeader -notmatch
    "(?m)^\s*#define\s+DOOR_INSTANCE_ROOM_INTERNAL\s+1\s*$" -or
    $switchSource -notmatch
    "door_state_open\s*\(\s*DOOR_INSTANCE_ROOM_INTERNAL\s*\)") {
    throw "Switch is not linked to the registered red door at (6,2)."
}

$cardinalDirections = @(@(0, -1), @(1, 0), @(0, 1), @(-1, 0))
for ($y = 0; $y -lt $height; ++$y) {
    for ($x = 0; $x -lt $width; ++$x) {
        $tile = Get-Tile $x $y
        if ($tile -in @("E", "Z")) {
            foreach ($direction in $cardinalDirections) {
                $neighbor = Get-Tile ($x + $direction[0]) ($y + $direction[1])
                if ($null -eq $neighbor -or $neighbor -eq "X") {
                    throw "Playable E at ($x,$y) touches VOID or out-of-bounds."
                }
            }
        }
        elseif ($tile -in @("D", "R")) {
            foreach ($direction in $cardinalDirections) {
                $neighbor = Get-Tile ($x + $direction[0]) ($y + $direction[1])
                if ($null -eq $neighbor -or $neighbor -eq "X") {
                    throw "Openable door at ($x,$y) exposes VOID or out-of-bounds."
                }
            }
            $expectedNorthOpening = if ($x -eq 6 -and $y -eq 2) { "Z" } else { "E" }
            Assert-Equal $expectedNorthOpening (Get-Tile $x ($y - 1)) `
                "Door north opening at ($x,$y)"
            Assert-Equal "E" (Get-Tile $x ($y + 1)) "Door south opening at ($x,$y)"
        }
    }
}

Assert-Equal "R" (Get-Tile 6 2) "Top red door"
Assert-Equal "Z" (Get-Tile 6 1) "Top red door north opening"
Assert-Equal "E" (Get-Tile 6 3) "Top red door south opening"
Assert-Equal "B" (Get-Tile 6 0) "Top chamber north cap"

# Treat every door as open and prove that the complete playable component is
# reachable from spawn and has only renderable tiles on its cardinal frontier.
$pending = [System.Collections.Generic.Queue[string]]::new()
$visited = @{}
$pending.Enqueue("$spawnX,$spawnY")
while ($pending.Count -ne 0) {
    $key = $pending.Dequeue()
    if ($visited.ContainsKey($key)) { continue }
    $visited[$key] = $true
    $coordinates = $key.Split(",")
    $x = [int]$coordinates[0]
    $y = [int]$coordinates[1]

    foreach ($direction in $cardinalDirections) {
        $nextX = $x + $direction[0]
        $nextY = $y + $direction[1]
        $neighbor = Get-Tile $nextX $nextY
        if ($null -eq $neighbor -or $neighbor -eq "X") {
            throw "Reachable region at ($x,$y) is not enclosed."
        }
        if ($neighbor -in @("E", "D", "R", "Z")) {
            $pending.Enqueue("$nextX,$nextY")
        }
    }
}

$playableCount = 0
for ($y = 0; $y -lt $height; ++$y) {
    for ($x = 0; $x -lt $width; ++$x) {
        if ((Get-Tile $x $y) -in @("E", "D", "R", "Z")) {
            ++$playableCount
            if (-not $visited.ContainsKey("$x,$y")) {
                throw "Playable tile at ($x,$y) is unreachable from spawn."
            }
        }
    }
}
Assert-Equal $playableCount $visited.Count "Reachable playable tile count"

# Runtime semantic checks: VOID and out-of-bounds are blocked before the map
# array can be read. Since every reachable frontier is renderable, a DDA's
# cardinal cell sequence must hit a wall/closed door before reaching VOID.
if ($worldSource -notmatch
    "if\s*\(\s*x\s*>=\s*WORLD_WIDTH\s*\|\|\s*y\s*>=\s*WORLD_HEIGHT\s*\)\s*return\s+WORLD_TILE_VOID\s*;" -or
    $worldSource -notmatch
    "if\s*\(\s*x\s*>=\s*WORLD_WIDTH\s*\|\|\s*y\s*>=\s*WORLD_HEIGHT\s*\)\s*return\s+1\s*;" -or
    $worldSource -notmatch
    "if\s*\(\s*tile_id\s*==\s*WORLD_TILE_EMPTY\s*\)\s*return\s+0\s*;" -or
    $worldSource -notmatch
    "tile_id\s*==\s*WORLD_TILE_SPRITE_MARKER") {
    throw "World bounds/solidity semantics do not safely block VOID."
}

$unexpectedMapCallers = @(
    @("engine", "game", "platform") |
        ForEach-Object {
            Get-ChildItem (Join-Path $repositoryPath $_) -Recurse -Filter "*.c"
        } |
        Where-Object {
            $_.FullName -notin @(
                (Join-Path $gamePath "world.c"),
                (Join-Path $gamePath "world_initialization.c"),
                (Join-Path $gamePath "workshop_map.c")
            )
        } |
        Where-Object {
            (Get-Content $_.FullName -Raw) -match "workshop_map_get_tile\s*\("
        }
)
Assert-Equal 0 $unexpectedMapCallers.Count "Unchecked workshop map callers"

if ($textureGenerator -match "WORLD_TILE_VOID") {
    throw "VOID must not enter the authored texture pipeline."
}

Write-Output "Workshop map validation PASS"
Write-Output "- dimensions: ${width}x${height}; rows and columns exact"
Write-Output "- spawn: ($spawnX,$spawnY), EMPTY with north-facing opening"
Write-Output "- registered doors: D (6,4), R (6,2), D (6,8)"
Write-Output "- registered switch: W (6,12), linked to R (6,2)"
Write-Output "- reachable playable tiles: $playableCount; renderable frontier enclosed"
Write-Output "- VOID collision, DDA traversal and out-of-bounds access blocked"

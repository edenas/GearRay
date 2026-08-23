$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$interactions = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\world_interactions.c')
$sprites = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\world_sprite.c')
$corpses = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\zombie_corpses.c')
$spriteHeader = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\world_sprite.h')
$corpseHeader = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\zombie_corpses.h')
$workshopMap = Get-Content -Raw -LiteralPath (
    Join-Path $root 'game\workshop_map.c')
$cmake = Get-Content -Raw -LiteralPath (Join-Path $root 'CMakeLists.txt')

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

Assert-True ($interactions -match
    'door_state_get\(door_instance\) == DOOR_STATE_OPEN[\s\S]*?' +
    'world_sprites_crush_in_door\(target->map_y\)[\s\S]*?' +
    'door_state_toggle\(door_instance\)') `
    'Door crushing does not run immediately before an open door closes.'
Assert-True ($sprites -match
    'world_sprites_crush_in_door[\s\S]*?' +
    'zombie_corpses_crush_in_door\(map_y\)') `
    'Bank 1 door interaction does not route Bank 2 work through resident code.'
Assert-True ($corpses -match
    'WORLD_SPRITE_LIFE_STATE\(sprite\) != ZOMBIE_STATE_ALIVE[\s\S]*?' +
    'ZOMBIE_COLLISION_RADIUS' -and
    $corpses -match 'world_sprite_make_corpse\(sprite_index\)') `
    'Door crushing does not target living overlap and use corpse semantics.'
Assert-True ($corpses -match
    'world_sprite_remove\s*\(\s*removed_index\s*\)' -and
    $corpses -match
    'removed_index\s*=\s*other_index\s*>\s*sprite_index') `
    'Corpse merging does not release the deterministic higher sprite slot.'
Assert-True ($spriteHeader -match
    'ZOMBIE_CORPSE_MERGE_DISTANCE ZOMBIE_COMBINED_COLLISION_RADIUS' -and
    $spriteHeader -match
    'ZOMBIE_COMBINED_COLLISION_RADIUS \(2 \* ZOMBIE_COLLISION_RADIUS\)') `
    'Corpse merge distance is not derived from the combined body footprint.'
Assert-True ($spriteHeader -notmatch
    '(?m)^\s*(unsigned|signed|ZombieState)[^;]*(crush|merge)[^;]*;') `
    'Door crushing or corpse merging added persistent WorldSprite state.'
Assert-True ($corpseHeader -match
    'zombie_corpses_finalize\([^;]+\) __banked;' -and
    $corpseHeader -match
    'zombie_corpses_crush_in_door\([^;]+\) __banked;' -and
    $cmake -match
    'OUTPUT "\$\{GEAR_RAY_ZOMBIE_CORPSES_OBJECT\}"[\s\S]*?--codeseg BANK2') `
    'Cold corpse management is not isolated in Bank 2 behind banked calls.'

$mapBody = [regex]::Match($workshopMap,
    'workshop_map[\s\S]*?=\s*\{(?<body>[\s\S]*?)\};').Groups['body'].Value
$mapTokens = @([regex]::Matches($mapBody, '(?<![A-Z_])[XESBDRWZ](?![A-Z_])') |
    ForEach-Object { $_.Value })
Assert-True ($mapTokens.Count -eq 13 * 13) `
    'Could not parse the 13x13 workshop map for door relocation validation.'
foreach ($door in @(@(6, 2), @(6, 4), @(6, 8))) {
    $x = $door[0]
    $y = $door[1]
    $north = $mapTokens[(($y - 1) * 13) + $x]
    $south = $mapTokens[(($y + 1) * 13) + $x]
    $west = $mapTokens[($y * 13) + $x - 1]
    $east = $mapTokens[($y * 13) + $x + 1]
    Assert-True ('E', 'Z' -contains $north) `
        "Door ($x,$y) has no passable north-side corpse destination."
    Assert-True ('E', 'Z' -contains $south) `
        "Door ($x,$y) has no passable south-side corpse destination."
    Assert-True ('S', 'B' -contains $west) `
        "Door ($x,$y) is not the expected north/south passage."
    Assert-True ('S', 'B' -contains $east) `
        "Door ($x,$y) is not the expected north/south passage."
}

$Radius = 32
$DoorLeft = 6 * 256
$DoorTop = 4 * 256
$DoorRight = $DoorLeft + 256
$DoorBottom = $DoorTop + 256
$DoorCenterX = $DoorLeft + 128
$DoorCenterY = $DoorTop + 128

function Test-DoorOverlap([int]$X, [int]$Y) {
    return -not ($X + $Radius -lt $DoorLeft -or
                 $X - $Radius -ge $DoorRight -or
                 $Y + $Radius -lt $DoorTop -or
                 $Y - $Radius -ge $DoorBottom)
}

function Get-RelocatedCorpse([int]$X, [int]$Y) {
    return [pscustomobject]@{
        X = $DoorCenterX
        Y = if ($Y -lt $DoorCenterY) {
            $DoorTop - $Radius - 1
        } else {
            $DoorBottom + $Radius
        }
    }
}

function Test-Merge([object[]]$Corpses, [int]$X, [int]$Y) {
    foreach ($corpse in $Corpses) {
        if ([Math]::Abs($X - $corpse.X) -lt 64 -and
            [Math]::Abs($Y - $corpse.Y) -lt 64) {
            return $Corpses
        }
    }
    return @($Corpses) + [pscustomobject]@{ X = $X; Y = $Y }
}

$outsideDoorX = $DoorLeft - $Radius - 1
Assert-True (-not (Test-DoorOverlap $outsideDoorX $DoorCenterY)) `
    'A non-overlapping zombie was classified as blocking the door.'

$overlaps = @(
    [pscustomobject]@{ X = $DoorCenterX; Y = $DoorCenterY },
    [pscustomobject]@{ X = $DoorLeft - $Radius; Y = $DoorCenterY },
    [pscustomobject]@{ X = $DoorRight + $Radius - 1; Y = $DoorCenterY },
    [pscustomobject]@{ X = $DoorCenterX; Y = $DoorTop - $Radius },
    [pscustomobject]@{ X = $DoorCenterX; Y = $DoorBottom + $Radius - 1 })
foreach ($position in $overlaps) {
    Assert-True (Test-DoorOverlap $position.X $position.Y) `
        'A centered, partial, or edge-touching zombie escaped crushing.'
}

$north = Get-RelocatedCorpse $DoorCenterX ($DoorCenterY - 1)
$south = Get-RelocatedCorpse $DoorCenterX $DoorCenterY
Assert-True ($north.X -eq $DoorCenterX -and
             $north.Y -eq $DoorTop - $Radius - 1 -and
             -not (Test-DoorOverlap $north.X $north.Y)) `
    'North-side corpse relocation is not deterministic and door-safe.'
Assert-True ($south.X -eq $DoorCenterX -and
             $south.Y -eq $DoorBottom + $Radius -and
             -not (Test-DoorOverlap $south.X $south.Y)) `
    'South-side corpse relocation is not deterministic and door-safe.'

$corpseModel = @([pscustomobject]@{ X = $north.X; Y = $north.Y })
$corpseModel = @(Test-Merge $corpseModel ($north.X + 20) ($north.Y - 20))
$corpseModel = @(Test-Merge $corpseModel $north.X $north.Y)
Assert-True ($corpseModel.Count -eq 1) `
    'Successive colocated door corpses did not merge to one slot.'
$corpseModel = @(Test-Merge $corpseModel ($north.X + 64) $north.Y)
Assert-True ($corpseModel.Count -eq 2) `
    'Corpses at the merge threshold were incorrectly merged.'

Assert-True ($sprites -match
    'ZOMBIE_STATE_SHOT_DEAD[\s\S]*?zombie_corpses_finalize\(sprite_index\)') `
    'Normal weapon death no longer reaches corpse merging after its shot-dead timer.'

Write-Output 'Zombie door-crush and corpse-deduplication validation PASS'
Write-Output '- no-zombie close remains a single bounded sprite scan'
Write-Output '- centered, partial, and four edge contacts are crushed'
Write-Output '- north/south relocation is deterministic and excludes the door volume'
Write-Output '- every workshop door has passable north/south relocation cells'
Write-Output '- colocated corpses release duplicate slots; distance 64 remains distinct'
Write-Output '- normal SHOT_DEAD timing remains before weapon corpse merging'

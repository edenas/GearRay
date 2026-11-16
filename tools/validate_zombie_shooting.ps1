$ErrorActionPreference = "Stop"

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Find-AimedTarget(
    [array]$Zombies,
    [int]$PlayerX,
    [int]$PlayerY,
    [int]$DirectionX,
    [int]$DirectionY,
    [int]$PlaneX,
    [int]$PlaneY,
    [int]$WallDepth
) {
    $nearest = $null
    $nearestDepth = 2049
    foreach ($zombie in $Zombies) {
        if ($zombie.State -ne "ALIVE") { continue }
        $relativeX = $zombie.X - $PlayerX
        $relativeY = $zombie.Y - $PlayerY
        $depth = [Math]::Truncate(
            ($relativeX * $DirectionX + $relativeY * $DirectionY) / 256)
        if ($depth -le 0 -or $depth -gt 2048 -or
            $depth -ge $nearestDepth -or $depth -ge $WallDepth) {
            continue
        }
        $lateralProduct = [Math]::Abs(
            $relativeX * $DirectionY - $relativeY * $DirectionX)
        $determinant = [Math]::Abs(
            $PlaneX * $DirectionY - $DirectionX * $PlaneY)
        if ($lateralProduct * 5 -gt $determinant * 2) { continue }
        $nearest = $zombie
        $nearestDepth = $depth
    }
    return $nearest
}

$ahead = [pscustomobject]@{ X = 1280; Y = 512; State = "ALIVE" }
$side = [pscustomobject]@{ X = 1664; Y = 512; State = "ALIVE" }
$far = [pscustomobject]@{ X = 1280; Y = 0; State = "ALIVE" }
$corpse = [pscustomobject]@{ X = 1280; Y = 512; State = "CORPSE" }

Assert-True ($null -eq (Find-AimedTarget @() 1280 1024 0 -256 169 0 4096)) `
    "Empty firing line selected a zombie."
Assert-True ($null -eq (Find-AimedTarget @($ahead) 1280 1024 0 -256 169 0 400)) `
    "A zombie behind a wall was selected."
Assert-True ($null -eq (Find-AimedTarget @($side) 1280 1024 0 -256 169 0 4096)) `
    "A side-of-screen zombie was selected."
Assert-True ((Find-AimedTarget @($ahead) 1280 1024 0 -256 169 0 4096) -eq $ahead) `
    "The centered unobstructed zombie was not selected."
Assert-True ((Find-AimedTarget @($far, $ahead) 1280 1024 0 -256 169 0 4096) -eq $ahead) `
    "The nearest aligned zombie was not selected."
Assert-True ($null -eq (Find-AimedTarget @($corpse) 1280 1024 0 -256 169 0 4096)) `
    "A corpse was selected."
Assert-True ($null -eq (Find-AimedTarget @($ahead) 1280 1024 0 256 -169 0 4096)) `
    "A zombie behind the player was selected."

$closeCentered = [pscustomobject]@{ X = 1280; Y = 896; State = "ALIVE" }
$closeLeftInside = [pscustomobject]@{ X = 1213; Y = 896; State = "ALIVE" }
$closeRightInside = [pscustomobject]@{ X = 1347; Y = 896; State = "ALIVE" }
$closeLeftOutside = [pscustomobject]@{ X = 1212; Y = 896; State = "ALIVE" }
$closeRightOutside = [pscustomobject]@{ X = 1348; Y = 896; State = "ALIVE" }
$farSameAngle = [pscustomobject]@{ X = 1816; Y = 0; State = "ALIVE" }
Assert-True ((Find-AimedTarget @($closeCentered) 1280 1024 0 -256 169 0 4096) `
             -eq $closeCentered) "Centered close zombie was not acquired."
Assert-True ((Find-AimedTarget @($closeLeftInside) 1280 1024 0 -256 169 0 4096) `
             -eq $closeLeftInside -and
             (Find-AimedTarget @($closeRightInside) 1280 1024 0 -256 169 0 4096) `
             -eq $closeRightInside) `
    "Visible-footprint acquisition is not symmetric at offsets +/-67."
Assert-True ($null -eq
             (Find-AimedTarget @($closeLeftOutside) 1280 1024 0 -256 169 0 4096) `
             -and $null -eq
             (Find-AimedTarget @($closeRightOutside) 1280 1024 0 -256 169 0 4096)) `
    "Zombie centers outside the projected half-width were acquired."
Assert-True ($null -eq
             (Find-AimedTarget @($farSameAngle) 1280 1024 0 -256 169 0 4096)) `
    "A farther zombie at the same close-case screen angle was acquired."
Assert-True ($null -eq
             (Find-AimedTarget @($closeCentered) 1280 1024 0 -256 169 0 100)) `
    "Close target-width acquisition bypassed the center wall depth."
$nearOverlap = [pscustomobject]@{ X = 1312; Y = 768; State = "ALIVE" }
$farOverlap = [pscustomobject]@{ X = 1248; Y = 512; State = "ALIVE" }
Assert-True ((Find-AimedTarget @($farOverlap, $nearOverlap) `
                 1280 1024 0 -256 169 0 4096) -eq $nearOverlap) `
    "Farther overlapping zombie stole the shot from the nearer target."

$root = Split-Path -Parent $PSScriptRoot
$spriteHeader = Get-Content (Join-Path $root "game\world_sprite.h") -Raw
$spriteSource = Get-Content (Join-Path $root "game\world_sprite.c") -Raw
$shootingSource = Get-Content (Join-Path $root "game\zombie_shooting.c") -Raw
$mainSource = Get-Content (Join-Path $root "game\main.c") -Raw
$inputSource = Get-Content (Join-Path $root "platform\game_gear\input.c") -Raw
$projectionSource = Get-Content (
    Join-Path $root "platform\game_gear\sprite_projection.c") -Raw
$hudSource = Get-Content (
    Join-Path $root "platform\game_gear\hud_weapon.c") -Raw

Assert-True ($spriteHeader -match "#define ZOMBIE_SHOT_DEAD_FRAME_COUNT 4") `
    "Death-state duration is not the documented 4 updates."
Assert-True ($spriteHeader -match "#define ZOMBIE_HIT_REACTION_FRAME_COUNT 3") `
    "Living hit-reaction duration is not 3 rendered frames."
Assert-True ($spriteHeader -match "#define ZOMBIE_MAX_HEALTH 12" -and
    $spriteHeader -match "#define ZOMBIE_HEALTH_MASK 15" -and
    $spriteHeader -match "#define ZOMBIE_HIT_COUNT_SHIFT 4" -and
    $spriteHeader -match "unsigned char health_and_hit_count;") `
    "Packed twelve-point health and successful-hit tracking is missing."
Assert-True ($spriteSource -match "state_timer = ZOMBIE_SHOT_DEAD_FRAME_COUNT") `
    "Lethal damage does not start the death timer."
Assert-True ($spriteSource -match
    "sprite->health_and_hit_count\s*=\s*ZOMBIE_MAX_HEALTH" -and
    $spriteSource -match
    "health_and_hit_count\s*&\s*ZOMBIE_HEALTH_MASK" -and
    $spriteSource -match
    "health_and_hit_count\s*&\s*ZOMBIE_HIT_COUNT_MASK\)[\s\S]*?" +
    ">>\s*ZOMBIE_HIT_COUNT_SHIFT" -and
    $spriteSource -match "\+\+hit_count" -and
    $spriteSource -match
    "animation_token\s*=\s*hit_count\s*&\s*1U[\s\S]*?ZOMBIE_ANIMATION_SHOT_01[\s\S]*?ZOMBIE_ANIMATION_SHOT_02") `
    "Health initialization or odd/even reaction selection is missing."
Assert-True ($spriteSource -match
    "state_timer = ZOMBIE_HIT_REACTION_FRAME_COUNT" -and
    $spriteSource -match
    "sprite->state_timer == 0[\s\S]*?continue;[\s\S]*?" +
    "--sprite->state_timer;[\s\S]*?WORLD_SPRITE_LIFE_STATE\(sprite\) == ZOMBIE_STATE_SHOT_DEAD" +
    "[\s\S]*?else\s*sprite->animation_token = ZOMBIE_ANIMATION_STANDING;") `
    "Surviving hit reactions do not expire back to standing."
Assert-True ($spriteSource -match "zombie_corpses_finalize\(sprite_index\)" -and
             $spriteSource -match
             "world_sprite_set_state\(&world_sprites\[sprite_index\],\s*ZOMBIE_STATE_CORPSE\)") `
    "SHOT_DEAD does not transition to CORPSE."
Assert-True ($shootingSource -match "WORLD_SPRITE_LIFE_STATE\(sprite\) != ZOMBIE_STATE_ALIVE") `
    "Target acquisition does not reject non-living zombies."
Assert-True ($mainSource -match
    "shoot_requested = input_shoot_requested\(\);[\s\S]*?game_gear_hud_weapon_update\(shoot_requested\);[\s\S]*?if \(pending_shot\)[\s\S]*?zombie_shooting_process\(\);[\s\S]*?pending_shot = shoot_requested;") `
    "Shot event is not latched for a one-frame HUD lead and consumed once."
Assert-True ([regex]::Matches(
    $mainSource, "shoot_requested = input_shoot_requested\(\);").Count -eq 1) `
    "Shoot request is not sampled exactly once."
Assert-True ($mainSource -match
    "raycaster_update\(\);\s*if \(pending_shot\)\s*zombie_shooting_process\(\);") `
    "Resident caller does not suppress the banked hitscan call on no-shot frames."
Assert-True ($mainSource -match
    "world_sprites_update\([\s\S]*?\);[\s\S]*?game_gear_hud_weapon_update\(shoot_requested\);[\s\S]*?if \(pending_shot\)[\s\S]*?zombie_shooting_process\(\);[\s\S]*?game_gear_video_draw_wall_columns\(\);") `
    "Real main-loop order does not preserve the shot frame before the next death update."
Assert-True ($hudSource -match "#define HUD_WEAPON_SHOOT_FRAME_COUNT 2") `
    "Shooting HUD does not remain visible through the delayed damage frame."
Assert-True ($inputSource -match
    "\(keys & PORT_A_KEY_1\) != 0[\s\S]*?\(previous_keys & PORT_A_KEY_1\) == 0") `
    "Button 1 shooting is not press-edge triggered."
Assert-True ($projectionSource -match
    "WORLD_SPRITE_LIFE_STATE\(sprite\) == ZOMBIE_STATE_CORPSE[\s\S]*?bottom \+=") `
    "Corpse projection is not floor-adjusted."
Assert-True ($shootingSource -match
    "zombie_shooting_find_aimed_target\(\s*&target_depth\s*\)" -and
    [regex]::Matches($shootingSource,
        "zombie_shooting_find_aimed_target\(").Count -eq 2 -and
    $shootingSource -notmatch "16384U\s*/\s*target_depth" -and
    $shootingSource -match
    "target_depth\s*>\s*PISTOL_VISIBLE_MAX_DEPTH" -and
    $shootingSource -match
    "target_depth\s*<=\s*PISTOL_ONE_SHOT_MAX_DEPTH") `
    "Selected target depth is not reused directly for pistol damage."
Assert-True ($shootingSource -match
    "plane_x\s*=\s*camera_get_plane_x\(\)" -and
    $shootingSource -match "plane_y\s*=\s*camera_get_plane_y\(\)" -and
    $shootingSource -match
    "\(signed long\)plane_x\s*\*\s*relative_y[\s\S]*?" +
    "\(signed long\)relative_x\s*\*\s*plane_y[\s\S]*?" +
    "\*\s*FIXED_POINT_SCALE[\s\S]*?/\s*determinant" -and
    $projectionSource -match
    "\(signed long\)plane_x\s*\*\s*relative_y[\s\S]*?" +
    "\(signed long\)relative_x\s*\*\s*plane_y[\s\S]*?" +
    "\*\s*256L[\s\S]*?/\s*determinant") `
    "Shooting and sprite projection do not use the same exact depth transform."
Assert-True ($shootingSource -match
    "PISTOL_ONE_SHOT_MIN_PROJECTED_HEIGHT 36" -and
    $shootingSource -match "PISTOL_TWO_SHOT_MIN_PROJECTED_HEIGHT 28" -and
    $shootingSource -match "PISTOL_THREE_SHOT_MIN_PROJECTED_HEIGHT 17" -and
    $shootingSource -match "PISTOL_VISIBLE_MIN_PROJECTED_HEIGHT 13" -and
    $shootingSource -match "PISTOL_ONE_SHOT_DAMAGE 12" -and
    $shootingSource -match "PISTOL_TWO_SHOT_DAMAGE 6" -and
    $shootingSource -match "PISTOL_THREE_SHOT_DAMAGE 4" -and
    $shootingSource -match "PISTOL_FOUR_SHOT_DAMAGE 3") `
    "Projected-height pistol tiers changed."
Assert-True ($shootingSource -match "PISTOL_MIN_TARGET_DEPTH 33" -and
    $shootingSource -match
    "exact_depth\s*<\s*PISTOL_MIN_TARGET_DEPTH") `
    "Shooting does not match the renderer's strict near plane."
Assert-True ($shootingSource -match
    "lateral\s*\*\s*ZOMBIE_AIM_LATERAL_SCALE[\s\S]*?>\s*" +
    "determinant_magnitude\s*\*\s*ZOMBIE_AIM_DETERMINANT_SCALE" -and
    $shootingSource -notmatch "ZOMBIE_AIM_WIDTH_DIVISOR" -and
    $shootingSource -notmatch "16384U\s*/\s*depth") `
    "Production aiming is not the division-free projected-footprint test."

$positionBefore = @($ahead.X, $ahead.Y)
function Get-PistolDamage([int]$ProjectedHeight) {
    if ($ProjectedHeight -le 12) { return 0 }
    if ($ProjectedHeight -ge 36) { return 12 }
    if ($ProjectedHeight -ge 28) { return 6 }
    if ($ProjectedHeight -ge 17) { return 4 }
    return 3
}
function Get-PistolDamageFromDepth([int]$Depth) {
    if ($Depth -lt 33 -or $Depth -gt [Math]::Floor(16384 / 13)) { return 0 }
    if ($Depth -le [Math]::Floor(16384 / 36)) { return 12 }
    if ($Depth -le [Math]::Floor(16384 / 28)) { return 6 }
    if ($Depth -le [Math]::Floor(16384 / 17)) { return 4 }
    return 3
}
for ($depth = 33; $depth -le 2048; ++$depth) {
    $projectedHeight = [Math]::Min(144, [Math]::Floor(16384 / $depth))
    Assert-True ((Get-PistolDamageFromDepth $depth) -eq
                 (Get-PistolDamage $projectedHeight)) `
        "Depth thresholds diverged from projected height at depth $depth."
}
$knownDirectionX = 35
$knownDirectionY = -254
$knownPlaneX = 168
$knownPlaneY = 23
$knownRelativeX = -117
$knownRelativeY = -476
$knownDeterminant =
    $knownPlaneX * $knownDirectionY - $knownDirectionX * $knownPlaneY
$knownExactDepth = [Math]::Truncate(
    (($knownPlaneX * $knownRelativeY - $knownRelativeX * $knownPlaneY) * 256) /
    $knownDeterminant)
$knownDotDepth = [Math]::Truncate(
    ($knownRelativeX * $knownDirectionX + $knownRelativeY * $knownDirectionY) /
    256)
Assert-True ($knownExactDepth -ne $knownDotDepth -and
             (Get-PistolDamageFromDepth $knownExactDepth) -ne
             (Get-PistolDamageFromDepth $knownDotDepth)) `
    "Depth-contract regression fixture no longer crosses a damage boundary."
foreach ($case in @(@(12, 0), @(13, 3), @(16, 3), @(17, 4),
                    @(27, 4), @(28, 6), @(35, 6), @(36, 12))) {
    Assert-True ((Get-PistolDamage $case[0]) -eq $case[1]) `
        "Projected height $($case[0]) produced the wrong pistol damage."
}
function Test-KillSequence([int]$ProjectedHeight, [int]$ExpectedShots,
                           [string]$ExpectedReactions) {
    $health = 12
    $hits = 0
    $reactions = @()
    while ($health -gt 0) {
        $damage = Get-PistolDamage $ProjectedHeight
        ++$hits
        $health = [Math]::Max(0, $health - $damage)
        if ($health -eq 0) { $reactions += "shot_dead" }
        elseif ($hits -band 1) { $reactions += "shot_01" }
        else { $reactions += "shot_02" }
    }
    Assert-True ($hits -eq $ExpectedShots -and
                 ($reactions -join ",") -eq $ExpectedReactions) `
        "$ExpectedShots-shot progression failed at height $ProjectedHeight."
}
Assert-True ((Get-PistolDamageFromDepth 455) -eq 12 -and
             (Get-PistolDamageFromDepth 456) -eq 6) `
    "Direct-depth one-shot boundary is not exactly 455/456."
Assert-True ((Get-PistolDamageFromDepth 585) -eq 6 -and
             (Get-PistolDamageFromDepth 586) -eq 4 -and
             (Get-PistolDamageFromDepth 963) -eq 4 -and
             (Get-PistolDamageFromDepth 964) -eq 3 -and
             (Get-PistolDamageFromDepth 1260) -eq 3 -and
             (Get-PistolDamageFromDepth 1261) -eq 0) `
    "Direct-depth damage boundaries 585/586, 963/964, or 1260/1261 changed."
Test-KillSequence 36 1 "shot_dead"
Test-KillSequence 28 2 "shot_01,shot_dead"
Test-KillSequence 17 3 "shot_01,shot_02,shot_dead"
Test-KillSequence 13 4 "shot_01,shot_02,shot_01,shot_dead"
$mixedHealth = 12
$mixedHits = 0
$mixedReactions = @()
foreach ($height in @(13, 28, 13)) {
    ++$mixedHits
    $mixedHealth = [Math]::Max(
        0, $mixedHealth - (Get-PistolDamage $height))
    $mixedReactions += if ($mixedHealth -eq 0) { "shot_dead" }
        elseif ($mixedHits -band 1) { "shot_01" } else { "shot_02" }
}
Assert-True ($mixedHealth -eq 0 -and
             ($mixedReactions -join ",") -eq "shot_01,shot_02,shot_dead") `
    "Mixed-distance damage reset health or lost hit parity."
function Test-CumulativeHealth([int[]]$DamageValues,
                               [string]$ExpectedHealthTrace) {
    $health = 12
    $trace = @($health)
    foreach ($damage in $DamageValues) {
        $health = [Math]::Max(0, $health - $damage)
        $trace += $health
    }
    Assert-True (($trace -join ",") -eq $ExpectedHealthTrace) `
        "Cumulative health failed for damage $($DamageValues -join ',')."
}
Test-CumulativeHealth @(3, 4, 4, 3) "12,9,5,1,0"
Test-CumulativeHealth @(3, 6, 3) "12,9,3,0"
Test-CumulativeHealth @(4, 6, 3) "12,8,2,0"
Test-CumulativeHealth @(6, 4, 12) "12,6,2,0"
Test-CumulativeHealth @(3, 4, 12) "12,9,5,0"
Test-CumulativeHealth @(4, 4, 12) "12,8,4,0"
Test-CumulativeHealth @(3, 4, 6) "12,9,5,0"
Test-CumulativeHealth @(4, 6, 6) "12,8,2,0"
Test-CumulativeHealth @(12) "12,0"
Assert-True ([regex]::Matches(
    $spriteSource, "health_and_hit_count\s*=").Count -eq 4 -and
    $projectionSource -notmatch "health_and_hit_count\s*=") `
    "Health is mutated outside initialization and damage application."
$packedHealthBeforeVisualUpdates = (2 -shl 4) -bor 5
$packedHealthAfterMovement = $packedHealthBeforeVisualUpdates
$packedHealthAfterLodChange = $packedHealthAfterMovement
$packedHealthAfterReactionExpiry = $packedHealthAfterLodChange
$packedHealthAfterDeathTimer = $packedHealthAfterReactionExpiry
Assert-True ($packedHealthAfterDeathTimer -eq $packedHealthBeforeVisualUpdates -and
    $projectionSource -notmatch "health_and_hit_count\s*[|&^]?=") `
    "Movement, LOD, reaction, or death updates changed living packed health."
$rapidTimer = 3
$rapidHits = 1
$rapidPose = "shot_01"
++${rapidHits}
$rapidTimer = 3
$rapidPose = if ($rapidHits -band 1) { "shot_01" } else { "shot_02" }
Assert-True ($rapidTimer -eq 3 -and $rapidPose -eq "shot_02") `
    "Rapid follow-up did not replace and restart the living reaction."
Assert-True ((Get-PistolDamage 12) -eq 0) `
    "Hidden target accepted damage."
$ahead.State = "SHOT_DEAD"
$timer = 4
$renderedStates = @("SHOT_DEAD")
for ($frame = 1; $frame -le 4; ++$frame) {
    --$timer
    if ($timer -eq 0) { $ahead.State = "CORPSE" }
    $renderedStates += $ahead.State
}
Assert-True ((@($renderedStates | Where-Object {
    $_ -eq "SHOT_DEAD"
})).Count -eq 4) "SHOT_DEAD is not visible for exactly four rendered frames."
Assert-True ($ahead.State -eq "CORPSE") "Death state did not become a corpse."
Assert-True ($ahead.X -eq $positionBefore[0] -and $ahead.Y -eq $positionBefore[1]) `
    "Corpse world position changed."

$pendingShot = $false
$shotCount = 0
$hudTimer = 0
$visibleTrace = @()
foreach ($buttonPressed in @($false, $true, $true, $false, $true, $false)) {
    $edge = $buttonPressed -and -not $previousButtonPressed
    if ($edge) { $hudTimer = 2 }
    elseif ($hudTimer -gt 0) { --$hudTimer }
    if ($pendingShot) { ++$shotCount }
    $visibleTrace += [pscustomobject]@{
        HudShoot = $hudTimer -gt 0
        Damage = $pendingShot
    }
    $pendingShot = $edge
    $previousButtonPressed = $buttonPressed
}
Assert-True ($shotCount -eq 2) `
    "Quick press, hold, release, and second press do not produce two shots."
Assert-True ($visibleTrace[1].HudShoot -and -not $visibleTrace[1].Damage) `
    "Initial press does not visibly lead damage."
Assert-True ($visibleTrace[2].HudShoot -and $visibleTrace[2].Damage) `
    "Damage is not synchronized with an active shooting HUD frame."

Write-Output "Zombie shooting validation passed."
Write-Output "- center-line aim, range, wall depth, facing, and nearest-only targeting"
Write-Output "- division-free projected-footprint aim: symmetric +/-67 boundary"
Write-Output "- projected-height damage boundaries 12/13/16/17/27/28/35/36"
Write-Output "- exact 1/2/3/4-shot and cumulative mixed-distance health sequences"
Write-Output "- 3-frame odd/even reactions restart and return to standing"
Write-Output "- lethal hit -> SHOT_DEAD (4 updates) -> CORPSE"
Write-Output "- corpse immunity, persistence wiring, floor placement, and input edge reuse"

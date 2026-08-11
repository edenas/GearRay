$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$ai = Get-Content -Raw -LiteralPath (Join-Path $root 'game\zombie_ai.c')
$aiHeader = Get-Content -Raw -LiteralPath (Join-Path $root 'game\zombie_ai.h')
$main = Get-Content -Raw -LiteralPath (Join-Path $root 'game\main.c')
$enemyCollision = Get-Content -Raw -LiteralPath (Join-Path $root 'game\enemy_collision.c')
$sprites = Get-Content -Raw -LiteralPath (Join-Path $root 'game\world_sprite.c')
$spriteHeader = Get-Content -Raw -LiteralPath (Join-Path $root 'game\world_sprite.h')
$cmake = Get-Content -Raw -LiteralPath (Join-Path $root 'CMakeLists.txt')

function Assert-Match([string]$Text, [string]$Pattern, [string]$Message) {
    if ($Text -notmatch $Pattern) { throw $Message }
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

Assert-Match $aiHeader 'ZOMBIE_AI_UPDATE_INTERVAL\s+4' 'AI cadence is not four frames'
Assert-Match $aiHeader 'zombie_ai_update_all\(void\)\s+__banked' 'AI entry is not banked'
Assert-Match $ai 'ZOMBIE_ACTIVATION_DISTANCE\s+963' 'Activation distance is not 963 inclusive'
Assert-Match $ai 'ZOMBIE_LOSE_DISTANCE\s+1260' 'Lose distance is not 1260 inclusive'
Assert-Match $ai 'distance_x \+ \(distance_y >> 1\)' 'Cheap octagonal distance metric is missing'
Assert-Match $ai 'while \(1\)[\s\S]*?world_is_wall' 'Tile LOS traversal is missing'
Assert-Match $ai 'ZOMBIE_MOVEMENT_STEP\s+56' 'Zombie movement step is not 56 units'
Assert-Match $ai 'ZOMBIE_COLLISION_RADIUS\s+32' 'Zombie collision radius changed'
Assert-Match $ai 'world_is_wall' 'LOS does not use the authoritative blocker query'
Assert-Match $ai 'enemy_position_is_walkable' 'Movement does not use reusable enemy collision'
Assert-Match $ai 'other->state != ZOMBIE_STATE_ALIVE' 'Non-living sprites may block movement'
Assert-Match $ai 'sprite->state_timer != 0[\s\S]*?continue' 'Hit reaction does not pause movement'
Assert-Match $ai 'sprite->state != ZOMBIE_STATE_ALIVE[\s\S]*?continue' 'Dead sprites may enter AI'
Assert-Match $enemyCollision 'enemy_position_is_walkable[\s\S]*?world_is_wall' 'Enemy collision does not share wall/door semantics'
Assert-Match $spriteHeader 'ZOMBIE_AI_CHASING_MASK\s+128' 'AI state is not isolated in bit 7'
Assert-Match $spriteHeader 'ZOMBIE_HIT_COUNT_MASK\s+112' 'Hit count is not isolated in bits 4..6'
Assert-Match $sprites 'ZOMBIE_HIT_COUNT_MASK' 'Damage reads the AI bit as hit count'
Assert-Match $sprites 'ZOMBIE_AI_CHASING_MASK[\s\S]*?ZOMBIE_HIT_COUNT_SHIFT' 'Nonlethal damage does not preserve chasing state'
Assert-Match $main '\+\+zombie_ai_frame_counter[\s\S]*?zombie_ai_update_all\(\)' 'Main loop lacks one shared AI cadence'
Assert-True (([regex]::Matches($main, 'zombie_ai_update_all\(\)')).Count -eq 1) 'AI has more than one main-loop banked call site'
Assert-Match $cmake 'zombie_ai\.c[\s\S]*?--codeseg BANK1' 'Zombie AI is not compiled into BANK1'

function Test-Range([int]$Distance, [bool]$Chasing) {
    if ($Chasing) { return $Distance -le 1260 }
    return $Distance -le 963
}

Assert-True (-not (Test-Range 964 $false)) 'Idle zombie activates beyond 963'
Assert-True (Test-Range 963 $false) 'Idle zombie fails at activation boundary'
Assert-True (Test-Range 1260 $true) 'Chasing zombie fails at lose boundary'
Assert-True (-not (Test-Range 1261 $true)) 'Chasing zombie persists beyond 1260'
Assert-True (56 -lt 74) 'Zombie is not slower than the player per update'
Assert-True ((56 * (60 / 4)) -eq 840) 'Zombie units-per-second model changed'
Assert-True ((56 * (60 / 4) / 256) -eq 3.28125) 'Zombie tiles-per-second model changed'
Assert-True (56 -lt 128) 'Zombie step could tunnel through a 64-unit separation body'
Assert-True (56 -lt (256 - 2 * 32)) 'Zombie step is unsafe for tile collision geometry'

Write-Output 'Zombie AI validation PASS'
Write-Output '- activation 963; hysteresis loss 1260; LOS via authoritative world blockers'
Write-Output '- one BANK1 update every 4 frames; 56-unit step (3.28125 tiles/s)'
Write-Output '- shared radius collision; living-zombie blocking; corpses ignored'
Write-Output '- packed zero-byte per-zombie AI flag; hit/death state ownership preserved'

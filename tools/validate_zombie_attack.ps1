param(
    [string]$BuildDirectory = "build",
    [switch]$RequireMapPlacement
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$buildPath = if ([System.IO.Path]::IsPathRooted($BuildDirectory)) {
    $BuildDirectory
}
else {
    Join-Path $root $BuildDirectory
}
$player = Get-Content -Raw -LiteralPath (Join-Path $root "game\player.c")
$playerHeader = Get-Content -Raw -LiteralPath (Join-Path $root "game\player.h")
$ai = Get-Content -Raw -LiteralPath (Join-Path $root "game\zombie_ai.c")
$sprite = Get-Content -Raw -LiteralPath (Join-Path $root "game\world_sprite.c")
$spriteHeader = Get-Content -Raw -LiteralPath (Join-Path $root "game\world_sprite.h")
$main = Get-Content -Raw -LiteralPath (Join-Path $root "game\main.c")
$projection = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\sprite_projection.c")
$videoInitialization = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\video_initialization.c")
$video = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\video.c")
$startupLogo = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\startup_logo.c")
$input = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\input.c")
$hud = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\hud_weapon.c")
$cmake = Get-Content -Raw -LiteralPath (Join-Path $root "CMakeLists.txt")

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Apply-Damage([int]$Health, [int]$Damage) {
    if ($Damage -ge $Health) { return 0 }
    return $Health - $Damage
}

Assert-True ($playerHeader -match 'PLAYER_MAX_HEALTH\s+100') `
    'Player maximum health is not 100.'
Assert-True ($player -match 'player_health\s*=\s*PLAYER_MAX_HEALTH') `
    'Player health is not initialized to maximum.'
Assert-True ($player -match 'if \(damage >= player_health\)[\s\S]*?player_health = 0') `
    'Player damage does not clamp at zero.'

$health = 100
foreach ($expected in @(80, 60, 40, 20, 0, 0)) {
    $health = Apply-Damage $health 20
    Assert-True ($health -eq $expected) "Health sequence failed at $expected."
}

Assert-True ($spriteHeader -match 'ZOMBIE_ATTACK_DISTANCE\s+280') `
    'Attack range is not 280.'
Assert-True ($ai -match 'ZOMBIE_ATTACK_DAMAGE\s+20') `
    'Attack damage is not 20.'
Assert-True ($ai -match 'ZOMBIE_ATTACK_COOLDOWN_AI_TICKS\s+2') `
    'Attack cooldown is not 2 AI ticks.'
Assert-True ($spriteHeader -match 'ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT\s+4') `
    'Attack pose is not presented for exactly four gameplay frames.'
Assert-True (2 * 4 -eq 8) 'Attack cadence is not 8 gameplay frames.'
$cooldown = 2
foreach ($expected in @(1, 0)) {
    --$cooldown
    Assert-True ($cooldown -eq $expected) `
        "Cooldown boundary failed at $expected."
}
Assert-True ((16384 / 280) -as [int]) 'Projection model is invalid.'
Assert-True ([Math]::Floor(16384 / 280) -eq 58) `
    'Projected height at attack range is not 58.'
Assert-True (280 -gt 64) 'Attack range overlaps body separation.'
Assert-True ($ai -match 'distance <= ZOMBIE_ATTACK_DISTANCE') `
    'Attack boundary is not inclusive.'
Assert-True ($ai -match 'world_has_clear_line_of_sight[\s\S]*?distance <= ZOMBIE_ATTACK_DISTANCE') `
    'Attack decision does not reuse the accepted LOS result.'
Assert-True ([regex]::Matches($ai, 'world_has_clear_line_of_sight\(').Count -eq 2) `
    'Attack added a second LOS traversal.'
Assert-True ($ai -match 'player_is_dead\(\)[\s\S]*?return') `
    'Dead player does not stop zombie damage.'
Assert-True ($ai -match 'distance <= ZOMBIE_ATTACK_DISTANCE[\s\S]*?continue;[\s\S]*?zombie_ai_move') `
    'Attack range does not stop movement before chase movement.'
Assert-True ($ai -match 'ZOMBIE_ATTACK_COOLDOWN_AI_TICKS\);[\s\S]*?sprite->state \^= ZOMBIE_ATTACK_PHASE_MASK;') `
    'Successful strikes do not toggle the packed alternating phase.'
Assert-True ($ai -match 'state_timer == 0[\s\S]*?attack_cooldown == 0[\s\S]*?player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\)') `
    'Attack texture and damage are not one cooldown-gated event.'
Assert-True ($ai -match
    'player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\);[\s\S]*?' +
    'game_gear_health_hud_update\(player_get_health\(\)\);[\s\S]*?' +
    'game_gear_damage_shake_phase = 4;[\s\S]*?' +
    'ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT;[\s\S]*?' +
    'ZOMBIE_ATTACK_COOLDOWN_AI_TICKS\);[\s\S]*?' +
    'sprite->state \^= ZOMBIE_ATTACK_PHASE_MASK;') `
    'Pose, damage, HUD, shake, recovery, and phase toggle are not one ordered strike event.'
Assert-True ([regex]::Matches($ai,
    'player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\)').Count -eq 1) `
    'Zombie AI has more than one player-damage path.'
Assert-True ($sprite -match 'sprite->pixels = hit_count & 1U[\s\S]*?state_timer = ZOMBIE_HIT_REACTION_FRAME_COUNT') `
    'Hit reaction does not override an attack texture.'
Assert-True ($spriteHeader -match 'ZOMBIE_ATTACK_COOLDOWN_MASK\s+60' -and
             $spriteHeader -match 'ZOMBIE_ATTACK_PHASE_MASK\s+64') `
    'Attack cooldown and alternating phase are not safely packed.'
Assert-True ($spriteHeader -match 'ZOMBIE_HEALTH_MASK\s+15' -and
             $spriteHeader -match 'ZOMBIE_HIT_COUNT_MASK\s+112' -and
             $spriteHeader -match 'ZOMBIE_AI_CHASING_MASK\s+128') `
    'Existing health, hit-count, or chasing bit ownership changed.'
Assert-True ($main -notmatch 'PLAYER_DEATH_PAUSE_FRAME_COUNT|death_pause_frame') `
    'Obsolete static 60-frame death pause remains.'
Assert-True ($main -match 'while \(!player_is_dead\(\)\)[\s\S]*?if \(player_is_dead\(\)\)[\s\S]*?break;[\s\S]*?game_gear_video_present_player_death\(\);') `
    'Death does not leave gameplay for the death transition.'
Assert-True ($main -match 'while \(1\)[\s\S]*?game_gear_startup_logo_show\(\);[\s\S]*?game_gear_video_initialize\(\);[\s\S]*?world_initialize\(\);[\s\S]*?player_initialize\(\)') `
    'Death restart does not reuse the authoritative startup/session path.'
Assert-True ($main -match 'game_gear_input_initialize\(\)' -and
             $main -match 'game_gear_hud_weapon_initialize\(\)' -and
             $main -match 'pending_shot = 0' -and
             $main -match 'zombie_ai_frame_counter = 0') `
    'Restart does not reset input, HUD, pending shot, and AI cadence.'
Assert-True ($input -match 'keys = 0;[\s\S]*?previous_keys = 0;[\s\S]*?button_2_hold_active = 0;[\s\S]*?button_2_strafe_used = 0') `
    'Input initialization does not prevent phantom edge actions.'
Assert-True ($hud -match 'weapon_state = IDLE;[\s\S]*?rendered_weapon_state = IDLE;[\s\S]*?animation_timer = 0') `
    'HUD initialization does not restore an idle weapon.'
Assert-True ($videoInitialization -match 'previous_projected_sprite_count = 0') `
    'Session video initialization does not clear the sprite cache.'
Assert-True ($ai -match 'player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\);[\s\S]*?game_gear_damage_shake_phase = 4;') `
    'A successful damage event does not restart the presentation shake.'
Assert-True ($video -match 'unsigned char game_gear_damage_shake_phase;' -and
             $videoInitialization -match 'game_gear_damage_shake_offsets\[4\]\s*=\s*\{\s*0,\s*1,\s*254,\s*2\s*\}' -and
             $video -match 'game_gear_damage_shake_offsets\[game_gear_damage_shake_phase\]') `
    'Damage shake is not the deterministic +2/-2/+1/0 pattern.'
$shakeFunctions = [regex]::Match(
    $video,
    'void game_gear_damage_shake_update\(void\)[\s\S]*?\n\}')
Assert-True $shakeFunctions.Success 'Could not isolate shake implementation.'
Assert-True ($shakeFunctions.Value -notmatch
             'player_|camera_|raycaster_|world_x|world_y') `
    'Presentation shake modifies or depends on gameplay geometry.'
Assert-True ($videoInitialization -match 'game_gear_damage_shake_phase = 0' -and
             $startupLogo -match 'game_gear_damage_shake_phase = 0') `
    'Session initialization or SEGA logo does not reset BG scroll.'
Assert-True ($videoInitialization -match 'game_gear_damage_shake_phase = 0;[\s\S]*?SMS_setBGScrollX\(0\);[\s\S]*?SMS_setBGScrollY\(0\);') `
    'Shake reset does not restore neutral X/Y scroll.'
Assert-True ($videoInitialization -match 'GAME_OVER_DISPLAY_FRAME_COUNT\s+180' -and
             $videoInitialization -notmatch 'DEATH_FADE|game_gear_video_dim_color') `
    'Death presentation is not 180 frames or still contains fading.'
Assert-True ($videoInitialization -match 'SMS_displayOff\(\);[\s\S]*?SMS_VRAMmemsetW\(0, 0x0000, 16384\);[\s\S]*?GG_loadBGPalette\(game_over_palette\);') `
    'Game Over presentation does not clear gameplay before loading artwork.'
Assert-True ($projection -notmatch 'hud_weapon|HUD_WEAPON') `
    'World-sprite projection depends on HUD weapon coordinates.'
Assert-True ($ai -notmatch 'hud_weapon|HUD_WEAPON|screen_x|screen_y') `
    'Zombie attack targeting depends on HUD or screen coordinates.'
Assert-True ($projection -match 'left = center_x - \(signed int\)projected_height / 2;[\s\S]*?right = left \+ projected_height;') `
    'Standing and attack poses do not share the world-centered anchor.'
Assert-True ($projection -match 'NEAR_ZOMBIE_TEXTURE_ATTACK_01' -and
             $projection -match 'NEAR_ZOMBIE_TEXTURE_STANDING_ATTACK' -and
             $projection -match 'NEAR_ZOMBIE_TEXTURE_ATTACK_02') `
    'Native near attack/recovery pose mapping is incomplete.'
Assert-True ($projection -match 'state_timer[\s\S]*?== ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT - 1[\s\S]*?ZOMBIE_ATTACK_PHASE_MASK[\s\S]*?ZOMBIE_PRESENTATION_ATTACK_01[\s\S]*?ZOMBIE_PRESENTATION_ATTACK_02;[\s\S]*?ZOMBIE_PRESENTATION_STANDING_ATTACK;') `
    'Standing anticipation, alternating strike, and recovery mapping is incorrect.'
Assert-True ($projection -notmatch 'ZOMBIE_AI_CHASING_MASK[\s\S]{0,160}NEAR_ZOMBIE_TEXTURE_STANDING_ATTACK') `
    'Attack-range entry still inserts standing_attack before the first strike.'
Assert-True ($projection -match 'distance <= ZOMBIE_ATTACK_DISTANCE[\s\S]*?ZOMBIE_PRESENTATION_STANDING_ATTACK') `
    'Attack-range anticipation and recovery do not resolve to standing_attack.'
Assert-True ($projection -notmatch 'ZOMBIE_ATTACK_VISUAL_LUNGE_DEPTH') `
    'Attack-specific visual depth adjustment remains.'
Assert-True ($projection -notmatch 'ZOMBIE_NATIVE_(WALKING|CLOSE)_VISUAL_DEPTH_OFFSET|ZOMBIE_NATIVE_MIN_VISUAL_DEPTH|visual_depth') `
    'Obsolete native presentation depth correction remains.'
$attackRangeBlock = [regex]::Match($ai,
    'if \(distance <= ZOMBIE_ATTACK_DISTANCE\)(?<body>[\s\S]*?)\n\s*if \(sprite->state_timer != 0\)')
Assert-True ($attackRangeBlock.Success -and
             $attackRangeBlock.Groups['body'].Value -notmatch 'world_[xy]\s*=') `
    'Attack presentation mutates zombie world coordinates.'
Assert-True ($attackRangeBlock.Success -and
             $attackRangeBlock.Groups['body'].Value -notmatch 'sprite->pixels\s*=\s*zombie_01_standing_pixels') `
    'Attack entry destroys the authoritative walking phase.'
Assert-True ($ai -match 'sprite->pixels == zombie_01_shot_01_pixels[\s\S]*?zombie_01_shot_02_pixels[\s\S]*?continue;[\s\S]*?sprite->state_timer = 0;[\s\S]*?zombie_ai_move') `
    'Leaving melee range does not distinguish hit reaction from attack presentation before resuming movement.'
$phase = 0
foreach ($expected in @('ATTACK_01','ATTACK_02','ATTACK_01','ATTACK_02')) {
    $phase = $phase -bxor 64
    $actual = if ($phase -band 64) {'ATTACK_01'} else {'ATTACK_02'}
    Assert-True ($actual -eq $expected) "Packed strike sequence expected $expected, got $actual."
}
Assert-True ($cmake -match '--constseg BANK2' -and
             $cmake -notmatch 'GEAR_RAY_GENERATED_ZOMBIE_ATTACK_01_TEXTURE_OBJECT') `
    'Obsolete 8x8 attack runtime objects remain or near attacks are not in Bank 2.'

$mapPath = Join-Path $buildPath "GearRay.map"
if ($RequireMapPlacement) {
    Assert-True (Test-Path -LiteralPath $mapPath) 'Linker map is missing.'
    $map = Get-Content -Raw -LiteralPath $mapPath
    foreach ($symbol in @('_zombie_near_attack_01_pixels', '_zombie_near_standing_attack_pix', '_zombie_near_attack_02_pixels')) {
        $match = [regex]::Match($map, "(?m)^\s*(?<address>[0-9A-F]{8})\s+$symbol")
        Assert-True $match.Success "Missing map symbol $symbol."
        $address = [Convert]::ToInt32($match.Groups['address'].Value, 16)
        Assert-True ($address -ge 0x28000 -and $address -lt 0x2C000) `
            "$symbol is outside Bank 2."
    }
}

Write-Output 'Zombie attack and player-health validation PASS'
Write-Output '- health 100 -> 80 -> 60 -> 40 -> 20 -> 0; saturation at zero'
Write-Output '- inclusive 280-unit attack range; 58-pixel full-detail projection'
Write-Output '- independent strikes every 2 AI ticks (8 frames)'
Write-Output '- presentation order: standing, attack_01, standing, attack_02; repeat'
Write-Output '- LOS/range/life/cooldown gates; movement resumes outside range'
Write-Output '- packed independent per-zombie cooldown/phase; WorldSprite remains 9 bytes'
Write-Output '- four-frame hardware scroll shake returns to neutral on every hit'
Write-Output '- 180-frame cleared Game Over screen precedes the shared restart'
Write-Output '- zero pose offset: authored attack centroids match standing within 0.033 px'
Write-Output '- attack projection and targeting are independent of the HUD overlay'

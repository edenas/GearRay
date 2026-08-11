$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$main = Get-Content -Raw -LiteralPath (Join-Path $root "game\main.c")
$video = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\video.c")
$startupLogo = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\startup_logo.c")
$cmake = Get-Content -Raw -LiteralPath (Join-Path $root "CMakeLists.txt")

$orderedCalls = @(
    'game_gear_startup_logo_show();',
    'game_gear_video_initialize();',
    'raycaster_update();',
    'game_gear_video_draw_wall_columns();',
    'game_gear_video_draw_viewport_border();',
    'SMS_displayOff();',
    'SMS_waitForVBlank();',
    'SMS_displayOn();',
    'while (1)'
)

$offset = -1
foreach ($call in $orderedCalls) {
    $nextOffset = $main.IndexOf($call, $offset + 1)
    if ($nextOffset -le $offset) {
        throw "Startup operation missing or out of order: $call"
    }
    $offset = $nextOffset
}

if ($main -notmatch
    'void main\(void\)[\s\S]*?\{[\s\S]*?' +
    'game_gear_startup_logo_show\(\);[\s\S]*?' +
    'game_gear_video_initialize\(\);[\s\S]*?' +
    'game_gear_input_initialize\(\);[\s\S]*?' +
    'game_gear_hud_weapon_initialize\(\);[\s\S]*?' +
    'world_initialize\(\);') {
    throw 'Gameplay initialization does not begin strictly after the logo'
}
if ($startupLogo -match
    'world_|raycaster_|hud_weapon|sprite_|zombie_|player_|camera_') {
    throw 'Startup logo module depends on gameplay or renderer code'
}
if ($startupLogo -notmatch '#define STARTUP_LOGO_FRAME_COUNT 180' -or
    $startupLogo -notmatch '#define STARTUP_LOGO_FIRST_TILE 1' -or
    $startupLogo -notmatch
    'SMS_displayOff\(\);[\s\S]*?' +
    'SMS_VRAMmemsetW\(0, 0x0000, 16384\);[\s\S]*?' +
    'GG_loadBGPalette\(sega_logo_palette\);[\s\S]*?' +
    'SMS_loadTiles\(sega_logo_tiles,[\s\S]*?' +
    'SMS_loadTileMapArea\(SEGA_LOGO_TILE_ORIGIN_X,[\s\S]*?' +
    'SMS_displayOn\(\);[\s\S]*?' +
    'frame = STARTUP_LOGO_FRAME_COUNT; frame != 0; --frame[\s\S]*?' +
    'SMS_displayOff\(\);[\s\S]*?' +
    'SMS_VRAMmemsetW\(0, 0x0000, 16384\);') {
    throw 'Startup logo display, timeout, blackout, or VRAM reset changed'
}
if ([regex]::Matches($startupLogo,
        'GG_loadBGPalette\(sega_logo_palette\);').Count -ne 1 -or
    [regex]::Matches($startupLogo,
        'SMS_loadTiles\(sega_logo_tiles,').Count -ne 1 -or
    [regex]::Matches($startupLogo,
        'SMS_loadTileMapArea\(').Count -ne 1) {
    throw 'Startup logo palette or VRAM content is uploaded repeatedly'
}
if ($cmake -notmatch
    'assets/logos/sega_logo\.png[\s\S]*?' +
    'generate_startup_logo\.ps1[\s\S]*?' +
    'generated_sega_logo\.rel' -or
    $cmake -notmatch
    'startup_logo\.c[\s\S]*?--codeseg BANK1') {
    throw 'Startup logo asset generation or isolated Bank 1 placement is missing'
}

if ([regex]::Matches(
        $main, 'game_gear_video_draw_viewport_border\(\);').Count -ne 1) {
    throw 'Debug border must be drawn exactly once during startup'
}
if ($main -match 'SMS_autoSetUpTextRenderer\(\);') {
    throw 'Profile-only SMSlib font setup must not consume fixed Bank 0'
}
if ($video -notmatch
    'SMS_load1bppTiles\(debug_border_tiles,[\s\S]*?sizeof\(debug_border_tiles\),\s*0,\s*12\);') {
    throw 'Debug border is not loaded with white BG index 12'
}

Write-Output 'Startup-order validation PASS'
Write-Output '- isolated 180-frame SEGA logo precedes every gameplay initializer'
Write-Output '- dedicated palette and native logo VRAM content upload exactly once'
Write-Output '- display blanks and VRAM clears before gameplay palette/content load'
Write-Output '- complete gameplay frame and border precede display enable'
Write-Output '- no profile-only SMSlib font or palette-repair startup path'
Write-Output '- static debug border is uploaded once with white BG index 12'

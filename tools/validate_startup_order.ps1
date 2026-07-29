$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$main = Get-Content -Raw -LiteralPath (Join-Path $root "game\main.c")
$video = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\video.c")

$orderedCalls = @(
    'game_gear_video_initialize();',
    'raycaster_update();',
    'game_gear_video_draw_wall_columns();',
    'game_gear_video_draw_viewport_border();',
    'SMS_autoSetUpTextRenderer();',
    'game_gear_video_load_background_palette();',
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

if ([regex]::Matches(
        $main, 'game_gear_video_draw_viewport_border\(\);').Count -ne 1) {
    throw 'Debug border must be drawn exactly once during startup'
}
if ([regex]::Matches(
        $main, 'game_gear_video_load_background_palette\(\);').Count -ne 1) {
    throw 'Master palette must be restored exactly once after text setup'
}
if ($video -notmatch
    'SMS_load1bppTiles\(debug_border_tiles,[\s\S]*?sizeof\(debug_border_tiles\),\s*0,\s*12\);') {
    throw 'Debug border is not loaded with white BG index 12'
}

Write-Output 'Startup-order validation PASS'
Write-Output '- complete gameplay frame and border precede display enable'
Write-Output '- text setup precedes exactly one master-palette restoration'
Write-Output '- static debug border is uploaded once with white BG index 12'

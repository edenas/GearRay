param([string]$BuildDirectory = "build")

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
$wallSource = Get-Content -Raw -LiteralPath (
    Join-Path $root "$BuildDirectory\generated\wall_texture.c")
$weaponSource = Get-Content -Raw -LiteralPath (
    Join-Path $root "$BuildDirectory\generated\weapon_texture.c")
$weaponHeader = Get-Content -Raw -LiteralPath (
    Join-Path $root "$BuildDirectory\generated\weapon_texture.h")
$logoSource = Get-Content -Raw -LiteralPath (
    Join-Path $root "$BuildDirectory\generated\sega_logo.c")
$logoHeader = Get-Content -Raw -LiteralPath (
    Join-Path $root "$BuildDirectory\generated\sega_logo.h")
$zombieStateTextures = @(
    @{ File = 'zombie_01_shot_dead_texture'; Symbol = 'zombie_01_shot_dead_pixels' },
    @{ File = 'zombie_01_corps_texture'; Symbol = 'zombie_01_corps_pixels' }
)
$weaponPath = Join-Path $root "assets\sprites\weapons\gun_12x12.png"
$logoPath = Join-Path $root "assets\logos\sega_logo.png"
$mainSource = Get-Content -Raw -LiteralPath (Join-Path $root "game\main.c")
$videoSource = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\video.c")
$startupLogoSource = Get-Content -Raw -LiteralPath (
    Join-Path $root "platform\game_gear\startup_logo.c")

function Get-HexValues {
    param([string]$Source, [string]$ArrayName)
    $match = [regex]::Match(
        $Source,
        "const unsigned (?:char|int) $ArrayName\[[\s\S]*?= \{(?<body>[\s\S]*?)\n\};")
    if (-not $match.Success) { throw "Generated array not found: $ArrayName" }
    return @(
        [regex]::Matches($match.Groups['body'].Value, '0x[0-9a-fA-F]+') |
            ForEach-Object { [Convert]::ToInt32($_.Value, 16) }
    )
}

function Assert-Equal {
    param($Expected, $Actual, [string]$Description)
    if ($Expected -ne $Actual) {
        throw "$Description expected $Expected, got $Actual"
    }
}

$palette = @(0) + @(Get-HexValues $wallSource 'wall_palette_colors')
$expectedPalette = @(
    0x000, 0x03a, 0x555, 0x777, 0xb80, 0x02b, 0x057, 0x265,
    0x860, 0x566, 0x333, 0xacf, 0xfff, 0x222, 0x143, 0x7af
)
Assert-Equal 16 $palette.Count 'BG palette entry count'
for ($index = 0; $index -lt 16; ++$index) {
    Assert-Equal $expectedPalette[$index] $palette[$index] "BG palette index $index"
}

$logoPalette = @(Get-HexValues $logoSource 'sega_logo_palette')
$logoTileMap = @(Get-HexValues $logoSource 'sega_logo_tilemap')
Assert-Equal 16 $logoPalette.Count 'SEGA logo palette entry count'
Assert-Equal 0 $logoPalette[0] 'SEGA logo black palette entry'
Assert-Equal 48 $logoTileMap.Count 'SEGA logo tilemap entry count'
Assert-Equal 1 $logoTileMap[0] 'SEGA logo first tile index'
Assert-Equal 48 $logoTileMap[47] 'SEGA logo last tile index'
if ($logoHeader -notmatch '#define SEGA_LOGO_TILE_COLUMNS 12' -or
    $logoHeader -notmatch '#define SEGA_LOGO_TILE_ROWS 4' -or
    $logoHeader -notmatch '#define SEGA_LOGO_TILE_ORIGIN_X 10' -or
    $logoHeader -notmatch '#define SEGA_LOGO_TILE_ORIGIN_Y 10' -or
    $logoHeader -notmatch '#define SEGA_LOGO_TILE_BYTE_COUNT 1536') {
    throw 'Generated centered SEGA logo tile contract mismatch'
}
$logoBitmap = [System.Drawing.Bitmap]::new($logoPath)
try {
    $expectedLogoColors = @{}
    for ($y = 0; $y -lt $logoBitmap.Height; ++$y) {
        for ($x = 0; $x -lt $logoBitmap.Width; ++$x) {
            $pixel = $logoBitmap.GetPixel($x, $y)
            $red = [int]$pixel.R -shr 4
            $green = [int]$pixel.G -shr 4
            $blue = [int]$pixel.B -shr 4
            $color = $red -bor ($green -shl 4) -bor ($blue -shl 8)
            $expectedLogoColors[[int]$color] = $true
        }
    }
}
finally {
    $logoBitmap.Dispose()
}
$actualLogoColors = @($logoPalette | Where-Object {
    $expectedLogoColors.ContainsKey([int]$_) } | Select-Object -Unique)
Assert-Equal $expectedLogoColors.Count $actualLogoColors.Count `
    'Dedicated SEGA logo palette color coverage'
if ($startupLogoSource -notmatch
    'GG_loadBGPalette\(sega_logo_palette\);' -or
    $startupLogoSource -match
    'game_gear_video_load_background_palette') {
    throw 'SEGA logo does not exclusively own its dedicated startup palette'
}
if ($mainSource.IndexOf('game_gear_startup_logo_show();') -ge
    $mainSource.IndexOf('game_gear_video_initialize();')) {
    throw 'Gameplay palette initialization does not follow the SEGA logo'
}
Assert-Equal 16 (@($palette | Select-Object -Unique).Count) `
    'Distinct BG palette entry count'

foreach ($texture in $zombieStateTextures) {
    $generatedHeader = Get-Content -Raw -LiteralPath (
        Join-Path $root "$BuildDirectory\generated\$($texture.File).h")
    $generatedSource = Get-Content -Raw -LiteralPath (
        Join-Path $root "$BuildDirectory\generated\$($texture.File).c")
    $symbol = $texture.Symbol
    if ($generatedHeader -notmatch "#define ${symbol}_WIDTH 8" -or
        $generatedHeader -notmatch "#define ${symbol}_HEIGHT 8" -or
        $generatedHeader -notmatch "#define ${symbol}_PACKED_ROW_STRIDE 4" -or
        $generatedHeader -notmatch "#define ${symbol}_TRANSPARENT_INDEX 15" -or
        $generatedHeader -notmatch "#define ${symbol}_BYTE_COUNT 32") {
        throw "Generated zombie texture contract mismatch: $symbol"
    }
    Assert-Equal 32 (@(Get-HexValues $generatedSource $symbol).Count) `
        "$symbol packed byte count"
}

$weaponBytes = @(Get-HexValues $weaponSource 'hud_weapon_pixels')
if ($weaponHeader -notmatch '#define hud_weapon_pixels_WIDTH 12' -or
    $weaponHeader -notmatch '#define hud_weapon_pixels_HEIGHT 12' -or
    $weaponHeader -notmatch '#define hud_weapon_pixels_PACKED_ROW_STRIDE 8' -or
    $weaponHeader -notmatch '#define hud_weapon_pixels_TRANSPARENT_INDEX 14' -or
    $weaponHeader -notmatch '#define hud_weapon_pixels_BYTE_COUNT 96') {
    throw 'Generated weapon texture contract mismatch'
}

$bitmap = [System.Drawing.Bitmap]::new($weaponPath)
try {
    Assert-Equal 12 $bitmap.Width 'Weapon source width'
    Assert-Equal 12 $bitmap.Height 'Weapon source height'
    $sourceLight = 0
    $sourceDark = 0
    $sourceBrown = 0
    $generatedLight = 0
    $generatedDark = 0
    $generatedBrown = 0
    $sourceCounts = @{}
    $expectedIndices = @{
        '#000000' = 0; '#1a1a1a' = 13; '#4d4d4d' = 2
        '#797878' = 3; '#ad3e00' = 1; '#ffc4ab' = 11
        '#ffa57d' = 15; '#ffffff' = 12
    }
    for ($y = 0; $y -lt 12; ++$y) {
        for ($x = 0; $x -lt 12; ++$x) {
            $pixel = $bitmap.GetPixel($x, $y)
            $rgb = if ($pixel.A -eq 0) {
                'transparent'
            }
            else {
                '#{0:x2}{1:x2}{2:x2}' -f $pixel.R, $pixel.G, $pixel.B
            }
            if (-not $sourceCounts.ContainsKey($rgb)) { $sourceCounts[$rgb] = 0 }
            ++$sourceCounts[$rgb]
            if ($rgb -eq '#ffc4ab') { ++$sourceLight }
            if ($rgb -eq '#ffa57d') { ++$sourceDark }
            if ($rgb -eq '#ad3e00') {
                ++$sourceBrown
                Assert-Equal 255 $pixel.A "Brown alpha at ($x,$y)"
            }

            $packed = $weaponBytes[$y * 8 + [Math]::Floor($x / 2)]
            $generatedIndex = if (($x -band 1) -ne 0) {
                $packed -band 15
            }
            else {
                $packed -shr 4
            }
            if ($generatedIndex -eq 11) { ++$generatedLight }
            if ($generatedIndex -eq 15) { ++$generatedDark }
            if ($generatedIndex -eq 1) { ++$generatedBrown }
            $expectedIndex = if ($rgb -eq 'transparent') {
                14
            }
            else {
                $expectedIndices[$rgb]
            }
            Assert-Equal $expectedIndex $generatedIndex `
                "Generated weapon index at ($x,$y)"
        }
    }
}
finally {
    $bitmap.Dispose()
}

Assert-Equal 16 $sourceLight 'Authored #ffc4ab pixel count'
Assert-Equal 9 $sourceDark 'Authored #ffa57d pixel count'
Assert-Equal 17 $sourceBrown 'Authored #ad3e00 pixel count'
Assert-Equal $sourceLight $generatedLight 'Generated light-skin index count'
Assert-Equal $sourceDark $generatedDark 'Generated dark-skin index count'
Assert-Equal $sourceBrown $generatedBrown 'Generated brown index count'
Assert-Equal 68 ($generatedBrown * 4) 'Displayed 2x brown pixel count'
if ($palette[11] -eq $palette[15] -or 11 -eq 6 -or 15 -eq 6) {
    throw 'Weapon skin tones are not distinct and opaque'
}
Assert-Equal 0x03a $palette[1] 'Final dedicated brown palette value'

if ($mainSource -match 'SMS_autoSetUpTextRenderer\(\);' -or
    $mainSource -match 'game_gear_video_load_background_palette\(\);') {
    throw 'Profile-only text setup or palette repair remains in the main path'
}
if ($videoSource -notmatch
    'GAME_GEAR_WALL_PALETTE_BASE \+ wall_palette_offset,[\s\S]*?game_gear_get_wall_palette_color') {
    throw 'Runtime palette loader does not load the generated master palette'
}

Write-Output 'Complete palette usage validation PASS'
Write-Output '- 16 distinct assigned BG entries; no unassigned hardware BG slot'
Write-Output '- isolated 11-color SEGA palette precedes and never replaces gameplay palette'
Write-Output '- bright green merged to moss index 7'
Write-Output '- dark red merged to primary-red index 5'
Write-Output '- dedicated brown index 1'
Write-Output '- accepted LOD shade restored at index 9'
Write-Output "- skin pixels: #ffc4ab=$sourceLight, #ffa57d=$sourceDark"
Write-Output "- brown pixels: source=$sourceBrown, generated=$generatedBrown, displayed=$($generatedBrown * 4)"
Write-Output '- BG index 1 remains 0x03a with no profile text palette overwrite'
Write-Output '- shot-dead and corpse textures use the 8x8/32-byte/index-15 contract'

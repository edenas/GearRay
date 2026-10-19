param(
    [Parameter(Mandatory = $true)]
    [string]$MapPath,

    [Parameter(Mandatory = $true)]
    [string]$RomPath
)

$ErrorActionPreference = "Stop"
$bank0Limit = 0x4000
$bank1Start = 0x14000
$bank1End = 0x18000
$bank2Start = 0x28000
$bank2End = 0x2C000
$bank3Start = 0x34000
$bank3End = 0x38000
$nearTextureBytes = 7 * 32 * 32 / 2

$map = Get-Content -LiteralPath $MapPath -Raw
foreach ($area in [regex]::Matches($map, '(?m)^(_BANK\w+)\s+[0-9A-Fa-f]{8}\s+([0-9A-Fa-f]{8})')) {
    if ([Convert]::ToInt32($area.Groups[2].Value,16) -ne 0 -and
        $area.Groups[1].Value -notmatch '^_BANK(?:\d+|3WALL)$') {
        throw "Malformed non-empty bank area: $($area.Groups[1].Value)"
    }
}

function Get-HexSymbolValue {
    param([string]$Name)

    $match = [regex]::Match(
        $map,
        "(?m)^\s*(?<value>[0-9A-Fa-f]{8})\s+$([regex]::Escape($Name))\s+")
    if (-not $match.Success) {
        throw "Required linker symbol is missing: $Name"
    }

    return [Convert]::ToInt32($match.Groups["value"].Value, 16)
}

$fixedEnd = (Get-HexSymbolValue "s__GSFINAL") +
    (Get-HexSymbolValue "l__GSFINAL")
$bank0Reserve = $bank0Limit - $fixedEnd
if ($bank0Reserve -lt 256) {
    Write-Warning "Bank 0 reserve is $bank0Reserve bytes; review before adding resident code."
}

foreach ($symbol in @("_main", "_raycaster_update", "_game_gear_video_draw_wall_colum", '_SMS_isr','_SMS_nmi_isr','___sdcc_bcall_ehl')) {
    $address = Get-HexSymbolValue $symbol
    if ($address -ge $bank0Limit) {
        throw "Hot resident symbol left Bank 0: $symbol at 0x$($address.ToString('X'))."
    }
}

foreach ($symbol in @("_world_initialize", "_game_gear_video_initialize")) {
    $address = Get-HexSymbolValue $symbol
    if ($address -lt $bank1Start -or $address -ge $bank1End) {
        throw "Cold startup symbol is not in Bank 1: $symbol at 0x$($address.ToString('X'))."
    }
}

$bank1SegmentStart = Get-HexSymbolValue "s__BANK1"
$bank1Length = Get-HexSymbolValue "l__BANK1"
if ($bank1SegmentStart -ne $bank1Start -or
    ($bank1SegmentStart + $bank1Length) -gt ($bank1End-16)) {
    throw "Bank 1 segment is outside its 16 KB page."
}

$bank2SegmentStart = Get-HexSymbolValue "s__BANK2"
$bank2Length = Get-HexSymbolValue "l__BANK2"
if ($bank2SegmentStart -ne $bank2Start -or
    ($bank2SegmentStart + $bank2Length) -gt $bank2End) {
    throw "Bank 2 segment is outside its dedicated 16 KB page."
}

$nearSymbols = @(
    '_zombie_near_walking_01_pixels',
    '_zombie_near_walking_02_pixels',
    '_zombie_near_standing_attack_pix',
    '_zombie_near_attack_01_pixels',
    '_zombie_near_attack_02_pixels',
    '_zombie_near_shot_01_pixels',
    '_zombie_near_corpse_pixels'
)
$bank3Length = Get-HexSymbolValue 'l__BANK3'
$bank3Extent = $bank3Length
$wallArea = [regex]::Match($map,'(?m)^\s*([0-9A-Fa-f]{8})\s+l__BANK3WALL\s+')
if ($wallArea.Success -and [Convert]::ToInt32($wallArea.Groups[1].Value,16) -gt 0) {
    $wallStart=Get-HexSymbolValue 's__BANK3WALL'
    $wallLength=Get-HexSymbolValue 'l__BANK3WALL'
    if ($wallStart -ne 0x39200 -or $bank3Length -gt 0x1200 -or $wallLength -gt 0x2E00) {
        throw 'Bank 3 slot-2 wall worker overlaps cold slot-1 content or leaves its physical page.'
    }
    foreach($symbol in @('_wall_plan_prepare','_wall_plan_rows')) {
        $address=Get-HexSymbolValue $symbol
        if($address -lt $wallStart -or $address -ge $wallStart+$wallLength) { throw "Wrong slot-2 wall entry: $symbol" }
    }
    $bank3Extent=0x1200+$wallLength
}
if ((Get-HexSymbolValue 's__BANK3') -ne $bank3Start -or
    $bank3Length -le 0 -or ($bank3Start + $bank3Length) -gt $bank3End) {
    throw 'Bank 3 must occupy page 3 in CPU slot 1 (virtual base 0x34000).'
}
foreach ($symbol in @('_game_gear_startup_logo_show','_sega_logo_tiles','_sega_logo_palette','_sega_logo_tilemap')) {
    $address = Get-HexSymbolValue $symbol
    if ($address -lt $bank3Start -or $address -ge ($bank3Start+$bank3Length)) {
        throw "Logo code/data is not co-located in Bank 3: $symbol"
    }
}
foreach ($symbol in @('_game_gear_video_present_player_','_game_over_tiles','_game_over_palette','_game_over_tilemap')) {
    $address = Get-HexSymbolValue $symbol
    if ($address -lt $bank3Start -or $address -ge ($bank3Start+$bank3Length)) {
        throw "Game Over code/data is not co-located in Bank 3: $symbol"
    }
}
if ((Get-HexSymbolValue 'b_game_gear_startup_logo_show') -ne 3) { throw 'Wrong startup dispatch bank.' }
if ((Get-HexSymbolValue 'b_game_gear_video_present_player') -ne 3) { throw 'Wrong Game Over dispatch bank.' }
$build = Split-Path -Parent (Resolve-Path -LiteralPath $MapPath)
. "$PSScriptRoot/production_build_artifacts.ps1"
foreach ($object in Get-ProductionBuildObjects $build) {
    $contents = Get-Content $object.FullName -Raw
    foreach ($area in [regex]::Matches($contents,'(?m)^A (_BANK\w+) size ([0-9A-Fa-f]+)')) {
        if ([Convert]::ToInt32($area.Groups[2].Value,16) -eq 0) { continue }
        if ($area.Groups[1].Value -notmatch '^_BANK(?:\d+|3WALL)$') { throw "Malformed non-empty bank in $($object.Name)" }
        if ($area.Groups[1].Value -eq '_BANK3WALL' -and $object.BaseName -ne 'native_wall') { throw "Unexpected wall-tail occupant: $($object.Name)" }
        if ($area.Groups[1].Value -eq '_BANK3' -and $object.BaseName -notin @('startup_logo','generated_sega_logo','generated_game_over','game_over_presentation')) {
            throw "Unexpected Bank 3 occupant: $($object.Name)"
        }
    }
}
foreach ($symbol in $nearSymbols) {
    $address = Get-HexSymbolValue $symbol
    if ($address -lt $bank2Start -or $address -ge $bank2End) {
        throw "Near zombie texture is not in Bank 2: $symbol at 0x$($address.ToString('X'))."
    }
}
if ($map -match '_shotgun_world_pixels\s') {
    foreach ($symbol in @('_shotgun_world_pixels',
        '_game_gear_hud_weapon_update','_game_gear_prepare_world_sprites')) {
        $address=Get-HexSymbolValue $symbol
        if ($address -lt $bank1Start -or $address -ge ($bank1Start+$bank1Length)) {throw "Warm weapon content left Bank 1: $symbol"}
    }
}

[byte[]]$rom = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $RomPath))
Test-ProductionRomPayload $build (Resolve-Path -LiteralPath $RomPath)
if ($rom.Length -lt 32KB -or ($rom.Length -band ($rom.Length-1)) -ne 0) {
    throw "ROM size $($rom.Length) is not a supported power-of-two image of at least 32 KB."
}
$logoSource = Get-Content "$build/generated/sega_logo.c" -Raw
foreach ($name in @('tiles','palette','tilemap')) {
    $array = [regex]::Match($logoSource,"(?s)sega_logo_$name\[.*?\]\s*=\s*\{(.*?)\}")
    if (!$array.Success) { throw "Missing generated logo $name" }
    $bytes = @([regex]::Matches($array.Groups[1].Value,'0x([0-9a-fA-F]+)') | ForEach-Object {
        $value=[Convert]::ToInt32($_.Groups[1].Value,16)
        [byte]($value -band 255)
        if ($name -ne 'tiles') { [byte]($value -shr 8) }
    })
    $address = Get-HexSymbolValue "_sega_logo_$name"
    $physical = (($address -shr 16)*16384) + ($address -band 0x3FFF)
    for ($i=0; $i -lt $bytes.Count; $i++) {
        if ($rom[$physical+$i] -ne $bytes[$i]) { throw "Bank 3 physical payload mismatch: $name byte $i" }
    }
}

$signature = [System.Text.Encoding]::ASCII.GetString($rom, 0x7FF0, 8)
if ($signature -ne "TMR SEGA") {
    throw "SEGA header signature is missing at 0x7FF0."
}

$headerRegionAndSize = $rom[0x7FFF]
$sizeCodes=@{32768=0xC;65536=0xE;131072=0xF;262144=0x0;524288=0x1;1048576=0x2}
if (!$sizeCodes.ContainsKey($rom.Length)) { throw "No SEGA header size code is defined for $($rom.Length) bytes." }
$expectedSizeCode=$sizeCodes[$rom.Length]
if (($headerRegionAndSize -band 0x0F) -ne $expectedSizeCode -or ($headerRegionAndSize -band 0xF0) -ne 0x70) {
    throw "Header byte 0x$($headerRegionAndSize.ToString('X2')) does not describe this international Game Gear ROM size."
}

$storedChecksum = [int]$rom[0x7FFA] -bor ([int]$rom[0x7FFB] -shl 8)
$checksum = 0
for ($offset = 0; $offset -lt 0x7FF0; $offset++) {
    $checksum = ($checksum + $rom[$offset]) -band 0xFFFF
}
if ($checksum -ne $storedChecksum) {
    throw "ROM checksum is 0x$($storedChecksum.ToString('X4')); calculated 0x$($checksum.ToString('X4'))."
}

$segaHeaderBytes = 16
$bank1Free = ($bank1End - $bank1Start) - $bank1Length - $segaHeaderBytes
$bank2Free = ($bank2End - $bank2Start) - $bank2Length
# The approved second native pause composite and carousel use a bounded 640-byte
# budget (192 data + up to 448 code) beyond the pistol checkpoint. Residency and
# physical bounds remain mandatory; this is a planning reserve, not a ROM limit.
if ($bank2Length -lt $nearTextureBytes) {
    throw "Bank 2 does not contain all near textures."
}
if ($bank2Free -lt (7680-640)) {
    Write-Warning "Bank 2 free space is $bank2Free bytes; the old planning reserve was 7040 bytes."
}

Write-Output "Bank layout validation PASS"
Write-Output "- fixed endpoint: 0x$($fixedEnd.ToString('X4')); Bank 0 reserve: $bank0Reserve bytes"
Write-Output "- Bank 1 used/free: $bank1Length/$bank1Free bytes"
Write-Output "- Bank 2 used/free: $bank2Length/$bank2Free bytes; seven native near-detail textures verified"
Write-Output "- Bank 3 extent/free: $bank3Extent/$(16384-$bank3Extent); cold slot-1 bytes $bank3Length; disjoint slot-2 wall tail and physical payload verified"
Write-Output "- seven 32x32 4bpp payloads: $nearTextureBytes bytes; planning reserves are advisory"
Write-Output "- ROM: $($rom.Length) bytes; header 0x$($headerRegionAndSize.ToString('X2')); checksum 0x$($storedChecksum.ToString('X4'))"
Write-Output "- hot main/raycaster/video paths remain fixed; cold initialization remains in Bank 1"

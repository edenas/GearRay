param(
    [Parameter(Mandatory = $true)]
    [string]$MapPath,

    [Parameter(Mandatory = $true)]
    [string]$RomPath
)

$ErrorActionPreference = "Stop"
$minimumBank0Reserve = 256
$bank0Limit = 0x4000
$bank1Start = 0x14000
$bank1End = 0x18000
$bank2Start = 0x28000
$bank2End = 0x2C000
$romSize = 64KB
$nearTextureBytes = 7 * 32 * 32 / 2

$map = Get-Content -LiteralPath $MapPath -Raw

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
if ($bank0Reserve -lt $minimumBank0Reserve) {
    throw "Bank 0 reserve is $bank0Reserve bytes; minimum is $minimumBank0Reserve."
}

foreach ($symbol in @("_main", "_raycaster_update", "_game_gear_video_draw_wall_colum")) {
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
    ($bank1SegmentStart + $bank1Length) -gt $bank1End) {
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
foreach ($symbol in $nearSymbols) {
    $address = Get-HexSymbolValue $symbol
    if ($address -lt $bank2Start -or $address -ge $bank2End) {
        throw "Near zombie texture is not in Bank 2: $symbol at 0x$($address.ToString('X'))."
    }
}

[byte[]]$rom = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $RomPath))
if ($rom.Length -ne $romSize) {
    throw "ROM is $($rom.Length) bytes; expected $romSize bytes."
}

$signature = [System.Text.Encoding]::ASCII.GetString($rom, 0x7FF0, 8)
if ($signature -ne "TMR SEGA") {
    throw "SEGA header signature is missing at 0x7FF0."
}

$headerRegionAndSize = $rom[0x7FFF]
if ($headerRegionAndSize -ne 0x7E) {
    throw "Header byte at 0x7FFF is 0x$($headerRegionAndSize.ToString('X2')); expected 0x7E for a 64 KB international Game Gear ROM."
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
if ($bank2Length -lt $nearTextureBytes -or $bank2Free -lt 8KB) {
    throw "Bank 2 does not contain all near textures or retain the required 8 KB reserve."
}

Write-Output "Bank layout validation PASS"
Write-Output "- fixed endpoint: 0x$($fixedEnd.ToString('X4')); Bank 0 reserve: $bank0Reserve bytes"
Write-Output "- Bank 1 used/free: $bank1Length/$bank1Free bytes"
Write-Output "- Bank 2 used/free: $bank2Length/$bank2Free bytes; seven native near-detail textures verified"
Write-Output "- seven 32x32 4bpp payloads: $nearTextureBytes bytes; current Bank 2 reserve exceeds 8 KB"
Write-Output "- ROM: $($rom.Length) bytes; header 0x$($headerRegionAndSize.ToString('X2')); checksum 0x$($storedChecksum.ToString('X4'))"
Write-Output "- hot main/raycaster/video paths remain fixed; cold initialization remains in Bank 1"

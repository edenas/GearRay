param(
    [Parameter(Mandatory = $true)][string]$IconPath,
    [Parameter(Mandatory = $true)][string]$BarPath,
    [Parameter(Mandatory = $true)][string]$OutputHeader
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

function Read-LogicalPixels([string]$Path, [int]$Width, [int]$Height) {
    $bitmap = [System.Drawing.Bitmap]::new($Path)
    try {
        if ($bitmap.Width -ne 2 * $Width -or $bitmap.Height -ne 2 * $Height) {
            throw "$(Split-Path -Leaf $Path) must be exactly $($Width * 2)x$($Height * 2) pixels."
        }
        $pixels = New-Object 'bool[,]' $Width, $Height
        for ($y = 0; $y -lt $Height; ++$y) {
            for ($x = 0; $x -lt $Width; ++$x) {
                $first = $null
                foreach ($dy in 0..1) { foreach ($dx in 0..1) {
                    $pixel = $bitmap.GetPixel(2 * $x + $dx, 2 * $y + $dy)
                    if ($pixel.A -ne 0 -and
                        -not ($pixel.R -eq 255 -and $pixel.G -eq 255 -and $pixel.B -eq 255)) {
                        throw "$(Split-Path -Leaf $Path) contains a non-white opaque pixel."
                    }
                    $ink = $pixel.A -ne 0
                    if ($null -eq $first) { $first = $ink }
                    elseif ($ink -ne $first) { throw "$(Split-Path -Leaf $Path) is not uniform 2x artwork at $x,$y." }
                }}
                $pixels[$x, $y] = $first
            }
        }
        return ,$pixels
    }
    finally { $bitmap.Dispose() }
}

$icon = Read-LogicalPixels $IconPath 7 7
$bar = Read-LogicalPixels $BarPath 1 7
for ($y = 0; $y -lt 7; ++$y) {
    if (-not $bar[0, $y]) { throw "Authored health bar must occupy all seven logical rows." }
}

$tiles = [System.Collections.Generic.List[byte]]::new(88)
$iconRows = New-Object byte[] 8
for ($y = 0; $y -lt 7; ++$y) {
    for ($x = 0; $x -lt 7; ++$x) {
        if ($icon[$x, $y] -and $x -lt 4) {
            $iconRows[$y + 1] = $iconRows[$y + 1] -bor (0x08 -shr $x)
        }
    }
}
$tiles.AddRange($iconRows)

$iconRightRows = New-Object byte[] 8
for ($y = 0; $y -lt 7; ++$y) {
    foreach ($x in 4..6) {
        if ($icon[$x, $y]) {
            $iconRightRows[$y + 1] = $iconRightRows[$y + 1] -bor (0x80 -shr ($x - 4))
        }
    }
}
$tiles.AddRange($iconRightRows)
foreach ($visible in 1..2) {
    $rows = [byte[]]$iconRightRows.Clone()
    foreach ($localBar in 0..($visible - 1)) {
        $tileX = 5 + 2 * $localBar
        for ($y = 1; $y -lt 8; ++$y) { $rows[$y] = $rows[$y] -bor (0x80 -shr $tileX) }
    }
    $tiles.AddRange($rows)
}
foreach ($visible in 1..4) {
    $rows = New-Object byte[] 8
    foreach ($localBar in 0..($visible - 1)) {
        $tileX = 1 + 2 * $localBar
        for ($y = 1; $y -lt 8; ++$y) { $rows[$y] = $rows[$y] -bor (0x80 -shr $tileX) }
    }
    $tiles.AddRange($rows)
}
while ($tiles.Count -lt 88) { $tiles.Add(0) }

$rows = for ($tile = 0; $tile -lt 11; ++$tile) {
    $offset = $tile * 8
    "    { " + (($tiles[$offset..($offset + 7)] |
        ForEach-Object { "0x{0:x2}" -f $_ }) -join ", ") + " }"
}
$header = @"
#ifndef GEAR_RAY_GENERATED_HEALTH_HUD_TILES_H
#define GEAR_RAY_GENERATED_HEALTH_HUD_TILES_H

static const unsigned char health_hud_tiles[11][8] = {
$($rows -join ",`r`n")
};

#endif
"@

$outputDirectory = Split-Path -Parent $OutputHeader
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
Set-Content -LiteralPath $OutputHeader -Value $header -Encoding Ascii

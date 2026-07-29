param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputSource,
    [Parameter(Mandatory = $true)][string]$OutputHeader,
    [Parameter(Mandatory = $true)][string]$Symbol
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$bitmap = [System.Drawing.Bitmap]::new($InputPath)
try {
    if ($bitmap.Width -ne 8 -or $bitmap.Height -ne 8) {
        throw "Sprite must be exactly 8x8."
    }

    $pixels = [System.Collections.Generic.List[byte]]::new(64)
    for ($y = 0; $y -lt 8; ++$y) {
        for ($x = 0; $x -lt 8; ++$x) {
            $pixel = $bitmap.GetPixel($x, $y)
            if ($pixel.A -eq 0) {
                $pixels.Add(15)
                continue
            }
            if ($pixel.A -ne 255) {
                throw "Unexpected partial alpha at ($x,$y): $($pixel.A)."
            }

            $rgb = ('#{0:x2}{1:x2}{2:x2}' -f
                    $pixel.R, $pixel.G, $pixel.B)
            $index = switch ($rgb) {
                '#000000' { 0; break }
                '#1a1a1a' { 13; break }
                '#2d2d2d' { 10; break }
                '#008cb4' { 4; break }
                '#b51a00' { 5; break }
                '#53602a' { 7; break }
                '#006d8f' { 8; break }
                default {
                    throw "Sprite color $rgb at ($x,$y) has no exact BG palette mapping."
                }
            }
            $pixels.Add($index)
        }
    }
}
finally {
    $bitmap.Dispose()
}

$bytes = [System.Collections.Generic.List[byte]]::new(32)
for ($index = 0; $index -lt 64; $index += 2) {
    $bytes.Add(($pixels[$index] -shl 4) -bor $pixels[$index + 1])
}

$rows = for ($index = 0; $index -lt 32; $index += 8) {
    "    " + (($bytes[$index..($index + 7)] |
        ForEach-Object { "0x{0:x2}" -f $_ }) -join ", ")
}

$headerGuard = "GEAR_RAY_GENERATED_" + $Symbol.ToUpperInvariant() + "_H"
$header = @"
#ifndef $headerGuard
#define $headerGuard

extern const unsigned char $Symbol[32];

#endif
"@

$headerName = Split-Path -Leaf $OutputHeader
$source = @"
#include "$headerName"

const unsigned char $Symbol[32] = {
$($rows -join ",`r`n")
};
"@

$outputDirectory = Split-Path -Parent $OutputSource
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
Set-Content -LiteralPath $OutputHeader -Value $header -Encoding Ascii
Set-Content -LiteralPath $OutputSource -Value $source -Encoding Ascii

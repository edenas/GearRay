param(
    [string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(!$InputPath){$InputPath=Join-Path (Split-Path $PSScriptRoot -Parent) 'assets/sprites/weapons/pick_up_shotgun.png'}
Add-Type -AssemblyName System.Drawing
$source=[Drawing.Bitmap]::new($InputPath)
try {
    if($source.Width -ne 16 -or $source.Height -ne 16){throw 'Shotgun source must be 16x16'}
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $lod=[Drawing.Bitmap]::new(8,8)
    $indices=New-Object byte[] 64
    $pattern=[Collections.Generic.List[string]]::new()
    for($y=0;$y -lt 8;$y++){
        $row=''
        for($x=0;$x -lt 8;$x++){
            # Nearest-neighbor point samples: no averaging, filtering or alpha blending.
            $pixel=$source.GetPixel($x*2,$y*2)
            if($pixel.A -eq 0){$index=15;$color=[Drawing.Color]::Transparent;$row+='.'}
            else {
                if($pixel.A -ne 255){throw 'Partial source alpha'}
                # Preserve sampled occupancy; flatten every authored highlight
                # to the existing dark gun tone, with no separate outer outline.
                $index=13;$gray=34;$row+='d'
                $color=[Drawing.Color]::FromArgb(255,$gray,$gray,$gray)
            }
            $indices[$y*8+$x]=$index
            $lod.SetPixel($x,$y,$color)
        }
        $pattern.Add($row)
    }
    $packed=for($i=0;$i -lt 64;$i+=2){($indices[$i] -shl 4) -bor $indices[$i+1]}
    $header=@"
/* Generated 8x8 nearest-neighbor dark silhouette from pick_up_shotgun.png at (2*x,2*y).
 * Alpha uses world transparent index 15; every opaque sample uses dark gray 13.
 * No white/light-gray outline or runtime recoloring. */
static const unsigned char shotgun_far_pixels[32] = {
    $(($packed | ForEach-Object {'0x{0:x2}' -f $_}) -join ', ')
};
"@
    Set-Content -LiteralPath (Join-Path $OutputDirectory 'shotgun_far_lod.h') -Value $header -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $OutputDirectory 'shotgun_far_pattern.txt') -Value $pattern -Encoding Ascii
    function Preview($image,[string]$name,[int]$scale){
        $preview=[Drawing.Bitmap]::new($image.Width*$scale,$image.Height*$scale)
        try {
            for($py=0;$py -lt $preview.Height;$py++){for($px=0;$px -lt $preview.Width;$px++){
                $color=$image.GetPixel([int][Math]::Floor($px/$scale),[int][Math]::Floor($py/$scale))
                # Preview transparent pixels against a dark HUD-like background.
                if($color.A -eq 0){$color=[Drawing.Color]::FromArgb(255,12,12,12)}
                $preview.SetPixel($px,$py,$color)
            }}
            $preview.Save((Join-Path $OutputDirectory $name),[Drawing.Imaging.ImageFormat]::Png)
        } finally {$preview.Dispose()}
    }
    Preview $source 'shotgun-authored-preview.png' 16
    Preview $lod 'shotgun-far-preview.png' 32
    $pair=[Drawing.Bitmap]::new(544,288)
    try {
        for($y=0;$y -lt 288;$y++){for($x=0;$x -lt 544;$x++){$pair.SetPixel($x,$y,[Drawing.Color]::FromArgb(255,12,12,12))}}
        foreach($item in @(@($source,16,16),@($lod,32,272))){
            $im=$item[0];$scale=$item[1];$left=$item[2]
            for($y=0;$y -lt 256;$y++){for($x=0;$x -lt 256;$x++){
                $c=$im.GetPixel([int][Math]::Floor($x/$scale),[int][Math]::Floor($y/$scale))
                if($c.A -ne 0){$pair.SetPixel($left+$x,16+$y,$c)}
            }}
        }
        $pair.Save((Join-Path $OutputDirectory 'shotgun-near-far-preview.png'),[Drawing.Imaging.ImageFormat]::Png)
    } finally {$pair.Dispose();$lod.Dispose()}
    Write-Output ($pattern -join "`n")
    Write-Output 'Generated FAR LOD: 32 packed ROM bytes.'
} finally {$source.Dispose()}


param(
    [Parameter(Mandatory=$true)][string]$CameraSource,
    [Parameter(Mandatory=$true)][string]$OutputSource,
    [Parameter(Mandatory=$true)][string]$OutputHeader
)
$ErrorActionPreference='Stop'
$source=Get-Content -LiteralPath $CameraSource -Raw
function Constant([string]$name) {
    $m=[regex]::Match($source,"#define\s+$name\s+(\d+)")
    if (!$m.Success) { throw "Missing camera contract $name" }
    return [long]$m.Groups[1].Value
}
$cosine=Constant 'ROTATION_COSINE'; $sine=Constant 'ROTATION_SINE'
$scale=Constant 'ROTATION_SCALE'; $length=Constant 'DIRECTION_LENGTH'
$plane=Constant 'CAMERA_PLANE_LENGTH'
function RoundScaled([long]$n,[long]$d) {
    # C signed division truncates toward zero. Do not use PowerShell's rounding cast.
    if ($n -lt 0) { $n-=[long][Math]::Floor($d/2) } else { $n+=[long][Math]::Floor($d/2) }
    return [long][Math]::Truncate($n/[double]$d)
}
$states=[Collections.Generic.List[object]]::new()
$edges=[Collections.Generic.List[object]]::new()
$ids=@{}; $states.Add(@(0L,-$length)); $ids["0,$(-$length)"]=0
for ($i=0; $i -lt $states.Count; ++$i) {
    $x=$states[$i][0]; $y=$states[$i][1]; $edge=@()
    foreach ($sign in @(-1,1)) {
        $nx=RoundScaled ($x*$cosine-$y*$sine*$sign) $scale
        $ny=RoundScaled ($y*$cosine+$x*$sine*$sign) $scale
        $root=[long][Math]::Floor([Math]::Sqrt($nx*$nx+$ny*$ny))
        if (!$root) { throw 'Zero-length camera graph state' }
        $nx=RoundScaled ($nx*$length) $root; $ny=RoundScaled ($ny*$length) $root
        $key="$nx,$ny"
        if (!$ids.ContainsKey($key)) { $ids[$key]=$states.Count; $states.Add(@($nx,$ny)) }
        $edge+=$ids[$key]
    }
    $edges.Add($edge)
    if ($states.Count -gt 256) { throw 'Camera closure exceeds byte state ID' }
}
if ($states.Count -ne 242) { throw "Changed reachable camera contract: $($states.Count) states" }
$lines=[Collections.Generic.List[string]]::new()
$lines.Add('/* Generated exact legacy integer rotation closure; do not edit. */')
$lines.Add('#include "camera_graph.h"')
$lines.Add('const signed int camera_graph_vectors[242][4] = {')
foreach ($state in $states) {
    $x=$state[0]; $y=$state[1]
    $lines.Add('    {'+(@($x,$y,(RoundScaled (-$y*$plane) $length),(RoundScaled ($x*$plane) $length)) -join ',')+'},')
}
$lines.Add('};')
$lines.Add('const unsigned char camera_graph_edges[242][2] = {')
foreach ($edge in $edges) { $lines.Add('    {'+($edge -join ',')+'},') }
$lines.Add('};')
[IO.File]::WriteAllLines($OutputSource,$lines,[Text.Encoding]::ASCII)
[IO.File]::WriteAllText($OutputHeader,"/* Generated exact graph declarations. */`nextern const signed int camera_graph_vectors[242][4];`nextern const unsigned char camera_graph_edges[242][2];`n",[Text.Encoding]::ASCII)
Write-Output 'Generated 242 exact camera states / 484 transitions / 2420 Bank 2 bytes.'

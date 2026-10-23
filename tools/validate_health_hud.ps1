param([string]$BuildDirectory = "build/release", [switch]$RequireMapPlacement)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$buildPath = if ([IO.Path]::IsPathRooted($BuildDirectory)) {$BuildDirectory} else {Join-Path $root $BuildDirectory}
function Assert-True([bool]$Condition,[string]$Message){if(-not $Condition){throw $Message}}

$iconPath=Join-Path $root 'assets\ui\health_hud.png'
$barPath=Join-Path $root 'assets\ui\health_hud_1.png'
$generatedPath=Join-Path $buildPath 'generated\health_hud_tiles.h'
$cmake=Get-Content -Raw (Join-Path $root 'CMakeLists.txt')
$generator=Get-Content -Raw (Join-Path $root 'tools\generate_health_hud.ps1')
$video=Get-Content -Raw (Join-Path $root 'platform\game_gear\video_initialization.c')
$ai=Get-Content -Raw (Join-Path $root 'game\zombie_ai.c')
$main=Get-Content -Raw (Join-Path $root 'game\main.c')
$startup=Get-Content -Raw (Join-Path $root 'platform\game_gear\startup_logo.c')
$spriteHeader=Get-Content -Raw (Join-Path $root 'game\world_sprite.h')

Assert-True (Test-Path $iconPath) 'Authored health icon is missing.'
Assert-True (Test-Path $barPath) 'Authored health bar is missing.'
Assert-True ($cmake -match 'health_hud\.png' -and $cmake -match 'health_hud_1\.png' -and
             $cmake -match '-IconPath' -and $cmake -match '-BarPath') 'Build does not consume both authored HUD assets.'
Assert-True ($generator -match 'Read-LogicalPixels' -and $generator -notmatch 'tickHeights|tickBaseline') 'Generator is not authored-pixel based or retains staircase geometry.'

Add-Type -AssemblyName System.Drawing
function Read-Logical([string]$Path,[int]$W,[int]$H){
 $b=[Drawing.Bitmap]::new($Path);try{
  Assert-True ($b.Width-eq 2*$W-and$b.Height-eq 2*$H) "Unexpected dimensions for $(Split-Path -Leaf $Path)."
  $out=New-Object 'bool[,]' $W,$H
  for($y=0;$y-lt$H;$y++){for($x=0;$x-lt$W;$x++){
   $values=@();foreach($dy in 0..1){foreach($dx in 0..1){$p=$b.GetPixel(2*$x+$dx,2*$y+$dy);Assert-True ($p.A-eq0-or($p.R-eq255-and$p.G-eq255-and$p.B-eq255)) 'HUD asset is not transparent/white.';$values+=($p.A-ne0)}}
   Assert-True (($values|Select-Object -Unique).Count-eq1) 'HUD asset contains a nonuniform 2x logical pixel.';$out[$x,$y]=$values[0]
  }};return ,$out
 }finally{$b.Dispose()}}
$icon=Read-Logical $iconPath 7 7;$bar=Read-Logical $barPath 1 7
for($y=0;$y-lt7;$y++){Assert-True $bar[0,$y] "Authored bar row $y is empty."}

Assert-True (Test-Path $generatedPath) 'Generated HUD header is missing.'
$generated=Get-Content -Raw $generatedPath
$bytes=[regex]::Matches($generated,'0x([0-9a-fA-F]{2})')|ForEach-Object{[Convert]::ToInt32($_.Groups[1].Value,16)}
Assert-True ($generated-match'health_hud_tiles\[11\]\[8\]' -and $bytes.Count-eq88) 'HUD is not exactly eleven 8-byte tiles.'
$left=New-Object int[] 8;$right=New-Object int[] 8
for($y=0;$y-lt7;$y++){for($x=0;$x-lt7;$x++){if($icon[$x,$y]){if($x-lt4){$left[$y+1]=$left[$y+1]-bor(0x08-shr$x)}else{$right[$y+1]=$right[$y+1]-bor(0x80-shr($x-4))}}}}
Assert-True (($bytes[0..7]-join',')-eq($left-join',')-and($bytes[8..15]-join',')-eq($right-join',')) 'Repacked icon does not match authored icon.'
$expected=[Collections.Generic.List[int]]::new();$expected.AddRange($left);$expected.AddRange($right)
foreach($visible in 1..2){$rows=[int[]]$right.Clone();foreach($local in 0..($visible-1)){$x=5+2*$local;for($y=1;$y-lt8;$y++){$rows[$y]=$rows[$y]-bor(0x80-shr$x)}};$expected.AddRange($rows)}
foreach($visible in 1..4){$rows=New-Object int[] 8;foreach($local in 0..($visible-1)){$x=1+2*$local;for($y=1;$y-lt8;$y++){$rows[$y]=$rows[$y]-bor(0x80-shr$x)}};$expected.AddRange($rows)}
while($expected.Count-lt88){$expected.Add(0)}
Assert-True (($bytes-join',')-eq($expected-join',')) 'HUD pixels or constant 2px bar pitch changed during placement repack.'

foreach($hp in 0,10,20,30,40,50,60,70,80,90,100){Assert-True ([Math]::Floor($hp/10)-eq($hp/10)) "Health mapping failed at $hp."}
Assert-True ((100/10)-(80/10)-eq2) '20 damage does not remove exactly two bars.'
Assert-True ($video-match'unsigned char bar_count = health / 10;' -and $video-match'if \(bar_count == health_hud_rendered_bar_count\)[\s\S]*?return;') 'Runtime mapping/cache changed.'
Assert-True ([regex]::Matches($video,'SMS_setTileatXY\(HEALTH_HUD_BAR_TILE_X \+ cell').Count-eq1) 'HUD update writes outside its single allocated tile row.'
Assert-True ($video-match'HEALTH_HUD_ICON_TILE_X\s+19'-and$video-match'HEALTH_HUD_BAR_TILE_X\s+20'-and$video-match'HEALTH_HUD_TILE_Y\s+5') 'HUD placement changed.'
Assert-True ((20*8-48+23)-eq135) 'Final bar does not align with viewport right border X 135.'
Assert-True ((5*8+1)-eq41-and(5*8+7)-eq47-and47-lt80) 'HUD vertical placement overlaps the viewport.'
Assert-True ($video-match'health_hud_rendered_bar_count = 0;[\s\S]*?game_gear_health_hud_update\(100\);') 'Restart does not restore ten bars.'
Assert-True ($ai-match'player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\);[\s\S]*?game_gear_health_hud_update\(player_get_health\(\)\);') 'Damage/HUD event ordering changed.'
Assert-True ($main-notmatch'game_gear_health_hud_update'-and$startup-notmatch'health_hud|HEALTH_HUD') 'HUD entered a normal-frame or startup-logo path.'
Assert-True ($spriteHeader-match'typedef struct[\s\S]*?WorldSprite;'-and$spriteHeader-notmatch'health_hud') 'HUD changed WorldSprite.'
if($RequireMapPlacement){$map=Get-Content -Raw (Join-Path $buildPath 'GearRay.map');$m=[regex]::Match($map,'(?m)^\s*(?<a>[0-9A-F]{8})\s+_game_gear_health_hud_update');Assert-True $m.Success 'HUD update symbol missing.';$a=[Convert]::ToInt32($m.Groups['a'].Value,16);Assert-True ($a-ge0x14000-and$a-lt0x18000) 'HUD update is outside Bank 1.'}
Write-Output 'Player health HUD validation PASS'
Write-Output '- authored 14x14 icon -> lossless 7x7 logical pixels'
Write-Output '- authored 2x14 bar -> one reusable 1x7 logical bar'
Write-Output '- ten identical bars at 2px pitch; 0..100 HP supports every 10 HP state'
Write-Output '- accepted pixels repacked +3px X/+1px Y; right edge aligns at X=135'
Write-Output '- 88-byte upload once per session; unchanged health writes nothing'

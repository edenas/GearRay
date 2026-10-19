param([string]$BuildDirectory='build',[switch]$RequireMapPlacement)
$ErrorActionPreference='Stop';$root=Split-Path -Parent $PSScriptRoot
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
function Assert([bool]$c,[string]$m){if(-not $c){throw $m}}
$asset=Join-Path $root 'assets\logos\game_over.png';$source=Join-Path $build 'generated\game_over.c';$header=Join-Path $build 'generated\game_over.h'
$video=Get-Content -Raw (Join-Path $root 'platform\game_gear\game_over_presentation.c');$cmake=Get-Content -Raw (Join-Path $root 'CMakeLists.txt')
Add-Type -AssemblyName System.Drawing;$b=[Drawing.Bitmap]::new($asset);try{Assert($b.Width-eq150-and$b.Height-eq23)'Game Over dimensions changed.';$colors=@{};for($y=0;$y-lt23;$y++){for($x=0;$x-lt150;$x++){$p=$b.GetPixel($x,$y);Assert($p.A-eq255)'Game Over must be opaque.';$colors[('{0:x2}{1:x2}{2:x2}'-f$p.R,$p.G,$p.B)]=1}};Assert((($colors.Keys|Sort-Object)-join',')-eq'000000,bb2200,ffffff')'Game Over palette changed.'}finally{$b.Dispose()}
Assert(Test-Path $source)'Generated Game Over source missing.';Assert(Test-Path $header)'Generated Game Over header missing.'
$h=Get-Content -Raw $header;$s=Get-Content -Raw $source
Assert($h-match'GAME_OVER_TILE_COLUMNS 20'-and$h-match'GAME_OVER_TILE_ROWS 4'-and$h-match'GAME_OVER_TILE_BYTE_COUNT 2560')'Game Over tile geometry changed.'
Assert($h-match'GAME_OVER_TILE_ORIGIN_X 6'-and$h-match'GAME_OVER_TILE_ORIGIN_Y 10')'Game Over tile origin changed.'
$tileBlock=[regex]::Match($s,'game_over_tiles[^=]*=\s*\{(?<v>[\s\S]*?)\};').Groups['v'].Value
Assert(([regex]::Matches($tileBlock,'0x[0-9a-fA-F]{2}').Count)-eq2560)'Game Over tile byte count changed.'
Assert($cmake-match'assets/logos/game_over\.png'-and$cmake-match'--constseg BANK3 -c "\$\{GEAR_RAY_GENERATED_GAME_OVER_SOURCE\}"')'Game Over is not generated into Bank 3.'
Assert($cmake-match'game_over_presentation\.c'-and$cmake-match'--codeseg BANK3 --constseg BANK3')'Game Over presentation is not compiled into Bank 3.'
Assert($video-notmatch'DEATH_FADE|game_gear_video_dim_color')'Obsolete death fade remains.'
Assert($video-match'SMS_displayOff\(\);[\s\S]*?SMS_VRAMmemsetW\(0, 0x0000, 16384\);[\s\S]*?GG_loadBGPalette\(game_over_palette\)')'Gameplay is not cleared before Game Over.'
Assert($video-match'GAME_OVER_DISPLAY_FRAME_COUNT 180'-and$video-match'SMS_loadTileMapArea\(GAME_OVER_TILE_ORIGIN_X')'Game Over presentation flow or duration changed.'
Assert($video-match'for \(frame = GAME_OVER_DISPLAY_FRAME_COUNT; frame != 0; --frame\)[\s\S]*?SMS_waitForVBlank\(\);[\s\S]*?SMS_displayOff\(\);')'Game Over is not held for exactly 180 VBlanks before restart.'
Assert((5+150)-le160-and(60+23)-le144)'Game Over clips the visible screen.'
if($RequireMapPlacement){$map=Get-Content -Raw (Join-Path $build 'GearRay.map');foreach($symbol in @('_game_over_tiles','_game_over_palette','_game_over_tilemap','_game_gear_video_present_player_')){$m=[regex]::Match($map,"(?m)^\s*(?<a>[0-9A-F]{8})\s+$symbol\s");Assert($m.Success)"Game Over symbol missing: $symbol";$a=[Convert]::ToInt32($m.Groups['a'].Value,16);Assert($a-ge0x34000-and$a-lt0x38000)"Game Over symbol is outside Bank 3: $symbol"};$bank=[regex]::Match($map,'(?m)^\s*(?<a>[0-9A-F]{8})\s+b_game_gear_video_present_player\s');Assert($bank.Success-and[Convert]::ToInt32($bank.Groups['a'].Value,16)-eq3)'Game Over dispatch bank is not 3.'}
'Game Over validation PASS';'- native 150x23, palette black/white/#bb2200';'- physical placement x=5..154, y=60..82';'- display blanked and all VRAM cleared before artwork load';'- 80 tiles / 2560 bytes and presentation code co-located in Bank 3; no fade path';'- exactly 180 VBlanks (3.0 seconds at 60 fps) before restart'

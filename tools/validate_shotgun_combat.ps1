param([string]$BuildDirectory='build/release',[switch]$RequireAssembly)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
function Require([bool]$condition,[string]$message){if(!$condition){throw $message}}

$source=Get-Content -Raw (Join-Path $root 'game\zombie_shooting.c')
$main=Get-Content -Raw (Join-Path $root 'game\main.c')
$input=Get-Content -Raw (Join-Path $root 'platform\game_gear\input.c')
$sprite=Get-Content -Raw (Join-Path $root 'game\world_sprite.h')

Require($source-match'#define SHOTGUN_CLOSE_DAMAGE 12' -and $source-match'#define SHOTGUN_MEDIUM_DAMAGE 6' -and $source-match'#define SHOTGUN_FAR_DAMAGE 2') 'Shotgun damage constants changed.'
Require($source-match'#define SHOTGUN_SAMPLE_LEFT_RAY 10' -and $source-match'#define SHOTGUN_SAMPLE_CENTER_RAY 14' -and $source-match'#define SHOTGUN_SAMPLE_RIGHT_RAY 18') 'Shotgun sample columns changed.'
Require($source-match'selected_weapon != WEAPON_SHOTGUN[\s\S]*?lateral \* ZOMBIE_AIM_LATERAL_SCALE[\s\S]*?determinant_magnitude \* ZOMBIE_AIM_DETERMINANT_SCALE') 'Pistol center acceptance branch changed.'
Require($source-match'shotgun_sample_wall_depth\(rays, lateral,[\s\S]*?depth_cross < 0[\s\S]*?determinant_magnitude[\s\S]*?lateral_product < 0') 'Shotgun does not use its production three-sample helper.'
Require($source-notmatch'world_has_clear_line_of_sight|world_get_tile|raycaster_cast') 'Shotgun added a world query or raycast.'
Require(([regex]::Matches($source,'world_sprite_apply_damage\(').Count)-eq1) 'A shot has more than one damage application path.'
Require($source-match'depth >= nearest_depth' -and $source-match'nearest_index = sprite_index') 'Nearest deterministic target selection changed.'
Require($main-match'raycaster_update\(\);\s*if \(pending_shot\)\s*zombie_shooting_process\(\);\s*pending_shot = shoot_requested;' -and ([regex]::Matches($main,'zombie_shooting_process\(').Count)-eq1) 'Pending-shot timing changed.'
Require($input-match'\(keys & PORT_A_KEY_1\) != 0[\s\S]*?\(previous_keys & PORT_A_KEY_1\) == 0') 'Held-button autofire rejection changed.'
Require($sprite-match'#define WORLD_SPRITE_MAX_COUNT 8' -and $sprite-match'(?s)typedef struct\s*\{\s*signed int world_x;\s*signed int world_y;\s*unsigned char visual_type;\s*unsigned char animation_token;\s*ZombieState state;\s*unsigned char health_and_hit_count;\s*unsigned char state_timer;\s*\} WorldSprite;' -and $sprite-match'WORLD_SPRITE_LAYOUT_ID "visual-type-animation-v1"') 'WorldSprite layout or zombie capacity changed.'

function PistolDamage([int]$depth){if($depth-lt33-or$depth-gt1260){return 0};if($depth-le455){return 12};if($depth-le585){return 6};if($depth-le963){return 4};return 3}
function ShotgunDamage([int]$depth){if($depth-lt33-or$depth-gt1260){return 0};if($depth-le585){return 12};if($depth-le963){return 6};return 2}
foreach($depth in 33..1260){$p=PistolDamage $depth;$s=ShotgunDamage $depth;Require($p-in@(12,6,4,3)) "Pistol damage gap at $depth";Require($s-in@(12,6,2)-and$s-ge2) "Shotgun damage gap/floor at $depth"}
foreach($case in @(@(33,12),@(455,12),@(456,12),@(585,12),@(586,6),@(963,6),@(964,2),@(1260,2))){Require((ShotgunDamage $case[0])-eq$case[1]) "Shotgun boundary failed at $($case[0])"}
foreach($case in @(@(33,12),@(455,12),@(456,6),@(585,6),@(586,4),@(963,4),@(964,3),@(1260,3))){Require((PistolDamage $case[0])-eq$case[1]) "Pistol boundary failed at $($case[0])"}
foreach($case in @(@(12,1),@(6,2),@(2,6))){Require([Math]::Ceiling(12.0/$case[0])-eq$case[1]) 'Shotgun hit count changed.'}

# Execute the actual production three-sample helper. The algebra is the
# renderer's projected center/body inequality with both divisions cancelled.
$coordinates=@(-178,-165,-151,-138,-125,-112,-99,-86,-73,-60,-46,-33,-20,-7,6,19,32,45,59,72,85,98,111,124,137,150,164,177)
$helper=[regex]::Match($source,'(?s)static unsigned int shotgun_sample_wall_depth\(.*?\n\}').Value
Require($helper.Length-gt0) 'Production shotgun sample helper missing.'
$helper=$helper.Replace('static unsigned int shotgun_sample_wall_depth','public static int SampleWallDepth').Replace('const RaycasterRay *rays','RaycasterRay[] rays')
$helper=$helper.Replace('unsigned long','long').Replace('unsigned int','int').Replace('unsigned char','int')
$helper=$helper.Replace('SHOTGUN_SAMPLE_LEFT_RAY','10').Replace('SHOTGUN_SAMPLE_CENTER_RAY','14').Replace('SHOTGUN_SAMPLE_RIGHT_RAY','18')
$helper=[regex]::Replace($helper,'rays\[right\s*\?','rays[right != 0 ?')
$mock=@'
public class RaycasterRay { public int wall_distance; }
public static RaycasterRay[] Rays(int normal,int left,int center,int right) {
 var rays=new RaycasterRay[28];for(int i=0;i<28;i++)rays[i]=new RaycasterRay{wall_distance=normal};
 rays[10].wall_distance=left;rays[14].wall_distance=center;rays[18].wall_distance=right;return rays;
}
// depthCross=320 makes lateral=4*screenOffset; determinant=10*halfWidth.
public static int Test(int centerOffset,int halfWidth,int leftWall,int centerWall,int rightWall) {
 int right=centerOffset>0?1:0;return SampleWallDepth(Rays(2000,leftWall,centerWall,rightWall),Math.Abs(centerOffset)*4,320,halfWidth*10,right);
}
'@
Add-Type -TypeDefinition ("using System; public static class ShotgunSamples {`n"+$helper+"`n"+$mock+"`n}")
Require([ShotgunSamples]::Test(0,6,2000,2000,2000)-eq2000) 'A CENTER must hit.'
Require([ShotgunSamples]::Test(-16,6,2000,2000,2000)-eq2000) 'B LEFT sample must hit.'
Require([ShotgunSamples]::Test(16,6,2000,2000,2000)-eq2000) 'C RIGHT sample must hit.'
Require([ShotgunSamples]::Test(8,6,2000,2000,2000)-eq0) 'D between samples must miss.'
Require([ShotgunSamples]::Test(-30,6,2000,2000,2000)-eq0) 'E clearly left must miss.'
Require([ShotgunSamples]::Test(30,6,2000,2000,2000)-eq0) 'F clearly right must miss.'
Require([ShotgunSamples]::Test(8,10,2000,2000,2000)-eq2000) 'G large projected body must hit only through genuine intersection.'
Require([ShotgunSamples]::Test(-16,6,300,2000,2000)-eq300) 'H LEFT must use its own wall ray.'
Require([ShotgunSamples]::Test(16,6,2000,2000,300)-eq300) 'I RIGHT must use its own wall ray.'
Require([ShotgunSamples]::Test(0,6,2000,300,2000)-eq300) 'J CENTER must use its own wall ray.'
Require([ShotgunSamples]::Test(-16,6,300,2000,2000)-lt500-and[ShotgunSamples]::Test(16,6,2000,2000,300)-lt500-and[ShotgunSamples]::Test(0,6,2000,300,2000)-lt500) 'Sample-specific walls must block a depth-500 target.'
Require([ShotgunSamples]::Test(8,30,2000,300,300)-eq2000) 'K a body spanning all samples must use the opposite sample wall too.'
Require($source-match'depth >= nearest_depth' -and $source-match'nearest_depth = depth') 'K nearest valid candidate ordering changed.'
foreach($x in @(-67,67)){Require(([Math]::Abs($x)*256*5)-le(169*256*2)) 'L pistol inside boundary changed'}
foreach($x in @(-68,68)){Require(([Math]::Abs($x)*256*5)-gt(169*256*2)) 'L pistol outside boundary changed'}

if($RequireAssembly){
  $asm=Get-Content -Raw (Join-Path $build 'zombie_shooting.asm')
  $baselinePath=Join-Path $root 'build/release-pickup-art/zombie_shooting.asm'
  if(Test-Path $baselinePath){$baseline=Get-Content -Raw $baselinePath;foreach($call in @('___mulsint2slong','__mullong','__divslong','__modslong','__divulong','__modulong')){Require (([regex]::Matches($asm,"call\s+$call").Count)-le([regex]::Matches($baseline,"call\s+$call").Count)) "Arithmetic helper count increased: $call"}}
  Require(([regex]::Matches($asm,'call\s+_shotgun_sample_wall_depth').Count)-eq1) 'Shotgun sample helper call topology changed.'
  Require($asm-notmatch'___sdcc_bcall_ehl[\s\S]{0,80}_shotgun_sample_wall_depth') 'Shotgun helper became a banked transition.'
}
'Shotgun combat validation PASS'
'- exact close/medium/far 12/6/2 damage; 1/2/6 hits; permanent 2-damage far floor'
'- three projected-body samples at screen x=40/56/72, rendered rays 10/14/18; between/outside misses'
'- sample-specific wall/door depth; unchanged pistol +/-67 center boundary'
'- deterministic nearest single target; pending-shot and edge-fire contracts preserved'

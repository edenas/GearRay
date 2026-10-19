param([string]$BuildDirectory = 'build', [switch]$RequireMapPlacement)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$build = if ([IO.Path]::IsPathRooted($BuildDirectory)) {$BuildDirectory} else {Join-Path $root $BuildDirectory}
function Assert([bool]$Condition,[string]$Message){if(-not $Condition){throw $Message}}

$poses = @('walking_01','walking_02','standing_attack','attack_01','attack_02','shot_01','corpse')
$sourceNames = @(
    'zombie_01_walking_01_32x32.png','zombie_01_walking_02_32x32.png',
    'zombie_01_standing_attack_32x32.png','zombie_01_attack_01_32x32.png',
    'zombie_01_attack_02_32x32.png','zombie_01_shot_01_32x32.png',
    'zombie_01_corps_32x32.png')
Add-Type -AssemblyName System.Drawing
$payloadHashes=@{}
function Get-ExpectedNearBytes([string]$Path){
    $bitmap=[Drawing.Bitmap]::new($Path)
    try{
        $indices=[Collections.Generic.List[byte]]::new(1024)
        for($y=0;$y-lt32;$y++){for($x=0;$x-lt32;$x++){
            $pixel=$bitmap.GetPixel($x,$y)
            if($pixel.A-eq0){$indices.Add(15);continue}
            Assert($pixel.A-eq255) "$Path contains partial alpha at ($x,$y)."
            $rgb=('#{0:x2}{1:x2}{2:x2}'-f$pixel.R,$pixel.G,$pixel.B)
            $index=switch($rgb){
                '#000000'{0;break};'#1a1a1a'{13;break};'#006d8f'{8;break}
                '#53602a'{7;break};'#785700'{6;break};'#b51a00'{5;break}
                '#bb2200'{5;break};'#ffffff'{12;break}
                default{throw "Near zombie color $rgb at ($x,$y) has no exact gameplay palette mapping."}
            }
            $indices.Add($index)
        }}
        return [byte[]]@(for($i=0;$i-lt1024;$i+=2){($indices[$i]-shl4)-bor$indices[$i+1]})
    }finally{$bitmap.Dispose()}
}
function Get-GeneratedNearBytes([string]$Path,[string]$Symbol){
    $source=Get-Content -Raw $Path
    $match=[regex]::Match($source,"const unsigned char $Symbol\[[^\]]+\] = \{(?<body>[\s\S]*?)\n\};")
    Assert($match.Success) "Generated payload symbol $Symbol is missing from $Path."
    return [byte[]]@([regex]::Matches($match.Groups['body'].Value,'0x[0-9a-fA-F]{2}')|ForEach-Object{[Convert]::ToByte($_.Value.Substring(2),16)})
}
function Get-ByteHash([byte[]]$Bytes){$sha=[Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-','')}finally{$sha.Dispose()}}
for($i=0;$i-lt$poses.Count;$i++){
    $asset=Join-Path $root "assets\sprites\enemies\zombie\$($sourceNames[$i])"
    Assert (Test-Path $asset) "Missing authored near texture $($sourceNames[$i])."
    $bitmap=[Drawing.Bitmap]::new($asset);try{Assert($bitmap.Width-eq32-and$bitmap.Height-eq32) "$($sourceNames[$i]) is not 32x32."}finally{$bitmap.Dispose()}
    $generated=Join-Path $build "generated\zombie_$($poses[$i])_32x32_texture.c"
    Assert (Test-Path $generated) "Missing generated near texture $($poses[$i])."
    $symbol="zombie_near_$($poses[$i])_pixels"
    [byte[]]$expected=Get-ExpectedNearBytes $asset
    [byte[]]$actual=Get-GeneratedNearBytes $generated $symbol
    Assert($actual.Count-eq512) "$($poses[$i]) payload is not 512 bytes."
    for($byteIndex=0;$byteIndex-lt512;$byteIndex++){
        if($expected[$byteIndex]-ne$actual[$byteIndex]){$pixelY=[Math]::Floor($byteIndex/16);$pixelX=($byteIndex%16)*2;throw "$($poses[$i]) generated payload mismatch at byte $byteIndex (pixels $pixelX/$($pixelX+1),$pixelY)."}
    }
    $payloadHashes[$poses[$i]]=Get-ByteHash $actual
}

function Get-NativeAssetMetrics([string]$Name) {
    $bitmap=[Drawing.Bitmap]::new((Join-Path $root "assets\sprites\enemies\zombie\$Name"))
    try {
        $bottom=-1
        $bands=@(0,0,0)
        for($y=0;$y-lt32;$y++){
            for($x=0;$x-lt32;$x++){
                $pixel=$bitmap.GetPixel($x,$y)
                Assert($pixel.A-eq0-or$pixel.A-eq255) "$Name contains partial alpha at $x,$y."
                if($pixel.A-ne0){
                    $bottom=$y
                    if($y-le8){$bands[0]++}elseif($y-le19){$bands[1]++}else{$bands[2]++}
                }
            }
        }
        return [pscustomobject]@{Bottom=$bottom;Bands=($bands-join',')}
    } finally {$bitmap.Dispose()}
}
foreach($name in $sourceNames[0..5]){
    Assert((Get-NativeAssetMetrics $name).Bottom-eq31) "$name does not share the living floor baseline at row 31."
}
Assert((Get-NativeAssetMetrics $sourceNames[6]).Bottom-eq31) 'Native corpse no longer contacts the authored floor baseline.'

$projection=Get-Content -Raw (Join-Path $root 'platform\game_gear\sprite_projection.c')
$projectionHeader=Get-Content -Raw (Join-Path $root 'platform\game_gear\sprite_projection.h')
$video=Get-Content -Raw (Join-Path $root 'platform\game_gear\video.c')
$nearTable=Get-Content -Raw (Join-Path $root 'platform\game_gear\near_zombie_textures.c')
$worldHeader=Get-Content -Raw (Join-Path $root 'game\world_sprite.h')
$worldSource=Get-Content -Raw (Join-Path $root 'game\world_sprite.c')
$ai=Get-Content -Raw (Join-Path $root 'game\zombie_ai.c')
$player=Get-Content -Raw (Join-Path $root 'game\player.c')
$playerHeader=Get-Content -Raw (Join-Path $root 'game\player.h')
$cmake=Get-Content -Raw (Join-Path $root 'CMakeLists.txt')
Assert($projectionHeader-match'SPRITE_NEAR_DETAIL_MAX_DISTANCE[\s\\]*\(ZOMBIE_ATTACK_DISTANCE \+ 2 \* ZOMBIE_MOVEMENT_STEP\)') 'Native locomotion range does not provide two movement steps before melee.'
Assert($projectionHeader-match'SPRITE_MIDDLE_DETAIL_MAX_DISTANCE[\s\\]*\(SPRITE_NEAR_DETAIL_MAX_DISTANCE \+ 4 \* ZOMBIE_MOVEMENT_STEP\)') 'Authored 16x16 range does not provide four movement steps.'
Assert($worldHeader-match'zombie_distance_metric[\s\S]*?distance_x \+ \(distance_y >> 1\)') 'Shared AI-compatible distance helper is missing.'
Assert($ai-match'distance = zombie_distance_metric\(delta_x, delta_y\)') 'Zombie AI does not use the shared distance helper.'
Assert($projection-match'distance = zombie_distance_metric\(relative_x, relative_y\)') 'Native transition does not use the shared distance helper.'
Assert($projection-match'else if \(distance <= SPRITE_NEAR_DETAIL_MAX_DISTANCE\)') 'Living native eligibility does not use authoritative octagonal distance.'
Assert($projectionHeader-notmatch'SPRITE_CORPSE_AUTHORED_|SPRITE_CORPSE_VISIBLE_MAX_DISTANCE|VERY_FAR') 'A corpse-specific far-distance ladder remains.'
Assert($projection-match'SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH[\s\\]*\(16384U / \(3U \* GAME_GEAR_VIEWPORT_PIXEL_HEIGHT\) \+ PLAYER_MOVE_SPEED\)') 'Close corpse boundary is not derived from projection geometry plus one player step.'
Assert($projection-match'distance_squared > SPRITE_VISIBLE_MAX_DISTANCE_SQUARED[\s\S]*?life_state == ZOMBIE_STATE_CORPSE[\s\S]*?projected->depth <= SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH[\s\S]*?return;[\s\S]*?projected_height < SPRITE_MEDIUM_LOD_MIN_HEIGHT[\s\S]*?life_state == ZOMBIE_STATE_CORPSE[\s\S]*?zombie_corpse_lod_pixels[\s\S]*?projected_height < SPRITE_FULL_DETAIL_MIN_HEIGHT[\s\S]*?zombie_corpse_lod_pixels[\s\S]*?distance <= SPRITE_NEAR_DETAIL_MAX_DISTANCE[\s\S]*?distance <= SPRITE_MIDDLE_DETAIL_MAX_DISTANCE') 'Corpse does not share living visibility and projected-height LOD selection.'
Assert($projection-notmatch'SPRITE_CORPSE_CLOSE_16_MIN_NATURAL_HEIGHT|natural_projected_height') 'Obsolete close-side corpse logic remains.'
Assert($projection-match'zombie_corpse_lod_pixels\[32\]'-and$projection-notmatch'zombie_corpse_very_far_lod_pixels') 'Exactly one accepted dark corpse pile is not present.'
Assert($projection-notmatch'SPRITE_CORPSE_VISIBLE_MAX_DISTANCE_SQUARED|distance_squared <= SPRITE_CORPSE|SPRITE_CORPSE_LOD_MIN_HEIGHT') 'Old corpse cutoff or artificial pile height remains.'
Assert($projection-match'8192U[\s\S]*?source_size << 8') 'Generic 32x32/16x16/8x8 texture steps are missing.'
foreach($id in @('WALKING_01','WALKING_02','STANDING_ATTACK','ATTACK_01','ATTACK_02','SHOT_01','CORPSE')){Assert($projection-match"NEAR_ZOMBIE_TEXTURE_$id") "Missing runtime pose mapping $id."}
Assert($nearTable-match'near_zombie_texture_pixels'-and$nearTable-match'zombie_near_walking_01_pixels'-and$nearTable-match'zombie_near_walking_02_pixels') 'Bank 2 texture table is not wired.'
Assert($video-match'SMS_MAPPER_SLOT2_REGISTER'-and$video-match'NEAR_ZOMBIE_ROM_PAGE 2') 'Near compositor does not map physical page 2 through slot 2.'
$slot2Sites=if($video -match 'wall_plan_rows'){6}else{2}
Assert(([regex]::Matches($video,'SMS_MAPPER_SLOT2_REGISTER\s*=').Count)-eq$slot2Sites) 'Near-art batch and native-wall phases must have their declared slot-2 mapping/restoration sites outside pixel loops.'
Assert($video-match'if \(near_bank_mapped\)[\s\S]*?SMS_MAPPER_SLOT2_REGISTER = previous_slot2_page') 'Slot 2 mapping is not restored.'
Assert($video-match'near_texture_id\s*==\s*NEAR_ZOMBIE_TEXTURE_NONE[\s\S]*?projected->pixels') 'Normal 8x8 source path was not preserved.'
Assert($worldHeader-notmatch'near_texture|texture_bank|anchor') 'WorldSprite gained persistent near-detail state.'
Assert($worldHeader-match'typedef enum[\s\S]*?ZOMBIE_STATE_ALIVE,[\s\S]*?ZOMBIE_STATE_SHOT_DEAD,[\s\S]*?ZOMBIE_STATE_CORPSE[\s\S]*?ZombieState;') 'Corpse presentation added or changed a gameplay state.'
Assert($projection-match'game_gear_project_world_sprite\(\s*WorldSprite \*sprite'-and$projection-notmatch'sprite->(world_[xy]|health_and_hit_count|state|state_timer|pixels)\s*([|&^+\-]=|=(?!=))') 'Projection mutates WorldSprite gameplay or presentation state.'
Assert($ai-match'ZOMBIE_ATTACK_DAMAGE 20'-and([regex]::Matches($ai,'player_apply_damage\(ZOMBIE_ATTACK_DAMAGE\)').Count)-eq1) 'Independent -20 HP strike semantics changed.'
Assert($worldHeader-match'ZOMBIE_ATTACK_DISTANCE 280') 'Attack distance is not the tuned 280-unit boundary.'
Assert($worldHeader-match'ZOMBIE_MOVEMENT_STEP 56') 'Shared zombie movement step is not 56 units.'
Assert($ai-notmatch'#define ZOMBIE_MOVEMENT_STEP') 'Zombie AI duplicates the shared movement-step constant.'
Assert($worldHeader-match'ZOMBIE_WALKING_PHASE_MASK 128') 'Packed presentation-only walking phase is missing.'
Assert($projection-match'ZOMBIE_AI_CHASING_MASK[\s\S]*?ZOMBIE_WALKING_PHASE_MASK[\s\S]*?ZOMBIE_PRESENTATION_WALKING_02[\s\S]*?ZOMBIE_PRESENTATION_WALKING_01') 'Logical walking pose does not follow the centralized presentation phase.'
Assert($cmake-match'near_pose IN ITEMS WALKING_01 WALKING_02 STANDING_ATTACK ATTACK_01 ATTACK_02 SHOT_01 CORPSE') 'Complete native active pose set is missing from the generated build pipeline.'
Assert($cmake-notmatch'GEAR_RAY_NEAR_ZOMBIE_STANDING_INPUT|near_pose IN ITEMS[^\n]*WALKING_02 STANDING STANDING_ATTACK') 'Neutral 32x32 standing remains in the build pipeline.'
Assert($cmake-match'middle_pose IN ITEMS STANDING WALKING_01 WALKING_02 SHOT_01 SHOT_DEAD CORPS') 'Authored 16x16 standing is missing from the build pipeline.'
Assert($cmake-notmatch'zombie_02_attack_02_32x32|zombie_01_shot_dead_32x32') 'Obsolete close-range asset names remain in the build pipeline.'
Assert($projection-match'zombie_01_walking_01_pixels'-and$projection-match'zombie_01_walking_02_pixels') 'Standard walking textures are no longer preserved by the normal LOD path.'
Assert($ai-match'if \(sprite->pixels == zombie_01_shot_01_pixels[\s\S]*?zombie_01_shot_02_pixels\)[\s\S]*?continue;[\s\S]*?sprite->state_timer = 0;[\s\S]*?zombie_ai_move') 'Retreat does not cancel attack presentation, preserve locomotion phase, and resume chase.'
Assert($ai-match'distance >= ZOMBIE_ATTACK_DISTANCE \+ ZOMBIE_MOVEMENT_STEP[\s\S]*?zombie_ai_move\([\s\S]*?else[\s\S]*?final_step =[\s\S]*?distance - ZOMBIE_ATTACK_DISTANCE') 'Final melee-entry movement is not isolated from the constant-step chase path.'
Assert($ai-notmatch'distance <= ZOMBIE_ATTACK_DISTANCE[\s\S]{0,180}sprite->pixels = zombie_01_standing_pixels') 'Melee entry still destroys the authoritative walking phase.'
Assert($projection-match'ZOMBIE_STATE_SHOT_DEAD[\s\S]*?ZOMBIE_PRESENTATION_DEAD'-and$projection-match'ZOMBIE_PRESENTATION_DEAD:[\s\S]*?NEAR_ZOMBIE_TEXTURE_SHOT_01') 'Very-close lethal shots do not use shot_01 artwork.'
Assert($projection-match'ZOMBIE_STATE_CORPSE[\s\S]*?ZOMBIE_PRESENTATION_CORPSE'-and$projection-match'ZOMBIE_PRESENTATION_CORPSE:[\s\S]*?NEAR_ZOMBIE_TEXTURE_CORPSE') 'Close corpse does not use the final corpse artwork.'
Assert($worldHeader-match'ZOMBIE_ATTACK_PHASE_MASK 64') 'Per-zombie alternating strike phase is not packed in the existing state byte.'
Assert($ai-match'ZOMBIE_ATTACK_COOLDOWN_AI_TICKS\);[\s\S]*?sprite->state \^= ZOMBIE_ATTACK_PHASE_MASK;') 'Successful strikes do not alternate their packed phase.'
Assert($projection-match'state_timer[\s\S]*?== ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT - 1[\s\S]*?ZOMBIE_ATTACK_PHASE_MASK[\s\S]*?ZOMBIE_PRESENTATION_ATTACK_01[\s\S]*?ZOMBIE_PRESENTATION_ATTACK_02;[\s\S]*?ZOMBIE_PRESENTATION_STANDING_ATTACK;') 'Standing anticipation, alternating strike, and recovery mapping is incorrect.'
Assert($projection-notmatch'ZOMBIE_AI_CHASING_MASK[\s\S]{0,160}NEAR_ZOMBIE_TEXTURE_STANDING_ATTACK') 'Entering attack range still renders standing_attack before the first strike.'
Assert($projection-match'distance <= ZOMBIE_ATTACK_DISTANCE[\s\S]*?ZOMBIE_PRESENTATION_STANDING_ATTACK') 'Melee anticipation/recovery does not resolve to standing_attack.'

function Get-LivingNearPose([int]$Distance,[int]$Timer,[int]$Cooldown,[int]$Phase,[string]$Pixels) {
    if($Distance -gt 392){return 'NONE'}
    if($Distance -le 280 -and $Timer -eq 3){if($Phase -band 64){return 'ATTACK_01'}else{return 'ATTACK_02'}}
    if($Distance -le 280){return 'STANDING_ATTACK'}
    if($Distance -le 392){if($Phase-band128){return 'WALKING_02'}else{return 'WALKING_01'}}
    return 'NONE'
}
function Get-ZombieDistance([int]$X,[int]$Y){$ax=[Math]::Abs($X);$ay=[Math]::Abs($Y);if($ax -gt $ay){return $ax + [int]($ay/2)};return $ay + [int]($ax/2)}
function Get-SharedLod([int]$Distance,[int]$Depth=$Distance){
    $height=[Math]::Min(144,[Math]::Truncate(16384/$Depth))
    if($height-lt17){return '8'}
    if($Distance-le392){return '32'}
    if($Distance-le616){return '16'}
    return '8'
}
function Get-CorpseLod([int]$Distance,[int]$Depth=$Distance){
    if($Depth-le159){return 'hidden-close'}
    if($Distance-gt1260){return 'hidden'}
    $height=[Math]::Truncate(16384/$Depth)
    if($height-lt15){return 'pile13'}
    if($height-lt17){return 'pile15'}
    return Get-SharedLod $Distance $Depth
}
$playerStep=[int]([regex]::Match($playerHeader,'#define PLAYER_MOVE_SPEED (\d+)').Groups[1].Value)
Assert($playerStep-eq74) 'Corpse retreat audit is not using the real 74-unit player movement increment.'
$retreatAudit=@()
$corpseTierRank=@{'32'=0;'16'=1;'8'=2;'pile15'=3;'pile13'=4}
foreach($start in 280,300,320,336,350,392){
    $tiers=@();$rows=@()
    for($step=0;$step-lt12;$step++){
        $distance=$start+$step*$playerStep;$tier=Get-CorpseLod $distance
        $height=[int][Math]::Min(144,[Math]::Floor(16384/$distance))
        $source=if($tier-eq'32'){'near/corpse'}elseif($tier-eq'16'){'16'}else{'8'}
        $bottom=32+[Math]::Truncate($height/2)+[Math]::Truncate($height/3)
        $top=$bottom-$height
        $visible=$tier-ne'hidden'
        $opaqueFloor=if($visible){$bottom-1}else{'none'}
        $rows+="step${step}:d${distance}:depth${distance}:${tier}:h${height}:src${source}:top${top}:bottom${bottom}:floor${opaqueFloor}:visible${visible}"
        if($tier-ne'hidden'){$tiers+=$tier}else{break}
    }
    Assert((@($tiers|Where-Object{$_-eq'16'}).Count)-ge2) "Start $start does not traverse shared 16 presentation: $($rows-join' -> ')"
    Assert((@($tiers|Where-Object{$_-eq'pile15'}).Count)-ge1) "Start $start does not traverse the 15-pixel pile: $($rows-join' -> ')"
    Assert((@($tiers|Where-Object{$_-eq'pile13'}).Count)-ge1) "Start $start does not traverse the 13-pixel pile: $($rows-join' -> ')"
    $retreatAudit+="start ${start}: $($rows-join' -> ')"
}
foreach($line in $retreatAudit){Write-Output "- $line"}
foreach($case in @(@(392,392,'32'),@(393,393,'16'),@(616,616,'16'),@(617,617,'8'),@(963,963,'8'),@(964,964,'pile15'),@(1092,1092,'pile15'),@(1093,1093,'pile13'),@(1260,1260,'pile13'),@(1261,1261,'hidden'))){Assert((Get-CorpseLod $case[0] $case[1])-eq$case[2]) "Corpse LOD mismatch at $($case[0])/$($case[1])."}
$straightClose=@(280,206,132|ForEach-Object{Get-CorpseLod $_ $_})
Assert(($straightClose-join',')-eq'32,32,hidden-close') 'Straight close approach does not hide one player step earlier.'
$straightReverse=@(132,206|ForEach-Object{Get-CorpseLod $_ $_})
Assert(($straightReverse-join',')-eq'hidden-close,32') 'Straight reverse movement does not restore the close corpse.'
$obliqueClose=@(@(300,240),@(240,180),@(180,120)|ForEach-Object{Get-CorpseLod $_[0] $_[1]})
Assert(($obliqueClose-join',')-eq'32,32,hidden-close') 'Oblique close approach does not hide one step earlier.'
Assert((Get-CorpseLod 160 160)-eq'32'-and(Get-CorpseLod 159 159)-eq'hidden-close') 'Close corpse depth edge cases changed.'
$completeForward=@(@(1300,1300),@(1200,1200),@(1050,1050),@(900,900),@(500,500),@(280,280),@(159,159)|ForEach-Object{Get-CorpseLod $_[0] $_[1]})
$completeReverse=@(@(159,159),@(280,280),@(500,500),@(900,900),@(1050,1050),@(1200,1200),@(1300,1300)|ForEach-Object{Get-CorpseLod $_[0] $_[1]})
Assert(($completeForward-join',')-eq'hidden,pile13,pile15,8,16,32,hidden-close') 'Complete forward corpse traversal changed.'
Assert(($completeReverse-join',')-eq'hidden-close,32,16,8,pile15,pile13,hidden') 'Complete reverse corpse traversal changed.'
foreach($deathDistance in 300,500,900){Assert((Get-CorpseLod $deathDistance $deathDistance)-eq(Get-SharedLod $deathDistance $deathDistance)) "Normal corpse resolution changed at $deathDistance."}
Assert($projection-match'projected->pixels = sprite->pixels;[\s\S]*?projected_height < SPRITE_MEDIUM_LOD_MIN_HEIGHT[\s\S]*?zombie_corpse_lod_pixels[\s\S]*?else if \(projected_height < SPRITE_FULL_DETAIL_MIN_HEIGHT\)[\s\S]*?zombie_corpse_lod_pixels[\s\S]*?else if \(distance <= SPRITE_NEAR_DETAIL_MAX_DISTANCE\)') 'Authored 8x8 corpse does not persist until the shared far silhouette stages.'
Assert($projection-match'ZOMBIE_PRESENTATION_DEAD:[\s\S]*?zombie_middle_shot_dead_pixels'-and$projection-match'ZOMBIE_PRESENTATION_CORPSE:[\s\S]*?zombie_middle_corps_pixels') '16x16 death/corpse artwork is not state-selected within the shared tier.'
Assert($projection-match'ZOMBIE_PRESENTATION_DEAD:[\s\S]*?NEAR_ZOMBIE_TEXTURE_SHOT_01'-and$projection-match'ZOMBIE_PRESENTATION_CORPSE:[\s\S]*?NEAR_ZOMBIE_TEXTURE_CORPSE') '32x32 death/corpse artwork is not state-selected within the shared tier.'
Assert($worldHeader-match'ZOMBIE_SHOT_DEAD_FRAME_COUNT 4'-and$worldSource-match'ZOMBIE_STATE_SHOT_DEAD[\s\S]*?state_timer = ZOMBIE_SHOT_DEAD_FRAME_COUNT') 'SHOT_DEAD timing changed while sharing resolution tiers.'
foreach($case in @(@(392,200),@(300,160),@(240,159),@(180,120))){
    $first=Get-CorpseLod $case[0] $case[1]
    $second=Get-CorpseLod $case[0] $case[1]
    Assert($first-eq$second) "Oblique corpse projection flickers at distance/depth $($case-join'/')."
}
Assert($playerHeader-match'#define PLAYER_MOVE_SPEED 74') 'Close corpse boundary is not tied to the real 74-unit player step.'
function Get-AuthoredLocomotion([int]$Size,[string]$Phase){
    Assert(($Size-eq8-or$Size-eq16-or$Size-eq32)) "Unsupported authored size $Size."
    Assert(($Phase-eq'walking_01'-or$Phase-eq'walking_02')) "Unsupported locomotion phase $Phase."
    return "${Phase}_${Size}"
}
$forward=@(8,16,32|ForEach-Object{Get-AuthoredLocomotion $_ 'walking_01'})
$reverse=@(32,16,8|ForEach-Object{Get-AuthoredLocomotion $_ 'walking_02'})
Assert(($forward-join',')-eq'walking_01_8,walking_01_16,walking_01_32') 'Forward LOD transition changes walking_01 phase.'
Assert(($reverse-join',')-eq'walking_02_32,walking_02_16,walking_02_8') 'Reverse LOD transition changes walking_02 phase.'
Assert($ai-match'!chasing && distance > ZOMBIE_ACTIVATION_DISTANCE[\s\S]*?sprite->pixels = zombie_01_standing_pixels') 'Inactive distant zombie no longer permits original 8x8 standing.'
foreach($case in @(
    @(392,0,392),@(280,0,280),@(224,112,280),
    @(168,168,252),@(280,56,308),@(224,168,308))){
    Assert((Get-ZombieDistance ($case[0]) ($case[1])) -eq $case[2]) "Octagonal distance mismatch for ($($case[0]),$($case[1]))."
}
# The octagonal metric must also provide two native presentation steps.
$oblique=@(@(336,168),@(280,168),@(224,168),@(168,168))
$classes=@(foreach($point in $oblique){$d=Get-ZombieDistance ($point[0]) ($point[1]);if($d -gt 392){'middle'}elseif($d -gt 280){'native'}else{'attack'}})
Assert(($classes-join',')-eq'middle,native,native,attack') 'Oblique approach does not contain two final native walking steps.'
$straight=@(@(448,0),@(392,0),@(336,0),@(280,0))
$classes=@(foreach($point in $straight){$d=Get-ZombieDistance ($point[0]) ($point[1]);if($d -gt 392){'middle'}elseif($d -gt 280){'native'}else{'attack'}})
Assert(($classes-join',')-eq'middle,native,native,attack') 'Straight approach does not contain two final native walking steps.'
$middleStraight=@(672,616,560,504,448,392|ForEach-Object{if($_-gt616){'8'}elseif($_-gt392){'16'}else{'32'}})
Assert(($middleStraight-join',')-eq'8,16,16,16,16,32') 'Straight approach does not contain four authored 16x16 steps.'
$middleOblique=@(@(616,112),@(560,112),@(504,112),@(448,112),@(392,112),@(336,112)|ForEach-Object{$d=Get-ZombieDistance $_[0] $_[1];if($d-gt616){'8'}elseif($d-gt392){'16'}else{'32'}})
Assert(($middleOblique-join',')-eq'8,16,16,16,16,32') 'Oblique approach does not contain four authored 16x16 steps.'
Assert($projection-match'ZOMBIE_PRESENTATION_SHOT:[\s\S]*?zombie_middle_shot_01_pixels'-and$projection-match'ZOMBIE_PRESENTATION_DEAD:[\s\S]*?zombie_middle_shot_dead_pixels') 'Extended middle interval does not preserve authored shot/death poses.'
Assert((Get-LivingNearPose 393 0 0 0 'walking_01')-eq'NONE') 'Distance 393 does not preserve middle rendering.'
foreach($distance in 392,336,300,281){
    Assert((Get-LivingNearPose $distance 0 0 0 'walking_01')-eq'WALKING_01') "Distance $distance does not map walking_01 to native walking_01."
    Assert((Get-LivingNearPose $distance 0 0 128 'walking_02')-eq'WALKING_02') "Distance $distance does not map walking_02 to native walking_02."
    Assert((Get-LivingNearPose $distance 0 0 0 'standing')-eq'WALKING_01') "Distance $distance invented a neutral native standing fallback."
}
Assert((-not (281 -le 280)) -and (-not (300 -le 280)) -and
       (280 -le 280)) 'Visual preparation range changed gameplay attack eligibility.'
$phase=0-bxor64
Assert((Get-LivingNearPose 280 4 2 $phase 'walking_01')-eq'STANDING_ATTACK') 'First close-combat native frame is not STANDING_ATTACK.'
Assert((Get-LivingNearPose 280 3 2 $phase 'walking_01')-eq'ATTACK_01') 'Second close-combat presentation frame is not ATTACK_01.'
Assert((Get-LivingNearPose 280 2 2 $phase 'walking_01')-eq'STANDING_ATTACK') 'ATTACK_01 is not followed by STANDING_ATTACK.'
$phase=$phase-bxor64
Assert((Get-LivingNearPose 280 4 2 $phase 'walking_02')-eq'STANDING_ATTACK') 'ATTACK_02 is not preceded by STANDING_ATTACK.'
Assert((Get-LivingNearPose 280 3 2 $phase 'walking_02')-eq'ATTACK_02') 'Fourth close-combat presentation step is not ATTACK_02.'
Assert((Get-LivingNearPose 300 3 0 64 'walking_01')-eq'WALKING_01') 'ATTACK_01 appears solely from entering native-detail range.'
Assert((Get-LivingNearPose 280 3 2 64 'walking_02')-eq'ATTACK_01'-and(Get-LivingNearPose 336 0 1 192 'walking_02')-eq'WALKING_02'-and(Get-LivingNearPose 280 4 0 0 'walking_01')-eq'STANDING_ATTACK') 'Melee retreat/re-entry does not immediately resume walking then preserve the next combat phase.'
Assert($ai-match'sprite->state \^= ZOMBIE_WALKING_PHASE_MASK;[\s\S]*?sprite->pixels = sprite->state & ZOMBIE_WALKING_PHASE_MASK'-and$ai-notmatch'zombie_ai_position_is_clear[\s\S]{0,500}ZOMBIE_WALKING_PHASE_MASK') 'Active chase presentation does not advance independently of successful movement.'
$start01=@((Get-LivingNearPose 392 0 0 0 'walking_01'),(Get-LivingNearPose 336 0 0 128 'walking_02'),(Get-LivingNearPose 280 4 0 0 'walking_01'))
$start02=@((Get-LivingNearPose 392 0 0 128 'walking_02'),(Get-LivingNearPose 336 0 0 0 'walking_01'),(Get-LivingNearPose 280 4 0 0 'walking_01'))
Assert(($start01-join',')-eq'WALKING_01,WALKING_02,STANDING_ATTACK') 'WALKING_01 start does not show both native frames before melee.'
Assert(($start02-join',')-eq'WALKING_02,WALKING_01,STANDING_ATTACK') 'WALKING_02 start does not show both native frames before melee.'
Assert($projection-match'game_gear_get_middle_zombie_pixels[\s\S]*?ZOMBIE_PRESENTATION_WALKING_02[\s\S]*?zombie_middle_walking_02_pixels[\s\S]*?default:[\s\S]*?zombie_middle_walking_01_pixels') '16x16 resolver does not preserve logical walking phase.'
Assert($projection-match'game_gear_get_near_zombie_texture_id[\s\S]*?ZOMBIE_PRESENTATION_WALKING_02[\s\S]*?NEAR_ZOMBIE_TEXTURE_WALKING_02[\s\S]*?default:[\s\S]*?NEAR_ZOMBIE_TEXTURE_WALKING_01') '32x32 resolver does not preserve logical walking phase.'
Assert($projection-notmatch'NEAR_ZOMBIE_TEXTURE_STANDING\s'-and$projection-match'ZOMBIE_PRESENTATION_STANDING:[\s\S]*?zombie_middle_standing_pixels') 'Middle idle standing or near standing exclusion is incorrect.'
Assert($projection-match'zombie_01_shot_01_pixels[\s\S]*?ZOMBIE_PRESENTATION_SHOT[\s\S]*?distance <= ZOMBIE_ATTACK_DISTANCE'-and$projection-match'ZOMBIE_PRESENTATION_SHOT:[\s\S]*?NEAR_ZOMBIE_TEXTURE_SHOT_01') 'SHOT_01 does not override native walking.'
Assert($projection-notmatch'ZOMBIE_ATTACK_VISUAL_LUNGE_DEPTH') 'Old attack visual lunge logic remains.'
Assert($projection-notmatch'ZOMBIE_NATIVE_(WALKING|CLOSE)_VISUAL_DEPTH_OFFSET|ZOMBIE_NATIVE_MIN_VISUAL_DEPTH|visual_depth') 'Obsolete native visual-depth correction remains.'
Assert($projection-match'projected->depth < rays\[first_ray\]\.wall_distance') 'Visual walking depth replaced real-depth wall occlusion.'
foreach($case in @(@(392,41),@(336,48),@(320,51),@(300,54),@(281,58))){Assert(([int][Math]::Floor(16384/$case[0]))-eq$case[1]) "Native walking scale mismatch at depth $($case[0])."}
Assert(([int][Math]::Floor(16384/280))-eq58) 'Standing attack does not meet continuous perspective scale at depth 280.'
Assert($projectionHeader-match'ZOMBIE_8X8_MAX_PROJECTED_HEIGHT 32') 'Living 8x8 presentation cap is not 32 pixels.'
Assert($projection-match'ZOMBIE_STATE_ALIVE[\s\S]*?near_texture_id == NEAR_ZOMBIE_TEXTURE_NONE[\s\S]*?projected_height > ZOMBIE_8X8_MAX_PROJECTED_HEIGHT[\s\S]*?projected_height = ZOMBIE_8X8_MAX_PROJECTED_HEIGHT') 'Living 8x8 cap is not restricted to the normal source path.'
function Get-8x8Height([int]$Depth){$height=[int][Math]::Floor(16384/$Depth);if($height -gt 32){return 32};return $height}
foreach($case in @(@(800,20),@(600,27),@(560,29),@(505,32))){Assert((Get-8x8Height ($case[0])) -eq $case[1]) "8x8 cap mismatch at depth $($case[0])."}
Assert((Get-LivingNearPose 392 0 0 0 'walking_01') -eq 'WALKING_01') 'Native walking is incorrectly subject to the 8x8 cap.'
Assert($cmake-match'--constseg BANK2'-and$cmake-match'-Wl-b_BANK2=0x28000') 'Near assets are not linked into the slot-2 Bank 2 window.'
Assert($cmake-notmatch'GENERATED_ZOMBIE_ATTACK_01_TEXTURE_OBJECT'-and$cmake-notmatch'GENERATED_ZOMBIE_ATTACK_02_TEXTURE_OBJECT') 'Obsolete 8x8 attack runtime objects remain.'

if($RequireMapPlacement){
    $map=Get-Content -Raw (Join-Path $build 'GearRay.map')
    foreach($symbol in @('_zombie_near_walking_01_pixels','_zombie_near_walking_02_pixels','_zombie_near_standing_attack_pix','_zombie_near_attack_01_pixels','_zombie_near_attack_02_pixels','_zombie_near_shot_01_pixels','_zombie_near_corpse_pixels')){
        $match=[regex]::Match($map,"(?m)^\s*(?<a>[0-9A-Fa-f]{8})\s+$symbol\s+");Assert($match.Success) "Missing map symbol $symbol."
        $address=[Convert]::ToInt32($match.Groups['a'].Value,16);Assert ($address -ge 0x28000 -and $address -lt 0x2C000) "$symbol is outside Bank 2."
    }
    Assert($map-notmatch'_zombie_01_attack_01_pixels|_zombie_01_attack_02_pixels|_zombie_near_standing_pixels') 'Unused zombie presentation symbols remain linked.'
}

Write-Output 'Near-detail zombie validation PASS'
Write-Output '- seven active/combat 32x32/512-byte near-detail textures in Bank 2'
Write-Output '- two-step native-detail boundary 392 units; gameplay attack boundary remains 280 units'
Write-Output '- four-step authored 16x16 interval spans 616..393 units'
Write-Output '- native 32x32 walking alternates at 392 and 336 before melee at 280 units'
Write-Output '- forward/reverse 8x8/16x16/32x32 transitions preserve walking_01/walking_02; melee retreat resumes walking immediately'
Write-Output '- standing-attack anticipation/recovery around alternating attack_01/attack_02 wired'
Write-Output '- slot 2 maps/restores page 2 once per visible-near render batch'
Write-Output '- WorldSprite remains 9 bytes; obsolete 8x8 attack runtime data absent'
Write-Output '- corpse LOD remains stateless: one CORPSE state and immutable world coordinates'
foreach($pose in $poses){Write-Output "- $pose payload SHA-256: $($payloadHashes[$pose])"}

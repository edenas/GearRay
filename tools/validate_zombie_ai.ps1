$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$ai = Get-Content -Raw -LiteralPath (Join-Path $root 'game\zombie_ai.c')
$aiHeader = Get-Content -Raw -LiteralPath (Join-Path $root 'game\zombie_ai.h')
$main = Get-Content -Raw -LiteralPath (Join-Path $root 'game\main.c')
$enemyCollision = Get-Content -Raw -LiteralPath (Join-Path $root 'game\enemy_collision.c')
$sprites = Get-Content -Raw -LiteralPath (Join-Path $root 'game\world_sprite.c')
$spriteHeader = Get-Content -Raw -LiteralPath (Join-Path $root 'game\world_sprite.h')
$cmake = Get-Content -Raw -LiteralPath (Join-Path $root 'CMakeLists.txt')

function Assert-Match([string]$Text, [string]$Pattern, [string]$Message) {
    if ($Text -notmatch $Pattern) { throw $Message }
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

Assert-Match $aiHeader 'ZOMBIE_AI_UPDATE_INTERVAL\s+4' 'AI cadence is not four frames'
Assert-Match $aiHeader 'zombie_ai_update_all\(void\);' 'AI entry declaration is missing'
Assert-Match $ai 'ZOMBIE_ACTIVATION_DISTANCE\s+963' 'Activation distance is not 963 inclusive'
Assert-Match $ai 'ZOMBIE_LOSE_DISTANCE\s+1260' 'Lose distance is not 1260 inclusive'
Assert-Match $spriteHeader 'zombie_distance_metric[\s\S]*?distance_x \+ \(distance_y >> 1\)' 'Shared octagonal distance metric is missing'
Assert-Match $ai 'distance = zombie_distance_metric\(delta_x, delta_y\)' 'Zombie AI does not use the shared distance metric'
Assert-Match $ai 'while \(1\)[\s\S]*?world_is_wall' 'Tile LOS traversal is missing'
Assert-Match $spriteHeader 'ZOMBIE_MOVEMENT_STEP\s+56' 'Zombie movement step is not the shared 56 units'
Assert-True ($ai -notmatch '#define ZOMBIE_MOVEMENT_STEP') 'Zombie AI duplicates the shared movement-step constant'
Assert-Match $ai 'distance >= ZOMBIE_ATTACK_DISTANCE \+ ZOMBIE_MOVEMENT_STEP[\s\S]*?zombie_ai_move\([\s\S]*?else[\s\S]*?final_step =[\s\S]*?distance - ZOMBIE_ATTACK_DISTANCE' 'Constant-step chase fast path and inline final approach are missing'
Assert-Match $spriteHeader 'ZOMBIE_COLLISION_RADIUS\s+32' 'Zombie collision radius changed'
Assert-Match $ai 'world_is_wall' 'LOS does not use the authoritative blocker query'
Assert-Match $ai 'enemy_position_is_walkable' 'Movement does not use reusable enemy collision'
Assert-Match $ai 'WORLD_SPRITE_LIFE_STATE\(other\) != ZOMBIE_STATE_ALIVE' 'Non-living sprites may block movement'
Assert-Match $ai 'sprite->state_timer != 0[\s\S]*?continue' 'Hit reaction does not pause movement'
Assert-Match $ai 'WORLD_SPRITE_LIFE_STATE\(sprite\) != ZOMBIE_STATE_ALIVE[\s\S]*?continue' 'Dead sprites may enter AI'
Assert-Match $enemyCollision 'enemy_position_is_walkable[\s\S]*?world_is_wall' 'Enemy collision does not share wall/door semantics'
Assert-Match $spriteHeader 'ZOMBIE_AI_CHASING_MASK\s+128' 'AI state is not isolated in bit 7'
Assert-Match $spriteHeader 'ZOMBIE_HIT_COUNT_MASK\s+112' 'Hit count is not isolated in bits 4..6'
Assert-Match $sprites 'ZOMBIE_HIT_COUNT_MASK' 'Damage reads the AI bit as hit count'
Assert-Match $sprites 'ZOMBIE_AI_CHASING_MASK[\s\S]*?ZOMBIE_HIT_COUNT_SHIFT' 'Nonlethal damage does not preserve chasing state'
Assert-Match $main '\+\+zombie_ai_frame_counter[\s\S]*?zombie_ai_update_all\(\)' 'Main loop lacks one shared AI cadence'
Assert-True (([regex]::Matches($main, 'zombie_ai_update_all\(\)')).Count -eq 1) 'AI has more than one main-loop call site'
Assert-Match $cmake 'zombie_ai\.c[\s\S]*?--codeseg BANK1' 'Zombie AI is not compiled into BANK1'
Assert-Match $spriteHeader 'ZOMBIE_WALKING_PHASE_MASK\s+128' 'Packed walking animation phase is missing'
Assert-Match $ai 'sprite->state \^= ZOMBIE_WALKING_PHASE_MASK;[\s\S]*?sprite->state_timer != 0[\s\S]*?sprite->animation_token = sprite->state & ZOMBIE_WALKING_PHASE_MASK[\s\S]*?ZOMBIE_ANIMATION_WALKING_02[\s\S]*?ZOMBIE_ANIMATION_WALKING_01' 'Active chase does not advance the packed walking phase and publish its logical token on the fixed AI cadence'
Assert-True ($ai -notmatch 'zombie_ai_position_is_clear[\s\S]{0,500}ZOMBIE_WALKING_PHASE_MASK') 'Walking phase still depends on accepted collision movement'
Assert-True (([regex]::Matches($ai, 'world_has_clear_line_of_sight\(')).Count -eq 2) 'Walking animation added an extra LOS query'
Assert-True (([regex]::Matches($ai, 'zombie_ai_position_is_clear\(')).Count -eq 4) 'Direct, bounded tangent-loop, and final movement collision queries changed unexpectedly'
Assert-Match $ai 'zombie_ai_wall_following_mask & sprite_mask[\s\S]*?zombie_ai_wall_negative_mask & sprite_mask[\s\S]*?slide_step = move_x \? step_y : step_x;[\s\S]*?for \(slide_attempt = 0; slide_attempt != 2; \+\+slide_attempt\)[\s\S]*?zombie_ai_position_is_clear[\s\S]*?slide_attempt != 0[\s\S]*?zombie_ai_wall_negative_mask \^= sprite_mask[\s\S]*?slide_step = -slide_step;' 'Blocked chase does not preserve and validate its player-relative tangent'
Assert-Match $ai 'if \(!chasing[\s\S]*?!world_has_clear_line_of_sight' 'LOS is not limited to initial activation'
Assert-True ($spriteHeader -notmatch '(?m)^\s*(unsigned|signed|ZombieState)[^;]*phase[^;]*;') 'Attack phase added a persistent struct field'
Assert-Match $aiHeader 'extern unsigned char zombie_ai_wall_following_mask;[\s\S]*?extern unsigned char zombie_ai_wall_negative_mask;' 'Two packed navigation masks are missing'
Assert-Match $sprites 'world_sprite_remove[\s\S]*?zombie_ai_wall_following_mask = 0;' 'Sprite compaction does not invalidate navigation masks'

function Test-Range([int]$Distance, [bool]$Chasing) {
    if ($Chasing) { return $Distance -le 1260 }
    return $Distance -le 963
}

Assert-True (-not (Test-Range 964 $false)) 'Idle zombie activates beyond 963'
Assert-True (Test-Range 963 $false) 'Idle zombie fails at activation boundary'
Assert-True (Test-Range 1260 $true) 'Chasing zombie fails at lose boundary'
Assert-True (-not (Test-Range 1261 $true)) 'Chasing zombie persists beyond 1260'
function Test-ChaseLos([bool]$Chasing,[int]$Distance,[bool]$HasLos){
    if(((-not $Chasing)-and$Distance-gt963)-or($Chasing-and$Distance-gt1260)){return $false}
    if((-not $Chasing)-and(-not $HasLos)){return $false}
    return $true
}
Assert-True (-not(Test-ChaseLos $false 900 $false)) 'Idle zombie activates through a wall.'
Assert-True (Test-ChaseLos $true 900 $false) 'Active pursuit cannot complete an occluded corner.'
Assert-True (-not(Test-ChaseLos $true 1261 $true)) 'LOS bypasses the existing lose-distance boundary.'
Assert-True (56 -lt 74) 'Zombie is not slower than the player per update'
Assert-True ((56 * (60 / 4)) -eq 840) 'Zombie units-per-second model changed'
Assert-True ((56 * (60 / 4) / 256) -eq 3.28125) 'Zombie tiles-per-second model changed'
Assert-True (56 -lt 128) 'Zombie step could tunnel through a 64-unit separation body'
Assert-True (56 -lt (256 - 2 * 32)) 'Zombie step is unsafe for tile collision geometry'

$walkingPhase = 0
$sequence = @()
foreach($tick in 1..6){$walkingPhase=$walkingPhase-bxor128;$sequence+=if($walkingPhase-band128){'walking_02'}else{'walking_01'}}
Assert-True (($sequence-join',')-eq'walking_02,walking_01,walking_02,walking_01,walking_02,walking_01') 'Fixed-cadence walking sequence does not alternate continuously'
Assert-True ((4 * 2) -eq 8) 'Two-frame walking loop cadence is not eight rendered frames'

function Test-CornerPosition([int]$X, [int]$Y) {
    $left = $X - 32; $right = $X + 32
    $top = $Y - 32; $bottom = $Y + 32
    return -not ($right -ge 512 -and $left -le 767 -and
                 $bottom -ge 512 -and $top -le 767)
}

function Move-CornerModel([int]$X, [int]$Y, [int]$PlayerX,
                          [int]$PlayerY) {
    $deltaX = $PlayerX - $X; $deltaY = $PlayerY - $Y
    $stepX = if ($deltaX -lt 0) { -56 } else { 56 }
    $stepY = if ($deltaY -lt 0) { -56 } else { 56 }
    $moveX = [Math]::Abs($deltaX) -ge [Math]::Abs($deltaY)
    $candidates = @()
    if ($moveX) {
        $candidates += [pscustomobject]@{ X = $X + $stepX; Y = $Y }
        $slide = $stepY
        $candidates += [pscustomobject]@{ X = $X; Y = $Y + $slide }
        $candidates += [pscustomobject]@{ X = $X; Y = $Y - $slide }
    }
    else {
        $candidates += [pscustomobject]@{ X = $X; Y = $Y + $stepY }
        $slide = $stepX
        $candidates += [pscustomobject]@{ X = $X + $slide; Y = $Y }
        $candidates += [pscustomobject]@{ X = $X - $slide; Y = $Y }
    }
    foreach ($candidate in $candidates) {
        if (Test-CornerPosition $candidate.X $candidate.Y) {
            return @($candidate.X, $candidate.Y)
        }
    }
    return @($X, $Y)
}

$unobstructed = Move-CornerModel 256 256 900 400
Assert-True ($unobstructed[0] -eq 312 -and $unobstructed[1] -eq 256) `
    'Unobstructed dominant-axis pursuit changed.'

function New-Wall([int]$Left,[int]$Top,[int]$Right,[int]$Bottom) {
    return [pscustomobject]@{Left=$Left;Top=$Top;Right=$Right;Bottom=$Bottom}
}
function Test-GeometryClear([int]$X,[int]$Y,[object[]]$Walls) {
    foreach($wall in $Walls){
        if($X+32-ge$wall.Left-and$X-32-le$wall.Right-and
           $Y+32-ge$wall.Top-and$Y-32-le$wall.Bottom){return $false}
    }
    return $true
}
function Get-ModelDistance([int]$X,[int]$Y,[int]$PlayerX,[int]$PlayerY){
    $dx=[Math]::Abs($PlayerX-$X);$dy=[Math]::Abs($PlayerY-$Y)
    if($dx-gt$dy){return $dx+[Math]::Truncate($dy/2)}
    return $dy+[Math]::Truncate($dx/2)
}
function Move-GeometryModel([int]$X,[int]$Y,[int]$PlayerX,[int]$PlayerY,
                            [object[]]$Walls,[object]$Follow){
    $dx=$PlayerX-$X;$dy=$PlayerY-$Y
    $sx=if($dx-lt0){-56}else{56};$sy=if($dy-lt0){-56}else{56}
    $moveX=[Math]::Abs($dx)-ge[Math]::Abs($dy);$queries=1
    $direct=if($moveX){@(($X + $sx),$Y)}else{@($X,($Y + $sy))}
    if(Test-GeometryClear $direct[0] $direct[1] $Walls){
        $Follow.Active=$false
        return [pscustomobject]@{X=$direct[0];Y=$direct[1];Mode='direct';Queries=1}
    }
    if($Follow.Active){$slide=if($Follow.Negative){-56}else{56}}
    else{$slide=if($moveX){$sy}else{$sx};$Follow.Active=$true;$Follow.Negative=$slide-lt0}
    $first=if($moveX){@($X,($Y + $slide))}else{@(($X + $slide),$Y)}
    $queries++
    if(Test-GeometryClear $first[0] $first[1] $Walls){
        return [pscustomobject]@{X=$first[0];Y=$first[1];Mode='tangent';Queries=$queries}
    }
    $second=if($moveX){@($X,($Y - $slide))}else{@(($X - $slide),$Y)}
    $queries++
    if(Test-GeometryClear $second[0] $second[1] $Walls){
        $Follow.Negative=-not$Follow.Negative
        return [pscustomobject]@{X=$second[0];Y=$second[1];Mode='tangent';Queries=$queries}
    }
    return [pscustomobject]@{X=$X;Y=$Y;Mode='blocked';Queries=$queries}
}
function Run-NavigationCase([string]$Name,[int]$X,[int]$Y,[int]$PlayerX,
                            [int]$PlayerY,[object[]]$Walls,[int]$Ticks=8,
                            [bool]$ExpectBlocked=$false){
    $positions=@([pscustomobject]@{X=$X;Y=$Y});$sawDirect=$false
    $follow=[pscustomobject]@{Active=$false;Negative=$false}
    $startDistance=Get-ModelDistance $X $Y $PlayerX $PlayerY
    foreach($tick in 1..$Ticks){
        $next=Move-GeometryModel $X $Y $PlayerX $PlayerY $Walls $follow
        Assert-True ($next.Queries-le3) "$Name exceeded three collision candidates."
        Assert-True (Test-GeometryClear $next.X $next.Y $Walls) "$Name entered solid geometry."
        if($next.Mode-eq'direct'){$sawDirect=$true}
        if($positions.Count-ge2){
            $twoBack=$positions[$positions.Count-2]
            Assert-True ($ExpectBlocked-or$next.X-ne$twoBack.X-or$next.Y-ne$twoBack.Y) `
                "$Name formed an A->B->A loop."
        }
        if(-not$ExpectBlocked){
            Assert-True ($next.X-ne$X-or$next.Y-ne$Y) "$Name retried one blocked position."
        }
        $X=$next.X;$Y=$next.Y;$positions+=[pscustomobject]@{X=$X;Y=$Y}
    }
    if($ExpectBlocked){
        Assert-True (($positions|Where-Object{$_.X-ne$positions[0].X-or$_.Y-ne$positions[0].Y}).Count-eq0) "$Name escaped a closed concave corner."
    }else{
        Assert-True $sawDirect "$Name never regained direct pursuit."
        Assert-True ((Get-ModelDistance $X $Y $PlayerX $PlayerY)-lt$startDistance) "$Name made no pursuit progress."
    }
    return ,$positions
}
function Assert-XMirror([string]$Name,[object[]]$Left,[object[]]$Right,[int]$Axis){
    Assert-True ($Left.Count-eq$Right.Count) "$Name mirror sequence lengths differ."
    for($i=0;$i-lt$Left.Count;$i++){
        Assert-True ($Right[$i].X-eq$Axis-$Left[$i].X-and$Right[$i].Y-eq$Left[$i].Y) "$Name is not X-mirrored at tick $i."
    }
}
function Assert-YMirror([string]$Name,[object[]]$Top,[object[]]$Bottom,[int]$Axis){
    Assert-True ($Top.Count-eq$Bottom.Count) "$Name mirror sequence lengths differ."
    for($i=0;$i-lt$Top.Count;$i++){
        Assert-True ($Bottom[$i].Y-eq$Axis-$Top[$i].Y-and$Bottom[$i].X-eq$Top[$i].X) "$Name is not Y-mirrored at tick $i."
    }
}

$block=@(New-Wall 512 512 767 767);$mirrorAxis=1279
$upperLeft=Run-NavigationCase 'vertical upper-left' 450 700 900 400 $block
$upperRight=Run-NavigationCase 'vertical upper-right' 829 700 379 400 $block
Assert-XMirror 'vertical wall pair' $upperLeft $upperRight $mirrorAxis
$lowerLeft=Run-NavigationCase 'horizontal lower-left' 700 450 400 900 $block
$lowerRight=Run-NavigationCase 'horizontal lower-right' 579 450 879 900 $block
Assert-XMirror 'horizontal wall pair' $lowerLeft $lowerRight $mirrorAxis
$north=Run-NavigationCase 'north approach' 700 450 400 900 $block
$south=Run-NavigationCase 'south approach' 700 829 400 379 $block
Assert-YMirror 'north/south pair' $north $south $mirrorAxis
[void](Run-NavigationCase 'near-axis vector' 450 500 900 430 $block)
[void](Run-NavigationCase 'near-diagonal vector' 450 700 900 300 $block)
[void](Run-NavigationCase 'equal absolute deltas' 450 700 900 250 $block)
$concave=@(New-Wall 512 512 735 1023;New-Wall 865 512 1023 1023;
           New-Wall 736 512 864 735;New-Wall 736 865 864 1023)
[void](Run-NavigationCase 'blocked concave corner' 800 800 600 600 $concave 4 $true)
$corridor=@(New-Wall 512 256 767 511;New-Wall 512 768 767 1023)
[void](Run-NavigationCase 'corridor entrance' 450 650 900 650 $corridor)
$movingFollow=[pscustomobject]@{Active=$false;Negative=$false}
$movingPositions=@([pscustomobject]@{X=450;Y=700});$movingX=450;$movingY=700;$movingDirect=$false
foreach($tick in 1..8){
    $movingPlayerX=if($tick-lt3){900}else{892}
    $movingPlayerY=if($tick-lt3){400}else{408}
    $next=Move-GeometryModel $movingX $movingY $movingPlayerX $movingPlayerY $block $movingFollow
    if($next.Mode-eq'direct'){$movingDirect=$true}
    if($movingPositions.Count-ge2){$twoBack=$movingPositions[-2];Assert-True($next.X-ne$twoBack.X-or$next.Y-ne$twoBack.Y)'Moving-player slide formed A->B->A.'}
    Assert-True(Test-GeometryClear $next.X $next.Y $block)'Moving-player slide entered a wall.'
    $movingX=$next.X;$movingY=$next.Y;$movingPositions+=[pscustomobject]@{X=$movingX;Y=$movingY}
}
Assert-True $movingDirect 'Moving-player slide never regained direct pursuit.'

Write-Output 'Zombie AI validation PASS'
Write-Output '- activation 963; hysteresis loss 1260; LOS via authoritative world blockers'
Write-Output '- one BANK1 update every 4 frames; 56-unit step (3.28125 tiles/s)'
Write-Output '- shared radius collision; living-zombie blocking; corpses ignored'
Write-Output '- packed zero-byte per-zombie AI flag; hit/death state ownership preserved'
Write-Output '- two global 8-bit masks remember wall-follow activity/sign; WorldSprite unchanged'
Write-Output '- zero-RAM packed walking phase alternates every AI tick (4 frames), independent of movement acceptance'
Write-Output '- blocked dominant-axis movement uses deterministic player-relative wall sliding'
Write-Output '- mirrored X/Y, near-axis/diagonal, corridor, concave, and moving-player cases validated'

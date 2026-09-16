$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$header=Get-Content -Raw (Join-Path $root 'game\world_sprite.h')
$sprites=Get-Content -Raw (Join-Path $root 'game\world_sprite.c')
$corpses=Get-Content -Raw (Join-Path $root 'game\zombie_corpses.c')
$ai=Get-Content -Raw (Join-Path $root 'game\zombie_ai.c')
$projection=Get-Content -Raw (Join-Path $root 'platform\game_gear\sprite_projection.c')
function Assert([bool]$c,[string]$m){if(-not$c){throw$m}}
function New-Corpse([string]$Name,[int]$X,[int]$Y){
    [pscustomobject]@{Name=$Name;State='CORPSE';Timer=0;X=$X;Y=$Y}
}
function Merge-Corpse([Collections.ArrayList]$World,[object]$Corpse){
    for($i=0;$i-lt$World.Count;$i++){
        $other=$World[$i]
        if($other.State-eq'CORPSE'-and
           [Math]::Abs($Corpse.X-$other.X)-lt64-and
           [Math]::Abs($Corpse.Y-$other.Y)-lt64){return}
    }
    [void]$World.Add($Corpse)
}

Assert($header-notmatch'ZOMBIE_CORPSE_SEEN_MASK|ZOMBIE_CORPSE_UNSEEN_REMOVE') 'Obsolete corpse lifetime constant or mask remains.'
Assert($ai-notmatch'zombie_ai_update_corpses|CORPSE_SEEN|UNSEEN_REMOVE') 'Periodic corpse lifetime work remains in zombie AI.'
Assert($projection-notmatch'CORPSE_SEEN|health_and_hit_count\s*[|&]=') 'Projection still mutates corpse gameplay visibility state.'
Assert($sprites-match'world_sprite_make_corpse[\s\S]*?world_sprite_set_state[\s\S]*?health_and_hit_count = 0;' -and
       $sprites-match'world_sprite_set_state[\s\S]*?state_timer = 0;') 'Stable corpse state is not initialized with zero timer/packed flags.'
Assert($sprites-match'ZOMBIE_STATE_CORPSE[\s\S]*?\+\+sprite_index;[\s\S]*?continue;') 'Stable corpses do not bypass periodic animation timing.'
Assert($sprites-notmatch'ZOMBIE_STATE_CORPSE[\s\S]*?world_sprite_remove') 'World-sprite update still removes stable corpses.'
Assert(([regex]::Matches($sprites,'world_sprite_remove\(').Count)-eq1) 'Unexpected world-sprite removal call remains.'
Assert(([regex]::Matches($corpses,'world_sprite_remove\(').Count)-eq1) 'Deduplication is not the sole corpse removal call.'
Assert($corpses-match'removed_index = other_index > sprite_index[\s\S]*?world_sprite_remove\(removed_index\)') 'Deterministic higher-slot corpse deduplication changed.'
Assert($header-match'ZOMBIE_SHOT_DEAD_FRAME_COUNT 4' -and
       $sprites-match'ZOMBIE_STATE_SHOT_DEAD[\s\S]*?state_timer = ZOMBIE_SHOT_DEAD_FRAME_COUNT') 'Approved four-frame SHOT_DEAD timing changed.'
Assert($corpses-match'zombie_corpses_finalize[\s\S]*?world_sprite_make_corpse' -and
       $corpses-match'zombie_corpses_crush_in_door[\s\S]*?world_sprite_make_corpse') 'Weapon and door corpses do not share persistent initialization.'
Assert($projection-match'SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH[\s\S]*?return;' -and
       $projection-match'zombie_corpse_lod_pixels') 'Close hiding or dark-pile presentation was removed.'

$world=[Collections.ArrayList]@()
for($i=0;$i-lt8;$i++){[void]$world.Add((New-Corpse "corpse$i" ($i*128) 512))}
for($frame=0;$frame-lt3600;$frame++){
    foreach($corpse in $world){Assert($corpse.Timer-eq0) 'Persistent corpse timer advanced.'}
}
Assert($world.Count-eq8) 'Persistent all-killed population lost a corpse over time.'
$merge=[Collections.ArrayList]@((New-Corpse first 100 100))
Merge-Corpse $merge (New-Corpse duplicate 163 100)
Assert($merge.Count-eq1) 'Corpse inside merge threshold did not deduplicate.'
Merge-Corpse $merge (New-Corpse separate 164 100)
Assert($merge.Count-eq2) 'Corpse at merge threshold was incorrectly removed.'

Write-Output 'Persistent corpse validation PASS'
Write-Output '- stable corpses have zero timer and no seen/unseen packed meaning'
Write-Output '- 3600 simulated frames preserve all eight non-merged corpses'
Write-Output '- visibility and projection cannot remove or mutate corpses'
Write-Output '- weapon and door corpses persist; merge-only removal remains'
Write-Output '- close hiding and dark-pile LOD remain presentation-only'

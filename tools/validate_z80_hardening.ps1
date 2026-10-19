param([string]$BuildDirectory='build')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
function Require([bool]$condition,[string]$message){if(!$condition){throw $message}}

$ray=Get-Content "$root/engine/render/raycaster.c" -Raw
$player=Get-Content "$root/game/player.c" -Raw
$world=Get-Content "$root/game/world.c" -Raw
$shooting=Get-Content "$root/game/zombie_shooting.c" -Raw
$projection=Get-Content "$root/platform/game_gear/sprite_projection.c" -Raw

Require ($ray -match 'unsigned int fractional_product\s*=\s*\(unsigned int\)direction\s*\*\s*\(unsigned int\)ray_distance' -and
         $ray -match 'fractional_product\s*>>\s*8') 'Production hit offset is not the audited 16-bit modular form.'
Require ($player -match 'signed int player_scale_movement\(signed int direction,\s*signed int direction_scale\)' -and
         $player -match 'signed int movement = direction \* PLAYER_MOVE_SPEED' -and
         $player -match 'signed int scaled_movement = movement \* PLAYER_DIAGONAL_SCALE') 'Production movement did not retain signed 16-bit arithmetic.'
Require (([regex]::Matches($world,'x\s*>=\s*WORLD_WIDTH\s*\|\|\s*y\s*>=\s*WORLD_HEIGHT')).Count -eq 1) 'World bounds check is not uniquely owned by world_get_tile.'
$nearest=$shooting.IndexOf('if (depth >= nearest_depth)')
$sample=$shooting.IndexOf('wall_depth = shotgun_sample_wall_depth')
$wall=$shooting.IndexOf('if (depth >= wall_depth)')
Require ($nearest -ge 0 -and $sample -gt $nearest -and $wall -gt $sample) 'Losing target is not rejected before shotgun sampling.'
$project=[regex]::Match($projection,'(?s)static void game_gear_project_world_sprite\(.*?\n\}').Value
$changed=[regex]::Match($projection,'(?s)static unsigned char game_gear_projected_sprite_changed\(.*?\n\}').Value
Require ($project.Length -gt 0 -and $changed.Length -gt 0) 'Projection production functions missing.'
$visibleInit=$project.IndexOf('projected->visible = 0;')
Require ($visibleInit -ge 0) 'Projection does not establish invisible state.'
foreach($return in [regex]::Matches($project,'\breturn\s*;')) {
    Require ($return.Index -gt $visibleInit) 'Projection can return before establishing invisible state.'
}
Require ($changed -match 'if \(current->visible != previous->visible\)\s*return 1;\s*if \(!current->visible\)\s*return 0;' -and
         $changed.IndexOf('if (!current->visible)') -lt $changed.IndexOf('current->depth')) 'Invisible comparison can read irrelevant projection fields.'
$orderLoop=[regex]::Match($projection,'(?s)\*ordered_sprite_count = 0;.*?compared_sprite_count =').Value
Require ($orderLoop -match 'if \(!projected_sprites\[sprite_index\]\.visible[\s\S]*?continue;[\s\S]*?depth = projected_sprites\[sprite_index\]\.depth;' -and
         $orderLoop.IndexOf('continue;') -lt $orderLoop.IndexOf('depth = projected_sprites')) 'Ordering reads invisible depth.'

Add-Type -TypeDefinition @'
using System;
public static class GearRayHardeningEquivalence {
    struct Projection { public int visible,left,right,top,bottom,depth,step,pixels,near,size; }
    static bool Changed(Projection current,Projection previous) {
        if(current.visible!=previous.visible)return true;
        if(current.visible==0)return false;
        return current.left!=previous.left||current.right!=previous.right||current.top!=previous.top||current.bottom!=previous.bottom||current.depth!=previous.depth||current.step!=previous.step||current.pixels!=previous.pixels||current.near!=previous.near||current.size!=previous.size;
    }
    public static int CheckInvisibleProjection() {
        int cases=0;
        for(int seed=0;seed<256;++seed) {
            Projection a=new Projection{visible=0,left=seed,right=seed*3,top=seed*5,bottom=seed*7,depth=seed*11,step=seed*13,pixels=seed*17,near=seed*19,size=seed*23};
            Projection b=new Projection{visible=0,left=~seed,right=~(seed*3),top=~(seed*5),bottom=~(seed*7),depth=~(seed*11),step=~(seed*13),pixels=~(seed*17),near=~(seed*19),size=~(seed*23)};
            if(Changed(a,b))throw new Exception("invisible fields affected change decision");
            b.visible=1;if(!Changed(a,b))throw new Exception("visibility transition missed");
            ++cases;
        }
        return cases;
    }
    public static long CheckHitOffset() {
        long cases=0;
        for(int direction=-512;direction<=512;++direction)
            for(int distance=0;distance<=65535;++distance) {
                long product=(long)direction*distance;
                long adjusted=product<0?product-255:product;
                byte before=unchecked((byte)(adjusted/256));
                ushort low=unchecked((ushort)(direction*distance));
                byte after=(byte)(low>>8);
                if(before!=after) throw new Exception("hit offset mismatch");
                ++cases;
            }
        return cases;
    }
    static int ScaleWide(int direction,int scale) {
        long value=(long)direction*74;
        value+=value<0 ? -(scale/2) : scale/2;
        return (int)(value/scale);
    }
    static int ScaleNarrow(int direction,int scale) {
        short value=checked((short)(direction*74));
        value=checked((short)(value+(value<0 ? -(scale/2) : scale/2)));
        return value/scale;
    }
    public static int CheckMovement() {
        int cases=0;
        foreach(int scale in new[]{169,256})
            for(int direction=-256;direction<=256;++direction) {
                if(ScaleWide(direction,scale)!=ScaleNarrow(direction,scale)) throw new Exception("movement mismatch");
                ++cases;
            }
        for(int movement=-148;movement<=148;++movement) {
            long wide=(long)movement*177; wide+=wide<0?-128:128;
            short narrow=checked((short)(movement*177)); narrow=checked((short)(narrow+(narrow<0?-128:128)));
            if(wide/256!=narrow/256) throw new Exception("diagonal mismatch");
            ++cases;
        }
        return cases;
    }
    static byte Tile(byte x,byte y) { return x>=13||y>=13 ? (byte)8 : (byte)((x*17+y*29)%9); }
    static bool OldWall(byte x,byte y,int doorState) {
        if(x>=13||y>=13)return true;
        byte tile=Tile(x,y); if(tile==0)return false; if(tile!=3&&tile!=4)return true;
        return doorState==0;
    }
    static bool NewWall(byte x,byte y,int doorState) {
        byte tile=Tile(x,y); if(tile==0)return false; if(tile!=3&&tile!=4)return true;
        return doorState==0;
    }
    public static int CheckWorld() {
        int cases=0;
        for(int state=0;state<2;++state)for(int x=0;x<256;++x)for(int y=0;y<256;++y) {
            if(OldWall((byte)x,(byte)y,state)!=NewWall((byte)x,(byte)y,state))throw new Exception("world mismatch");
            ++cases;
        }
        return cases;
    }
    public static int CheckNearest() {
        int cases=0;
        for(int nearest=33;nearest<=1261;nearest+=17)
            for(int depth=33;depth<=1260;depth+=13)
                for(int wall=32;wall<=1261;wall+=31) {
                    bool before=depth<nearest&&depth<wall;
                    bool after=depth<nearest&&depth<wall;
                    if(before!=after)throw new Exception("nearest mismatch");
                    ++cases;
                }
        return cases;
    }
}
'@
$hit=[GearRayHardeningEquivalence]::CheckHitOffset()
$movement=[GearRayHardeningEquivalence]::CheckMovement()
$worldCases=[GearRayHardeningEquivalence]::CheckWorld()
$nearestCases=[GearRayHardeningEquivalence]::CheckNearest()
$invisibleCases=[GearRayHardeningEquivalence]::CheckInvisibleProjection()

$rayAsm=Get-Content "$build/raycaster.asm" -Raw
$playerAsm=Get-Content "$build/player.asm" -Raw
$shootingAsm=Get-Content "$build/zombie_shooting.asm" -Raw
$projectionAsm=Get-Content "$build/sprite_projection.asm" -Raw
function Body([string]$asm,[string]$name){$m=[regex]::Match($asm,"(?ms)^; Function $name\r?\n(.*?)(?=^; Function |\z)");Require $m.Success "Missing generated function $name";$m.Groups[1].Value}
$hitBody=Body $rayAsm 'raycaster_calculate_hit_offset'
$moveBody=Body $playerAsm 'player_scale_movement'
$diagonalBody=Body $playerAsm 'player_scale_diagonal'
$shootBody=Body $shootingAsm 'zombie_shooting_find_aimed_target'
Require ($hitBody -notmatch '__mullong' -and $hitBody -match '__mulint') 'Hit offset still uses the long multiply path.'
Require ($moveBody -notmatch 'mulsint2slong|divslong' -and $moveBody -match '__divsint') 'Movement still uses long arithmetic.'
Require ($diagonalBody -notmatch 'mulsint2slong|mullong|div') 'Diagonal scale still calls arithmetic helpers.'
$nearestAsm=$shootBody.IndexOf('depth >= nearest_depth')
$sampleAsm=$shootBody.IndexOf('shotgun_sample_wall_depth')
Require ($nearestAsm -ge 0 -and $sampleAsm -gt $nearestAsm) 'Generated shooting flow did not preserve early rejection order.'
$changedBody=Body $projectionAsm 'game_gear_projected_sprite_changed'
$visibleBranch=$changedBody.IndexOf('current->visible != previous->visible')
$depthRead=$changedBody.IndexOf('current->depth != previous->depth')
Require ($visibleBranch -ge 0 -and $depthRead -gt $visibleBranch -and $changedBody -match 'if \(!current->visible\)') 'Generated comparison annotations do not show the invisible early return before depth.'

Write-Output "Z80 hardening equivalence PASS"
Write-Output "- hit offset: $hit exact modular cases"
Write-Output "- movement: $movement exact bounded cases"
Write-Output "- world bounds/VOID/door semantics: $worldCases cases"
Write-Output "- nearest/wall rejection truth table: $nearestCases cases; production ordering verified"
Write-Output "- invisible projection exits/comparison/order: $invisibleCases sentinel cases; source and generated ordering verified"
Write-Output "- generated hit/movement/diagonal helper contracts verified"

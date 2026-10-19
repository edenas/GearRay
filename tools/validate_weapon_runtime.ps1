param([string]$BuildDirectory='build')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
function Require($condition,[string]$message){if(!$condition){throw $message}}
$projection=Get-Content "$root/platform/game_gear/sprite_projection.c" -Raw
$body=[regex]::Match($projection,'(?s)static void game_gear_project_world_sprite\(.*?\n\}').Value
Require ($body.Length -gt 0) 'Production projection body missing'
# Execute the production projection body with host camera/ray adapters. Asset
# pointers become immutable identity integers; pickup branches use no zombie APIs.
$body=[regex]::Replace($body,',\r?\n    signed int position_x,\r?\n    signed int position_y,\r?\n    signed int direction_x,\r?\n    signed int direction_y,\r?\n    signed int plane_x,\r?\n    signed int plane_y,\r?\n    signed long determinant','')
foreach($pair in @(@('position_x','camera_get_position_x()'),@('position_y','camera_get_position_y()'),@('direction_x','camera_get_direction_x()'),@('direction_y','camera_get_direction_y()'),@('plane_x','camera_get_plane_x()'),@('plane_y','camera_get_plane_y()'))){$body=[regex]::Replace($body,"\b$($pair[0])\b",$pair[1])}
$body=[regex]::Replace($body,'\bdeterminant\b','((signed long)camera_get_plane_x() * camera_get_direction_y() - (signed long)camera_get_direction_x() * camera_get_plane_y())')
$body=$body.Replace(",`r`n    const GameGearProjectionContext *context",'').Replace(",`n    const GameGearProjectionContext *context",'')
$body=$body.Replace('context->position_x','camera_get_position_x()').Replace('context->position_y','camera_get_position_y()')
$body=$body.Replace('context->direction_x','camera_get_direction_x()').Replace('context->direction_y','camera_get_direction_y()')
$body=$body.Replace('context->plane_x','camera_get_plane_x()').Replace('context->plane_y','camera_get_plane_y()')
$body=$body.Replace('context->determinant','((signed long)camera_get_plane_x() * camera_get_direction_y() - (signed long)camera_get_direction_x() * camera_get_plane_y())')
$body=$body.Replace('WorldSprite *sprite','WorldSprite sprite').Replace('GameGearProjectedSprite *projected','GameGearProjectedSprite projected')
$body=$body.Replace('const RaycasterRay *rays','RaycasterRay[] rays').Replace('sprite->','sprite.').Replace('projected->','projected.')
$body=$body.Replace('WORLD_SPRITE_LIFE_STATE(sprite)','(sprite.state & 3)').Replace('ZombieState','int')
$body=$body.Replace('unsigned long','long').Replace('signed long','long').Replace('unsigned int','int').Replace('signed int','int').Replace('unsigned char','int')
$body=[regex]::Replace($body,'\b(\d+)(?:UL|U|L)\b','$1')
$body=$body.Replace('if (sprite)','if (sprite != null)').Replace('if (!sprite)','if (sprite == null)').Replace('sprite ?','sprite != null ?')
$body=$body.Replace('static void game_gear_project_world_sprite','public static void Project')
$mock=@'
public const int SPRITE_NEAR_PLANE_DEPTH=32, SPRITE_VISIBLE_MAX_DISTANCE=1260;
public const long SPRITE_VISIBLE_MAX_DISTANCE_SQUARED=1260L*1260L;
public const int SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH=159,ZOMBIE_STATE_ALIVE=0,ZOMBIE_STATE_CORPSE=2;
public const int GAME_GEAR_VIEWPORT_PIXEL_WIDTH=112,GAME_GEAR_VIEWPORT_PIXEL_HEIGHT=64;
public const int SPRITE_MEDIUM_LOD_MIN_HEIGHT=15,SPRITE_SIMPLE_LOD_MIN_HEIGHT=13,SPRITE_FULL_DETAIL_MIN_HEIGHT=17;
public const int SPRITE_NEAR_DETAIL_MAX_DISTANCE=392,SPRITE_MIDDLE_DETAIL_MAX_DISTANCE=616;
public const int ZOMBIE_8X8_MAX_PROJECTED_HEIGHT=32,SPRITE_HORIZONTAL_PROJECTION_SCALE=80,NEAR_ZOMBIE_TEXTURE_NONE=255;
public const int shotgun_far_pixels=101,shotgun_world_pixels=102,zombie_corpse_lod_pixels=103;
public static int shotgun_cell_x=11,shotgun_cell_y=6,CX,CY;
public class WorldSprite {public int world_x,world_y,pixels,state;}
public class GameGearProjectedSprite {public int visible,left,right,top,bottom,depth,texture_step,pixels,near_texture_id,source_size;}
public class RaycasterRay {public int wall_distance;}
public static RaycasterRay[] Rays=new RaycasterRay[28];
public static int camera_get_position_x(){return CX;} public static int camera_get_position_y(){return CY;}
public static int camera_get_direction_x(){return 0;} public static int camera_get_direction_y(){return -256;}
public static int camera_get_plane_x(){return 192;} public static int camera_get_plane_y(){return 0;}
public static RaycasterRay[] raycaster_get_rendered_rays(){return Rays;}
public static int zombie_distance_metric(int x,int y){throw new Exception("Pickup queried zombie distance");}
public static int game_gear_get_zombie_presentation_pose(WorldSprite s,int d){throw new Exception("Pickup queried zombie pose");}
public static int game_gear_get_zombie_lod_pixels(WorldSprite s,int m){throw new Exception("Pickup queried zombie LOD");}
public static int game_gear_get_near_zombie_texture_id(int p){throw new Exception("Pickup queried zombie near asset");}
public static int game_gear_get_middle_zombie_pixels(int p){throw new Exception("Pickup queried zombie middle asset");}
public static GameGearProjectedSprite Test(int x,int depth,int wall){
 CX=(shotgun_cell_x<<8)+128-x; CY=(shotgun_cell_y<<8)+128+depth;
 for(int i=0;i<28;i++)Rays[i]=new RaycasterRay{wall_distance=wall};
 var p=new GameGearProjectedSprite(); Project(null,p); return p;
}
'@
Add-Type -TypeDefinition ("using System; public static class WeaponProjectionContract {`n"+$body+"`n"+$mock+"`n}")
$geometry=@()
$previousSize=65535
foreach($depth in 33..1260){
    $p=[WeaponProjectionContract]::Test(0,$depth,65535)
    $billboard=[Math]::Min(64,[Math]::Floor(16384/$depth))
    $size=[Math]::Max(1,$billboard)
    $source=if($size -gt 16){16}else{8}
    $worldFloor=32+[int][Math]::Floor($size/2)
    $floor=$worldFloor+[int][Math]::Floor($size/4)
    Require ($size -le $previousSize) 'Projected pickup size must decrease monotonically'
    $previousSize=$size
    Require ($p.depth -eq $depth -and $p.source_size -eq $source) 'FAR/NEAR source threshold changed'
    Require ($p.visible -eq [int]($floor-$size -lt 64)) 'Floor/viewport rejection remains correct near the camera'
    Require ($size -le 64 -and $p.bottom -le 80) 'Close cap and floor point must never run away'
    if(!$p.visible){continue}
    Require ($p.right-$p.left -eq $size -and $p.bottom-$p.top -eq $size) 'Zombie-model depth perspective scale'
    Require ($p.texture_step -eq [Math]::Floor(($source*256)/$size)) 'Existing nearest-neighbor 8.8 texture stepping'
    Require ($p.bottom -eq $floor -and $p.bottom-[int][Math]::Floor($size/4) -eq $worldFloor) 'Visible contact must match the same-depth wall floor projection'
    $hidden=[WeaponProjectionContract]::Test(0,$depth,$depth)
    Require ($hidden.visible -eq 0) 'Wall wins strict-depth tie for pickup'
    if($depth -in @(33,64,96,128,192,250,251,252,253,254,255,256,257,258,259,260,261,262,384,743,744,745,746,747,512,616,800,1000,1260)){
        $geometry+=@{Depth=$depth;Size=$size;Source=$source;Left=$p.left;Right=$p.right;Top=$p.top;Bottom=$p.bottom;TextureStep=$p.texture_step}
    }
}
foreach($case in @(@(963,16,102,17),@(964,8,101,16))){
    $p=[WeaponProjectionContract]::Test(0,$case[0],65535)
    Require ($p.source_size -eq $case[1] -and $p.pixels -eq $case[2] -and $p.right-$p.left -eq $case[3]) 'Exact NEAR/FAR boundary changed'
}
foreach($expected in @(@(256,64),@(277,59),@(350,46),@(356,46),@(357,45),@(384,42),@(424,38),@(512,32),@(616,26),@(800,20),@(963,17),@(964,16),@(1000,16),@(1260,13))){
    $p=[WeaponProjectionContract]::Test(0,$expected[0],65535)
    Require ($p.right-$p.left -eq $expected[1]) 'Regression: pickup must retain the approved substantial scale, never quarter-scale'
}
$close=[WeaponProjectionContract]::Test(0,33,65535)
Require ($close.visible -eq 1 -and $close.right-$close.left -eq 64 -and $close.top -eq 16 -and $close.bottom -eq 80) 'Very-close pickup cap or floor anchor changed'
foreach($depth in 33..256){
    $p=[WeaponProjectionContract]::Test(0,$depth,65535)
    Require ($p.top -eq 16 -and $p.bottom -eq 80 -and $p.right-$p.left -eq 64) 'Very-close normalized cap changed'
}
foreach($depth in 250..262){
    $before=[WeaponProjectionContract]::Test(0,$depth,65535)
    $after=[WeaponProjectionContract]::Test(0,($depth+1),65535)
    foreach($field in @('left','right','top')){Require ([Math]::Abs($before.$field-$after.$field) -le 1) 'Cap entry geometry must remain continuous within integer rounding'}
    $beforeFloor=$before.bottom-(($before.right-$before.left)-shr 2);$afterFloor=$after.bottom-(($after.right-$after.left)-shr 2)
    Require ([Math]::Abs($beforeFloor-$afterFloor) -le 1) 'Cap entry world-floor projection must remain continuous'
}
$previousWorldFloor=255
foreach($depth in 33..1260){
    $p=[WeaponProjectionContract]::Test(0,$depth,65535)
    $size=$p.right-$p.left
    $worldFloor=$p.bottom-[int][Math]::Floor($size/4)
    $wallFloor=[int][Math]::Truncate((64-$size)/2)+$size
    Require ($worldFloor -eq $wallFloor) 'Pickup contact diverged from same-depth wall/floor perspective'
    Require ($worldFloor -le $previousWorldFloor) 'Floor projection must move toward the horizon as depth increases'
    $previousWorldFloor=$worldFloor
}
$farFloor=[WeaponProjectionContract]::Test(0,800,65535);$nearFloor=[WeaponProjectionContract]::Test(0,350,65535)
Require (($farFloor.bottom-(($farFloor.right-$farFloor.left)-shr 2)) -lt ($nearFloor.bottom-(($nearFloor.right-$nearFloor.left)-shr 2))) 'Substantially different depths cannot share a fixed visible floor Y'
$geometry|ConvertTo-Json|Set-Content "$build/shotgun-projection-table.json"
foreach($depth in @(-100,0,32,1261,65536)) {Require (([WeaponProjectionContract]::Test(0,$depth,65535)).visible -eq 0) 'Behind/near/far cutoff'}
Require (([WeaponProjectionContract]::Test(1000,512,65535)).visible -eq 0) 'Viewport clipping'
foreach($x in @(-265,265)){
    $p=[WeaponProjectionContract]::Test($x,512,65535)
    Require ($p.visible -eq 1 -and ($p.left -lt 0 -or $p.right -gt 112)) 'Partly clipped pickup retains unclipped texture origin'
}
# Execute the unchanged production compositor at both source resolutions over
# projected/clipped geometry, with transparent destination pixels and mixed walls.
$video=Get-Content "$root/platform/game_gear/video.c" -Raw
$overlay=[regex]::Match($video,'(?s)static void game_gear_overlay_sprite_tile\(.*?\n\}').Value
Require ($overlay.Length -gt 0) 'Production compositor missing'
$overlay=$overlay.Replace('const GameGearProjectedSprite *projected','GameGearProjectedSprite projected').Replace('const RaycasterRay *rays','RaycasterRay[] rays')
$overlay=$overlay.Replace('unsigned char *destination','int[] destination').Replace('const unsigned char *pixels','int[] pixels').Replace('projected->','projected.')
$overlay=$overlay.Replace('const unsigned char *source_row;','int source_row;').Replace('source_row = pixels + texture_y * packed_row_stride;','source_row = texture_y * packed_row_stride;').Replace('source_row[texture_x >> 1]','pixels[source_row + (texture_x >> 1)]')
$overlay=$overlay.Replace('unsigned char source_x[8],pixel_x,pixel_y,palette_index,mask,keep,b0,b1,b2,b3;','unsigned char[] source_x=new unsigned char[8]; unsigned char pixel_x,pixel_y,palette_index,mask,keep,b0,b1,b2,b3;')
$overlay=[regex]::Replace($overlay,'source_row\s*=\s*pixels\s*\+\s*texture_y\s*\*\s*packed_row_stride;','source_row = texture_y * packed_row_stride;')
$overlay=[regex]::Replace($overlay,'source_row\[texture_x\s*>>\s*1\]','pixels[source_row + (texture_x >> 1)]')
$overlay=[regex]::Replace($overlay,'if\s*\(texture_x\s*&\s*1\)','if ((texture_x & 1) != 0)')
$overlay=[regex]::Replace($overlay,'if\s*\(palette_index\s*&\s*([1248])\)','if ((palette_index & $1) != 0)')
$overlay=$overlay.Replace('unsigned char','int').Replace('unsigned int','int').Replace('signed int','int')
$overlay=[regex]::Replace($overlay,'\b(\d+)U\b','$1')
$overlay=$overlay.Replace('if (texture_x & 1)','if ((texture_x & 1) != 0)').Replace('if (palette_index & (1 << plane))','if ((palette_index & (1 << plane)) != 0)')
foreach($bit in @(1,2,4,8)) { $overlay=$overlay.Replace("if (palette_index & $bit)","if ((palette_index & $bit) != 0)") }
$overlay=$overlay.Replace('static void game_gear_overlay_sprite_tile','public static void Overlay')
$compositionMock=@'
public const int NEAR_ZOMBIE_TEXTURE_NONE=255,SPRITE_TRANSPARENT_INDEX=15;
public static int[][] near_zombie_texture_pixels=new int[0][];
public class GameGearProjectedSprite {public int left,right,top,bottom,depth,texture_step,source_size,near_texture_id=255;public int[] pixels;}
public class RaycasterRay {public int wall_distance;}
public static bool game_gear_sprite_covers_tile(GameGearProjectedSprite p,int column,int row){return p.right>column*8&&p.left<column*8+8&&p.bottom>row*8&&p.top<row*8+8;}
public static void Verify(int[] pixels,int depth,int left,int right,int top,int bottom,int source){
 var p=new GameGearProjectedSprite{pixels=pixels,depth=depth,left=left,right=right,top=top,bottom=bottom,source_size=source,texture_step=source*256/(right-left)};
 var rays=new RaycasterRay[28];for(int i=0;i<28;i++)rays[i]=new RaycasterRay{wall_distance=i%3==0?depth:65535};
 for(int row=0;row<8;row++)for(int col=0;col<14;col++){
  var tile=new int[32];for(int y=0;y<8;y++)for(int x=0;x<8;x++){int c=(col*8+x+row*8+y)&15;for(int b=0;b<4;b++)if((c&(1<<b))!=0)tile[y*4+b]|=128>>x;}
  Overlay(tile,col,row,p,rays);
  for(int y=0;y<8;y++)for(int x=0;x<8;x++){
   int sx=col*8+x,sy=row*8+y,expected=(sx+sy)&15;
   if(sx>=left&&sx<right&&sy>=top&&sy<bottom&&depth<rays[sx/4].wall_distance){
    int tx=Math.Min(source-1,(sx-left)*p.texture_step/256),ty=Math.Min(source-1,(sy-top)*p.texture_step/256);
    int packed=pixels[ty*source/2+tx/2],c=tx%2==0?packed>>4:packed&15;if(c!=15)expected=c;
   }
   int actual=0;for(int b=0;b<4;b++)if((tile[y*4+b]&(128>>x))!=0)actual|=1<<b;
   if(actual!=expected)throw new Exception("Perspective compositor sampling/clipping/alpha/wall mismatch");
  }
 }
}
'@
Add-Type -TypeDefinition ("using System; public static class PickupCompositionContract {`n"+$overlay+"`n"+$compositionMock+"`n}")
$nearText=Get-Content "$build/generated/shotgun_world.c" -Raw
$farText=Get-Content "$build/generated/shotgun_far_lod.h" -Raw
$nearData=@([regex]::Matches([regex]::Match($nearText,'(?s)=\s*\{(.*?)\}').Groups[1].Value,'0x[0-9a-f]+')|ForEach-Object{[Convert]::ToInt32($_.Value.Substring(2),16)})
$farData=@([regex]::Matches($farText,'0x[0-9a-f]+')|ForEach-Object{[Convert]::ToInt32($_.Value.Substring(2),16)})
foreach($depth in @(33,64,114,160,256,384,743,744,745,746,747,512,616,800,1000,1260)){
    foreach($x in @(-265,-16,0,16,265)){
        $p=[WeaponProjectionContract]::Test($x,$depth,65535)
        Require (($p.right-$p.left) -le 64 -and $p.bottom -le 80) 'Close cap and floor point must never run away'
    if(!$p.visible){continue}
        foreach($source in @(8,16)){
            $data=if($source -eq 8){$farData}else{$nearData}
            [PickupCompositionContract]::Verify($data,$depth,$p.left,$p.right,$p.top,$p.bottom,$source)
        }
    }
}
Write-Output '- production compositor executed: FAR/NEAR sources, continuous zombie-model perspective sizes, clipping, alpha preservation, mixed wall rays and strict ties'
# Execute the actual acquisition/animation/cache functions. No synthetic
# inventory implementation substitutes for the ownership guard under test.
$hud=Get-Content "$root/platform/game_gear/hud_weapon.c" -Raw
$playerHeader=Get-Content "$root/game/player.h" -Raw
$moveSpeed=[int][regex]::Match($playerHeader,'#define PLAYER_MOVE_SPEED\s+(\d+)').Groups[1].Value
$bodyRadius=[int][regex]::Match($playerHeader,'#define PLAYER_COLLISION_RADIUS\s+(\d+)').Groups[1].Value
Require ($moveSpeed -eq 74 -and $bodyRadius -eq 32 -and $hud -match '#define SHOTGUN_PICKUP_TOUCH_EXTENT \(128U \+ 2U \* PLAYER_MOVE_SPEED\)') 'Measured movement/body and one-step contact expansion changed'
$touchLiteral=[string](128+2*$moveSpeed)+'U'
$touchExtent=128+2*$moveSpeed
$oppositeWallDistance=128+256+$bodyRadius
Require ($touchExtent -lt $oppositeWallDistance) 'Touch region must not reach a legal center across an adjacent full solid wall'
Require ($touchExtent-(128+$moveSpeed) -eq $moveSpeed) 'Contact must expand exactly one normal movement step from the previous boundary'
Write-Output "- touch extent $touchExtent; expansion $moveSpeed; body radius $bodyRadius; earliest west x=$(2944-$touchExtent); opposite solid-wall center distance $oppositeWallDistance"
$hudBodies=''
foreach($name in @('initialize','update','changed','render_complete')){
    $function=[regex]::Match($hud,"(?s)(?:void|unsigned char) game_gear_hud_weapon_$name\(.*?\n\}").Value
    Require ($function.Length -gt 0) "HUD function missing: $name"
    $function=$function.Replace('__banked','').Replace('(void)','()').Replace('unsigned char','int').Replace('unsigned int','ushort').Replace('SHOTGUN_PICKUP_TOUCH_EXTENT',$touchLiteral)
    $function=$function.Replace('SHOTGUN_PICKUP_PRESENT','(owned_weapons & WEAPON_OWNED_SHOTGUN) == 0').Replace('if (shoot_requested)','if (shoot_requested != 0)')
    $function=$function.Replace("int game_gear_hud_weapon_$name","public static bool game_gear_hud_weapon_$name").Replace("void game_gear_hud_weapon_$name","public static void game_gear_hud_weapon_$name")
    $hudBodies+=$function+"`n"
}
$hudMock=@'
public const int IDLE=0,SHOOT=1,HUD_WEAPON_SHOOT_FRAME_COUNT=2,WEAPON_SHOTGUN=1,WEAPON_OWNED_SHOTGUN=2;
public static int owned_weapons,selected_weapon,weapon_state,rendered_weapon_state,animation_timer,Queries;
public static int shotgun_cell_x=11,shotgun_cell_y=6,X,Y;
public static int player_get_position_x(){Queries++;return X;}public static int player_get_position_y(){Queries++;return Y;}
public static void Probe(int dx,int dy,bool expected){
 owned_weapons=1;selected_weapon=0;X=(11<<8)+128+dx;Y=(6<<8)+128+dy;game_gear_hud_weapon_initialize();game_gear_hud_weapon_update(0);
 if((owned_weapons==3)!=expected || selected_weapon!=(expected?1:0))throw new Exception("Touch boundary/selection mismatch");
}
public static void Test(){ foreach(int sign in new[]{-1,1}){Probe(sign*277,0,false);Probe(0,sign*277,false);Probe(sign*276,0,true);Probe(0,sign*276,true);Probe(sign*203,0,true);Probe(0,sign*203,true);foreach(int sy in new[]{-1,1}){Probe(sign*276,sy*276,true);Probe(sign*277,sy*276,false);Probe(sign*276,sy*277,false);}}
 Probe(0,0,true);Probe(-128,-128,true);Probe(127,127,true);Probe(-512,0,false);Probe(0,512,false);Probe(416,0,false);Probe(0,416,false);Probe(0,-416,false);
 for(int edge=0;edge<2;edge++){
  owned_weapons=1;selected_weapon=0;Queries=0;X=0;Y=0;game_gear_hud_weapon_initialize();
  if(weapon_state!=0||animation_timer!=0||game_gear_hud_weapon_changed())throw new Exception("Initial pistol state/cache");
  game_gear_hud_weapon_update(0);if(owned_weapons!=1||selected_weapon!=0)throw new Exception("Non-contact acquisition");
  weapon_state=SHOOT;animation_timer=1;game_gear_hud_weapon_render_complete();
  X=(11<<8)+128;Y=(6<<8)+128;game_gear_hud_weapon_update(edge);
  if(owned_weapons!=3||selected_weapon!=1||weapon_state!=edge||animation_timer!=(edge==0?0:2))throw new Exception("First ownership/equip/clean pose or fresh edge");
  if(!game_gear_hud_weapon_changed())throw new Exception("Acquisition must invalidate identity cache immediately");
  game_gear_hud_weapon_render_complete();if(game_gear_hud_weapon_changed())throw new Exception("No unconditional idle redraw");
  game_gear_hud_weapon_update(0);game_gear_hud_weapon_update(0);
  if(weapon_state!=IDLE||animation_timer!=0)throw new Exception("Fresh fire pose must expire without held autofire");
  selected_weapon=0;game_gear_hud_weapon_render_complete();int queries=Queries;
  for(int i=0;i<100;i++)game_gear_hud_weapon_update(0);
  if(owned_weapons!=3||selected_weapon!=0||Queries!=queries||game_gear_hud_weapon_changed())throw new Exception("Owned repeat must not switch/query/redraw");
 }
}
'@
Add-Type -TypeDefinition ("using System; public static class AcquisitionContract {`n"+$hudBodies+"`n"+$hudMock+"`n}")
[AcquisitionContract]::Test()
Write-Output '- actual acquisition/cache: first ownership equips, old SHOOT resets, fresh edge retained, identity redraw then idle no-redraw, owned repeat preserves manual pistol and skips contact queries'
$prepare=[regex]::Match($projection,'(?s)unsigned int game_gear_prepare_world_sprites\(.*?\n\}').Value
Require ($prepare -match 'if \(SHOTGUN_PICKUP_PRESENT\) --zombie_count;' -and $prepare -match 'sprite_index < zombie_count\s*\? world_sprite_get\(sprite_index\) : 0') 'Independent pickup never enters zombie array'
$orderBody=$prepare.Replace('__banked','').Replace('const GameGearProjectedSprite *previous_sprites','GameGearProjectedSprite[] previous_sprites')
$orderBody=$orderBody.Replace('    GameGearProjectionContext context;'+"`r`n",'').Replace('    GameGearProjectionContext context;'+"`n",'')
$orderBody=[regex]::Replace($orderBody,'(?s)    context\.position_x = camera_get_position_x\(\);.*?context\.plane_y;\r?\n','')
$orderBody=$orderBody.Replace(",`r`n            &context",'').Replace(",`n            &context",'')
$orderBody=[regex]::Replace($orderBody,'(?s)(&projected_sprites\[sprite_index\]),\r?\n            context\.position_x,.*?context\.determinant\);','$1);')
$orderBody=$orderBody.Replace('GameGearProjectedSprite *projected_sprites','GameGearProjectedSprite[] projected_sprites')
$orderBody=$orderBody.Replace('unsigned char *ordered_sprite_indices','int[] ordered_sprite_indices').Replace('unsigned char *ordered_sprite_count','ref int ordered_sprite_count')
$orderBody=$orderBody.Replace('GameGearProjectedSprite *projected','GameGearProjectedSprite projected').Replace('&projected_sprites[','projected_sprites[')
$orderBody=$orderBody.Replace('&previous_sprites[','previous_sprites[').Replace('projected->','projected.').Replace('*ordered_sprite_count','ordered_sprite_count')
$orderBody=$orderBody.Replace('unsigned int','int').Replace('signed int','int').Replace('unsigned char','int')
$orderBody=[regex]::Replace($orderBody,'\b(\d+)U\b','$1')
$orderBody=$orderBody.Replace('SHOTGUN_PICKUP_PRESENT','(owned_weapons & 2) == 0').Replace('? world_sprite_get(sprite_index) : 0','? world_sprite_get(sprite_index) : null')
$orderBody=$orderBody.Replace('!projected.visible','projected.visible == 0')
$orderBody=$orderBody.Replace('!projected_sprites[sprite_index].visible','projected_sprites[sprite_index].visible == 0')
$orderBody=[regex]::Replace($orderBody,'!\((accepted_mask|ordered_mask) & \(1 << sprite_index\)\)','(($1 & (1 << sprite_index)) == 0)')
$orderBody=$orderBody.Replace('(accepted_mask & (1 << sprite_index)))','(accepted_mask & (1 << sprite_index)) != 0)')
$orderBody=$orderBody.Replace('(ordered_mask & (1 << sprite_index)))','(ordered_mask & (1 << sprite_index)) != 0)')
$orderBody=[regex]::Replace($orderBody,'if \(projected_sprites\[sprite_index\]\.visible(?!\s*==)','if (projected_sprites[sprite_index].visible != 0')
$orderBody=$orderBody.Replace('int game_gear_prepare_world_sprites','public static int Prepare')
$orderMock=@'
public const int PROJECTED_SPRITE_MAX_COUNT=9,SPRITE_RENDER_BUDGET=12,GAME_GEAR_VIEWPORT_PIXEL_WIDTH=112;
public static int owned_weapons=1,PickupProjections,ZombieGets;
public class WorldSprite {public int index;}
public class GameGearProjectedSprite {public int visible,left,right,top,bottom,depth,pixels;}
public static WorldSprite world_sprite_get(int i){if(i>=8)throw new Exception("Pickup consumed zombie slot");ZombieGets++;return new WorldSprite{index=i};}
public static void game_gear_project_world_sprite(WorldSprite s,GameGearProjectedSprite p){if(s==null)PickupProjections++;p.visible=1;p.left=40;p.right=48;p.top=40;p.bottom=48;p.depth=s==null?513:700+s.index;}
public static int game_gear_get_sprite_render_cost(GameGearProjectedSprite p){return 1;}
public static bool game_gear_projected_sprite_changed(GameGearProjectedSprite p,GameGearProjectedSprite old){return p.visible!=old.visible||p.depth!=old.depth;}
public static void Test(){
 var current=new GameGearProjectedSprite[9];var old=new GameGearProjectedSprite[9];for(int i=0;i<9;i++){current[i]=new GameGearProjectedSprite();old[i]=new GameGearProjectedSprite();}
 var order=new int[9];int count=0;int mask=Prepare(current,9,old,0,order,ref count);
 if(mask!=511||count!=9||PickupProjections!=1||ZombieGets!=8)throw new Exception("Eight zombies plus independent ninth pickup mask/budget");
 var seen=new bool[9];int depth=65535;for(int i=0;i<count;i++){if(seen[order[i]]||current[order[i]].depth>depth)throw new Exception("Unique far-to-near order");seen[order[i]]=true;depth=current[order[i]].depth;}
 owned_weapons=3;count=0;mask=Prepare(current,8,current,9,order,ref count);
 if(mask!=256||count!=8||PickupProjections!=1||ZombieGets!=16)throw new Exception("Collected pickup cleanup bit / no projection work");
}
'@
Add-Type -TypeDefinition ("using System; public static class WeaponOrderContract {`n"+$orderBody+"`n"+$orderMock+"`n}")
[WeaponOrderContract]::Test()
$video=Get-Content "$root/platform/game_gear/video.c" -Raw
Require ($video -match 'if \(SHOTGUN_PICKUP_PRESENT\) \+\+projected_sprite_count;' -and $video -match 'unsigned int sprite_changed_mask;' -and $prepare -match 'unsigned int accepted_mask') 'Collected early rejection and ninth presentation bit'
$header=Get-Content "$root/game/world_sprite.h" -Raw
Require ($header -match '#define WORLD_SPRITE_MAX_COUNT 8') 'Eight zombie slots remain available'
$world=Get-Content "$root/game/world.c" -Raw
Require ($world -match 'tile_id == WORLD_TILE_SPRITE_MARKER\s*\|\| tile_id == WORLD_TILE_SHOTGUN_MARKER\)\s*\? WORLD_TILE_EMPTY') 'G and Z both preserve EMPTY geometry'
$init=Get-Content "$root/game/world_initialization.c" -Raw
Require ($init -match 'owned_weapons = WEAPON_OWNED_PISTOL;' -and $init -match 'selected_weapon = WEAPON_PISTOL;' -and $init -match 'tile == WORLD_TILE_SHOTGUN_MARKER[\s\S]*?shotgun_cell_x = x;[\s\S]*?shotgun_cell_y = y;') 'Ownership and authored marker initialization'
$main=Get-Content "$root/game/main.c" -Raw
Require ($main -match 'if \(pending_shot\)\s*zombie_shooting_process\(\);\s*pending_shot = shoot_requested;') 'Pending-shot pipeline unchanged'
foreach($name in @('zombie_ai.c','zombie_corpses.c','enemy_collision.c','world_interactions.c')){
    Require ((Get-Content "$root/game/$name" -Raw) -notmatch 'shotgun|owned_weapons|selected_weapon') "Pickup/selection leaked into existing gameplay: $name"
}
. "$PSScriptRoot/production_build_artifacts.ps1"
foreach($file in Get-ProductionBuildAssembly $build){
    $assembly=Get-Content $file.FullName -Raw
    $startupDispatches=[regex]::Matches($assembly,'ld\s+e, #b_game_gear_startup_logo_show').Count
    $deathDispatches=[regex]::Matches($assembly,'ld\s+e, #b_game_gear_video_present_player_death').Count
    Require ($startupDispatches -eq $(if($file.BaseName -eq 'main'){1}else{0})) "Unexpected startup Bank 3 dispatch: $($file.Name)"
    Require ($deathDispatches -eq $(if($file.BaseName -eq 'main'){1}else{0})) "Unexpected Game Over Bank 3 dispatch: $($file.Name)"
    if($file.BaseName -eq 'main') {
        Require ($assembly -match 'ld\s+e, #b_game_gear_startup_logo_show\s+ld\s+hl, #_game_gear_startup_logo_show\s+call\s+___sdcc_bcall_ehl[\s\S]*?ld\s+e, #b_game_gear_video_initialize') 'Production startup dispatch must precede gameplay initialization'
    }
}
Write-Output 'Weapon runtime validation PASS: deterministic FAR/NEAR projection, continuous depth-derived scale and floor anchor, unchanged touch acquisition, depth/occlusion/clipping, collected rejection and combat wiring.'

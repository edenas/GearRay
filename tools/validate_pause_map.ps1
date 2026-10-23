param([string]$BuildDirectory = 'build/release', [switch]$RequireMapPlacement)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/production_build_artifacts.ps1"
$root = Split-Path $PSScriptRoot -Parent
$build = if ([IO.Path]::IsPathRooted($BuildDirectory)) { $BuildDirectory } else { Join-Path $root $BuildDirectory }
$source = Get-Content "$root/platform/game_gear/pause_map.c" -Raw
$iconHeader=Get-Content "$build/generated/pause_weapon_icon.h" -Raw
Add-Type -AssemblyName System.Drawing
$icon=[System.Drawing.Bitmap]::new("$root/assets/sprites/weapons/pistol.png")
if($icon.Width -ne 16 -or $icon.Height -ne 16){throw 'Pistol canvas must be 16x16'}
$iconExpected=New-Object int[] 256
$opaque=0
$minIconX=16;$minIconY=16;$maxIconX=-1;$maxIconY=-1
for($iy=0;$iy -lt 16;$iy++){for($ix=0;$ix -lt 16;$ix++){
    $c=$icon.GetPixel($ix,$iy);$iconExpected[$iy*16+$ix]=-1
    if($c.A -eq 0){continue}
    if($c.A -ne 255 -or $ix -lt 1 -or $ix -gt 14 -or $iy -lt 1 -or $iy -gt 14){throw 'Pistol opaque pixel outside native slot interior'}
    $rgb='#{0:x2}{1:x2}{2:x2}' -f $c.R,$c.G,$c.B
    $iconExpected[$iy*16+$ix]=switch($rgb){'#000000'{0} '#1a1a1a'{13} '#4d4d4d'{2} '#797878'{3} '#ffffff'{12} default{throw "Unexpected pistol color $rgb"}}
    $opaque++
    $minIconX=[Math]::Min($minIconX,$ix);$minIconY=[Math]::Min($minIconY,$iy)
    $maxIconX=[Math]::Max($maxIconX,$ix);$maxIconY=[Math]::Max($maxIconY,$iy)
}}
$icon.Dispose()
if($opaque -ne 63){throw 'Expected all 63 opaque pistol pixels'}
if($minIconX -ne 3 -or $maxIconX -ne 12 -or $minIconY -ne 4 -or $maxIconY -ne 12){throw 'Authored pistol bounding box changed'}
$shotgunHeader=Get-Content "$build/generated/pause_shotgun_icon.h" -Raw
if($iconHeader -match 'shotgun' -or $shotgunHeader -notmatch 'pause_shotgun_tiles'){throw 'Pause weapon composite sources are not isolated'}
$header = Get-Content "$root/platform/game_gear/pause_map.h" -Raw
$world = Get-Content "$root/game/world.h" -Raw
$workshop = Get-Content "$root/game/workshop_map.c" -Raw
$inputSource = Get-Content "$root/platform/game_gear/input.c" -Raw
$main = Get-Content "$root/game/main.c" -Raw
$video = Get-Content "$root/platform/game_gear/video_initialization.c" -Raw
function Require($Condition, [string]$Message) { if (!$Condition) { throw $Message } }

# Execute mechanically translated production map functions with a mock VDP.
# No geometry/position algorithm is reimplemented here. This is a host contract
# test, not a Z80 emulator: generated assembly is audited separately below.
$constants = @{}
foreach ($text in @($header, $source, $world, (Get-Content "$root/game/weapons.h" -Raw), (Get-Content "$root/game/workshop_map.h" -Raw), (Get-Content "$root/game/door_states.h" -Raw), (Get-Content "$root/game/door_instances.h" -Raw))) {
    foreach ($m in [regex]::Matches($text, '(?m)^#define\s+(\w+)\s+(0x[0-9a-fA-F]+|\d+)\b')) {
        $constants[$m.Groups[1].Value] = [int]$m.Groups[2].Value
    }
}
$constants['WORLD_WIDTH'] = $constants['WORKSHOP_MAP_WIDTH']
$constants['WORLD_HEIGHT'] = $constants['WORKSHOP_MAP_HEIGHT']
$constants['GG_KEY_START'] = 0x8000
$constants['ZOMBIE_STATE_CORPSE']=2
$constants['PORT_A_KEY_UP']=1; $constants['PORT_A_KEY_DOWN']=2
$constants['PORT_A_KEY_LEFT']=4; $constants['PORT_A_KEY_RIGHT']=8
$constants['PORT_A_KEY_1']=16; $constants['PORT_A_KEY_2']=32
Require ($constants['WORLD_WIDTH'] -eq 13 -and $constants['WORLD_HEIGHT'] -eq 13) 'Workshop dimensions changed'
$defs = ($constants.GetEnumerator() | ForEach-Object {
    if ($_.Key -in @('WORLD_WIDTH','WORLD_HEIGHT','WEAPON_COUNT')) { "public static int $($_.Key) = $($_.Value);" }
    else { "public const int $($_.Key) = $($_.Value);" }
}) -join "`n"
$aliases = @{}
foreach ($m in [regex]::Matches($workshop, '(?m)^#define\s+(\w)\s+(WORLD_TILE_\w+)')) {
    $aliases[$m.Groups[1].Value] = $constants[$m.Groups[2].Value]
}
$mapBody = [regex]::Match($workshop, '(?s)\[WORKSHOP_MAP_HEIGHT\]\[WORKSHOP_MAP_WIDTH\]\s*=\s*\{(.*?)\};').Groups[1].Value
$cells = @([regex]::Matches($mapBody, '\b[XESBDRWZG]\b') | ForEach-Object { $aliases[$_.Value] })
Require ($cells.Count -eq 169) 'Authoritative map must contain 169 cells'
. "$PSScriptRoot/pause_freeze_fixture.ps1"
$translated = $source + "`n" + $inputSource + "`n" + $freezeProduction
$translated=[regex]::Replace($translated,'(?s)#if SCROLL_X != 0 && SCROLL_Y != 0\s+if \(state != WEAPONS_FOCUS\)\s+(tile = FRAME_PATTERN.*?EDGE_TOP\);)\s+#endif','if (state != WEAPONS_FOCUS && SCROLL_X != 0 && SCROLL_Y != 0) $1')
$translated=$translated.Replace('+ (SCROLL_Y != 0)','+ (SCROLL_Y != 0 ? 1 : 0)').Replace('+ (SCROLL_X != 0)','+ (SCROLL_X != 0 ? 1 : 0)');$translated=$translated.Replace('2 + (SCROLL_Y != 0)', '2 + (SCROLL_Y != 0 ? 1 : 0)').Replace('2 + (SCROLL_X != 0)', '2 + (SCROLL_X != 0 ? 1 : 0)')
$iconCases=[regex]::Matches($iconHeader,'(?s)#if SCROLL_X == (\d) && SCROLL_Y == (\d)\s*(.*?)#endif')
foreach($case in $iconCases){$translated += "`n"+$case.Groups[3].Value.Replace('pause_pistol_tiles',"pistol_$($case.Groups[1].Value)_$($case.Groups[2].Value)").Replace('pause_empty_rows',"empty_$($case.Groups[1].Value)_$($case.Groups[2].Value)")}
foreach($case in [regex]::Matches($shotgunHeader,'(?s)#if SCROLL_X == (\d) && SCROLL_Y == (\d)\s*(.*?)#endif')){
    $translated += "`n"+$case.Groups[3].Value.Replace('pause_shotgun_tiles',"shotgun_$($case.Groups[1].Value)_$($case.Groups[2].Value)")
}
# Execute the actual authoritative state accessor; synthetic maps provide only
# the instance positions/storage through the host adapter.
$doorSource=Get-Content "$root/game/door_states.c" -Raw
$doorGetter=[regex]::Match($doorSource,'(?s)DoorState door_state_get\([^)]*\)\s*\{.*?\n\}').Value
Require ($doorGetter.Length -gt 0) 'Authoritative door accessor missing'
$translated += "`n" + $doorGetter.Replace('DoorState','unsigned char').Replace('DoorInstanceId','unsigned char').Replace("{", "{ DoorFrames[Frame]++;")
# Expand only object-like geometry macros; WORLD extents remain mutable host inputs.
$expressions=@{}
foreach($m in [regex]::Matches($source,'(?m)^#define\s+(\w+)\s+(\(.*\))\s*$')) { $expressions[$m.Groups[1].Value]=$m.Groups[2].Value }
for($pass=0;$pass -lt 8;$pass++) { foreach($name in $expressions.Keys) { $translated=[regex]::Replace($translated,"\b$name\b",$expressions[$name]) } }
$translated = [regex]::Replace($translated, '(?s)/\*.*?\*/', '')
$translated = [regex]::Replace($translated, '(?m)^#.*$', '')
$translated=[regex]::Replace($translated,'(?m)^__sfr.*$','')
$translated=$translated.Replace('WorldSprite *sprite','WorldSprite sprite').Replace('WORLD_SPRITE_LIFE_STATE(sprite)','(sprite.state & 3)').Replace('sprite->','sprite.')
$translated = $translated.Replace('__banked', '').Replace('(void)', '()')
$translated = $translated.Replace('unsigned char', 'int').Replace('unsigned int', 'int').Replace('signed int', 'int').Replace('signed char', 'int')
$translated = [regex]::Replace($translated, '\b(\d+|0x[\da-fA-F]+)U\b', '$1')
$translated = $translated.Replace('int *rows', 'int[] rows')
$translated = [regex]::Replace($translated, 'int (\w+)\[(\d+)\];', 'int[] $1 = new int[$2];')
$translated = [regex]::Replace($translated, 'static const int (\w+)\[(\d+)\] =', 'public static int[] $1 =')
$translated = [regex]::Replace($translated, 'sizeof\((\w+)\)', '$1.Length')
$translated = $translated.Replace('static int passage(', 'static bool passage(')
foreach($name in @('input_pause_requested','input_interaction_requested','input_shoot_requested')) { $translated=$translated.Replace("int $name(","bool $name(") }
$translated=[regex]::Replace($translated,'(?m)^(?:static )?int (keys|previous_keys|input_blocked|button_2_strafe_used);','public static int $1;')
$translated=$translated.Replace('!button_2_strafe_used','button_2_strafe_used == 0')
$translated=[regex]::Replace($translated,'if \(!\((keys|previous_keys) & ([^)]+)\)\)','if (($1 & $2) == 0)')
$translated=[regex]::Replace($translated,'if \(keys & \(([^)]+)\)\)','if ((keys & ($1)) != 0)')
$translated=[regex]::Replace($translated,'if \(keys & (\w+)\)','if ((keys & $1) != 0)')
$translated = [regex]::Replace($translated, '(?m)^(?:static )?(int|void|bool) (\w+)\(', 'public static $1 $2(')
$translated = [regex]::Replace($translated,'int map_tile\(int x, int y\)\s*\{', 'int map_tile(int x, int y) { x &= 255; y &= 255;')
$translated = $translated.Replace('+ (scroll_x != 0)', '+ (scroll_x != 0 ? 1 : 0)').Replace('+ (scroll_y != 0)', '+ (scroll_y != 0 ? 1 : 0)')
$translated=$translated.Replace('focus_frame_pixels + ((int)pattern << 5)', 'Slice(focus_frame_pixels, pattern << 5)')
$translated=$translated.Replace('pause_pistol_tiles + ((int)bits << 5)', 'Slice(SelectPistolTiles(), bits << 5)')
$translated=$translated.Replace('pause_shotgun_tiles + ((int)bits << 5)', 'Slice(SelectShotgunTiles(), bits << 5)')
foreach($weapon in @('pistol','shotgun')){
    $selector=if($weapon -eq 'pistol'){'Pistol'}else{'Shotgun'}
    foreach($suffix in @('_rows','_side','')){
        $method=if($suffix -eq '_rows'){'Rows'}elseif($suffix -eq '_side'){'Side'}else{''}
        $translated=[regex]::Replace($translated,"\bpause_${weapon}_tiles$suffix\b","Select${selector}Tiles$method()")
    }
}
$translated=$translated.Replace('const int *indices','int[] indices').Replace('const int *pixels','int[] pixels')
$translated=$translated.Replace('pixels + ((int)index << 2)','Slice(pixels, index << 2)').Replace('*indices++','indices[token++]').Replace('int repeats = 0;','int token=0; int repeats = 0;').Replace('if (index & 0x80)','if ((index & 0x80) != 0)')
$translated=[regex]::Replace($translated,'\bpause_empty_rows\b','SelectEmptyRows()')
$translated=$translated.Replace('pressed = (int)(keys & ~previous_keys);','FocusStates[Frame]=state; pressed = (int)(keys & ~previous_keys);')
$translated=$translated.Replace('+ (SCROLL_Y != 0)','+ (SCROLL_Y != 0 ? 1 : 0)').Replace('+ (SCROLL_X != 0)','+ (SCROLL_X != 0 ? 1 : 0)');$translated=$translated.Replace('2 + (SCROLL_Y != 0)', '2 + (SCROLL_Y != 0 ? 1 : 0)').Replace('2 + (SCROLL_X != 0)', '2 + (SCROLL_X != 0 ? 1 : 0)')
$translated=[regex]::Replace($translated,'\+ (\([^;\r\n]+ != 0\))\s*;','+ ($1 ? 1 : 0);')
$translated=[regex]::Replace($translated,'int corpse_pixel\(int x, int y,\s*int next_tile\)\s*\{','int corpse_pixel(int x,int y,int next_tile) { x &= 255; y &= 255;')
# passage() is a C integer predicate, a C# bool predicate in the host adapter.

$mock = @'
public static int[] Slice(int[] data,int offset) { int[] result=new int[data.Length-offset]; Array.Copy(data,offset,result,0,result.Length); return result; }
public static int[] SelectPistolTiles(){return ScrollX==0?(ScrollY==0?pistol_0_0:pistol_0_4):(ScrollY==0?pistol_4_0:pistol_4_4);}
public static int[] SelectShotgunTiles(){return ScrollX==0?(ScrollY==0?shotgun_0_0:shotgun_0_4):(ScrollY==0?shotgun_4_0:shotgun_4_4);}
public static int[] SelectPistolTilesRows(){return ScrollX==0?(ScrollY==0?pistol_0_0_rows:pistol_0_4_rows):(ScrollY==0?pistol_4_0_rows:pistol_4_4_rows);}
public static int[] SelectPistolTilesSide(){return ScrollX==0?(ScrollY==0?pistol_0_0_side:pistol_0_4_side):(ScrollY==0?pistol_4_0_side:pistol_4_4_side);}
public static int[] SelectShotgunTilesRows(){return ScrollX==0?(ScrollY==0?shotgun_0_0_rows:shotgun_0_4_rows):(ScrollY==0?shotgun_4_0_rows:shotgun_4_4_rows);}
public static int[] SelectShotgunTilesSide(){return ScrollX==0?(ScrollY==0?shotgun_0_0_side:shotgun_0_4_side):(ScrollY==0?shotgun_4_0_side:shotgun_4_4_side);}
public static int[] SelectEmptyRows(){return ScrollX==0?(ScrollY==0?empty_0_0:empty_0_4):(ScrollY==0?empty_4_0:empty_4_4);}
public static int[] FocusStates=new int[2048],PatternBytes=new int[2048];
public static int owned_weapons=1,selected_weapon=0,shotgun_cell_x=11,shotgun_cell_y=6;
public static int[] DoorX={6,6,6},DoorY={4,2,8},door_states=new int[3];
public static int[] DoorFrames=new int[2048],DoorFindFrames=new int[2048],DoorPixelFrames=new int[2048];
public static bool TraceDoors;
public static int door_instance_find_at(int x,int y){DoorFindFrames[Frame]++;for(int i=0;i<DOOR_INSTANCE_COUNT;i++)if(DoorX[i]==x&&DoorY[i]==y)return i;return DOOR_INSTANCE_COUNT;}
public static int CountDoorPixels(){int n=0;for(int y=24;y<88;y++)for(int x=24;x<136;x++){int c=BackgroundPixel(x,y);if(c==1||c==5)n++;}return n;}
public class WorldSprite { public int world_x,world_y,state,pixels,health_and_hit_count,state_timer; public WorldSprite(int x,int y,int s){world_x=x;world_y=y;state=s;} }
public static WorldSprite[] Corpses=new WorldSprite[0];
public static void SetEntities(int[] data){Corpses=new WorldSprite[data.Length/3];for(int i=0;i<Corpses.Length;i++)Corpses[i]=new WorldSprite(data[i*3],data[i*3+1],data[i*3+2]);}
public static bool TraceCorpses;
public static bool TraceWeaponSafety;
public static string WeaponSnapshot;
public static string WeaponPixels() {
 var result=new System.Text.StringBuilder();
 for(int slot=0;slot<3;slot++)for(int y=110;y<130;y++)for(int x=38+32*slot;x<58+32*slot;x++)result.Append(BackgroundPixel(x,y)).Append(',');
 return result.ToString();
}
public static int[] RedFrames=new int[2048];
public static int CountRed(){int n=0;for(int y=24;y<88;y++)for(int x=24;x<136;x++)if(BackgroundPixel(x,y)==5)n++;return n;}
public static int[] BackgroundSnapshot(){int[] p=new int[160*144];for(int y=0;y<144;y++)for(int x=0;x<160;x++)p[y*160+x]=BackgroundPixel(x,y);return p;}
public static void CheckStamps(int[] before,int[] centers){
 for(int y=0;y<144;y++)for(int x=0;x<160;x++){
  bool marked=false;
  for(int i=0;i<centers.Length;i+=2){int dx=x-centers[i],dy=y-centers[i+1];if((dx==0&&dy==0)||(Math.Abs(dx)==1&&Math.Abs(dy)==1))marked=true;}
  marked=marked&&x>=24&&x<136&&y>=24&&y<88;
  int expected=marked?5:before[y*160+x];
  if(BackgroundPixel(x,y)!=expected)throw new Exception("Corpse stamp/background preservation at "+x+","+y);
 }
}
public static int[] ScanFrames=new int[2048], EntityFrames=new int[2048], CorpseWrites=new int[2048];
public static int ReadAddress, CloneCount, MaxClone;
public static int world_sprite_get_count(){ScanFrames[Frame]++;return Corpses.Length;}
public static WorldSprite world_sprite_get(int i){EntityFrames[Frame]++;return Corpses[i];}
public static void SMS_setAddr(int address){ReadAddress=address;}
public static int pause_data_port { get {return ReadByte(ReadAddress++);} }
public static int ReadByte(int address) {
 if(address>=0x3800) {int index=(address-0x3800)>>1;return (address&1)==0 ? Names[index%32,index/32] : 0;}
 int tile=address>>5,row=(address&31)>>2,plane=address&3,value=0;
 for(int x=0;x<8;x++) if((Pixels[tile,row,x]&(1<<plane))!=0)value|=128>>x;
 return value;
}
public static void SMS_VRAMmemcpy(int address,int[] data,int size) {
 Write();
 bool weapon=(address>=72*32&&address+size<=88*32)||(address>=128*32&&address+size<=160*32)||(address>=176*32&&address+size<=192*32);
 if(weapon){if(Frame!=0||size!=4)throw new Exception("Weapon rows loaded outside entry");PatternBytes[Frame]+=size;}
 else {CorpseWrites[Frame]++;if(address<96*32 || address+size>128*32)throw new Exception("Corpse write escaped private tile pool");}
 for(int i=0;i<size;i++){
  int a=address+i,tile=a>>5,row=(a&31)>>2,plane=a&3;
  if(!weapon)MaxClone=Math.Max(MaxClone,tile);
  for(int x=0;x<8;x++)Pixels[tile,row,x]=(Pixels[tile,row,x]&~(1<<plane))|(((data[i]&(128>>x))!=0)?(1<<plane):0);
 }
}
public static int[] Map;
public static int[,,] Pixels = new int[512,8,8];
public static int[,] Names = new int[32,28];
public static int PlayerX = 6*256+128, PlayerY = 7*256+128, DirectionX=0, DirectionY=-256;
public static int Frame, Writes, ScrollX, ScrollY, Queries, TileWrites;
public static int SpriteY, SpriteTerminator, SpriteX, SpriteTile;
public static int MinX,MaxX,MinY,MaxY;
public static bool Visible;
public static int world_get_tile(int x,int y) {
    QueryFrames[Frame]++;
    if(x<0 || y<0 || x>=WORLD_WIDTH || y>=WORLD_HEIGHT) throw new Exception("Invalid authoritative world read");
    Queries++; MinX=Math.Min(MinX,x); MaxX=Math.Max(MaxX,x); MinY=Math.Min(MinY,y); MaxY=Math.Max(MaxY,y);
    int t=Map[y*WORLD_WIDTH+x]; return t==WORLD_TILE_SPRITE_MARKER || t==WORLD_TILE_SHOTGUN_MARKER ? WORLD_TILE_EMPTY : t;
}
public static void ReadSnapshot() { if(Frame!=0) throw new Exception("Snapshot read while paused"); }
public static int player_get_position_x() { ReadSnapshot(); return PlayerX; }
public static int player_get_position_y() { ReadSnapshot(); return PlayerY; }
public static int camera_get_direction_x() { ReadSnapshot(); return DirectionX; }
public static int camera_get_direction_y() { ReadSnapshot(); return DirectionY; }
public static int[] Script;
public static int RawKeys, InitialBlocked;
public static int[] QueryFrames=new int[2048], TileFrames=new int[2048], SatFrames=new int[2048];
public static int[] FocusFrames=new int[2048], SpriteYFrames=new int[2048], SpriteXFrames=new int[2048];
public static int[] FocusTileFrames=new int[2048];
public static int SMS_getKeysStatus() {
    return Script==null ? RawKeys : Script[Frame];
}
public static void SMS_waitForVBlank() {
    AssertFrozen();
    if(TraceDoors)DoorPixelFrames[Frame]=CountDoorPixels();
    if(TraceCorpses)RedFrames[Frame]=CountRed();
    if(TraceWeaponSafety){string pixels=WeaponPixels();if(Frame==0)WeaponSnapshot=pixels;else if(pixels!=WeaponSnapshot)throw new Exception("Corpse pan corrupted weapon artwork, padding or slot borders");}
    SpriteYFrames[Frame]=SpriteY; SpriteXFrames[Frame]=SpriteX;
    FocusTileFrames[Frame]=Names[(12+48-ScrollX)>>3,(12+24+ScrollY)>>3];
    Frame++; if(Frame>=Script.Length) throw new Exception("Pause failed to exit on fresh START");
}
public static void SMS_displayOff() { Visible=false; }
public static void SMS_displayOn() { Visible=true; }
public static void SMS_setBGScrollX(int x) { ScrollX=x; }
public static void SMS_setBGScrollY(int y) { ScrollY=y; }
public static void Write() {
    Writes++;
    WriteFrames[Frame]++;
}
public static void SMS_VRAMmemsetW(int address,int value,int size) {
    Write();
    if(address==0 && size==16384) { if(Frame!=0) throw new Exception("Pan cleared VRAM"); Array.Clear(Pixels,0,Pixels.Length); Array.Clear(Names,0,Names.Length); SpriteY=SpriteTerminator=SpriteX=SpriteTile=0; }
    else if(address==PAUSE_MAP_SAT_Y && size==2) { SatFrames[Frame]++; SpriteY=value&255; SpriteTerminator=(value>>8)&255; }
    else if(address==PAUSE_MAP_SAT_X_TILE && size==2) { SatFrames[Frame]++; SpriteX=value&255; SpriteTile=(value>>8)&255; }
    else if(address>=0x3800 && address<0x3f00 && size==2){
        int index=(address-0x3800)>>1;Names[index%32,index/32]=value;
        TileFrames[Frame]++;TileWrites++;CloneCount++;
        if(value<96 || value>=128)throw new Exception("Corpse clone index overflow");
    }
    else throw new Exception("Unexpected VRAM operation");
}
public static void SMS_load1bppTiles(int[] rows,int tile,int size,int bg,int fg) {
    PatternBytes[Frame]+=size*4;
    if(Frame!=0) throw new Exception("Idle/pan/focus reloaded patterns"); Write(); for(int i=0;i<size/8;i++) for(int y=0;y<8;y++) for(int x=0;x<8;x++)
        Pixels[tile+i,y,x]=(rows[i*8+y]&(128>>x))!=0?fg:bg;
}
public static void SMS_loadTiles(int[] data,int tile,int size) {
    PatternBytes[Frame]+=size;
    if(Frame!=0) throw new Exception("Pan/focus loaded 4bpp patterns"); Write(); for(int y=0;y<8;y++) for(int x=0;x<8;x++) {
        int color=0; for(int p=0;p<4;p++) if((data[y*4+p]&(128>>x))!=0) color|=1<<p;
        Pixels[tile,y,x]=color;
    }
}
public static void SMS_setTileatXY(int x,int y,int tile) {
    Write(); Names[x,y]=tile; TileWrites++; TileFrames[Frame]++;
    if(tile>=FOCUS_PATTERN || tile==0) {
        if(x==((12+48-ScrollX)>>3) || x==((145+48-ScrollX)>>3)) FocusFrames[Frame]++;
    }
}
public static string SceneSignature() {
    var result=new System.Text.StringBuilder();
    foreach(int tile in Names) result.Append(tile).Append(',');
    return result.Append(ScrollX).Append(',').Append(ScrollY).Append(',')
        .Append(SpriteX).Append(',').Append(SpriteY).Append(',')
        .Append(SpriteTile).Append(',').Append(SpriteTerminator).ToString();
}
public static int BackgroundPixel(int x,int y) {
    x=(x+48-ScrollX)&255; y=(y+24+ScrollY)%224;
    return Pixels[Names[x/8,y/8],y%8,x%8];
}
public static int Pixel(int x,int y) {
    int sx=x+48-SpriteX, sy=y+24-(SpriteY+1);
    if(SpriteY!=208 && sx>=0 && sx<8 && sy>=0 && sy<8) {
        int color=Pixels[256+SpriteTile,sy,sx]; if(color!=0) return color;
    }
    return BackgroundPixel(x,y);
}
public static void Show(int x,int y) {
    Script=new int[131]; for(int i=0;i<120;i++) Script[i]=GG_KEY_START; Script[130]=GG_KEY_START;
    Run(x,y);
    if(Frame!=130) throw new Exception("Held START exited pause");
}
public static void Run(int x,int y) {
    int[] frozenDoors=(int[])door_states.Clone();
    Array.Clear(DoorFrames,0,2048);Array.Clear(DoorFindFrames,0,2048);
    PlayerX=x; PlayerY=y; Frame=0; game_gear_input_initialize(); input_blocked=InitialBlocked; keys=Script!=null&&Script[0]!=0?Script[0]:GG_KEY_START; Writes=0;
    Array.Clear(WriteFrames,0,WriteFrames.Length);
    Array.Clear(FocusStates,0,FocusStates.Length);Array.Clear(PatternBytes,0,PatternBytes.Length);
    Array.Clear(QueryFrames,0,2048); Array.Clear(TileFrames,0,2048); Array.Clear(SatFrames,0,2048);
    Array.Clear(FocusFrames,0,2048); Array.Clear(ScanFrames,0,2048); Array.Clear(EntityFrames,0,2048); Array.Clear(CorpseWrites,0,2048); CloneCount=0;MaxClone=0;
    Queries=TileWrites=0; MinX=MinY=255; MaxX=MaxY=0;
    game_gear_pause_map_show();
    for(int i=0;i<DOOR_INSTANCE_COUNT;i++)if(door_states[i]!=frozenDoors[i])throw new Exception("Pause changed authoritative door state");
}
'@
$mock=$mock.Replace('2048','40016')
Add-Type -TypeDefinition ("using System; public static class PauseMapContract {`n" + $defs + "`n" + $translated + "`n" + $mock + "`n" + $freezeMock + "`n}")
function Check-Layout {
    Require ($constants.AUTOMAP_FRAME_X -eq 16 -and $constants.AUTOMAP_FRAME_Y -eq 16 -and $constants.AUTOMAP_FRAME_WIDTH -eq 128 -and $constants.AUTOMAP_FRAME_HEIGHT -eq 80) 'V3 frame rectangle changed'
    for($x=16;$x -lt 144;$x++) { foreach($y in @(16,95)) { Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Frame horizontal continuity' } }
    for($y=16;$y -lt 96;$y++) { foreach($x in @(16,143)) { Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Frame vertical continuity' } }
    foreach($sx in @(40,72,104)) {
        for($y=110;$y -le 129;$y++){for($x=$sx-2;$x -le $sx+17;$x++){
            $expected=0
            if($x -eq $sx-2 -or $x -eq $sx+17 -or $y -eq 110 -or $y -eq 129){$expected=if($sx -eq 72){12}else{2}}
            if($sx -eq 72 -and $x -ge 72 -and $x -le 87 -and $y -ge 112 -and $y -le 127 -and $iconExpected[($y-112)*16+$x-72] -ge 0){$expected=$iconExpected[($y-112)*16+$x-72]}
            Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq $expected) 'Exact native artwork, 20x20 border, 1px black padding and empty gray sides'
        }}
    }
    Require ([PauseMapContract]::BackgroundPixel(12,108) -eq 12 -and [PauseMapContract]::BackgroundPixel(147,131) -eq 12) 'Default active WEAPONS brackets must be white'
    $left=@(0x08,0x30,0xc0,0xc0,0x30,0x08)
    for($ay=0;$ay -lt 6;$ay++){for($ax=0;$ax -lt 5;$ax++){
        $expected=if($left[$ay] -band (128 -shr $ax)){3}else{0}
        Require ([PauseMapContract]::BackgroundPixel((20+$ax),(117+$ay)) -eq $expected) 'Left arrow pixels wrong'
        Require ([PauseMapContract]::BackgroundPixel((139-$ax),(117+$ay)) -eq $expected) 'Arrow mirror symmetry wrong'
    }}
    Require ((117+122)/2 -eq (112+127)/2) 'Arrow and slot centers differ'
    for($y=0;$y -lt 144;$y++) { for($x=0;$x -lt 160;$x++) {
        if($x -lt 12 -or $x -gt 147 -or $y -lt 12 -or $y -gt 131) {
            Require ([PauseMapContract]::Pixel($x,$y) -eq 0) 'Content escaped physical outer margins'
        }
    } }
}
function Check-Window([int]$width,[int]$height,[int]$px,[int]$py) {
    $columns=[math]::Min($width,14); $rows=[math]::Min($height,8)
    $cx=[math]::Max(0,[math]::Min([math]::Floor($px/256)-7,$width-$columns))
    $cy=[math]::Max(0,[math]::Min([math]::Floor($py/256)-4,$height-$rows))
    [PauseMapContract]::Show($px,$py)
    Require ([PauseMapContract]::window_origin(($px -shr 8),$width,14) -eq $cx) 'Horizontal window origin/clamp wrong'
    Require ([PauseMapContract]::window_origin(($py -shr 8),$height,8) -eq $cy) 'Vertical window origin/clamp wrong'
    $mx=24+(14-$columns)*4; $my=24+(8-$rows)*4
    $screenX=$mx+[math]::Floor(($px-$cx*256)/32)
    $screenY=$my+[math]::Floor(($py-$cy*256)/32)
    Require ([PauseMapContract]::SpriteX -eq $screenX+47 -and [PauseMapContract]::SpriteY -eq $screenY+22) 'Sub-cell marker/window/LCD transform wrong'
    Require ([PauseMapContract]::SpriteTerminator -eq 208 -and [PauseMapContract]::SpriteTile -lt 8) 'SAT marker or terminator incorrect'
    Require ([PauseMapContract]::MinX -ge [math]::Max(0,$cx-1) -and [PauseMapContract]::MaxX -le [math]::Min($width-1,$cx+$columns)) 'Queries escaped horizontal window halo'
    Require ([PauseMapContract]::MinY -ge [math]::Max(0,$cy-1) -and [PauseMapContract]::MaxY -le [math]::Min($height-1,$cy+$rows)) 'Queries escaped vertical window halo'
    Require ([PauseMapContract]::Queries -le 5*$columns*$rows) 'Entry work scales with whole world instead of visible cells'
    $sx=[int]([PauseMapContract]::ScrollX -ne 0); $sy=[int]([PauseMapContract]::ScrollY -ne 0)
    $expected=$columns*$rows+2*(16+$sx+10+$sy)-4+2*(2*(4-$sx+4-$sy)-4)+(4-$sx)*(4-$sy)+4+2*(2-$sx)*(2-$sy)
    Require ([PauseMapContract]::TileWrites -eq $expected) 'Incorrect entry map/frame/slot/focus/arrow writes'
    for($f=1;$f -lt 131;$f++) { Require (([PauseMapContract]::TileFrames[$f]+[PauseMapContract]::DoorFrames[$f]+[PauseMapContract]::DoorFindFrames[$f]+[PauseMapContract]::QueryFrames[$f]+[PauseMapContract]::SatFrames[$f]) -eq 0) 'Idle pause performed render/world/SAT work'; Require (([PauseMapContract]::ScanFrames[$f]+[PauseMapContract]::EntityFrames[$f]+[PauseMapContract]::CorpseWrites[$f]) -eq 0) 'Idle scanned corpses' }
    return @($mx,$my)
}

# Exercise production window/render code on test-only synthetic extents.
foreach ($size in @(@(13,13),@(16,10),@(16,16),@(32,16),@(16,32),@(32,32),@(64,64),@(128,128),@(1,1),@(4,4),@(8,4),@(4,8))) {
    $w=$size[0]; $h=$size[1]
    [PauseMapContract]::WORLD_WIDTH=$w; [PauseMapContract]::WORLD_HEIGHT=$h
    [PauseMapContract]::Map=New-Object int[] ($w*$h)
    foreach ($px in @(0,([int][math]::Floor($w/2)*256), ($w*256-1))) {
        foreach ($py in @(0,([int][math]::Floor($h/2)*256), ($h*256-1))) { $null=Check-Window $w $h $px $py }
    }
    Check-Layout
}

# Eight sectors, cardinal/diagonal centers and both sides of all boundaries.
foreach ($direction in @(@(0,-256,0),@(181,-181,1),@(256,0,2),@(181,181,3),@(0,256,4),@(-181,181,5),@(-256,0,6),@(-181,-181,7),@(97,-237,0),@(98,-237,1),@(237,-98,1),@(237,-97,2),@(237,97,2),@(237,98,3),@(98,237,3),@(97,237,4),@(-97,237,4),@(-98,237,5),@(-237,98,5),@(-237,97,6),@(-237,-97,6),@(-237,-98,7),@(-98,-237,7),@(-97,-237,0))) {
    [PauseMapContract]::Frame=0; [PauseMapContract]::DirectionX=$direction[0]; [PauseMapContract]::DirectionY=$direction[1]
    Require ([PauseMapContract]::player_facing() -eq $direction[2]) 'Eight-way quantization failed'
}
$expectedGlyphs=@(@(0x40,0xa0,0xa0),@(0x60,0x60,0x80),@(0xc0,0x20,0xc0),@(0x80,0x60,0x60),@(0xa0,0xa0,0x40),@(0x20,0xc0,0xc0),@(0x60,0x80,0x60),@(0xc0,0xc0,0x20))
[PauseMapContract]::Frame=0; [PauseMapContract]::load_ui()
for($d=0;$d -lt 8;$d++) {
    $lit=0
    [PauseMapContract]::draw_player(80,56,$d)
    Require ([PauseMapContract]::SpriteTile -eq $d) 'Facing SAT tile index wrong'
    for($y=0;$y -lt 8;$y++) { for($x=0;$x -lt 8;$x++) {
        $color=if($y -lt 3 -and ($expectedGlyphs[$d][$y] -band (128 -shr $x))){7}else{0}
        Require ([PauseMapContract]::Pixels[(256+$d),$y,$x] -eq $color) 'Directional sprite pixels/color wrong'
        if($color -eq 7){$lit++;Require ($x -lt 3 -and $y -lt 3) 'Player pixel escaped 3x3 canvas'}
    } }
    Require ($lit -eq 5) "Direction $d must contain exactly five green pixels"
    # Authored cardinal/diagonal families must agree under 90-degree rotation.
    for($y=0;$y -lt 3;$y++){for($x=0;$x -lt 3;$x++){
        Require ([PauseMapContract]::Pixels[(256+$d),$y,$x] -eq [PauseMapContract]::Pixels[(256+(($d+2)%8)),$x,(2-$y)]) 'Directional rotational symmetry failed'
    }}
}
# All four wall-mounted computers: white wall face stays in the wall cell;
# blue protrusion occupies the adjacent room tile without a gap or thick wall.
foreach($mount in @(@(3,1,20),@(5,3,21),@(3,5,22),@(1,3,23))) {
    [PauseMapContract]::WORLD_WIDTH=7; [PauseMapContract]::WORLD_HEIGHT=7
    $testMap=New-Object int[] 49
    for($y=0;$y -lt 7;$y++){for($x=0;$x -lt 7;$x++){
        $testMap[$y*7+$x]=if($x -ge 2 -and $x -le 4 -and $y -ge 2 -and $y -le 4){0}else{1}
    }}
    $testMap[$mount[1]*7+$mount[0]]=7; [PauseMapContract]::Map=$testMap
    $null=Check-Window 7 7 896 896; Check-Layout
    [PauseMapContract]::Frame=0
    $rx=[math]::Max(2,[math]::Min(4,$mount[0])); $ry=[math]::Max(2,[math]::Min(4,$mount[1]))
    Require ([PauseMapContract]::cell_pattern($rx,$ry) -eq $mount[2]) 'Computer protrusion mount/orientation wrong'
    $face= switch($mount[2]){20{4}21{8}22{1}23{2}}
    Require ([PauseMapContract]::cell_pattern($mount[0],$mount[1]) -eq $face) 'Computer replaced structural wall'
    for($p=0;$p -lt 8;$p++) {
        $wx=52+$mount[0]*8; $wy=28+$mount[1]*8
        switch($mount[2]){20{$wx+=$p;$wy+=7}21{$wy+=$p}22{$wx+=$p}23{$wx+=7;$wy+=$p}}
        Require ([PauseMapContract]::BackgroundPixel($wx,$wy) -eq 12) 'Structural wall has a computer gap'
    }
    $blue=0
    for($y=0;$y -lt 8;$y++){for($x=0;$x -lt 8;$x++){
        if([PauseMapContract]::Pixels[$mount[2],$y,$x] -eq 4){$blue++}
    }}
    Require ($blue -eq 8) 'Computer must have a 4x2/2x4 blue protrusion'
}

# Drive the actual blocking menu and actual resident input functions.
function Run-Menu([int[]]$script,[int]$px=128,[int]$py=128) {
    [PauseMapContract]::Script=$script; [PauseMapContract]::Run($px,$py)
}
# Frozen authoritative normal/red door fixtures: both orientations, viewport
# edge and pan-in. Set state before entry; never mutate it during a pause.
[PauseMapContract]::WORLD_WIDTH=32; [PauseMapContract]::WORLD_HEIGHT=32
[PauseMapContract]::TraceDoors=$true
foreach($type in @(5,6)){foreach($vertical in @(0,1)){foreach($open in @(0,1)){foreach($dx in @(13,14)){
    $map=New-Object int[] 1024; $dy=3; $map[$dy*32+$dx]=$type
    if($vertical){$map[($dy-1)*32+$dx]=1;$map[($dy+1)*32+$dx]=1}
    else{$map[$dy*32+$dx-1]=1;$map[$dy*32+$dx+1]=1}
    [PauseMapContract]::Map=$map
    [PauseMapContract]::DoorX=@($dx,255,255);[PauseMapContract]::DoorY=@($dy,255,255)
    [PauseMapContract]::door_states=@($open,0,0);[PauseMapContract]::Frame=0
    $pattern=if($open){0}else{16+2*($type-5)+$vertical}
    Require ([PauseMapContract]::cell_pattern($dx,$dy) -eq $pattern) 'Door open/closed/orientation classification failed'
    # Open-door topology must exactly match an EMPTY cell, including its halo.
    if($open){
        $before=@();foreach($p in @(@($dx,$dy),@(($dx-1),$dy),@(($dx+1),$dy),@($dx,($dy-1)),@($dx,($dy+1)))){$before+= [PauseMapContract]::cell_pattern($p[0],$p[1])}
        $map[$dy*32+$dx]=0;[PauseMapContract]::Map=$map;$i=0
        foreach($p in @(@($dx,$dy),@(($dx-1),$dy),@(($dx+1),$dy),@($dx,($dy-1)),@($dx,($dy+1)))){Require ([PauseMapContract]::cell_pattern($p[0],$p[1]) -eq $before[$i++]) 'Open door changed passage topology'}
        $map[$dy*32+$dx]=$type;[PauseMapContract]::Map=$map
    }
    $script=New-Object int[] 15
    $script[2]=1;$script[3]=2;$script[5]=1;$script[6]=16 # enter MAP, focus only, then browse
    $script[7]=4 # outward edge: reject
    $script[8]=8;$script[9]=4 # pan in and back out
    $script[11]=32;$script[14]=0x8000
    Run-Menu $script
    $entryPixels=if(!$open -and $dx -eq 13){8}else{0}
    $panPixels=if($open){0}else{8}
    Require ([PauseMapContract]::DoorPixelFrames[0] -eq $entryPixels -and [PauseMapContract]::DoorPixelFrames[8] -eq $panPixels -and [PauseMapContract]::DoorPixelFrames[9] -eq $entryPixels) 'Frozen door pixels on entry/pan/return wrong'
    if(!$open){for($y=0;$y -lt 8;$y++){for($x=0;$x -lt 8;$x++){
        $ink=if($vertical){$x -eq 3}else{$y -eq 3}
        $color=if($ink){if($type -eq 5){1}else{5}}else{0}
        Require ([PauseMapContract]::Pixels[$pattern,$y,$x] -eq $color) 'Closed door line/palette wrong'
    }}}
    foreach($f in 0..14){
        $visible=if($f -eq 8 -or (($f -eq 0 -or $f -eq 9) -and $dx -eq 13)){1}else{0}
        Require ([PauseMapContract]::DoorFrames[$f] -eq $visible -and [PauseMapContract]::DoorFindFrames[$f] -eq $visible) 'Door query outside visible event or duplicate lookup'
        if($f -notin @(0,8,9)){
            Require (([PauseMapContract]::QueryFrames[$f]+[PauseMapContract]::ScanFrames[$f]+[PauseMapContract]::EntityFrames[$f]+[PauseMapContract]::CorpseWrites[$f]+[PauseMapContract]::SatFrames[$f]) -eq 0) 'Idle/focus/rejected pan touched frozen world'
            $ui=if($f -in @(2,3,5)){8}elseif($f -in @(6,11)){4}else{0}
            Require ([PauseMapContract]::TileFrames[$f] -eq $ui) 'Non-event map write in door fixture'
        }
    }
}}}}
# An open door next to a computer shares the ordinary passage protrusion path.
[PauseMapContract]::Frame=0;[PauseMapContract]::Map=New-Object int[] 1024
[PauseMapContract]::Map[3*32+3]=5;[PauseMapContract]::Map[2*32+3]=7
[PauseMapContract]::DoorX=@(3,255,255);[PauseMapContract]::DoorY=@(3,255,255);[PauseMapContract]::door_states=@(1,0,0)
Require ([PauseMapContract]::cell_pattern(3,3) -eq 20) 'Open door did not inherit passage computer pixels'
[PauseMapContract]::DoorX=@(6,6,6);[PauseMapContract]::DoorY=@(4,2,8);[PauseMapContract]::door_states=@(0,0,0);[PauseMapContract]::TraceDoors=$false
Require ([PauseMapContract]::door_state_get(3) -eq 0) 'Invalid door instance must stay closed'
Write-Output '- V4.1 frozen normal/red doors: open/closed, H/V, viewport edge/pan-in, passage topology, zero idle/focus/rejected queries'
[PauseMapContract]::WORLD_WIDTH=32; [PauseMapContract]::WORLD_HEIGHT=32
[PauseMapContract]::Map=New-Object int[] 1024
$script=New-Object int[] 13
$script[2]=1; $script[3]=2; $script[4]=18; $script[5]=4; $script[6]=8; $script[7]=1
$script[8]=16; $script[9]=16; $script[10]=32; $script[11]=32; $script[12]=0x803f
Run-Menu $script
Require ([PauseMapContract]::Frame -eq 12) 'START did not exit immediately'
for($f=2;$f -le 12;$f++) {
     $expected=switch($f){2{8}3{8}7{8}8{4}10{4}default{0}}
    Require ([PauseMapContract]::TileFrames[$f] -eq $expected) "Navigation/focus/held-button writes wrong at $f"
    Require (([PauseMapContract]::DoorFrames[$f]+[PauseMapContract]::DoorFindFrames[$f]+[PauseMapContract]::QueryFrames[$f]+[PauseMapContract]::SatFrames[$f]) -eq 0) 'Navigation queried world or updated SAT'
}
Require ([PauseMapContract]::FocusTileFrames[3] -eq 0 -and [PauseMapContract]::FocusTileFrames[7] -eq 48 -and [PauseMapContract]::FocusTileFrames[8] -eq 52 -and [PauseMapContract]::FocusTileFrames[10] -eq 48) 'State focus tile transitions wrong'
# Repeat initial delay 12 and cadence 4, immediate direction change/repress.
$script=New-Object int[] 33; $script[2]=1;$script[3]=16
for($f=4;$f -le 28;$f++){$script[$f]=8}
$script[29]=4; $script[31]=8; $script[32]=0x8008
Run-Menu $script
$pans=@(4,16,20,24,28,29,31)
for($f=4;$f -le 32;$f++) {
    $expected=if($f -in $pans){112}else{0}
    Require ([PauseMapContract]::TileFrames[$f] -eq $expected) "Pan/repeat writes wrong at $f"
    Require ([PauseMapContract]::QueryFrames[$f] -le 5*$expected) 'Pan query work exceeded visible-cell budget'
    if($expected -eq 0){Require ([PauseMapContract]::SatFrames[$f] -eq 0) 'Idle/rejected pan touched SAT'}
}
# Move away from a stationary player, then return: true hide/show, not edge pinning.
$script=New-Object int[] 8; $script[2]=1;$script[3]=16; $script[4]=8; $script[5]=4; $script[7]=0x8000
Run-Menu $script
Require ([PauseMapContract]::SpriteYFrames[4] -eq 208 -and [PauseMapContract]::SpriteYFrames[5] -ne 208) 'Off-window player did not hide and reappear'
Require ([PauseMapContract]::SatFrames[4] -eq 1 -and [PauseMapContract]::SatFrames[5] -eq 2) 'Hide/show SAT write count wrong'
# Opposing and outward-at-edge directions must be render-free.
$script=New-Object int[] 8; $script[2]=1;$script[3]=16; $script[4]=5; $script[5]=15; $script[7]=0x8000
Run-Menu $script
for($f=4;$f -le 7;$f++){Require (([PauseMapContract]::TileFrames[$f]+[PauseMapContract]::SatFrames[$f]+[PauseMapContract]::QueryFrames[$f]) -eq 0) 'Rejected edge/opposed pan performed work'}
# Every legal origin for requested extents, including axes smaller than the view.
foreach($size in @(@(13,13),@(16,10),@(32,32),@(64,64),@(128,128),@(1,1),@(7,7))) {
    foreach($axis in @(@($size[0],14),@($size[1],8))) {
        $limit=[math]::Max(0,$axis[0]-$axis[1])
        for($origin=0;$origin -le $limit;$origin++) { foreach($negative in @(0,1)){foreach($positive in @(0,1)){
            $expected=$origin
            if($negative -and !$positive){$expected=[math]::Max(0,$origin-1)}
            if($positive -and !$negative){$expected=[math]::Min($limit,$origin+1)}
            Require ([PauseMapContract]::pan_axis($origin,$axis[0],$axis[1],$negative,$positive) -eq $expected) 'Pan axis overflow/underflow/clamp failed'
        }} }
    }
}
# START in each state wins over simultaneous UI actions, then all 64 possible
# gameplay holds remain masked until release. Execute production input intents.
foreach($state in @(0,1,2)) {
 for($held=0;$held -lt 64;$held++) {
    $script=New-Object int[] 6
    $script[2]=if($state -eq 1){0}else{1}; $script[3]=if($state -eq 2){16}else{0}
    $script[5]=0x8000 -bor $held; Run-Menu $script
    Require ([PauseMapContract]::Frame -eq 5 -and [PauseMapContract]::TileFrames[5] -eq 0) 'START priority/state exit failed'
    [PauseMapContract]::Script=$null; [PauseMapContract]::RawKeys=$held
    [PauseMapContract]::game_gear_input_update()
    Require (([PauseMapContract]::keys -band 63) -eq 0) 'Held pause UI input leaked after resume'
    Require (![PauseMapContract]::input_shoot_requested() -and ![PauseMapContract]::input_interaction_requested()) 'Pause UI caused phantom action'
    # Release each bit independently, retaining the others, with no B2 release action.
    $raw=$held
    foreach($bit in @(1,2,4,8,16,32)) {
        $raw=$raw -band (-bnot $bit); [PauseMapContract]::RawKeys=$raw
        [PauseMapContract]::game_gear_input_update()
        Require (([PauseMapContract]::keys -band 63) -eq 0 -and ![PauseMapContract]::input_interaction_requested()) 'Independent release mask failed'
    }
    [PauseMapContract]::RawKeys=16; [PauseMapContract]::game_gear_input_update()
    Require ([PauseMapContract]::input_shoot_requested()) 'Fresh B1 after release failed'
    [PauseMapContract]::RawKeys=32; [PauseMapContract]::game_gear_input_update()
    [PauseMapContract]::RawKeys=0; [PauseMapContract]::game_gear_input_update()
    Require ([PauseMapContract]::input_interaction_requested()) 'Fresh B2 press/release interaction failed'
 }
}
# Reopening pause while a prior exit hold remains blocked must retain that mask.
for($held=0;$held -lt 64;$held++) {
    [PauseMapContract]::InitialBlocked=$held
    $script=New-Object int[] 6
    for($f=0;$f -lt 5;$f++){$script[$f]=$held}
    $script[5]=0x8000 -bor $held; Run-Menu $script
    Require ([PauseMapContract]::input_blocked -eq $held) 'Repeated pause lost a still-held release mask'
}
[PauseMapContract]::InitialBlocked=0
# All four scroll parities preserve frame corners through focus/browse changes.
foreach($size in @(@(7,7),@(8,7),@(7,6),@(8,6))) {
    [PauseMapContract]::WORLD_WIDTH=$size[0]; [PauseMapContract]::WORLD_HEIGHT=$size[1]
    [PauseMapContract]::Map=New-Object int[] ($size[0]*$size[1])
    foreach($mode in @(0,1,2)) {
        $script=New-Object int[] 8
        if($mode -eq 0){$script[2]=1;$script[3]=2;$script[5]=1}
        if($mode -eq 1){$script[3]=2}
        if($mode -eq 2){$script[2]=1;$script[3]=16}
        $script[7]=0x8000; Run-Menu $script
        for($x=16;$x -lt 144;$x++){foreach($y in @(16,95)){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Focus changed horizontal frame pixels'}}
        for($y=16;$y -lt 96;$y++){foreach($x in @(16,143)){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Focus changed vertical frame pixels'}}
    }
}
# Normal unmasked B2/strafe semantics and movement remain unchanged.
[PauseMapContract]::Script=$null
for($raw=0;$raw -lt 64;$raw++) {
    [PauseMapContract]::game_gear_input_initialize(); [PauseMapContract]::RawKeys=$raw
    [PauseMapContract]::game_gear_input_update()
    $forward=[int](($raw-band 1)-ne 0)-[int](($raw-band 2)-ne 0)
    $horizontal=[int](($raw-band 8)-ne 0)-[int](($raw-band 4)-ne 0)
    $strafe=if($raw-band 32){$horizontal}else{0}; $rotation=if($raw-band 32){0}else{$horizontal}
    Require ([PauseMapContract]::input_get_forward_intent() -eq $forward -and [PauseMapContract]::input_get_strafe_intent() -eq $strafe -and [PauseMapContract]::input_get_rotation_intent() -eq $rotation) 'Normal gameplay movement semantics changed'
    [PauseMapContract]::RawKeys=0; [PauseMapContract]::game_gear_input_update()
    Require ([PauseMapContract]::input_interaction_requested() -eq (($raw-band 32)-ne 0 -and ($raw-band 12)-eq 0)) 'B2 strafe release interaction semantics changed'
}
Write-Output '- production state/input traces: focus, browse, START priority, repeat, edge rejection, hide/show; 192 resume hold combinations'
# V4: authoritative corpse scan, exact five-pixel stamps and unchanged background.
[PauseMapContract]::WORLD_WIDTH=32; [PauseMapContract]::WORLD_HEIGHT=32
[PauseMapContract]::Map=New-Object int[] 1024
[PauseMapContract]::SetEntities(@()); [PauseMapContract]::Show(128,128)
$before=[PauseMapContract]::BackgroundSnapshot()
Require ([PauseMapContract]::CountRed() -eq 0) 'Zero corpses emitted red markers'
foreach($n in @(1,2,4,8)){
    $entities=@();$centers=@()
    for($i=0;$i -lt $n;$i++){$entities+=@((($i+1)*256+128),640,2);$centers+=@((24+($i+1)*8+4),44)}
    [PauseMapContract]::SetEntities($entities);[PauseMapContract]::Show(128,640)
    [PauseMapContract]::CheckStamps($before,$centers)
    Require ([PauseMapContract]::CountRed() -eq 5*$n) 'Corpse marker pixel count/overflow'
    Require ([PauseMapContract]::ScanFrames[0] -eq 1 -and [PauseMapContract]::EntityFrames[0] -eq $n) 'Corpse scan must be one bounded pass'
    for($f=1;$f -le 130;$f++){Require (([PauseMapContract]::ScanFrames[$f]+[PauseMapContract]::EntityFrames[$f]+[PauseMapContract]::CorpseWrites[$f]+[PauseMapContract]::SatFrames[$f]+[PauseMapContract]::TileFrames[$f]) -eq 0) 'Idle corpse/map/SAT work'}
}
# ALIVE and SHOT_DEAD are not corpses; unrelated packed state flags are ignored.
[PauseMapContract]::SetEntities(@(640,640,0,896,640,1,1152,640,66));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($before,@(60,44))
# All sub-cell pixel phases, including truncated boundary phases.
foreach($phase in @(0,31,32,63,64,127,128,223,224,255)){
 [PauseMapContract]::SetEntities(@((512+$phase),(512+$phase),2));[PauseMapContract]::Show(128,128)
 $center=40+($phase -shr 5);[PauseMapContract]::CheckStamps($before,@($center,$center))
}
# Viewport corners clip individual pixels rather than pinning the marker.
foreach($point in @(@(0,0,24,24),@(3583,2047,135,87))){
 [PauseMapContract]::SetEntities(@($point[0],$point[1],2));[PauseMapContract]::Show(128,128)
 [PauseMapContract]::CheckStamps($before,@($point[2],$point[3]))
}
# Eight disjoint four-tile crossings exhaust exactly the bounded 32-tile pool.
$entities=@();$centers=@()
foreach($cy in @(2,4)){foreach($cx in @(2,4,6,8)){$entities+=@(($cx*256),($cy*256),2);$centers+=@((24+$cx*8),(24+$cy*8))}}
[PauseMapContract]::SetEntities($entities);[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($before,$centers)
Require ([PauseMapContract]::CloneCount -eq 32 -and [PauseMapContract]::MaxClone -eq 127) 'Corpse clone pool upper bound failed'
# Same-tile/corpse overlaps must retain earlier marks, not replace the first clone.
[PauseMapContract]::SetEntities(@(640,640,2,704,640,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($before,@(44,44,46,44))
# Offscreen -> accepted pan -> visible -> accepted pan back -> absent.
[PauseMapContract]::SetEntities(@(3712,640,2));[PauseMapContract]::TraceCorpses=$true
$trace=New-Object int[] 8;$trace[2]=1;$trace[3]=16;$trace[4]=8;$trace[5]=4;$trace[7]=0x8000
Run-Menu $trace
Require ([PauseMapContract]::RedFrames[0] -eq 0 -and [PauseMapContract]::RedFrames[4] -eq 5 -and [PauseMapContract]::RedFrames[5] -eq 0) 'Corpse pan visibility failed'
foreach($f in @(0,4,5)){Require ([PauseMapContract]::ScanFrames[$f] -eq 1 -and [PauseMapContract]::EntityFrames[$f] -eq 1) 'Accepted pan must scan once'}
foreach($f in @(2,3,6,7)){Require (([PauseMapContract]::ScanFrames[$f]+[PauseMapContract]::CorpseWrites[$f]) -eq 0) 'Idle/focus scanned or drew corpse'}
$trace=New-Object int[] 8;$trace[2]=1;$trace[3]=16;$trace[4]=5;$trace[7]=0x8000;Run-Menu $trace
Require (([PauseMapContract]::ScanFrames[4]+[PauseMapContract]::CorpseWrites[4]+[PauseMapContract]::SatFrames[4]) -eq 0) 'Rejected pan touched corpse/SAT'
$trace=New-Object int[] 9;$trace[3]=2;$trace[5]=1;$trace[6]=16;$trace[7]=32;$trace[8]=0x8000
Run-Menu $trace
for($f=2;$f -le 8;$f++){Require (([PauseMapContract]::ScanFrames[$f]+[PauseMapContract]::EntityFrames[$f]+[PauseMapContract]::CorpseWrites[$f]) -eq 0) 'Focus/mode changes rescanned corpse state'}
[PauseMapContract]::TraceCorpses=$false
# Player priority: NE glyph overlaps red X pixels; hardware player remains green.
[PauseMapContract]::DirectionX=181;[PauseMapContract]::DirectionY=-181
[PauseMapContract]::SetEntities(@(640,640,2));[PauseMapContract]::Show(640,640)
$overlap=0
for($y=43;$y -le 45;$y++){for($x=43;$x -le 45;$x++){
 if([PauseMapContract]::Pixels[257,($y-43),($x-43)] -eq 7){
  Require ([PauseMapContract]::Pixel($x,$y) -eq 7) 'Corpse hid green player'
  if([PauseMapContract]::BackgroundPixel($x,$y) -eq 5){$overlap++}
 }
}}
Require ($overlap -gt 0) 'Priority fixture did not overlap opaque pixels'
# Final authoritative relocation position (door-crush cause has no presentation special case).
[PauseMapContract]::SetEntities(@(1408,896,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($before,@(68,52))
# Swap-with-last/dedup is reflected by the next render, with no copied position list.
[PauseMapContract]::SetEntities(@(640,640,2,896,640,2,1152,640,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::SetEntities(@(640,640,2,1152,640,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($before,@(44,44,60,44))
# Preserve every underlying wall/door/computer pixel except the five overlaid X pixels.
[PauseMapContract]::Map[2*32+2]=7
[PauseMapContract]::SetEntities(@());[PauseMapContract]::Show(128,128);$occupied=[PauseMapContract]::BackgroundSnapshot()
[PauseMapContract]::SetEntities(@(512,512,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($occupied,@(40,40))
[PauseMapContract]::WORLD_WIDTH=7;[PauseMapContract]::WORLD_HEIGHT=7;[PauseMapContract]::Map=New-Object int[] 49
[PauseMapContract]::SetEntities(@());[PauseMapContract]::Show(128,128);$centered=[PauseMapContract]::BackgroundSnapshot()
[PauseMapContract]::SetEntities(@(896,896,2));[PauseMapContract]::Show(128,128)
[PauseMapContract]::CheckStamps($centered,@(80,56))
[PauseMapContract]::SetEntities(@());[PauseMapContract]::DirectionX=0;[PauseMapContract]::DirectionY=-256
Require ($source -match 'WORLD_SPRITE_LIFE_STATE\(sprite\) != ZOMBIE_STATE_CORPSE') 'Markers must use authoritative corpse life state'
Require ($source -notmatch 'world_sprite_(remove|make_corpse|apply_damage)\(') 'Pause mutated corpse gameplay state'
Write-Output '- V4 corpses: 0/1/2/4/8, phases/clipping/pan/dedup/relocation/overlap, 32 clone limit, player priority, no idle scans'
# Real workshop and all sub-cell phases; no synthetic production map is added.
[PauseMapContract]::WORLD_WIDTH=13; [PauseMapContract]::WORLD_HEIGHT=13
[PauseMapContract]::Map=[int[]]$cells
[PauseMapContract]::DirectionX=0; [PauseMapContract]::DirectionY=-256
$null=Check-Window 13 13 1664 1920
$spawnQueries=[PauseMapContract]::Queries; $spawnWrites=[PauseMapContract]::TileWrites
Check-Layout
[PauseMapContract]::Frame=0
foreach ($point in @(@(6,4,16),@(6,8,16),@(6,2,18),@(6,12,1),@(6,11,22),@(5,0,0),@(5,1,2),@(7,1,8),@(6,0,4),@(0,0,0))) {
    Require ([PauseMapContract]::cell_pattern($point[0],$point[1]) -eq $point[2]) 'Workshop structural wall/door/computer semantics changed'
}
for($offset=0;$offset -lt 256;$offset++) { $null=Check-Window 13 13 (1536+$offset) (1792+$offset) }
Write-Output "- workshop spawn snapshot: $spawnQueries authoritative queries; $spawnWrites BG tile writes"
Require ($inputSource -match 'previous_keys = keys;\s*keys = SMS_getKeysStatus\(\);') 'START must share authoritative input history'
Require ($main -match 'game_gear_input_update\(\);\s*if \(input_pause_requested\(\)\)\s*\{\s*game_gear_pause_map_show\(\);\s*game_gear_video_restore_gameplay\(\);\s*continue;\s*\}\s*world_sprites_update\(\);') 'Pause must intercept all simulation and resume the same loop'
Require ($source -match 'game_gear_input_update\(\);\s*if \(input_pause_requested\(\)\) break;') 'START must precede UI actions in all states'
Require ($source -match 'if \(next_x == origin_x && next_y == origin_y\) continue;') 'Rejected pans must skip rendering'
Require ($inputSource -match 'input_blocked &= \(unsigned char\)keys;' -and $source -match 'input_blocked \|= \(unsigned char\)keys & 63;') 'Pause exit must mask held gameplay inputs until independent release'
Require ($source -notmatch 'GG_.*Palette|world_initialize|player_initialize|raycaster|hud_weapon|zombie_\w+\(|damage_shake_phase\s*=') 'Pause renderer must not mutate palette/gameplay or run the 3D renderer'
$restore = [regex]::Match($video, '(?s)void game_gear_video_restore_gameplay.*?\n\}').Value
Require ($restore -match '(?s)game_gear_video_initialize\(\);.*game_gear_health_hud_update\(player_get_health\(\)\);.*game_gear_video_draw_wall_columns\(\);.*SMS_displayOn\(\);') 'Restore must initialize display, restore health and fully compose before showing'
Require ($restore -notmatch 'world_initialize|player_initialize|hud_weapon_initialize|raycaster_update|damage_shake_update') 'Restore may not restart or advance simulation'
Require ($video -match 'SMS_VRAMmemsetW\(0, 0x0000, 16384\);' -and $video -match 'previous_wall_columns\[tile_column\].side_and_valid_flags = 0;' -and $video -match 'previous_projected_sprite_count = 0;') 'Restore must clear VRAM and invalidate wall/sprite caches'
Require ($restore -match 'game_gear_damage_shake_phase = shake_phase;') 'Restore must preserve damage shake timer'
Require ($video -match 'SMS_VRAMmemsetW\(PAUSE_MAP_SAT_Y, 0x00d0, 2\);') 'Gameplay must terminate the hardware marker SAT before showing'
Require ($video -match '(?s)GG_setSpritePaletteColor\(PAUSE_MAP_PLAYER_COLOR,\s*game_gear_get_wall_palette_color\(PAUSE_MAP_PLAYER_COLOR - GAME_GEAR_WALL_PALETTE_BASE\)\);') 'Sprite green must reuse the authoritative gameplay palette at startup/restore'
Require ($source -notmatch 'SMS_initSprites|SMS_addSprite|SMS_copySpritestoSAT|SMS_setSpriteMode|SMS_useFirstHalfTilesforSprites') 'Marker must not allocate a sprite list or change the audited native sprite setup'
Require ($constants.PAUSE_MAP_PLAYER_COLOR -eq 7 -and $constants.PAUSE_MAP_PLAYER_TILE -eq 256 -and $constants.PAUSE_MAP_SAT_Y -eq 0x3f00 -and $constants.PAUSE_MAP_SAT_X_TILE -eq 0x3f80) 'Marker VRAM/SAT defaults changed'
$sprite = Get-Content "$root/game/world_sprite.h" -Raw
$struct = [regex]::Match($sprite,'(?s)typedef struct\s*\{(.*?)\}\s*WorldSprite;').Groups[1].Value
$bytes = 2*[regex]::Matches($struct,'(?:signed|unsigned) int\s+\w+;').Count + [regex]::Matches($struct,'unsigned char\s+\w+;').Count + 2*[regex]::Matches($struct,'const unsigned char \*\w+;').Count + [regex]::Matches($struct,'ZombieState\s+\w+;').Count
Require ($bytes -eq 9) 'WorldSprite must remain exactly 9 Z80 bytes'
$asm = Get-Content "$build/pause_map.asm" -Raw
Require ($asm -notmatch '(?m)^\s*(?:call|jp)\s+_+(?:div|mod|mul|sdcc_bcall)') 'Pause path introduced arithmetic helper or nested bank call'
$rel = Get-Content "$build/pause_map.rel" -Raw
Require ($rel -match 'A _DATA size 0 ' -and $rel -match 'A _BANK2 size ') 'Pause must have zero static RAM and live in Bank 2'
$largestFrame = ([regex]::Matches($asm, 'ld\s+(?:hl|iy), #-(\d+)') | ForEach-Object { [int]$_.Groups[1].Value } | Measure-Object -Maximum).Maximum
Require ($largestFrame -le 22) 'Pause local frame exceeded V4 baseline 22 bytes'
if ($RequireMapPlacement) {
    $linkMap=Get-Content "$build/GearRay.map" -Raw
    foreach($helper in @('door_instance_find_at','door_state_get')){
        $address=[regex]::Match($linkMap,"(?m)^\s*([0-9A-F]{8})\s+_$helper\s")
        Require ($address.Success -and [Convert]::ToInt32($address.Groups[1].Value,16) -lt 0x4000) "Door helper $helper must remain resident"
    }
    $show=[regex]::Match($linkMap,'(?m)^\s*([0-9A-F]{8})\s+_game_gear_pause_map_show\s')
    Require $show.Success 'Linked pause entry is missing'
    $showAddress=[Convert]::ToInt32($show.Groups[1].Value,16)
    Require ($showAddress -ge 0x28000 -and $showAddress -lt 0x2c000) 'Linked pause entry left Bank 2'
    $restoreSymbol=[regex]::Match($linkMap,'(?m)^\s*([0-9A-F]{8})\s+_game_gear_video_restore_gamepla\s')
    Require $restoreSymbol.Success 'Linked restore entry is missing'
    $restoreAddress=[Convert]::ToInt32($restoreSymbol.Groups[1].Value,16)
    Require ($restoreAddress -ge 0x14000 -and $restoreAddress -lt 0x18000) 'Linked restore left Bank 1'
    $showOffset=[Convert]::ToInt32([regex]::Match($rel,'S _game_gear_pause_map_show Def([0-9A-F]+)').Groups[1].Value,16)
    $symbols=Get-Content "$build/pause_map.sym" -Raw
    $glyphOffset=[Convert]::ToInt32([regex]::Match($symbols,'(?m)^\s*\d+\s+_player_rows\s+([0-9A-F]+)\s').Groups[1].Value,16)
    $rom=[IO.File]::ReadAllBytes((Get-ProductionBuildRom $build))
    $pistolOffset=[Convert]::ToInt32([regex]::Match($symbols,'(?m)^\s*\d+\s+_pause_pistol_tiles\s+([0-9A-F]+)\s').Groups[1].Value,16)
    $pistolAddress=($showAddress-$showOffset+$pistolOffset)-band 0xffff
    # Workshop: 13 columns centered at X=28 (scroll X=4), Y=24 (scroll Y=0).
    $pistolData=[PauseMapContract]::pistol_4_0
    for($i=0;$i -lt $pistolData.Length;$i++){Require ($rom[$pistolAddress+$i] -eq $pistolData[$i]) 'Linked pistol composite differs from pixel-validated native canvas'}
    $glyphRomAddress=($showAddress-$showOffset+$glyphOffset)-band 0xffff
    for($i=0;$i -lt 64;$i++) {
        Require ($rom[$glyphRomAddress+$i] -eq [PauseMapContract]::player_rows[$i]) 'Final ROM directional glyph payload differs from validated pixels'
    }
    $arrowOffset=[Convert]::ToInt32([regex]::Match($symbols,'(?m)^\s*\d+\s+_arrow_rows\s+([0-9A-F]+)\s').Groups[1].Value,16)
    $arrowAddress=($showAddress-$showOffset+$arrowOffset)-band 0xffff
    for($i=0;$i -lt 12;$i++){Require ($rom[$arrowAddress+$i] -eq [PauseMapContract]::arrow_rows[$i]) 'Linked arrow payload differs from validated geometry'}
    Write-Output "- final linked Bank 2 entry / Bank 1 restore / resident door accessors; 64 five-pixel player glyph bytes and 12 arrow bytes verified"
}
$paletteSource = Get-Content "$build/generated/wall_texture.c" -Raw
$paletteBody = [regex]::Match($paletteSource,'(?s)wall_palette_colors\[.*?\]\s*=\s*\{(.*?)\}').Groups[1].Value
$palette = @(0) + @([regex]::Matches($paletteBody,'0x[0-9a-fA-F]+') | ForEach-Object { [Convert]::ToInt32($_.Value,16) })
Require ($palette[12] -eq 0xfff -and $palette[1] -eq 0x03a -and $palette[5] -eq 0x02b -and $palette[4] -eq 0xb80) 'Reused gameplay palette semantics changed'
Require ($palette[7] -eq 0x265) 'Existing olive-green player color changed'

# Pixel-exact host preview, derived from production tile writes (not emulator capture).
Add-Type -AssemblyName System.Drawing
foreach($preview in @(@('pause-map-preview.png',1664,1920,0),@('pause-map-computer-preview.png',1664,2944,0),@('pause-weapons-focus-preview.png',1664,2944,1),@('pause-map-browse-preview.png',1664,1920,2),@('pause-map-corpses-preview.png',1664,1920,0))) {
 [PauseMapContract]::SetEntities(@())
 if($preview[0] -eq 'pause-map-corpses-preview.png'){[PauseMapContract]::SetEntities(@(1408,1664,2,1920,1920,2))}
 $script=New-Object int[] 7
 if($preview[3] -eq 0){$script[2]=1}
 if($preview[3] -eq 2){$script[2]=1;$script[3]=16; $script[4]=2}
 $script[6]=0x8000
 Run-Menu $script $preview[1] $preview[2]
 $shortScene=[PauseMapContract]::SceneSignature()
 $longScript=New-Object int[] 131
 [Array]::Copy($script,$longScript,6); $longScript[130]=0x8000
 Run-Menu $longScript $preview[1] $preview[2]
 Require ([PauseMapContract]::SceneSignature() -eq $shortScene) 'Short preview trace differs from prolonged idle scene'
 for($x=16;$x -lt 144;$x++){foreach($y in @(16,95)){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Preview lost horizontal frame'}}
 for($y=16;$y -lt 96;$y++){foreach($x in @(16,143)){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 12) 'Preview lost vertical frame'}}
 $bitmap = New-Object Drawing.Bitmap 160,144
 try {
    for ($y=0; $y -lt 144; $y++) { for ($x=0; $x -lt 160; $x++) {
        $c=$palette[[PauseMapContract]::Pixel($x,$y)]
        $bitmap.SetPixel($x,$y,[Drawing.Color]::FromArgb(($c-band 15)*17,(($c-shr 4)-band 15)*17,(($c-shr 8)-band 15)*17))
    } }
    $bitmap.Save((Join-Path $build $preview[0]),[Drawing.Imaging.ImageFormat]::Png)
 } finally { $bitmap.Dispose() }
}
# Execute the production carousel and selection paths in all scroll parities.
$shotgunIcon=[Drawing.Bitmap]::new("$root/assets/sprites/weapons/shotgun.png")
$shotgunExpected=New-Object int[] 256
try {
    Require ($shotgunIcon.Width -eq 16 -and $shotgunIcon.Height -eq 16) 'Native shotgun pause canvas'
    for($y=0;$y -lt 16;$y++){for($x=0;$x -lt 16;$x++){
        $c=$shotgunIcon.GetPixel($x,$y);$shotgunExpected[$y*16+$x]=-1
        if($c.A -eq 0){continue}
        Require ($c.A -eq 255) 'Shotgun partial alpha'
        $rgb='#{0:x2}{1:x2}{2:x2}' -f $c.R,$c.G,$c.B
        $index=switch($rgb){'#000000'{0} '#1a1a1a'{13} '#4d4d4d'{2} '#797878'{3} '#ffffff'{12} default{throw "Unexpected shotgun color $rgb"}}
        $shotgunExpected[$y*16+$x]=$index
    }}
} finally {$shotgunIcon.Dispose()}
function Check-Carousel([int[]]$weapons) {
    for($y=110;$y -lt 130;$y++){foreach($x in @((25..37)+(122..134))){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 0) 'Exactly 13 black columns must separate slots from the existing arrows'}}
    foreach($y in @(109,130)){for($x=38;$x -le 121;$x++){Require ([PauseMapContract]::BackgroundPixel($x,$y) -eq 0) 'Unmoved focus brackets must retain balanced black clearance above and below slots'}}
    for($slot=0;$slot -lt 3;$slot++){
        $origin=40+32*$slot
        for($y=0;$y -lt 20;$y++){for($x=0;$x -lt 20;$x++){
            $expected=if($x -eq 0 -or $x -eq 19 -or $y -eq 0 -or $y -eq 19){if($slot -eq 1){12}else{2}}else{0}
            $pixels=if($weapons[$slot] -eq 0){$iconExpected}elseif($weapons[$slot] -eq 1){$shotgunExpected}else{$null}
            if($null -ne $pixels -and $x -ge 2 -and $x -le 17 -and $y -ge 2 -and $y -le 17 -and $pixels[($y-2)*16+$x-2] -ge 0){$expected=$pixels[($y-2)*16+$x-2]}
            Require ([PauseMapContract]::BackgroundPixel($origin-2+$x,110+$y) -eq $expected) 'Exact native artwork, background alpha, 1px black padding and independent 20x20 border'
        }}
        $base=if($weapons[$slot] -eq 2){161}elseif($weapons[$slot] -eq 0){if($slot -eq 1){72}else{128}}else{if($slot -eq 1){176}else{144}}
        $limit=if($weapons[$slot] -eq 2){175}else{$base+15}
        $tx=($origin-2+48-[PauseMapContract]::ScrollX) -shr 3;$ty=(110+24+[PauseMapContract]::ScrollY) -shr 3
        $columns=4-[int]([PauseMapContract]::ScrollX -ne 0);$rows=4-[int]([PauseMapContract]::ScrollY -ne 0)
        for($r=0;$r -lt $rows;$r++){for($c=0;$c -lt $columns;$c++){
            $tile=[PauseMapContract]::Names[($tx+$c),($ty+$r)]
            Require (($weapons[$slot] -eq 2 -and $tile -eq 0) -or ($tile -ge $base -and $tile -le $limit)) 'Weapon tile reference escaped approved allocation'
        }}
    }
}
foreach($extent in @(@(14,8),@(13,8),@(14,7),@(13,7))){
    [PauseMapContract]::WORLD_WIDTH=$extent[0];[PauseMapContract]::WORLD_HEIGHT=$extent[1]
    [PauseMapContract]::Map=New-Object int[] ($extent[0]*$extent[1])
    foreach($owned in @(1,3)) {foreach($selected in @(0,1)) {
        if($owned -eq 1 -and $selected -eq 1){continue}
        [PauseMapContract]::owned_weapons=$owned;[PauseMapContract]::selected_weapon=$selected
        $trace=New-Object int[] 12;$trace[11]=0x8000;Run-Menu $trace
        Require ([PauseMapContract]::FocusStates[2] -eq 1) 'Every entry must start with WEAPONS focus'
        Require ([PauseMapContract]::BackgroundPixel(12,108) -eq 12) 'WEAPONS entry brackets must be white'
        $other=if($owned -eq 1){2}else{1-$selected};Check-Carousel @($other,$selected,$other)
        for($f=1;$f -lt 11;$f++){Require ([PauseMapContract]::WriteFrames[$f] -eq 0) 'Owned-weapon idle pause wrote VRAM'}
    }}
}
[PauseMapContract]::WORLD_WIDTH=13;[PauseMapContract]::WORLD_HEIGHT=13;[PauseMapContract]::Map=$cells
# No DOWN is needed: first usable fresh edge selects immediately.
[PauseMapContract]::owned_weapons=3;[PauseMapContract]::selected_weapon=0
$trace=New-Object int[] 7;$trace[2]=8;$trace[3]=8;$trace[6]=0x8000;Run-Menu $trace
Require ([PauseMapContract]::FocusStates[2] -eq 1 -and [PauseMapContract]::selected_weapon -eq 1 -and [PauseMapContract]::TileFrames[2] -eq 36 -and [PauseMapContract]::WriteFrames[3] -eq 0) 'Immediate WEAPONS control must select once on a fresh edge'
Check-Carousel @(0,1,0)
$trace=New-Object int[] 7;$trace[2]=1;$trace[6]=0x8000;Run-Menu $trace
Require ([PauseMapContract]::FocusStates[3] -eq 0 -and [PauseMapContract]::selected_weapon -eq 1) 'UP must reach MAP without changing selection'
Check-Carousel @(0,1,0)
Require ([PauseMapContract]::BackgroundPixel(12,12) -eq 3 -and [PauseMapContract]::BackgroundPixel(12,108) -eq 0) 'MAP focus must have gray brackets and clear weapon brackets'
$trace=New-Object int[] 8;$trace[2]=1;$trace[3]=0;$trace[4]=16;$trace[7]=0x8000;Run-Menu $trace
Require ([PauseMapContract]::BackgroundPixel(12,12) -eq 12) 'MAP browse brackets must be white'
Check-Carousel @(0,1,0)
$trace=New-Object int[] 7;$trace[6]=0x8000;Run-Menu $trace
Require ([PauseMapContract]::FocusStates[2] -eq 1 -and [PauseMapContract]::selected_weapon -eq 1) 'Reopening after MAP must reset focus only, preserving shotgun'
Write-Output ('- native entry pattern upload bytes: '+[PauseMapContract]::PatternBytes[0]+'; idle pattern upload bytes: '+[PauseMapContract]::PatternBytes[3])
Check-Carousel @(0,1,0)
foreach($key in @(4,8)){
    [PauseMapContract]::selected_weapon=0
    $trace=New-Object int[] 8;$trace[0]=0x8000 -bor $key;$trace[1]=$key;$trace[2]=$key;$trace[4]=$key;$trace[7]=0x8000;Run-Menu $trace
    Require ([PauseMapContract]::TileFrames[1] -eq 0 -and [PauseMapContract]::TileFrames[2] -eq 0 -and [PauseMapContract]::TileFrames[4] -eq 36 -and [PauseMapContract]::selected_weapon -eq 1) 'Entry-held direction must wait for release and fresh edge'
}
Write-Output '- WEAPONS entry, immediate fresh selection, MAP navigation/border invariance, reopen focus reset with selected shotgun preserved, held-entry direction debounce'
# Exhaust the unchanged clone pool with both weapon identities, then pan back
# repeatedly. Entry and every accepted pan must retain all eight X markers.
[PauseMapContract]::WORLD_WIDTH=32;[PauseMapContract]::WORLD_HEIGHT=16
[PauseMapContract]::Map=New-Object int[] 512
$entities=@();foreach($cy in @(2,4)){foreach($cx in @(2,4,6,8)){$entities+=@(($cx*256),($cy*256),2)}}
[PauseMapContract]::SetEntities($entities);[PauseMapContract]::TraceCorpses=$true
[PauseMapContract]::TraceWeaponSafety=$true
foreach($selected in @(0,1)){
    [PauseMapContract]::owned_weapons=3;[PauseMapContract]::selected_weapon=$selected
    $trace=New-Object int[] 15;$trace[2]=1;$trace[4]=16;$trace[6]=8;$trace[8]=4;$trace[10]=8;$trace[12]=4;$trace[14]=0x8000
    Run-Menu $trace 128 128
    Require ([PauseMapContract]::MaxClone -eq 127 -and [PauseMapContract]::CloneCount -eq 160) 'Five redraws must each use exactly the full 96..127 corpse clone pool'
    foreach($f in @(0,6,8,10,12)){Require ([PauseMapContract]::RedFrames[$f] -eq 40) 'Maximum corpse panning lost or corrupted an X marker'}
    $other=1-$selected;Check-Carousel @($other,$selected,$other)
}
[PauseMapContract]::TraceCorpses=$false;[PauseMapContract]::TraceWeaponSafety=$false;[PauseMapContract]::SetEntities(@())
[PauseMapContract]::WORLD_WIDTH=13;[PauseMapContract]::WORLD_HEIGHT=13;[PauseMapContract]::Map=$cells
Write-Output '- maximum 32-clone corpse pool, four accepted pans, eight exact X markers and unchanged padded weapon pixels for both selections'
foreach($selected in @(0,1)){
    [PauseMapContract]::selected_weapon=$selected
    $trace=New-Object int[] 7;$trace[6]=0x8000;Run-Menu $trace 1664 1920
    $image=[Drawing.Bitmap]::new(160,144)
    try {
        for($y=0;$y -lt 144;$y++){for($x=0;$x -lt 160;$x++){
            $c=$palette[[PauseMapContract]::Pixel($x,$y)]
            $image.SetPixel($x,$y,[Drawing.Color]::FromArgb(($c -band 15)*17,(($c -shr 4) -band 15)*17,(($c -shr 8) -band 15)*17))
        }}
        $image.Save("$build/pause-carousel-$selected-preview.png",[Drawing.Imaging.ImageFormat]::Png)
    } finally {$image.Dispose()}
}
foreach($key in @(4,8)){
    [PauseMapContract]::owned_weapons=3;[PauseMapContract]::selected_weapon=0
    $trace=New-Object int[] 12;$trace[2]=0;$trace[4]=$key;$trace[5]=$key;$trace[6]=$key;$trace[11]=0x8000
    Run-Menu $trace;Require ([PauseMapContract]::selected_weapon -eq 1) 'Both fresh directions select the other owned weapon without held repeat'
    Check-Carousel @(0,1,0)
    Require ([PauseMapContract]::TileFrames[4] -eq 36) 'Accepted selection redraws only three twelve-tile slots'
    foreach($f in @(3,5,6,7,8,9,10)){Require ([PauseMapContract]::WriteFrames[$f] -eq 0) 'Held/released/idle selection wrote VRAM'}
    Require (([PauseMapContract]::QueryFrames[4]+[PauseMapContract]::ScanFrames[4]+[PauseMapContract]::SatFrames[4]) -eq 0) 'Selection queried/rendered frozen world'
    $trace=New-Object int[] 8;$trace[2]=0;$trace[4]=$key;$trace[7]=0x8000
    Run-Menu $trace;Require ([PauseMapContract]::selected_weapon -eq 0) 'Selection persists across pause and wraps back'
    Check-Carousel @(1,0,1)
    [PauseMapContract]::owned_weapons=1;Run-Menu $trace;Require ([PauseMapContract]::selected_weapon -eq 0 -and [PauseMapContract]::WriteFrames[4] -eq 0) 'Single owned weapon rejects selection without work'
}
[PauseMapContract]::owned_weapons=1;[PauseMapContract]::selected_weapon=0
# Future compile-time count changes use the same bounded circular source helper.
[PauseMapContract]::WEAPON_COUNT=3;[PauseMapContract]::owned_weapons=7
foreach($current in 0..2){
    Require ([PauseMapContract]::adjacent_weapon($current,0) -eq (($current+2)%3)) 'Three-owned previous circular lookup'
    Require ([PauseMapContract]::adjacent_weapon($current,1) -eq (($current+1)%3)) 'Three-owned next circular lookup'
}
[PauseMapContract]::owned_weapons=5
Require ([PauseMapContract]::adjacent_weapon(0,1) -eq 2 -and [PauseMapContract]::adjacent_weapon(2,1) -eq 0) 'Circular search skips unowned future IDs'
[PauseMapContract]::WEAPON_COUNT=2;[PauseMapContract]::owned_weapons=3
$trace=New-Object int[] 8;$trace[2]=0;$trace[4]=12;$trace[7]=0x8000
Run-Menu $trace;Require ([PauseMapContract]::selected_weapon -eq 0 -and [PauseMapContract]::WriteFrames[4] -eq 0) 'Opposed simultaneous selection edges reject without work'
[PauseMapContract]::owned_weapons=1
# The fixture executes the actual production HUD update body, including pickup.
[PauseMapContract]::Frame=0;[PauseMapContract]::FreezeGuard=$false
[PauseMapContract]::shotgun_cell_x=11;[PauseMapContract]::shotgun_cell_y=6
foreach($position in @(@(2667,1664),@(3221,1664),@(2944,1387),@(2944,1941))){
    [PauseMapContract]::PlayerX=$position[0];[PauseMapContract]::PlayerY=$position[1]
    [PauseMapContract]::game_gear_hud_weapon_update(0)
    Require ([PauseMapContract]::owned_weapons -eq 1) 'Pickup collected outside touch region'
}
foreach($position in @(@(2816,1536),@(3071,1791),@(2668,1664),@(3220,1664),@(2944,1388),@(2944,1940),@(2668,1388),@(3220,1940))){
    [PauseMapContract]::owned_weapons=1;[PauseMapContract]::selected_weapon=0
    [PauseMapContract]::PlayerX=$position[0];[PauseMapContract]::PlayerY=$position[1]
    [PauseMapContract]::game_gear_hud_weapon_update(0)
    Require ([PauseMapContract]::owned_weapons -eq 3 -and [PauseMapContract]::selected_weapon -eq 1) 'First contact ownership immediately equips shotgun'
    [PauseMapContract]::PlayerX=0;[PauseMapContract]::PlayerY=0
    [PauseMapContract]::game_gear_hud_weapon_update(0)
    Require ([PauseMapContract]::owned_weapons -eq 3) 'Collected pickup ownership persists away from source'
}
# Show the actual pause carousel immediately after first acquisition, then
# select pistol through production menu input and revisit an already-owned item.
$trace=New-Object int[] 8;$trace[7]=0x8000;Run-Menu $trace
Check-Carousel @(0,1,0)
$trace=New-Object int[] 8;$trace[2]=0;$trace[4]=4;$trace[7]=0x8000;Run-Menu $trace
Require ([PauseMapContract]::selected_weapon -eq 0) 'Manual pause selection persists after auto-equip'
Check-Carousel @(1,0,1)
[PauseMapContract]::PlayerX=2944;[PauseMapContract]::PlayerY=1664
[PauseMapContract]::game_gear_hud_weapon_update(0)
Require ([PauseMapContract]::owned_weapons -eq 3 -and [PauseMapContract]::selected_weapon -eq 0) 'Already-owned contact must never override manual selection'
# Drive mechanically extracted main iterations and actual input edges across
# acquisition. Previously accepted shots execute once; a fresh edge queues once.
foreach($pending in @(0,1)){foreach($mode in @(0,1,2)){
    [PauseMapContract]::SeedFreeze();[PauseMapContract]::FreezeGuard=$false
    [PauseMapContract]::owned_weapons=1;[PauseMapContract]::selected_weapon=0
    [PauseMapContract]::PlayerX=2944;[PauseMapContract]::PlayerY=1664
    [PauseMapContract]::pending_shot=$pending
    $fresh=[int]($mode -eq 1);$key=if($mode -eq 0){0}else{16}
    if($mode -eq 2){[PauseMapContract]::keys=16;[PauseMapContract]::previous_keys=16}
    [PauseMapContract]::Script=@($key,$key,0,0)
    [PauseMapContract]::FreezeMainStep()
    Require ([PauseMapContract]::ShotCalls -eq $pending -and [PauseMapContract]::pending_shot -eq $fresh) 'Acquisition preserves accepted pending shot and fresh-edge queue timing'
    Require ([PauseMapContract]::owned_weapons -eq 3 -and [PauseMapContract]::selected_weapon -eq 1 -and [PauseMapContract]::weapon_state -eq $fresh) 'Main acquisition equips with clean or newly requested pose'
    [PauseMapContract]::FreezeMainStep();[PauseMapContract]::FreezeMainStep()
    Require ([PauseMapContract]::ShotCalls -eq $pending+$fresh -and [PauseMapContract]::pending_shot -eq 0 -and [PauseMapContract]::weapon_state -eq 0) 'Held fire cannot duplicate a shot or retain stale pose after acquisition'
}}
[PauseMapContract]::owned_weapons=1;[PauseMapContract]::selected_weapon=0
Write-Output '- first acquisition equips shotgun; actual post-pickup/manual-pistol carousels; already-owned repeat; production main/input traces preserve pending shots and reject held autofire'
Write-Output '- shotgun: current authoritative 16x16 source, binary alpha and exact palette/conversion pixels; all scroll parities; circular LEFT/RIGHT edges, hold rejection, persistence and idle no-write traces'
Write-Output 'Pause map validation PASS'
Write-Output '- production geometry/marker code executed with mock VDP; authoritative 13x13 map'
Write-Output '- 12 synthetic extents including 1x1 and 128x128; nine edge/center positions; exact small-map centering'
Write-Output '- native 16x16 pistol at (72,112), all 63 opaque pixels; alpha preserves outline/background, empty side slots; four scroll parities'
Write-Output '- continuous computer wall and room-side blue protrusion in all four mount orientations'
Write-Output '- held START/release/fresh edge; static pause display; simulation/restore source contracts'
Write-Output '- WorldSprite 9 bytes; unchanged palette; full VRAM/cache restoration; Bank 2, zero static RAM/helpers'
Write-Output "- host preview: $build/pause-map-preview.png (hardware behavior still needs Emulicious)"
Test-LongPauseFreeze
if($RequireMapPlacement){. "$PSScriptRoot/pause_freeze_audit.ps1";Test-PauseFreezeAssembly}

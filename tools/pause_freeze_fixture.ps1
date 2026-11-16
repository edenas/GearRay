# Development-only extension of the production-C pause host adapter.
function Get-FreezeBody([string]$text,[string]$pattern) {
    $text=[regex]::Replace($text,'(?s)/\*.*?\*/','')
    $m=[regex]::Match($text,$pattern+'\s*\{')
    if(!$m.Success){throw "Freeze fixture cannot find $pattern"}
    $start=$m.Index+$m.Length;$depth=1;$end=$start
    while($depth -gt 0 -and $end -lt $text.Length){if($text[$end] -eq '{'){$depth++};if($text[$end] -eq '}'){$depth--};$end++}
    if($depth){throw 'Unbalanced production body'}
    return $text.Substring($start,$end-$start-1)
}
$freezeMain=[regex]::Replace($main,'(?s)#ifdef GEARRAY_PROFILE_RENDERER.*?#endif','')
$freezeStep=Get-FreezeBody $freezeMain 'while\s*\(!player_is_dead\(\)\)'
$freezeStep=$freezeStep.Replace('continue;','return;').Replace('break;','return;').Replace('shoot_requested = input_shoot_requested();','shoot_requested = input_shoot_requested() ? 1 : 0;').Replace('if (pending_shot)','if (pending_shot != 0)')
$freezeSprite=Get-FreezeBody (Get-Content "$root/game/world_sprite.c" -Raw) 'void world_sprites_update\(void\)'
$freezeSprite=$freezeSprite.Replace('&world_sprites[','Corpses[').Replace('world_sprite_count','Corpses.Length')
$freezeWeapon=Get-FreezeBody (Get-Content "$root/platform/game_gear/hud_weapon.c" -Raw) 'void game_gear_hud_weapon_update\(unsigned char shoot_requested\)'
$touchLiteral=[string](128+2*[int][regex]::Match((Get-Content "$root/game/player.h" -Raw),'#define PLAYER_MOVE_SPEED\s+(\d+)').Groups[1].Value)+'U'
$freezeWeapon=$freezeWeapon.Replace('(unsigned int)','(ushort)').Replace('SHOTGUN_PICKUP_TOUCH_EXTENT',$touchLiteral)
$freezeWeapon=$freezeWeapon.Replace('if (shoot_requested)','if (shoot_requested != 0)')
$freezeWeapon=$freezeWeapon.Replace('SHOTGUN_PICKUP_PRESENT','(owned_weapons & WEAPON_OWNED_SHOTGUN) == 0')
$freezeWeapon=$freezeWeapon.Replace('player_get_position_x()','PlayerX').Replace('player_get_position_y()','PlayerY')
$freezeSwitch=Get-FreezeBody (Get-Content "$root/game/red_door_switch.c" -Raw) 'void red_door_switch_update\(void\)'
$freezeProduction=@"
static void FreezeMainStep(void) {
    signed char forward_direction, strafe_direction, rotation_direction;
    unsigned char shoot_requested;
    $freezeStep
}
static void world_sprites_update(void) { GameplayCall("world_sprites_update"); $freezeSprite }
static void game_gear_hud_weapon_update(unsigned char shoot_requested) { GameplayCall("weapon_update"); $freezeWeapon }
static void red_door_switch_update(void) { GameplayCall("switch_update"); $freezeSwitch }
"@
$freezeMock=@'
public const int ZOMBIE_AI_UPDATE_INTERVAL=4, HUD_WEAPON_SHOOT_FRAME_COUNT=2, RED_DOOR_SWITCH_FRAME_INTERVAL=6;
public const int IDLE=0,SHOOT=1,ZOMBIE_STATE_ALIVE=0,ZOMBIE_STATE_SHOT_DEAD=1,zombie_01_standing_pixels=0x9000;
public static int pending_shot,zombie_ai_frame_counter,weapon_state,animation_timer;
public static int PendingSeed=1;
public static int red_door_switch_frame_counter,red_door_switch_frame;
public static int PlayerHealth,CameraX,CameraY,PlaneX,PlaneY,DamagePhase,SwitchState,FollowingMask,NegativeMask;
public static int RestoreCount,GameplayCalls,Raycasts,RenderCalls,MoveCalls,TurnCalls,ShotCalls,InteractionCalls;
public static string GameplayTrace="";
public static bool FreezeGuard;
public static byte[] FrozenState;
public static int[] WriteFrames=new int[40016];
public static byte[] GameplayBytes(){
 var b=new System.Collections.Generic.List<byte>();
 foreach(int v in new int[]{PlayerX,PlayerY,CameraX,CameraY,DirectionX,DirectionY,PlaneX,PlaneY}){b.Add((byte)v);b.Add((byte)(v>>8));}
 foreach(int v in new int[]{PlayerHealth,DamagePhase,pending_shot,zombie_ai_frame_counter,weapon_state,animation_timer,SwitchState,red_door_switch_frame_counter,red_door_switch_frame,FollowingMask,NegativeMask,Corpses.Length,owned_weapons,shotgun_cell_x,shotgun_cell_y})b.Add((byte)v);
 foreach(int v in door_states)b.Add((byte)v);
 foreach(WorldSprite s in Corpses){foreach(int v in new int[]{s.world_x,s.world_y}){b.Add((byte)v);b.Add((byte)(v>>8));}b.Add((byte)s.visual_type);b.Add((byte)s.animation_token);b.Add((byte)s.state);b.Add((byte)s.health_and_hit_count);b.Add((byte)s.state_timer);}
 return b.ToArray();
}
public static void AssertFrozen(){if(!FreezeGuard)return;byte[] now=GameplayBytes();if(now.Length!=FrozenState.Length)throw new Exception("Frozen entity count changed");for(int i=0;i<now.Length;i++)if(now[i]!=FrozenState[i])throw new Exception("Gameplay mutation during pause at byte "+i+", VBlank "+Frame);}
public static void GameplayCall(string name){if(FreezeGuard)throw new Exception("Gameplay reachable during pause: "+name);GameplayCalls++;GameplayTrace+=name+",";}
public static bool player_is_dead(){return PlayerHealth==0;}
public static void player_move_combined(int forward,int strafe){GameplayCall("move");MoveCalls++;}
public static void camera_rotate_left(){GameplayCall("turn_left");TurnCalls++;}
public static void camera_rotate_right(){GameplayCall("turn_right");TurnCalls++;}
public static void camera_set_fixed_position(int x,int y){GameplayCall("camera_set");CameraX=x;CameraY=y;}
public static void zombie_ai_update_all(){GameplayCall("AI");}
public static void player_process_interaction(){GameplayCall("interaction_poll");if(input_interaction_requested())InteractionCalls++;}
public static void raycaster_update(){GameplayCall("raycaster");Raycasts++;}
public static void zombie_shooting_process(){GameplayCall("pending_shot");ShotCalls++;}
public static bool zombie_corpses_finalize(int i){GameplayCall("corpse_finalize");throw new Exception("Unexpected death completion in next-step fixture");}
public static void game_gear_damage_shake_update(){GameplayCall("shake");if(DamagePhase!=0)DamagePhase--;}
public static void game_gear_video_draw_wall_columns(){GameplayCall("renderer");RenderCalls++;}
public static void game_gear_video_restore_gameplay(){AssertFrozen();FreezeGuard=false;RestoreCount++;}
public static void SeedFreeze(){
 WORLD_WIDTH=WORLD_HEIGHT=32;Map=new int[1024];Map[4*32+6]=5;Map[2*32+6]=6;Map[8*32+6]=5;
 DoorX=new int[]{6,6,6};DoorY=new int[]{4,2,8};door_states=new int[]{0,1,0};
 PlayerX=CameraX=128;PlayerY=CameraY=128;DirectionX=0;DirectionY=-256;PlaneX=169;PlaneY=0;PlayerHealth=73;DamagePhase=3;
 pending_shot=PendingSeed;zombie_ai_frame_counter=3;weapon_state=SHOOT;animation_timer=2;SwitchState=1;red_door_switch_frame_counter=5;red_door_switch_frame=1;FollowingMask=0x6a;NegativeMask=0x24;
 Corpses=new WorldSprite[8];
 int[] states={0,0,128,64,20,0,1,2};int[] timers={0,0,0,4,0,3,4,17};
 for(int i=0;i<8;i++){Corpses[i]=new WorldSprite(384+i*256,640,states[i]);Corpses[i].visual_type=i&1;Corpses[i].animation_token=i%7;Corpses[i].health_and_hit_count=i==7?0:(i==0?12:0x89);Corpses[i].state_timer=timers[i];}
 Frame=Writes=Queries=TileWrites=RestoreCount=GameplayCalls=Raycasts=RenderCalls=MoveCalls=TurnCalls=ShotCalls=InteractionCalls=CloneCount=MaxClone=0;GameplayTrace="";
 game_gear_input_initialize();InitialBlocked=0;TraceDoors=TraceCorpses=false;
 foreach(int[] a in new int[][]{WriteFrames,QueryFrames,DoorFrames,DoorFindFrames,ScanFrames,EntityFrames,CorpseWrites,SatFrames,TileFrames})Array.Clear(a,0,a.Length);
}
public static void RunFreeze(int frames,int mode,int held){
 SeedFreeze();int exitHeld=mode==7?0:held;Script=new int[frames+8];Script[0]=GG_KEY_START|held;Script[frames]=GG_KEY_START|exitHeld;
 if(mode==1)Script[3]=1;
 if(mode>=2&&mode<=4){Script[2]=1;Script[3]=16;}
 if(mode==3)for(int f=4;f<frames;f++)Script[f]=8;
 if(mode==4)for(int f=4;f<frames;f++)Script[f]=4;
 if(mode==5){Script[3]=2;Script[4]=16;Script[5]=0;Script[6]=16;}
 if(mode==6){for(int f=0;f<frames;f++)Script[f]|=held;Script[1]&=~GG_KEY_START;}
 if(mode==8){Script[3]=2;Script[4]=16;Script[5]=32;Script[6]=4;Script[7]=8;}
 FrozenState=GameplayBytes();FreezeGuard=true;FreezeMainStep();
 if(FreezeGuard||RestoreCount!=1||Frame!=frames)throw new Exception("Pause did not restore/exit exactly once");
 byte[] after=GameplayBytes();for(int i=0;i<after.Length;i++)if(after[i]!=FrozenState[i])throw new Exception("Freeze drift after return");
 if(GameplayCalls!=0)throw new Exception("Main advanced simulation on pause/resume iteration");
 for(int f=2;f<frames;f++){
  bool pan=mode==3&&f>=4&&(f==4||f>=16&&(f-16)%4==0)&&f<=80;
  bool focus=(mode==1&&f==3)||(mode>=2&&mode<=4&&(f==2||f==3));
  if(!pan){if(QueryFrames[f]+DoorFrames[f]+DoorFindFrames[f]+ScanFrames[f]+EntityFrames[f]+CorpseWrites[f]+SatFrames[f]!=0)throw new Exception("Non-pan frame queried or rendered world: "+f);}
  if(!pan&&!focus&&WriteFrames[f]!=0)throw new Exception("Idle/delay/rejected frame wrote VRAM: "+f);
 }
 // Execute the mechanically extracted next main iteration. Gameplay-heavy
 // subsystems are call spies; sprite/weapon/switch countdown bodies are real C.
 Script[frames]=exitHeld;FreezeMainStep();
 if(RestoreCount!=1||MoveCalls!=0||TurnCalls!=0||InteractionCalls!=0||ShotCalls!=PendingSeed)throw new Exception("Input carryover or pending-shot error");
}
'@
function Test-LongPauseFreeze {
    foreach($mode in 0..5){[PauseMapContract]::RunFreeze(3600,$mode,0)}
    [PauseMapContract]::RunFreeze(36000,0,0)
    $long=[Convert]::ToBase64String([PauseMapContract]::GameplayBytes());$trace=[PauseMapContract]::GameplayTrace
    [PauseMapContract]::RunFreeze(8,0,0)
    Require ([Convert]::ToBase64String([PauseMapContract]::GameplayBytes()) -eq $long -and [PauseMapContract]::GameplayTrace -eq $trace) 'Long pause changed the next production main-step result/call trace'
    foreach($held in @(16,32,1,4,8,63)){foreach($mode in @(0,6,7,8)){[PauseMapContract]::RunFreeze(3600,$mode,$held)}}
    [PauseMapContract]::PendingSeed=0;[PauseMapContract]::RunFreeze(3600,8,63);[PauseMapContract]::PendingSeed=1
    # Repeated actual blocking calls on the same gameplay state (no reseeding).
    [PauseMapContract]::SeedFreeze();$frozen=[Convert]::ToBase64String([PauseMapContract]::GameplayBytes())
    for($cycle=0;$cycle -lt 100;$cycle++){
        [PauseMapContract]::Frame=0;[PauseMapContract]::Script=@(0x8000,0,0,0,0,0,0,0x8000)
        [PauseMapContract]::keys=0;[PauseMapContract]::previous_keys=0
        [PauseMapContract]::FrozenState=[PauseMapContract]::GameplayBytes();[PauseMapContract]::FreezeGuard=$true
        [PauseMapContract]::FreezeMainStep()
        Require ([Convert]::ToBase64String([PauseMapContract]::GameplayBytes()) -eq $frozen) 'Repeated pause caused gameplay drift'
    }
    Require ([PauseMapContract]::RestoreCount -eq 100 -and [PauseMapContract]::GameplayCalls -eq 0) 'Repeated restore count or gameplay freeze failed'
    [PauseMapContract]::SetEntities(@());[PauseMapContract]::door_states=@(0,0,0)
    Write-Output '- freeze: six 3600-VBlank UI modes, 36000-VBlank next-step equivalence, B1/B2/direction entry/exit holds, 100 cycles; all authoritative fixture bytes unchanged'
}

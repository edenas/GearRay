cmake_minimum_required(VERSION 3.20)

# SDCC is driven explicitly below, so CMake does not need a host compiler.
project(gear_ray VERSION 0.1.0 LANGUAGES NONE)

option(GEARRAY_PROFILE_RENDERER "Collect renderer profiling counters" OFF)
if(GEARRAY_PROFILE_RENDERER)
    set(GEAR_RAY_RENDERER_PROFILE_DEFINE -DGEARRAY_PROFILE_RENDERER)
    set(GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION --opt-code-size)
else()
    set(GEAR_RAY_RENDERER_PROFILE_DEFINE)
    set(GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION)
endif()

set(GEAR_RAY_BUILD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Generated build output directory")
set(GEAR_RAY_ROM_FILENAME "GearRay.gg" CACHE STRING "Packaged Game Gear ROM filename")
set(GEAR_RAY_DEVKITSMS_ROOT "D:/Tools/devkitSMS" CACHE PATH "Path to the local devkitSMS installation")
set(GEAR_RAY_MAKESMS_EXECUTABLE "${GEAR_RAY_DEVKITSMS_ROOT}/makesms/Windows/makesms.exe" CACHE FILEPATH "Path to makesms.exe")

find_program(GEAR_RAY_SDCC_EXECUTABLE NAMES sdcc DOC "Path to SDCC executable")
if(NOT GEAR_RAY_SDCC_EXECUTABLE)
    message(FATAL_ERROR "SDCC was not found on PATH.")
endif()

find_program(GEAR_RAY_POWERSHELL_EXECUTABLE NAMES powershell DOC "Path to Windows PowerShell")
if(NOT GEAR_RAY_POWERSHELL_EXECUTABLE)
    message(FATAL_ERROR "Windows PowerShell was not found on PATH.")
endif()

set(GEAR_RAY_SMSLIB_INCLUDE "${GEAR_RAY_DEVKITSMS_ROOT}/SMSlib/src")
set(GEAR_RAY_SMSLIB_LIBRARY "${GEAR_RAY_DEVKITSMS_ROOT}/SMSlib/SMSlib_GG.lib")
set(GEAR_RAY_CRT0 "${GEAR_RAY_DEVKITSMS_ROOT}/crt0/crt0_sms.rel")
set(GEAR_RAY_GAME_GEAR_PLATFORM_DIR "${CMAKE_SOURCE_DIR}/platform/game_gear")
set(GEAR_RAY_GAME_DIR "${CMAKE_SOURCE_DIR}/game")
set(GEAR_RAY_RENDER_DIR "${CMAKE_SOURCE_DIR}/engine/render")
set(GEAR_RAY_MAIN_SOURCE "${GEAR_RAY_GAME_DIR}/main.c")
set(GEAR_RAY_MAIN_OBJECT "${CMAKE_BINARY_DIR}/main.rel")
set(GEAR_RAY_CAMERA_SOURCE "${GEAR_RAY_GAME_DIR}/camera.c")
set(GEAR_RAY_CAMERA_HEADER "${GEAR_RAY_GAME_DIR}/camera.h")
set(GEAR_RAY_CAMERA_OBJECT "${CMAKE_BINARY_DIR}/camera.rel")
set(GEAR_RAY_RAYCASTER_SOURCE "${GEAR_RAY_RENDER_DIR}/raycaster.c")
set(GEAR_RAY_RAYCASTER_HEADER "${GEAR_RAY_RENDER_DIR}/raycaster.h")
set(GEAR_RAY_RAYCASTER_OBJECT "${CMAKE_BINARY_DIR}/raycaster.rel")
set(GEAR_RAY_WALL_SIDE_HEADER "${GEAR_RAY_RENDER_DIR}/wall_side.h")
set(GEAR_RAY_PLAYER_SOURCE "${GEAR_RAY_GAME_DIR}/player.c")
set(GEAR_RAY_PLAYER_HEADER "${GEAR_RAY_GAME_DIR}/player.h")
set(GEAR_RAY_PLAYER_OBJECT "${CMAKE_BINARY_DIR}/player.rel")
set(GEAR_RAY_RED_DOOR_SWITCH_SOURCE "${GEAR_RAY_GAME_DIR}/red_door_switch.c")
set(GEAR_RAY_RED_DOOR_SWITCH_HEADER "${GEAR_RAY_GAME_DIR}/red_door_switch.h")
set(GEAR_RAY_RED_DOOR_SWITCH_OBJECT "${CMAKE_BINARY_DIR}/red_door_switch.rel")
set(GEAR_RAY_INTERACTION_RAY_SOURCE "${GEAR_RAY_GAME_DIR}/interaction_ray.c")
set(GEAR_RAY_INTERACTION_RAY_HEADER "${GEAR_RAY_GAME_DIR}/interaction_ray.h")
set(GEAR_RAY_INTERACTION_RAY_OBJECT "${CMAKE_BINARY_DIR}/interaction_ray.rel")
set(GEAR_RAY_INTERACTION_TARGET_HEADER "${GEAR_RAY_GAME_DIR}/interaction_target.h")
set(GEAR_RAY_WORLD_INTERACTIONS_SOURCE "${GEAR_RAY_GAME_DIR}/world_interactions.c")
set(GEAR_RAY_WORLD_INTERACTIONS_HEADER "${GEAR_RAY_GAME_DIR}/world_interactions.h")
set(GEAR_RAY_WORLD_INTERACTIONS_OBJECT "${CMAKE_BINARY_DIR}/world_interactions.rel")
set(GEAR_RAY_WORLD_SOURCE "${GEAR_RAY_GAME_DIR}/world.c")
set(GEAR_RAY_WORLD_HEADER "${GEAR_RAY_GAME_DIR}/world.h")
set(GEAR_RAY_WORLD_OBJECT_HEADER "${GEAR_RAY_GAME_DIR}/world_object.h")
set(GEAR_RAY_WORLD_OBJECT "${CMAKE_BINARY_DIR}/world.rel")
set(GEAR_RAY_WORLD_INITIALIZATION_SOURCE "${GEAR_RAY_GAME_DIR}/world_initialization.c")
set(GEAR_RAY_WORLD_INITIALIZATION_OBJECT "${CMAKE_BINARY_DIR}/world_initialization.rel")
set(GEAR_RAY_WORKSHOP_MAP_SOURCE "${GEAR_RAY_GAME_DIR}/workshop_map.c")
set(GEAR_RAY_WORKSHOP_MAP_HEADER "${GEAR_RAY_GAME_DIR}/workshop_map.h")
set(GEAR_RAY_WORKSHOP_MAP_OBJECT "${CMAKE_BINARY_DIR}/workshop_map.rel")
set(GEAR_RAY_WORKSHOP_LAYOUT "${GEAR_RAY_GAME_DIR}/workshop_map.layout")
set(GEAR_RAY_WORKSHOP_MAP_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_workshop_map.ps1")
set(GEAR_RAY_WORLD_OBJECTS_SOURCE "${GEAR_RAY_GAME_DIR}/world_objects.c")
set(GEAR_RAY_WORLD_OBJECTS_HEADER "${GEAR_RAY_GAME_DIR}/world_objects.h")
set(GEAR_RAY_WORLD_OBJECTS_OBJECT "${CMAKE_BINARY_DIR}/world_objects.rel")
set(GEAR_RAY_WORLD_SPRITE_SOURCE "${GEAR_RAY_GAME_DIR}/world_sprite.c")
set(GEAR_RAY_WORLD_SPRITE_HEADER "${GEAR_RAY_GAME_DIR}/world_sprite.h")
set(GEAR_RAY_WORLD_SPRITE_OBJECT "${CMAKE_BINARY_DIR}/world_sprite.rel")
set(GEAR_RAY_ZOMBIE_SHOOTING_SOURCE "${GEAR_RAY_GAME_DIR}/zombie_shooting.c")
set(GEAR_RAY_ZOMBIE_SHOOTING_HEADER "${GEAR_RAY_GAME_DIR}/zombie_shooting.h")
set(GEAR_RAY_ZOMBIE_SHOOTING_OBJECT "${CMAKE_BINARY_DIR}/zombie_shooting.rel")
set(GEAR_RAY_ZOMBIE_AI_SOURCE "${GEAR_RAY_GAME_DIR}/zombie_ai.c")
set(GEAR_RAY_ZOMBIE_AI_HEADER "${GEAR_RAY_GAME_DIR}/zombie_ai.h")
set(GEAR_RAY_ZOMBIE_AI_OBJECT "${CMAKE_BINARY_DIR}/zombie_ai.rel")
set(GEAR_RAY_ZOMBIE_CORPSES_SOURCE "${GEAR_RAY_GAME_DIR}/zombie_corpses.c")
set(GEAR_RAY_ZOMBIE_CORPSES_HEADER "${GEAR_RAY_GAME_DIR}/zombie_corpses.h")
set(GEAR_RAY_ZOMBIE_CORPSES_OBJECT "${CMAKE_BINARY_DIR}/zombie_corpses.rel")
set(GEAR_RAY_ENEMY_COLLISION_SOURCE "${GEAR_RAY_GAME_DIR}/enemy_collision.c")
set(GEAR_RAY_ENEMY_COLLISION_HEADER "${GEAR_RAY_GAME_DIR}/enemy_collision.h")
set(GEAR_RAY_ENEMY_COLLISION_OBJECT "${CMAKE_BINARY_DIR}/enemy_collision.rel")
set(GEAR_RAY_DOOR_STATES_SOURCE "${GEAR_RAY_GAME_DIR}/door_states.c")
set(GEAR_RAY_DOOR_STATES_HEADER "${GEAR_RAY_GAME_DIR}/door_states.h")
set(GEAR_RAY_DOOR_STATES_OBJECT "${CMAKE_BINARY_DIR}/door_states.rel")
set(GEAR_RAY_DOOR_INSTANCES_SOURCE "${GEAR_RAY_GAME_DIR}/door_instances.c")
set(GEAR_RAY_DOOR_INSTANCES_HEADER "${GEAR_RAY_GAME_DIR}/door_instances.h")
set(GEAR_RAY_DOOR_INSTANCES_OBJECT "${CMAKE_BINARY_DIR}/door_instances.rel")
set(GEAR_RAY_INPUT_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input.c")
set(GEAR_RAY_INPUT_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input.h")
set(GEAR_RAY_INPUT_OBJECT "${CMAKE_BINARY_DIR}/input.rel")
set(GEAR_RAY_STARTUP_LOGO_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/startup_logo.c")
set(GEAR_RAY_STARTUP_LOGO_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/startup_logo.h")
set(GEAR_RAY_STARTUP_LOGO_OBJECT "${CMAKE_BINARY_DIR}/startup_logo.rel")
set(GEAR_RAY_NEAR_ZOMBIE_TEXTURES_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/near_zombie_textures.c")
set(GEAR_RAY_NEAR_ZOMBIE_TEXTURES_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/near_zombie_textures.h")
set(GEAR_RAY_NEAR_ZOMBIE_TEXTURES_OBJECT "${CMAKE_BINARY_DIR}/near_zombie_textures.rel")
set(GEAR_RAY_ZOMBIE_VISUALS_OBJECT "${CMAKE_BINARY_DIR}/zombie_visuals_assets.rel")
set(GEAR_RAY_ZOMBIE_ASSET_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_zombie_assets.ps1")
set(GEAR_RAY_VIDEO_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.c")
set(GEAR_RAY_VIDEO_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.h")
set(GEAR_RAY_VIDEO_OBJECT "${CMAKE_BINARY_DIR}/video.rel")
set(GEAR_RAY_VIDEO_INTERNAL_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video_internal.h")
set(GEAR_RAY_VIDEO_INITIALIZATION_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video_initialization.c")
set(GEAR_RAY_VIDEO_INITIALIZATION_OBJECT "${CMAKE_BINARY_DIR}/video_initialization.rel")
set(GEAR_RAY_GAME_OVER_PRESENTATION_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/game_over_presentation.c")
set(GEAR_RAY_GAME_OVER_PRESENTATION_OBJECT "${CMAKE_BINARY_DIR}/game_over_presentation.rel")
set(GEAR_RAY_HUD_WEAPON_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/hud_weapon.c")
set(GEAR_RAY_HUD_WEAPON_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/hud_weapon.h")
set(GEAR_RAY_HUD_WEAPON_OBJECT "${CMAKE_BINARY_DIR}/hud_weapon.rel")
set(GEAR_RAY_SPRITE_PROJECTION_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/sprite_projection.c")
set(GEAR_RAY_SPRITE_PROJECTION_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/sprite_projection.h")
set(GEAR_RAY_SPRITE_PROJECTION_OBJECT "${CMAKE_BINARY_DIR}/sprite_projection.rel")
set(GEAR_RAY_RENDERER_PROFILE_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/renderer_profile.c")
set(GEAR_RAY_RENDERER_PROFILE_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/renderer_profile.h")
set(GEAR_RAY_RENDERER_PROFILE_OBJECT "${CMAKE_BINARY_DIR}/renderer_profile.rel")
if(GEARRAY_PROFILE_RENDERER)
    set(GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT
        "${GEAR_RAY_RENDERER_PROFILE_OBJECT}")
else()
    set(GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT)
endif()
set(GEAR_RAY_WALL_TEXTURES_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/wall_textures.c")
set(GEAR_RAY_WALL_TEXTURES_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/wall_textures.h")
set(GEAR_RAY_WALL_TEXTURES_OBJECT "${CMAKE_BINARY_DIR}/wall_textures.rel")
set(GEAR_RAY_WALL_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/wall_concrete.png")
set(GEAR_RAY_BLOOD_WALL_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/wall_concrete_blood.png")
set(GEAR_RAY_DOOR_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/wall_door.png")
set(GEAR_RAY_RED_DOOR_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/wall_door_red.png")
set(GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_1_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/switch_off_01.png")
set(GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_2_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/switch_off_02.png")
set(GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_1_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/switch_on_01.png")
set(GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_2_INPUT "${CMAKE_SOURCE_DIR}/assets/textures/walls/switch_on_02.png")
set(GEAR_RAY_WALL_TEXTURE_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_wall_texture.ps1")
set(GEAR_RAY_WORKSHOP_MAP_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_workshop_map.ps1")
set(GEAR_RAY_ZOMBIE_SHOOTING_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_zombie_shooting.ps1")
set(GEAR_RAY_SHOTGUN_COMBAT_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_shotgun_combat.ps1")
set(GEAR_RAY_ZOMBIE_AI_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_zombie_ai.ps1")
set(GEAR_RAY_ZOMBIE_ATTACK_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_zombie_attack.ps1")
set(GEAR_RAY_CORPSE_PERSISTENCE_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_corpse_persistence.ps1")
set(GEAR_RAY_HEALTH_HUD_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_health_hud.ps1")
set(GEAR_RAY_BANK_LAYOUT_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_bank_layout.ps1")
set(GEAR_RAY_NEAR_ZOMBIE_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_near_zombie.ps1")
set(GEAR_RAY_MIDDLE_ZOMBIE_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_middle_zombie.ps1")
set(GEAR_RAY_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
set(GEAR_RAY_ZOMBIE_ASSET_STAMP "${GEAR_RAY_GENERATED_DIR}/zombie_assets.stamp")
# Declare every generator-owned output. Missing generated files must invalidate
# the stamp too; a stamp alone cannot describe the build's actual inputs.
set(GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS)
foreach(zombie_type IN ITEMS security scientist)
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 shot_01 shot_02 shot_dead corps)
        foreach(extension IN ITEMS c h)
            list(APPEND GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS
                "${GEAR_RAY_GENERATED_DIR}/zombie_${zombie_type}_${zombie_pose}_8x8.${extension}")
        endforeach()
    endforeach()
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 shot_01 shot_dead corps)
        foreach(extension IN ITEMS c h)
            list(APPEND GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS
                "${GEAR_RAY_GENERATED_DIR}/zombie_${zombie_type}_${zombie_pose}_16x16.${extension}")
        endforeach()
    endforeach()
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 standing_attack attack_01 attack_02 shot_01 corps)
        foreach(extension IN ITEMS c h)
            list(APPEND GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS
                "${GEAR_RAY_GENERATED_DIR}/zombie_near_${zombie_type}_${zombie_pose}_32x32.${extension}")
        endforeach()
    endforeach()
endforeach()
list(APPEND GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS
    "${GEAR_RAY_GENERATED_DIR}/zombie_visuals_assets.c"
    "${GEAR_RAY_GENERATED_DIR}/near_zombie_assets.c"
    "${GEAR_RAY_GENERATED_DIR}/zombie_asset_manifest.json")
set(GEAR_RAY_ZOMBIE_ASSET_INPUTS)
foreach(zombie_species IN ITEMS 01 02)
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 shot_01 shot_02 shot_dead corps)
        list(APPEND GEAR_RAY_ZOMBIE_ASSET_INPUTS
            "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_${zombie_species}_${zombie_pose}.png")
    endforeach()
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 shot_01 shot_dead corps)
        list(APPEND GEAR_RAY_ZOMBIE_ASSET_INPUTS
            "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_${zombie_species}_${zombie_pose}_16x16.png")
    endforeach()
    foreach(zombie_pose IN ITEMS standing walking_01 walking_02 standing_attack attack_01 attack_02 shot_01 corps)
        list(APPEND GEAR_RAY_ZOMBIE_ASSET_INPUTS
            "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_${zombie_species}_${zombie_pose}_32x32.png")
    endforeach()
endforeach()
list(APPEND GEAR_RAY_ZOMBIE_ASSET_INPUTS
    "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/shotgun_held.png"
    "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/shotgun_held_shoot.png")
set(GEAR_RAY_ZOMBIE_ASSET_HASHES)
foreach(zombie_asset IN LISTS GEAR_RAY_ZOMBIE_ASSET_INPUTS)
    file(SHA256 "${zombie_asset}" zombie_asset_hash)
    list(APPEND GEAR_RAY_ZOMBIE_ASSET_HASHES "${zombie_asset_hash}")
endforeach()
string(SHA256 GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT "${GEAR_RAY_ZOMBIE_ASSET_HASHES}")
set(GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT_FILE "${CMAKE_BINARY_DIR}/zombie_asset_inputs.sha256")
file(CONFIGURE OUTPUT "${GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT_FILE}"
     CONTENT "${GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT}\n" @ONLY)
set(GEAR_RAY_HEALTH_HUD_ICON_INPUT "${CMAKE_SOURCE_DIR}/assets/ui/health_hud.png")
set(GEAR_RAY_HEALTH_HUD_BAR_INPUT "${CMAKE_SOURCE_DIR}/assets/ui/health_hud_1.png")
set(GEAR_RAY_HEALTH_HUD_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_health_hud.ps1")
set(GEAR_RAY_GENERATED_HEALTH_HUD_HEADER "${GEAR_RAY_GENERATED_DIR}/health_hud_tiles.h")
set(GEAR_RAY_SEGA_LOGO_INPUT "${CMAKE_SOURCE_DIR}/assets/logos/sega_logo.png")
set(GEAR_RAY_STARTUP_LOGO_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_startup_logo.ps1")
set(GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE "${GEAR_RAY_GENERATED_DIR}/sega_logo.c")
set(GEAR_RAY_GENERATED_SEGA_LOGO_HEADER "${GEAR_RAY_GENERATED_DIR}/sega_logo.h")
set(GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT "${CMAKE_BINARY_DIR}/generated_sega_logo.rel")
set(GEAR_RAY_GAME_OVER_INPUT "${CMAKE_SOURCE_DIR}/assets/logos/game_over.png")
set(GEAR_RAY_GAME_OVER_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_game_over.ps1")
set(GEAR_RAY_GENERATED_GAME_OVER_SOURCE "${GEAR_RAY_GENERATED_DIR}/game_over.c")
set(GEAR_RAY_GENERATED_GAME_OVER_HEADER "${GEAR_RAY_GENERATED_DIR}/game_over.h")
set(GEAR_RAY_GENERATED_GAME_OVER_OBJECT "${CMAKE_BINARY_DIR}/generated_game_over.rel")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/wall_texture.c")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/wall_texture.h")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_wall_texture.rel")
set(GEAR_RAY_SPRITE_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_standing.png")
set(GEAR_RAY_SPRITE_TEXTURE_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_sprite_texture.ps1")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/sprite_texture.c")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/sprite_texture.h")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_sprite_texture.rel")
set(GEAR_RAY_NEAR_ZOMBIE_WALKING_01_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_walking_01_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_WALKING_02_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_walking_02_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_STANDING_ATTACK_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_standing_attack_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_ATTACK_01_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_attack_01_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_ATTACK_02_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_attack_02_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_SHOT_01_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_shot_01_32x32.png")
set(GEAR_RAY_NEAR_ZOMBIE_CORPSE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_corps_32x32.png")
foreach(near_pose IN ITEMS WALKING_01 WALKING_02 STANDING_ATTACK ATTACK_01 ATTACK_02 SHOT_01 CORPSE)
    string(TOLOWER "${near_pose}" near_pose_lower)
    set(GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_${near_pose_lower}_32x32_texture.c")
    set(GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_${near_pose_lower}_32x32_texture.h")
    set(GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_${near_pose_lower}_32x32_texture.rel")
endforeach()
foreach(middle_pose IN ITEMS STANDING WALKING_01 WALKING_02 SHOT_01 SHOT_DEAD CORPS)
    string(TOLOWER "${middle_pose}" middle_pose_lower)
    set(GEAR_RAY_MIDDLE_ZOMBIE_${middle_pose}_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_${middle_pose_lower}_16x16.png")
    set(GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_${middle_pose_lower}_16x16_texture.c")
    set(GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_${middle_pose_lower}_16x16_texture.h")
    set(GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_${middle_pose_lower}_16x16_texture.rel")
endforeach()
set(GEAR_RAY_ZOMBIE_WALKING_01_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_walking_01.png")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_01_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_walking_01_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_01_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_walking_01_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_01_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_walking_01_texture.rel")
set(GEAR_RAY_ZOMBIE_WALKING_02_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_walking_02.png")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_02_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_walking_02_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_02_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_walking_02_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_WALKING_02_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_walking_02_texture.rel")
set(GEAR_RAY_ZOMBIE_SHOT_01_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_shot_01.png")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_01_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_01_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_shot_01_texture.rel")
set(GEAR_RAY_ZOMBIE_SHOT_02_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_shot_02.png")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_02_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_02_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_shot_02_texture.rel")
set(GEAR_RAY_ZOMBIE_SHOT_DEAD_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_shot_dead.png")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_dead_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_shot_dead_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_shot_dead_texture.rel")
set(GEAR_RAY_ZOMBIE_CORPS_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_corps.png")
set(GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/zombie_01_corps_texture.c")
set(GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/zombie_01_corps_texture.h")
set(GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_zombie_01_corps_texture.rel")
set(GEAR_RAY_WEAPON_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/gun_12x12.png")
set(GEAR_RAY_GENERATED_WEAPON_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/weapon_texture.c")
set(GEAR_RAY_GENERATED_WEAPON_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/weapon_texture.h")
set(GEAR_RAY_WEAPON_SHOOT_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/gun_shoot_12x12.png")
set(GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.c")
set(GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.h")

# build.bat configures before building. Detect asset replacements that preserve
# an older mtime too; file(CONFIGURE) updates each dependency only on content change.
foreach(weapon_pose IN ITEMS WEAPON WEAPON_SHOOT)
    file(SHA256 "${GEAR_RAY_${weapon_pose}_TEXTURE_INPUT}" weapon_input_sha256)
    set(GEAR_RAY_${weapon_pose}_TEXTURE_FINGERPRINT
        "${GEAR_RAY_GENERATED_DIR}/${weapon_pose}_input.sha256")
    file(CONFIGURE
        OUTPUT "${GEAR_RAY_${weapon_pose}_TEXTURE_FINGERPRINT}"
        CONTENT "${weapon_input_sha256}\n" @ONLY)
endforeach()
set(GEAR_RAY_VRAM_LAYOUT_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/vram_layout.h")
set(GEAR_RAY_IHX "${CMAKE_BINARY_DIR}/GearRay.ihx")
set(GEAR_RAY_WORKSHOP_MAP_DATA "${GEAR_RAY_GENERATED_DIR}/workshop_map_data.h")
file(SHA256 "${GEAR_RAY_WORKSHOP_LAYOUT}" workshop_input_sha256)
set(GEAR_RAY_WORKSHOP_FINGERPRINT "${GEAR_RAY_GENERATED_DIR}/workshop_input.sha256")
file(CONFIGURE OUTPUT "${GEAR_RAY_WORKSHOP_FINGERPRINT}"
    CONTENT "${workshop_input_sha256}\n" @ONLY)
set(GEAR_RAY_ROM_DIR "${CMAKE_SOURCE_DIR}/rom" CACHE PATH "Directory for the packaged Game Gear ROM")
set(GEAR_RAY_ROM "${GEAR_RAY_ROM_DIR}/${GEAR_RAY_ROM_FILENAME}")

# The canonical directory belongs to the anchored Release workflow. A profile,
# development or experiment configure must choose its own output directory.
get_filename_component(GEAR_RAY_CANONICAL_ROM_DIR "${CMAKE_SOURCE_DIR}/rom" ABSOLUTE)
get_filename_component(GEAR_RAY_CONFIGURED_ROM_DIR "${GEAR_RAY_ROM_DIR}" ABSOLUTE)
string(TOLOWER "${GEAR_RAY_CANONICAL_ROM_DIR}" GEAR_RAY_CANONICAL_ROM_DIR_CHECK)
string(TOLOWER "${GEAR_RAY_CONFIGURED_ROM_DIR}" GEAR_RAY_CONFIGURED_ROM_DIR_CHECK)
string(TOLOWER "${CMAKE_BINARY_DIR}" GEAR_RAY_CONFIGURED_BUILD_CHECK)
string(TOLOWER "${CMAKE_SOURCE_DIR}/build/release" GEAR_RAY_RELEASE_BUILD_CHECK)
if(GEAR_RAY_CONFIGURED_ROM_DIR_CHECK STREQUAL GEAR_RAY_CANONICAL_ROM_DIR_CHECK)
    if(NOT GEAR_RAY_CONFIGURED_BUILD_CHECK STREQUAL GEAR_RAY_RELEASE_BUILD_CHECK
       OR NOT CMAKE_BUILD_TYPE STREQUAL "Release" OR GEARRAY_PROFILE_RENDERER)
        message(FATAL_ERROR "Only build/release with Release/profiling OFF may write rom/. Set GEAR_RAY_ROM_DIR to your dev/profile/experiment build's own rom directory.")
    endif()
endif()

foreach(required_path
        "${GEAR_RAY_DEVKITSMS_ROOT}"
        "${GEAR_RAY_MAKESMS_EXECUTABLE}"
        "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
        "${GEAR_RAY_SMSLIB_LIBRARY}"
        "${GEAR_RAY_CRT0}")
    if(NOT EXISTS "${required_path}")
        message(FATAL_ERROR "Required Game Gear toolchain file was not found: ${required_path}")
    endif()
endforeach()

add_custom_command(
    OUTPUT "${GEAR_RAY_MAIN_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_MAIN_SOURCE}"
            -o "${GEAR_RAY_MAIN_OBJECT}"
    DEPENDS "${GEAR_RAY_MAIN_SOURCE}" "${GEAR_RAY_CAMERA_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_WALL_SIDE_HEADER}" "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_HUD_WEAPON_HEADER}" "${GEAR_RAY_PLAYER_HEADER}" "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}" "${GEAR_RAY_STARTUP_LOGO_HEADER}" "${GEAR_RAY_VIDEO_HEADER}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}" "${GEAR_RAY_ZOMBIE_AI_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/pause_map.h"
    COMMENT "Compiling game/main.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            -c "${GEAR_RAY_RED_DOOR_SWITCH_SOURCE}"
            -o "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}"
    DEPENDS "${GEAR_RAY_RED_DOOR_SWITCH_SOURCE}" "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
    COMMENT "Compiling red-door switch gameplay"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RAYCASTER_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            -c "${GEAR_RAY_RAYCASTER_SOURCE}"
            -o "${GEAR_RAY_RAYCASTER_OBJECT}"
    DEPENDS "${GEAR_RAY_RAYCASTER_SOURCE}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_WALL_SIDE_HEADER}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_CAMERA_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
    COMMENT "Compiling engine/render/raycaster.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_CAMERA_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            -c "${GEAR_RAY_CAMERA_SOURCE}"
            -o "${GEAR_RAY_CAMERA_OBJECT}"
    DEPENDS "${GEAR_RAY_CAMERA_SOURCE}" "${GEAR_RAY_CAMERA_HEADER}"
            "${GEAR_RAY_GENERATED_DIR}/camera_graph.h"
    COMMENT "Compiling game/camera.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORLD_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_WORLD_SOURCE}"
            -o "${GEAR_RAY_WORLD_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_SOURCE}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_WORLD_SPRITE_HEADER}" "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/world.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORLD_INITIALIZATION_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK1
            -c "${GEAR_RAY_WORLD_INITIALIZATION_SOURCE}"
            -o "${GEAR_RAY_WORLD_INITIALIZATION_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_INITIALIZATION_SOURCE}"
            "${GEAR_RAY_GAME_DIR}/weapons.h"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}"
            "${GEAR_RAY_DOOR_STATES_HEADER}"
    COMMENT "Compiling banked world initialization"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORKSHOP_MAP_DATA}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_WORKSHOP_MAP_GENERATOR}"
            -InputPath "${GEAR_RAY_WORKSHOP_LAYOUT}"
            -OutputHeader "${GEAR_RAY_WORKSHOP_MAP_DATA}"
    DEPENDS "${GEAR_RAY_WORKSHOP_LAYOUT}" "${GEAR_RAY_WORKSHOP_MAP_GENERATOR}"
            "${GEAR_RAY_WORKSHOP_FINGERPRINT}"
    COMMENT "Encoding numeric workshop authoring markers"
    VERBATIM
)
add_custom_target(gear_ray_map_data DEPENDS "${GEAR_RAY_WORKSHOP_MAP_DATA}")

add_custom_command(
    OUTPUT "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            -c "${GEAR_RAY_WORKSHOP_MAP_SOURCE}"
            -o "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
    DEPENDS "${GEAR_RAY_WORKSHOP_MAP_SOURCE}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
            "${GEAR_RAY_WORKSHOP_MAP_DATA}"
    COMMENT "Compiling game/workshop_map.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORLD_OBJECTS_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            -c "${GEAR_RAY_WORLD_OBJECTS_SOURCE}"
            -o "${GEAR_RAY_WORLD_OBJECTS_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_OBJECTS_SOURCE}" "${GEAR_RAY_WORLD_OBJECTS_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}"
    COMMENT "Compiling game/world_objects.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORLD_SPRITE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            -c "${GEAR_RAY_WORLD_SPRITE_SOURCE}"
            -o "${GEAR_RAY_WORLD_SPRITE_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_SPRITE_SOURCE}" "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_ZOMBIE_AI_HEADER}"
            "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_HEADER}"
            ${GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_HEADERS}
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_HEADER}"
    COMMENT "Compiling static world sprite"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_DOOR_INSTANCES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            -c "${GEAR_RAY_DOOR_INSTANCES_SOURCE}"
            -o "${GEAR_RAY_DOOR_INSTANCES_OBJECT}"
    DEPENDS "${GEAR_RAY_DOOR_INSTANCES_SOURCE}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}"
    COMMENT "Compiling game/door_instances.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_ENGINE_DIR}/render"
            --codeseg BANK1
            -c "${GEAR_RAY_ZOMBIE_SHOOTING_SOURCE}"
            -o "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}"
    DEPENDS "${GEAR_RAY_ZOMBIE_SHOOTING_SOURCE}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_CAMERA_HEADER}"
            "${GEAR_RAY_RAYCASTER_HEADER}"
    COMMENT "Compiling banked zombie hitscan"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ZOMBIE_AI_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK1
            -c "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            -o "${GEAR_RAY_ZOMBIE_AI_OBJECT}"
    DEPENDS "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_ZOMBIE_AI_HEADER}"
            "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_WALKING_01_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_WALKING_02_TEXTURE_HEADER}"
    COMMENT "Compiling banked zombie AI"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ENEMY_COLLISION_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK1
            -c "${GEAR_RAY_ENEMY_COLLISION_SOURCE}"
            -o "${GEAR_RAY_ENEMY_COLLISION_OBJECT}"
    DEPENDS "${GEAR_RAY_ENEMY_COLLISION_SOURCE}"
            "${GEAR_RAY_ENEMY_COLLISION_HEADER}"
            "${GEAR_RAY_WORLD_HEADER}"
    COMMENT "Compiling banked enemy collision query"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ZOMBIE_CORPSES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK2
            -c "${GEAR_RAY_ZOMBIE_CORPSES_SOURCE}"
            -o "${GEAR_RAY_ZOMBIE_CORPSES_OBJECT}"
    DEPENDS "${GEAR_RAY_ZOMBIE_CORPSES_SOURCE}"
            "${GEAR_RAY_ZOMBIE_CORPSES_HEADER}"
            "${GEAR_RAY_ENEMY_COLLISION_HEADER}"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
    COMMENT "Compiling cold Bank 2 zombie corpse management"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_DOOR_STATES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            -c "${GEAR_RAY_DOOR_STATES_SOURCE}"
            -o "${GEAR_RAY_DOOR_STATES_OBJECT}"
    DEPENDS "${GEAR_RAY_DOOR_STATES_SOURCE}" "${GEAR_RAY_DOOR_STATES_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}"
    COMMENT "Compiling game/door_states.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_VIDEO_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            --constseg BANK1
            -c "${GEAR_RAY_VIDEO_SOURCE}"
            -o "${GEAR_RAY_VIDEO_OBJECT}"
    DEPENDS "${GEAR_RAY_VIDEO_SOURCE}" "${GEAR_RAY_VIDEO_HEADER}" "${GEAR_RAY_VIDEO_INTERNAL_HEADER}" "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_HEADER}" "${GEAR_RAY_HUD_WEAPON_HEADER}" "${GEAR_RAY_SPRITE_PROJECTION_HEADER}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_VRAM_LAYOUT_HEADER}" "${GEAR_RAY_WALL_TEXTURES_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_WALL_SIDE_HEADER}" "${GEAR_RAY_WORLD_SPRITE_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    DEPENDS "${GEAR_RAY_GAME_DIR}/weapons.h"
    COMMENT "Compiling platform/game_gear/video.c"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_HEALTH_HUD_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_HEALTH_HUD_GENERATOR}"
            -IconPath "${GEAR_RAY_HEALTH_HUD_ICON_INPUT}"
            -BarPath "${GEAR_RAY_HEALTH_HUD_BAR_INPUT}"
            -OutputHeader "${GEAR_RAY_GENERATED_HEALTH_HUD_HEADER}"
    DEPENDS "${GEAR_RAY_HEALTH_HUD_ICON_INPUT}"
            "${GEAR_RAY_HEALTH_HUD_BAR_INPUT}"
            "${GEAR_RAY_HEALTH_HUD_GENERATOR}"
    COMMENT "Generating reference-derived health HUD tiles"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_VIDEO_INITIALIZATION_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK1
            --constseg BANK1
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_VIDEO_INITIALIZATION_SOURCE}"
            -o "${GEAR_RAY_VIDEO_INITIALIZATION_OBJECT}"
    DEPENDS "${GEAR_RAY_VIDEO_INITIALIZATION_SOURCE}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_VIDEO_INTERNAL_HEADER}"
            "${GEAR_RAY_VRAM_LAYOUT_HEADER}"
            "${GEAR_RAY_WALL_TEXTURES_HEADER}"
            "${GEAR_RAY_GENERATED_HEALTH_HUD_HEADER}"
            "${GEAR_RAY_GENERATED_GAME_OVER_HEADER}"
            "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    DEPENDS "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/pause_map.h"
    COMMENT "Compiling banked video initialization"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_DIR}/hud_masks.h"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/generate_hud_masks.ps1"
            -GeneratedDirectory "${GEAR_RAY_GENERATED_DIR}"
            -OutputHeader "${GEAR_RAY_GENERATED_DIR}/hud_masks.h"
    DEPENDS "${CMAKE_SOURCE_DIR}/tools/generate_hud_masks.ps1"
            "${GEAR_RAY_HUD_WEAPON_HEADER}"
            "${GEAR_RAY_GENERATED_DIR}/weapon_texture.c"
            "${GEAR_RAY_GENERATED_DIR}/weapon_texture.h"
            "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.c"
            "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.h"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_held.c"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_held.h"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_fire.c"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_fire.h"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_HUD_WEAPON_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK1
            --constseg BANK1
            -c "${GEAR_RAY_HUD_WEAPON_SOURCE}"
            -o "${GEAR_RAY_HUD_WEAPON_OBJECT}"
    DEPENDS "${GEAR_RAY_HUD_WEAPON_SOURCE}"
            "${GEAR_RAY_GENERATED_DIR}/hud_masks.h"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_held.h"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_fire.h"
            "${GEAR_RAY_GAME_DIR}/weapons.h"
            "${GEAR_RAY_HUD_WEAPON_HEADER}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER}"
    COMMENT "Compiling banked static HUD weapon overlay"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK1
            --constseg BANK1
            -c "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            -o "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"
    DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/zombie_visuals.h"
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_world.h"
            "${GEAR_RAY_GENERATED_DIR}/shotgun_far_lod.h"
            "${GEAR_RAY_GAME_DIR}/weapons.h"
            "${GEAR_RAY_SPRITE_PROJECTION_HEADER}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_CAMERA_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_WALKING_01_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_WALKING_02_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_STANDING_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_WALKING_01_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_WALKING_02_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_SHOT_01_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_SHOT_DEAD_HEADER}"
            "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_CORPS_HEADER}"
    COMMENT "Compiling banked static sprite projection"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RENDERER_PROFILE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            --codeseg BANK1
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_RENDERER_PROFILE_SOURCE}"
            -o "${GEAR_RAY_RENDERER_PROFILE_OBJECT}"
    DEPENDS "${GEAR_RAY_RENDERER_PROFILE_SOURCE}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling renderer profiling diagnostics"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
           "${GEAR_RAY_GENERATED_SEGA_LOGO_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_STARTUP_LOGO_GENERATOR}"
            -InputPath "${GEAR_RAY_SEGA_LOGO_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_SEGA_LOGO_HEADER}"
    DEPENDS "${GEAR_RAY_SEGA_LOGO_INPUT}"
            "${GEAR_RAY_STARTUP_LOGO_GENERATOR}"
    COMMENT "Generating native SEGA startup logo"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK3
            -c "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
            -o "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
            "${GEAR_RAY_GENERATED_SEGA_LOGO_HEADER}"
    COMMENT "Compiling generated SEGA startup logo"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_GAME_OVER_SOURCE}" "${GEAR_RAY_GENERATED_GAME_OVER_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_GAME_OVER_GENERATOR}"
            -InputPath "${GEAR_RAY_GAME_OVER_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_GAME_OVER_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_GAME_OVER_HEADER}"
    DEPENDS "${GEAR_RAY_GAME_OVER_INPUT}" "${GEAR_RAY_GAME_OVER_GENERATOR}"
    COMMENT "Generating centered Game Over screen"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_GAME_OVER_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80 "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK3 -c "${GEAR_RAY_GENERATED_GAME_OVER_SOURCE}"
            -o "${GEAR_RAY_GENERATED_GAME_OVER_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_GAME_OVER_SOURCE}" "${GEAR_RAY_GENERATED_GAME_OVER_HEADER}"
    COMMENT "Compiling generated Game Over screen"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GAME_OVER_PRESENTATION_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80 -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK3 --constseg BANK3
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_GAME_OVER_PRESENTATION_SOURCE}"
            -o "${GEAR_RAY_GAME_OVER_PRESENTATION_OBJECT}"
    DEPENDS "${GEAR_RAY_GAME_OVER_PRESENTATION_SOURCE}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_VIDEO_INTERNAL_HEADER}"
            "${GEAR_RAY_GENERATED_GAME_OVER_HEADER}"
            "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling cold Game Over presentation in Bank 3"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}" "${GEAR_RAY_GENERATED_DIR}/wall_palette.c"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_WALL_TEXTURE_GENERATOR}"
            -InputPath "${GEAR_RAY_WALL_TEXTURE_INPUT}"
            -BloodInputPath "${GEAR_RAY_BLOOD_WALL_TEXTURE_INPUT}"
            -DoorInputPath "${GEAR_RAY_DOOR_TEXTURE_INPUT}"
            -RedDoorInputPath "${GEAR_RAY_RED_DOOR_TEXTURE_INPUT}"
            -SwitchOffFrame1InputPath "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_1_INPUT}"
            -SwitchOffFrame2InputPath "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_2_INPUT}"
            -SwitchOnFrame1InputPath "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_1_INPUT}"
            -SwitchOnFrame2InputPath "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_2_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
            -OutputPaletteSource "${GEAR_RAY_GENERATED_DIR}/wall_palette.c"
    DEPENDS "${GEAR_RAY_WALL_TEXTURE_INPUT}" "${GEAR_RAY_BLOOD_WALL_TEXTURE_INPUT}" "${GEAR_RAY_DOOR_TEXTURE_INPUT}" "${GEAR_RAY_RED_DOOR_TEXTURE_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_1_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_2_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_1_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_2_INPUT}" "${GEAR_RAY_WALL_TEXTURE_GENERATOR}"
    COMMENT "Generating packed 4bpp indexed-color wall texture"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            -c "${GEAR_RAY_GENERATED_DIR}/wall_palette.c"
            -o "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_DIR}/wall_palette.c" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
    COMMENT "Compiling generated wall texture"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE}"
           "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
            -InputPath "${GEAR_RAY_SPRITE_TEXTURE_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
            -Symbol zombie_01_standing_pixels
    DEPENDS "${GEAR_RAY_SPRITE_TEXTURE_INPUT}"
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating packed standing zombie sprite"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_SOURCE}"
           "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
            -InputPath "${GEAR_RAY_WEAPON_TEXTURE_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_HEADER}"
            -Symbol hud_weapon_pixels
            -SpriteKind HudWeapon
    DEPENDS "${GEAR_RAY_WEAPON_TEXTURE_INPUT}"
            "${GEAR_RAY_WEAPON_TEXTURE_FINGERPRINT}"
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating packed static HUD weapon"
    VERBATIM
)

set(GEAR_RAY_NEAR_ZOMBIE_GENERATED_OBJECTS)
set(GEAR_RAY_NEAR_ZOMBIE_GENERATED_HEADERS)
foreach(near_pose IN ITEMS WALKING_01 WALKING_02 STANDING_ATTACK ATTACK_01 ATTACK_02 SHOT_01 CORPSE)
    string(TOLOWER "${near_pose}" near_pose_lower)
    set(near_input "${GEAR_RAY_NEAR_ZOMBIE_${near_pose}_INPUT}")
    set(near_source "${GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_SOURCE}")
    set(near_header "${GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_HEADER}")
    set(near_object "${GEAR_RAY_GENERATED_NEAR_ZOMBIE_${near_pose}_OBJECT}")
    add_custom_command(
        OUTPUT "${near_source}" "${near_header}"
        COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
                -NoProfile -ExecutionPolicy Bypass
                -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
                -InputPath "${near_input}"
                -OutputSource "${near_source}"
                -OutputHeader "${near_header}"
                -Symbol "zombie_near_${near_pose_lower}_pixels"
                -SpriteKind NearZombie
        DEPENDS "${near_input}" "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
        COMMENT "Generating native 32x32 near zombie ${near_pose_lower}"
        VERBATIM
    )
    add_custom_command(
        OUTPUT "${near_object}"
        COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
                -mz80 "-I${GEAR_RAY_GENERATED_DIR}"
                --constseg BANK4
                -c "${near_source}" -o "${near_object}"
        DEPENDS "${near_source}" "${near_header}"
        COMMENT "Compiling Bank 4 near zombie ${near_pose_lower}"
        VERBATIM
    )
    list(APPEND GEAR_RAY_NEAR_ZOMBIE_GENERATED_OBJECTS "${near_object}")
    list(APPEND GEAR_RAY_NEAR_ZOMBIE_GENERATED_HEADERS "${near_header}")
endforeach()

set(GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_OBJECTS)
set(GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_HEADERS)
foreach(middle_pose IN ITEMS STANDING WALKING_01 WALKING_02 SHOT_01 SHOT_DEAD CORPS)
    string(TOLOWER "${middle_pose}" middle_pose_lower)
    set(middle_input "${GEAR_RAY_MIDDLE_ZOMBIE_${middle_pose}_INPUT}")
    set(middle_source "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_SOURCE}")
    set(middle_header "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_HEADER}")
    set(middle_object "${GEAR_RAY_GENERATED_MIDDLE_ZOMBIE_${middle_pose}_OBJECT}")
    add_custom_command(
        OUTPUT "${middle_source}" "${middle_header}"
        COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
                -NoProfile -ExecutionPolicy Bypass
                -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
                -InputPath "${middle_input}"
                -OutputSource "${middle_source}"
                -OutputHeader "${middle_header}"
                -Symbol "zombie_middle_${middle_pose_lower}_pixels"
                -SpriteKind MiddleZombie
        DEPENDS "${middle_input}" "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
        COMMENT "Generating authored 16x16 zombie ${middle_pose_lower}"
        VERBATIM
    )
    add_custom_command(
        OUTPUT "${middle_object}"
        COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
                -mz80 "-I${GEAR_RAY_GENERATED_DIR}"
                --constseg BANK1
                -c "${middle_source}" -o "${middle_object}"
        DEPENDS "${middle_source}" "${middle_header}"
        COMMENT "Compiling Bank 1 middle zombie ${middle_pose_lower}"
        VERBATIM
    )
    list(APPEND GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_OBJECTS "${middle_object}")
    list(APPEND GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_HEADERS "${middle_header}")
endforeach()

add_custom_command(
    OUTPUT "${GEAR_RAY_ZOMBIE_ASSET_STAMP}"
    BYPRODUCTS ${GEAR_RAY_ZOMBIE_ASSET_BYPRODUCTS}
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_ZOMBIE_ASSET_GENERATOR}"
            -RepositoryRoot "${CMAKE_SOURCE_DIR}"
            -OutputDirectory "${GEAR_RAY_GENERATED_DIR}"
            -SpriteGenerator "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
            -Stamp "${GEAR_RAY_ZOMBIE_ASSET_STAMP}"
    DEPENDS ${GEAR_RAY_ZOMBIE_ASSET_INPUTS}
            "${GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT_FILE}"
            "${GEAR_RAY_ZOMBIE_ASSET_GENERATOR}"
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating explicit security/scientist authored sprite manifest"
    VERBATIM
)
add_custom_target(gear_ray_zombie_assets DEPENDS "${GEAR_RAY_ZOMBIE_ASSET_STAMP}")

add_custom_command(
    OUTPUT "${GEAR_RAY_ZOMBIE_VISUALS_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            "-I${CMAKE_SOURCE_DIR}/docs/development/2026-11-16-zombie-variants/implementation"
            --constseg BANK1
            -c "${GEAR_RAY_GENERATED_DIR}/zombie_visuals_assets.c"
            -o "${GEAR_RAY_ZOMBIE_VISUALS_OBJECT}"
    DEPENDS "${GEAR_RAY_ZOMBIE_ASSET_STAMP}"
            "${CMAKE_SOURCE_DIR}/docs/development/2026-11-16-zombie-variants/implementation/security-lod-reference.c"
    COMMENT "Compiling both species' base, middle and distant visuals in Bank 1"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK4
            -c "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_SOURCE}"
            -o "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_OBJECT}"
    DEPENDS "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_SOURCE}"
            "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_HEADER}"
            "${GEAR_RAY_ZOMBIE_ASSET_STAMP}"
    COMMENT "Compiling Bank 4 near zombie texture table"
    VERBATIM
)

foreach(zombie_state IN ITEMS WALKING_01 WALKING_02 SHOT_01 SHOT_02 SHOT_DEAD CORPS)
    string(TOLOWER "${zombie_state}" zombie_state_lower)
    set(zombie_lod_argument)
    if(zombie_state STREQUAL "WALKING_01" OR zombie_state STREQUAL "WALKING_02")
        set(zombie_lod_argument -GenerateWalkingLod)
    endif()
    add_custom_command(
        OUTPUT "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_SOURCE}"
               "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_HEADER}"
        COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
                -NoProfile
                -ExecutionPolicy Bypass
                -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
                -InputPath "${GEAR_RAY_ZOMBIE_${zombie_state}_TEXTURE_INPUT}"
                -OutputSource "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_SOURCE}"
                -OutputHeader "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_HEADER}"
                -Symbol "zombie_01_${zombie_state_lower}_pixels"
                ${zombie_lod_argument}
        DEPENDS "${GEAR_RAY_ZOMBIE_${zombie_state}_TEXTURE_INPUT}"
                "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
        COMMENT "Generating packed zombie ${zombie_state_lower} sprite"
        VERBATIM
    )

    add_custom_command(
        OUTPUT "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_OBJECT}"
        COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
                -mz80
                "-I${GEAR_RAY_GENERATED_DIR}"
                --constseg BANK1
                -c "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_SOURCE}"
                -o "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_OBJECT}"
        DEPENDS "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_SOURCE}"
                "${GEAR_RAY_GENERATED_ZOMBIE_${zombie_state}_TEXTURE_HEADER}"
        COMMENT "Compiling generated zombie ${zombie_state_lower} sprite"
        VERBATIM
    )
endforeach()

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE}"
           "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
            -InputPath "${GEAR_RAY_WEAPON_SHOOT_TEXTURE_INPUT}"
            -OutputSource "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE}"
            -OutputHeader "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER}"
            -Symbol hud_weapon_shoot_pixels
            -SpriteKind HudWeapon
    DEPENDS "${GEAR_RAY_WEAPON_SHOOT_TEXTURE_INPUT}"
            "${GEAR_RAY_WEAPON_SHOOT_TEXTURE_FINGERPRINT}"
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating packed shooting HUD weapon"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK1
            -c "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE}"
            -o "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE}"
            "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
    COMMENT "Compiling generated standing zombie sprite"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WALL_TEXTURES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_WALL_TEXTURES_SOURCE}"
            -o "${GEAR_RAY_WALL_TEXTURES_OBJECT}"
    DEPENDS "${GEAR_RAY_WALL_TEXTURES_SOURCE}" "${GEAR_RAY_WALL_TEXTURES_HEADER}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
    COMMENT "Compiling platform/game_gear/wall_textures.c"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_INTERACTION_RAY_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK1
            -c "${GEAR_RAY_INTERACTION_RAY_SOURCE}"
            -o "${GEAR_RAY_INTERACTION_RAY_OBJECT}"
    DEPENDS "${GEAR_RAY_INTERACTION_RAY_SOURCE}" "${GEAR_RAY_INTERACTION_RAY_HEADER}" "${GEAR_RAY_INTERACTION_TARGET_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECTS_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
    COMMENT "Compiling game/interaction_ray.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK1
            -c "${GEAR_RAY_WORLD_INTERACTIONS_SOURCE}"
            -o "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_INTERACTIONS_SOURCE}" "${GEAR_RAY_WORLD_INTERACTIONS_HEADER}" "${GEAR_RAY_INTERACTION_TARGET_HEADER}" "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECTS_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_WORLD_SPRITE_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
    COMMENT "Compiling game/world_interactions.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_PLAYER_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_PLAYER_SOURCE}"
            -o "${GEAR_RAY_PLAYER_OBJECT}"
    DEPENDS "${GEAR_RAY_PLAYER_SOURCE}" "${GEAR_RAY_PLAYER_HEADER}" "${GEAR_RAY_INTERACTION_RAY_HEADER}" "${GEAR_RAY_INTERACTION_TARGET_HEADER}" "${GEAR_RAY_WORLD_INTERACTIONS_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECTS_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}" "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_CAMERA_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/player.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_INPUT_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_INPUT_SOURCE}"
            -o "${GEAR_RAY_INPUT_OBJECT}"
    DEPENDS "${GEAR_RAY_INPUT_SOURCE}" "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
            "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input_internal.h"
    COMMENT "Compiling platform/game_gear/input.c"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_STARTUP_LOGO_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --codeseg BANK3 --constseg BANK3
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_STARTUP_LOGO_SOURCE}"
            -o "${GEAR_RAY_STARTUP_LOGO_OBJECT}"
    DEPENDS "${GEAR_RAY_STARTUP_LOGO_SOURCE}"
            "${GEAR_RAY_STARTUP_LOGO_HEADER}"
            "${GEAR_RAY_GENERATED_SEGA_LOGO_HEADER}"
            "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling isolated SEGA startup screen"
    VERBATIM
)

set(GEAR_RAY_PAUSE_MAP_OBJECT "${CMAKE_BINARY_DIR}/pause_map.rel")
set(GEAR_RAY_PAUSE_WEAPON_HEADER "${GEAR_RAY_GENERATED_DIR}/pause_weapon_icon.h")
set(GEAR_RAY_PAUSE_SHOTGUN_HEADER "${GEAR_RAY_GENERATED_DIR}/pause_shotgun_icon.h")
set(GEAR_RAY_SHOTGUN_FAR_HEADER "${GEAR_RAY_GENERATED_DIR}/shotgun_far_lod.h")
set(GEAR_RAY_SHOTGUN_OBJECTS)
foreach(kind IN ITEMS held fire world)
    if(kind STREQUAL "held")
        set(asset shotgun_held.png)
        set(sprite_kind HudWeapon20x16)
    elseif(kind STREQUAL "fire")
        set(asset shotgun_held_shoot.png)
        set(sprite_kind HudWeapon20x16)
    else()
        set(asset pick_up_shotgun.png)
        set(sprite_kind WorldPickup)
    endif()
    set(source "${GEAR_RAY_GENERATED_DIR}/shotgun_${kind}.c")
    set(header "${GEAR_RAY_GENERATED_DIR}/shotgun_${kind}.h")
    set(object "${CMAKE_BINARY_DIR}/shotgun_${kind}.rel")
    add_custom_command(OUTPUT "${source}" "${header}"
        COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/generate_sprite_texture.ps1"
            -InputPath "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/${asset}"
            -OutputSource "${source}" -OutputHeader "${header}"
            -Symbol "shotgun_${kind}_pixels" -SpriteKind "${sprite_kind}"
        DEPENDS "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/${asset}"
            "${CMAKE_SOURCE_DIR}/tools/generate_sprite_texture.ps1"
            "${GEAR_RAY_ZOMBIE_ASSET_FINGERPRINT_FILE}" VERBATIM)
    if(kind STREQUAL "world")
    add_custom_command(OUTPUT "${object}"
        COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80 --constseg BANK1
            -c "${source}" -o "${object}" DEPENDS "${source}" "${header}" VERBATIM)
    list(APPEND GEAR_RAY_SHOTGUN_OBJECTS "${object}")
    endif()
endforeach()
add_custom_command(OUTPUT "${GEAR_RAY_PAUSE_SHOTGUN_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
        -File "${CMAKE_SOURCE_DIR}/tools/generate_pause_weapon_icon.ps1"
        -InputPath "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/shotgun.png"
        -OutputHeader "${GEAR_RAY_PAUSE_SHOTGUN_HEADER}"
        -Symbol pause_shotgun_tiles
    DEPENDS "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/shotgun.png"
        "${CMAKE_SOURCE_DIR}/tools/generate_pause_weapon_icon.ps1" VERBATIM)
add_custom_command(OUTPUT "${GEAR_RAY_SHOTGUN_FAR_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
        -File "${CMAKE_SOURCE_DIR}/tools/generate_shotgun_lod.ps1"
        -InputPath "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/pick_up_shotgun.png"
        -OutputDirectory "${GEAR_RAY_GENERATED_DIR}"
    DEPENDS "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/pick_up_shotgun.png"
        "${CMAKE_SOURCE_DIR}/tools/generate_shotgun_lod.ps1" VERBATIM)
add_custom_target(gear_ray_weapon_assets DEPENDS ${GEAR_RAY_SHOTGUN_OBJECTS}
    "${GEAR_RAY_GENERATED_DIR}/hud_masks.h"
    "${GEAR_RAY_PAUSE_SHOTGUN_HEADER}" "${GEAR_RAY_SHOTGUN_FAR_HEADER}")

add_custom_command(
    OUTPUT "${GEAR_RAY_PAUSE_WEAPON_HEADER}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/generate_pause_weapon_icon.ps1"
            -InputPath "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/pistol.png"
            -OutputHeader "${GEAR_RAY_PAUSE_WEAPON_HEADER}"
    DEPENDS "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/pistol.png"
            "${CMAKE_SOURCE_DIR}/tools/generate_pause_weapon_icon.ps1"
    VERBATIM
)
add_custom_command(
    OUTPUT "${GEAR_RAY_PAUSE_MAP_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80 -DTARGET_GG
            "-I${GEAR_RAY_GENERATED_DIR}"
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_DIR}"
            --codeseg BANK2 --constseg BANK2
            -c "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/pause_map.c"
            -o "${GEAR_RAY_PAUSE_MAP_OBJECT}"
    DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/pause_map.c"
            "${GEAR_RAY_PAUSE_WEAPON_HEADER}"
            "${GEAR_RAY_PAUSE_SHOTGUN_HEADER}"
            "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/pause_map.h"
            "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input_internal.h"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_DOOR_STATES_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}"
            "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_CAMERA_HEADER}"
            "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}"
    COMMENT "Compiling event-only Bank 2 pause map"
    DEPENDS "${GEAR_RAY_GAME_DIR}/weapons.h"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_DIR}/camera_graph.c" "${GEAR_RAY_GENERATED_DIR}/camera_graph.h"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/generate_camera_graph.ps1"
            -CameraSource "${GEAR_RAY_CAMERA_SOURCE}"
            -OutputSource "${GEAR_RAY_GENERATED_DIR}/camera_graph.c"
            -OutputHeader "${GEAR_RAY_GENERATED_DIR}/camera_graph.h"
    DEPENDS "${CMAKE_SOURCE_DIR}/tools/generate_camera_graph.ps1" "${GEAR_RAY_CAMERA_SOURCE}"
    VERBATIM
)
add_custom_command(
    OUTPUT "${CMAKE_BINARY_DIR}/camera_graph.rel"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80 --constseg BANK2
            -c "${GEAR_RAY_GENERATED_DIR}/camera_graph.c"
            -o "${CMAKE_BINARY_DIR}/camera_graph.rel"
    DEPENDS "${GEAR_RAY_GENERATED_DIR}/camera_graph.c" "${GEAR_RAY_GENERATED_DIR}/camera_graph.h"
    VERBATIM
)

add_custom_command(OUTPUT "${GEAR_RAY_GENERATED_DIR}/wall_schedules.h"
 COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
 -File "${CMAKE_SOURCE_DIR}/tools/generate_native_wall_tables.ps1"
 -OutputHeader "${GEAR_RAY_GENERATED_DIR}/wall_schedules.h" -GeneratedDirectory "${GEAR_RAY_GENERATED_DIR}"
 DEPENDS "${CMAKE_SOURCE_DIR}/tools/generate_native_wall_tables.ps1" "${GEAR_RAY_GENERATED_DIR}/wall_texture.c" VERBATIM)
add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/native_wall.rel"
 COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80 -DTARGET_GG --codeseg BANK3WALL --constseg BANK3WALL
 "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}" "-I${GEAR_RAY_GENERATED_DIR}"
 -c "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/native_wall.c" -o "${CMAKE_BINARY_DIR}/native_wall.rel"
 DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/native_wall.c" "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/native_wall.h" "${GEAR_RAY_GENERATED_DIR}/wall_schedules.h" VERBATIM)
add_custom_command(
    OUTPUT "${GEAR_RAY_IHX}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -o "${GEAR_RAY_IHX}"
            -mz80
            --no-std-crt0
            --data-loc 0xC000
            -Wl-b_BANK1=0x14000
            -Wl-b_BANK2=0x28000
            -Wl-b_BANK3=0x34000
            -Wl-b_BANK3WALL=0x39200
            -Wl-b_BANK4=0x48000
            "${GEAR_RAY_CRT0}"
            "${GEAR_RAY_MAIN_OBJECT}"
            "${GEAR_RAY_PAUSE_MAP_OBJECT}"
            "${GEAR_RAY_CAMERA_OBJECT}"
            "${CMAKE_BINARY_DIR}/camera_graph.rel"
            "${GEAR_RAY_RAYCASTER_OBJECT}"
            "${GEAR_RAY_PLAYER_OBJECT}"
            "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}"
            "${GEAR_RAY_WORLD_OBJECT}"
            "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
            "${GEAR_RAY_WORLD_OBJECTS_OBJECT}"
            "${GEAR_RAY_WORLD_SPRITE_OBJECT}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}"
            "${GEAR_RAY_ZOMBIE_AI_OBJECT}"
            "${GEAR_RAY_ZOMBIE_CORPSES_OBJECT}"
            "${GEAR_RAY_ENEMY_COLLISION_OBJECT}"
            "${GEAR_RAY_DOOR_INSTANCES_OBJECT}"
            "${GEAR_RAY_DOOR_STATES_OBJECT}"
            "${GEAR_RAY_INPUT_OBJECT}"
            "${GEAR_RAY_VIDEO_OBJECT}"
            "${CMAKE_BINARY_DIR}/native_wall.rel"
            "${GEAR_RAY_HUD_WEAPON_OBJECT}"
            ${GEAR_RAY_SHOTGUN_OBJECTS}
            "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"

            "${GEAR_RAY_WALL_TEXTURES_OBJECT}"
            "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}"
            "${GEAR_RAY_GENERATED_GAME_OVER_OBJECT}"
            "${GEAR_RAY_GAME_OVER_PRESENTATION_OBJECT}"
            "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
            "${GEAR_RAY_ZOMBIE_VISUALS_OBJECT}"


            "${GEAR_RAY_SMSLIB_LIBRARY}"
            "${GEAR_RAY_STARTUP_LOGO_OBJECT}"
            "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_OBJECT}"
            "${GEAR_RAY_INTERACTION_RAY_OBJECT}"
            "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}"
            "${GEAR_RAY_WORLD_INITIALIZATION_OBJECT}"
            "${GEAR_RAY_VIDEO_INITIALIZATION_OBJECT}"
            ${GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT}
    DEPENDS "${GEAR_RAY_MAIN_OBJECT}" "${GEAR_RAY_CAMERA_OBJECT}" "${GEAR_RAY_RAYCASTER_OBJECT}" "${GEAR_RAY_PLAYER_OBJECT}" "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}" "${GEAR_RAY_STARTUP_LOGO_OBJECT}" "${GEAR_RAY_ZOMBIE_VISUALS_OBJECT}" "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_OBJECT}" "${GEAR_RAY_INTERACTION_RAY_OBJECT}" "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}" "${GEAR_RAY_WORLD_INITIALIZATION_OBJECT}" "${GEAR_RAY_VIDEO_INITIALIZATION_OBJECT}" "${GEAR_RAY_WORLD_OBJECT}" "${GEAR_RAY_WORKSHOP_MAP_OBJECT}" "${GEAR_RAY_WORLD_OBJECTS_OBJECT}" "${GEAR_RAY_WORLD_SPRITE_OBJECT}" "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}" "${GEAR_RAY_ZOMBIE_AI_OBJECT}" "${GEAR_RAY_ZOMBIE_CORPSES_OBJECT}" "${GEAR_RAY_ENEMY_COLLISION_OBJECT}" "${GEAR_RAY_DOOR_INSTANCES_OBJECT}" "${GEAR_RAY_DOOR_STATES_OBJECT}" "${GEAR_RAY_INPUT_OBJECT}" "${GEAR_RAY_VIDEO_OBJECT}" "${GEAR_RAY_HUD_WEAPON_OBJECT}" "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}" ${GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT} "${GEAR_RAY_WALL_TEXTURES_OBJECT}" "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}" "${GEAR_RAY_CRT0}" "${GEAR_RAY_SMSLIB_LIBRARY}"
    DEPENDS "${GEAR_RAY_PAUSE_MAP_OBJECT}" "${GEAR_RAY_GENERATED_GAME_OVER_OBJECT}" "${GEAR_RAY_GAME_OVER_PRESENTATION_OBJECT}"
    DEPENDS ${GEAR_RAY_SHOTGUN_OBJECTS}
    DEPENDS "${CMAKE_BINARY_DIR}/native_wall.rel" "${CMAKE_BINARY_DIR}/camera_graph.rel"
    COMMENT "Linking GearRay for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ROM}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${GEAR_RAY_ROM_DIR}"
    COMMAND "${GEAR_RAY_MAKESMS_EXECUTABLE}" -pm "${GEAR_RAY_IHX}" "${GEAR_RAY_ROM}"
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_BANK_LAYOUT_VALIDATOR}"
            -MapPath "${CMAKE_BINARY_DIR}/GearRay.map"
            -RomPath "${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_IHX}"
            "${GEAR_RAY_BANK_LAYOUT_VALIDATOR}"
            "${CMAKE_SOURCE_DIR}/tools/production_build_artifacts.ps1"
    COMMENT "Generating ${GEAR_RAY_ROM}"
    VERBATIM
)

# Preserve the existing project target structure while making the game target real.
add_custom_target(gear_ray_engine)
add_custom_target(gear_ray_validate_workshop
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_WORKSHOP_MAP_VALIDATOR}"
    DEPENDS
            "${GEAR_RAY_WORKSHOP_MAP_VALIDATOR}"
            "${GEAR_RAY_WORKSHOP_MAP_SOURCE}"
            "${GEAR_RAY_WORKSHOP_MAP_HEADER}"
            "${GEAR_RAY_WORLD_SOURCE}"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_DOOR_INSTANCES_SOURCE}"
            "${GEAR_RAY_DOOR_INSTANCES_HEADER}"
            "${GEAR_RAY_RED_DOOR_SWITCH_SOURCE}"
            "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}"
            "${GEAR_RAY_WALL_TEXTURE_GENERATOR}"
    COMMENT "Validating workshop map, instances, enclosure, and VOID safety"
    VERBATIM
)
add_custom_target(gear_ray_game ALL DEPENDS "${GEAR_RAY_ROM}")
add_custom_target(gear_ray_validate_zombie_shooting
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_ZOMBIE_SHOOTING_VALIDATOR}"
    DEPENDS "${GEAR_RAY_ZOMBIE_SHOOTING_VALIDATOR}"
            "${GEAR_RAY_WORLD_SPRITE_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_SOURCE}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_HEADER}"
            "${GEAR_RAY_MAIN_SOURCE}"
            "${GEAR_RAY_INPUT_SOURCE}"
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
    COMMENT "Validating zombie hitscan and death states"
    VERBATIM
)
add_custom_target(gear_ray_validate_shotgun_combat
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_SHOTGUN_COMBAT_VALIDATOR}"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
            -RequireAssembly
    DEPENDS "${GEAR_RAY_SHOTGUN_COMBAT_VALIDATOR}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_SOURCE}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}"
            "${GEAR_RAY_MAIN_SOURCE}" "${GEAR_RAY_INPUT_SOURCE}"
    COMMENT "Validating shotgun combat identity and off-axis occlusion"
    VERBATIM
)
add_custom_target(gear_ray_validate_zombie_ai
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_ZOMBIE_AI_VALIDATOR}"
    DEPENDS "${GEAR_RAY_ZOMBIE_AI_VALIDATOR}"
            "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_ZOMBIE_AI_HEADER}"
            "${GEAR_RAY_ENEMY_COLLISION_SOURCE}"
            "${GEAR_RAY_ENEMY_COLLISION_HEADER}"
            "${GEAR_RAY_WORLD_SOURCE}"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_MAIN_SOURCE}"
    COMMENT "Validating zombie activation, pursuit, and collision contracts"
    VERBATIM
)

add_custom_target(gear_ray_validate_corpse_persistence
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_CORPSE_PERSISTENCE_VALIDATOR}"
    DEPENDS "${GEAR_RAY_CORPSE_PERSISTENCE_VALIDATOR}"
            "${GEAR_RAY_WORLD_SPRITE_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_ZOMBIE_CORPSES_SOURCE}"
            "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            "${GEAR_RAY_MAIN_SOURCE}"
    COMMENT "Validating persistent corpse gameplay"
    VERBATIM
)

add_custom_target(gear_ray_validate_zombie_attack
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_ZOMBIE_ATTACK_VALIDATOR}"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
    DEPENDS
            "${GEAR_RAY_ZOMBIE_ATTACK_VALIDATOR}"
            "${GEAR_RAY_PLAYER_SOURCE}"
            "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
            "${GEAR_RAY_MAIN_SOURCE}"
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            ${GEAR_RAY_NEAR_ZOMBIE_GENERATED_HEADERS}
    COMMENT "Validating zombie attack, player health, and game over"
    VERBATIM
)
add_custom_target(gear_ray_validate_health_hud
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile
            -ExecutionPolicy Bypass
            -File "${GEAR_RAY_HEALTH_HUD_VALIDATOR}"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
    DEPENDS
            "${GEAR_RAY_HEALTH_HUD_VALIDATOR}"
            "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_VIDEO_INITIALIZATION_SOURCE}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_GENERATED_HEALTH_HUD_HEADER}"
            "${GEAR_RAY_STARTUP_LOGO_SOURCE}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
    COMMENT "Validating minimal player health HUD"
    VERBATIM
)
add_custom_target(gear_ray_validate_near_zombie
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_NEAR_ZOMBIE_VALIDATOR}"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
    DEPENDS "${GEAR_RAY_NEAR_ZOMBIE_VALIDATOR}"
            ${GEAR_RAY_NEAR_ZOMBIE_GENERATED_HEADERS}
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            "${GEAR_RAY_VIDEO_SOURCE}"
            "${GEAR_RAY_NEAR_ZOMBIE_TEXTURES_SOURCE}"
    COMMENT "Validating native 32x32 near-detail zombie"
    VERBATIM
)
add_custom_target(gear_ray_validate_middle_zombie
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile -ExecutionPolicy Bypass
            -File "${GEAR_RAY_MIDDLE_ZOMBIE_VALIDATOR}"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
    DEPENDS "${GEAR_RAY_MIDDLE_ZOMBIE_VALIDATOR}"
            ${GEAR_RAY_MIDDLE_ZOMBIE_GENERATED_HEADERS}
            "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            "${GEAR_RAY_VIDEO_SOURCE}"
    COMMENT "Validating 8x8/16x16/32x32 zombie presentation ladder"
    VERBATIM
)
add_dependencies(gear_ray_validate_near_zombie gear_ray_zombie_assets)
add_dependencies(gear_ray_validate_middle_zombie gear_ray_zombie_assets)
add_dependencies(gear_ray_game gear_ray_engine gear_ray_validate_workshop
                 gear_ray_validate_zombie_shooting
                 gear_ray_validate_shotgun_combat
                 gear_ray_validate_zombie_ai
                 gear_ray_validate_corpse_persistence
                 gear_ray_validate_zombie_attack
                 gear_ray_validate_health_hud
                 gear_ray_validate_near_zombie
                 gear_ray_validate_middle_zombie)

add_custom_target(gear_ray_info ALL
    COMMAND "${CMAKE_COMMAND}" -E echo "GearRay Game Gear ROM: ${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_ROM}"
    VERBATIM
)

add_custom_target(gear_ray_validate_pause_map
    COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}"
            -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/validate_pause_map.ps1"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
    DEPENDS "${GEAR_RAY_PAUSE_MAP_OBJECT}"
            "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}"
            "${CMAKE_SOURCE_DIR}/tools/production_build_artifacts.ps1"
    COMMENT "Validating pause map geometry, START edges, and restoration contracts"
    VERBATIM
)
add_dependencies(gear_ray_game gear_ray_validate_pause_map)

add_dependencies(gear_ray_game gear_ray_weapon_assets)
foreach(validator IN ITEMS weapon_assets weapon_runtime)
    add_custom_target(gear_ray_validate_${validator}
        COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
            -File "${CMAKE_SOURCE_DIR}/tools/validate_${validator}.ps1"
            -BuildDirectory "${CMAKE_BINARY_DIR}"
        DEPENDS "${GEAR_RAY_HUD_WEAPON_OBJECT}" "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"
            "${GEAR_RAY_MAIN_OBJECT}" "${GEAR_RAY_VIDEO_OBJECT}" ${GEAR_RAY_SHOTGUN_OBJECTS}
            "${GEAR_RAY_PAUSE_SHOTGUN_HEADER}" "${GEAR_RAY_SHOTGUN_FAR_HEADER}"
            "${GEAR_RAY_ROM}"
            "${CMAKE_SOURCE_DIR}/tools/production_build_artifacts.ps1"
        VERBATIM)
    add_dependencies(gear_ray_game gear_ray_validate_${validator})
endforeach()

add_custom_command(OUTPUT "${GEAR_RAY_VIDEO_OBJECT}" APPEND DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/native_wall.h")

add_custom_target(gear_ray_validate_native_wall ALL
 COMMAND "${GEAR_RAY_POWERSHELL_EXECUTABLE}" -NoProfile -ExecutionPolicy Bypass
 -File "${CMAKE_SOURCE_DIR}/tools/validate_native_wall.ps1" -BuildDirectory "${CMAKE_BINARY_DIR}"
 -RequireMapPlacement -RequireAssembly
 DEPENDS "${GEAR_RAY_IHX}" "${CMAKE_SOURCE_DIR}/tools/validate_native_wall.ps1" VERBATIM)

# Public layout dependencies used by generated native wall/projection clients.
add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/native_wall.rel" APPEND DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.h" "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/wall_textures.h" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}")
add_custom_command(OUTPUT "${GEAR_RAY_VIDEO_INITIALIZATION_OBJECT}" APPEND DEPENDS "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/sprite_projection.h")

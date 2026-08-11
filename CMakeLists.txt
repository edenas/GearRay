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
set(GEAR_RAY_WORKSHOP_MAP_SOURCE "${GEAR_RAY_GAME_DIR}/workshop_map.c")
set(GEAR_RAY_WORKSHOP_MAP_HEADER "${GEAR_RAY_GAME_DIR}/workshop_map.h")
set(GEAR_RAY_WORKSHOP_MAP_OBJECT "${CMAKE_BINARY_DIR}/workshop_map.rel")
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
set(GEAR_RAY_VIDEO_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.c")
set(GEAR_RAY_VIDEO_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.h")
set(GEAR_RAY_VIDEO_OBJECT "${CMAKE_BINARY_DIR}/video.rel")
set(GEAR_RAY_HUD_WEAPON_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/hud_weapon.c")
set(GEAR_RAY_HUD_WEAPON_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/hud_weapon.h")
set(GEAR_RAY_HUD_WEAPON_OBJECT "${CMAKE_BINARY_DIR}/hud_weapon.rel")
set(GEAR_RAY_SPRITE_PROJECTION_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/sprite_projection.c")
set(GEAR_RAY_SPRITE_PROJECTION_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/sprite_projection.h")
set(GEAR_RAY_SPRITE_PROJECTION_OBJECT "${CMAKE_BINARY_DIR}/sprite_projection.rel")
set(GEAR_RAY_RENDER_TEXTURES_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/render_textures.c")
set(GEAR_RAY_RENDER_TEXTURES_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/render_textures.h")
set(GEAR_RAY_RENDER_TEXTURES_OBJECT "${CMAKE_BINARY_DIR}/render_textures.rel")
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
set(GEAR_RAY_ZOMBIE_AI_VALIDATOR "${CMAKE_SOURCE_DIR}/tools/validate_zombie_ai.ps1")
set(GEAR_RAY_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
set(GEAR_RAY_SEGA_LOGO_INPUT "${CMAKE_SOURCE_DIR}/assets/logos/sega_logo.png")
set(GEAR_RAY_STARTUP_LOGO_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_startup_logo.ps1")
set(GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE "${GEAR_RAY_GENERATED_DIR}/sega_logo.c")
set(GEAR_RAY_GENERATED_SEGA_LOGO_HEADER "${GEAR_RAY_GENERATED_DIR}/sega_logo.h")
set(GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT "${CMAKE_BINARY_DIR}/generated_sega_logo.rel")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/wall_texture.c")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/wall_texture.h")
set(GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_wall_texture.rel")
set(GEAR_RAY_SPRITE_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/enemies/zombie/zombie_01_standing.png")
set(GEAR_RAY_SPRITE_TEXTURE_GENERATOR "${CMAKE_SOURCE_DIR}/tools/generate_sprite_texture.ps1")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/sprite_texture.c")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/sprite_texture.h")
set(GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_sprite_texture.rel")
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
set(GEAR_RAY_GENERATED_WEAPON_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_weapon_texture.rel")
set(GEAR_RAY_WEAPON_SHOOT_TEXTURE_INPUT "${CMAKE_SOURCE_DIR}/assets/sprites/weapons/gun_shoot_12x12.png")
set(GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.c")
set(GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER "${GEAR_RAY_GENERATED_DIR}/weapon_shoot_texture.h")
set(GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_OBJECT "${CMAKE_BINARY_DIR}/generated_weapon_shoot_texture.rel")
set(GEAR_RAY_VRAM_LAYOUT_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/vram_layout.h")
set(GEAR_RAY_IHX "${CMAKE_BINARY_DIR}/GearRay.ihx")
set(GEAR_RAY_ROM_DIR "${CMAKE_SOURCE_DIR}/rom")
set(GEAR_RAY_ROM "${GEAR_RAY_ROM_DIR}/${GEAR_RAY_ROM_FILENAME}")

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
            -c "${GEAR_RAY_CAMERA_SOURCE}"
            -o "${GEAR_RAY_CAMERA_OBJECT}"
    DEPENDS "${GEAR_RAY_CAMERA_SOURCE}" "${GEAR_RAY_CAMERA_HEADER}"
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
    OUTPUT "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            -c "${GEAR_RAY_WORKSHOP_MAP_SOURCE}"
            -o "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
    DEPENDS "${GEAR_RAY_WORKSHOP_MAP_SOURCE}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
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
            "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_HEADER}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_HEADER}"
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
            --codeseg BANK1
            -c "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            -o "${GEAR_RAY_ZOMBIE_AI_OBJECT}"
    DEPENDS "${GEAR_RAY_ZOMBIE_AI_SOURCE}"
            "${GEAR_RAY_ZOMBIE_AI_HEADER}"
            "${GEAR_RAY_PLAYER_HEADER}"
            "${GEAR_RAY_ENEMY_COLLISION_HEADER}"
            "${GEAR_RAY_WORLD_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
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
            -c "${GEAR_RAY_VIDEO_SOURCE}"
            -o "${GEAR_RAY_VIDEO_OBJECT}"
    DEPENDS "${GEAR_RAY_VIDEO_SOURCE}" "${GEAR_RAY_VIDEO_HEADER}" "${GEAR_RAY_HUD_WEAPON_HEADER}" "${GEAR_RAY_SPRITE_PROJECTION_HEADER}" "${GEAR_RAY_RENDER_TEXTURES_HEADER}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_VRAM_LAYOUT_HEADER}" "${GEAR_RAY_WALL_TEXTURES_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_WALL_SIDE_HEADER}" "${GEAR_RAY_WORLD_SPRITE_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling platform/game_gear/video.c"
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
            --codeseg BANK1
            --constseg BANK1
            -c "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            -o "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"
    DEPENDS "${GEAR_RAY_SPRITE_PROJECTION_SOURCE}"
            "${GEAR_RAY_SPRITE_PROJECTION_HEADER}"
            "${GEAR_RAY_VIDEO_HEADER}"
            "${GEAR_RAY_CAMERA_HEADER}"
            "${GEAR_RAY_WORLD_SPRITE_HEADER}"
    COMMENT "Compiling banked static sprite projection"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            ${GEAR_RAY_RENDERER_PROFILE_DEFINE}
            ${GEAR_RAY_RENDERER_PROFILE_SIZE_OPTIMIZATION}
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            "-I${GEAR_RAY_GENERATED_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_RENDER_TEXTURES_SOURCE}"
            -o "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
    DEPENDS "${GEAR_RAY_RENDER_TEXTURES_SOURCE}" "${GEAR_RAY_RENDER_TEXTURES_HEADER}" "${GEAR_RAY_WALL_SIDE_HEADER}" "${GEAR_RAY_RENDERER_PROFILE_HEADER}" "${GEAR_RAY_WALL_TEXTURES_HEADER}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
    COMMENT "Compiling platform/game_gear/render_textures.c"
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
            --constseg BANK1
            -c "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
            -o "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_SEGA_LOGO_SOURCE}"
            "${GEAR_RAY_GENERATED_SEGA_LOGO_HEADER}"
    COMMENT "Compiling generated SEGA startup logo"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
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
    DEPENDS "${GEAR_RAY_WALL_TEXTURE_INPUT}" "${GEAR_RAY_BLOOD_WALL_TEXTURE_INPUT}" "${GEAR_RAY_DOOR_TEXTURE_INPUT}" "${GEAR_RAY_RED_DOOR_TEXTURE_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_1_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_OFF_FRAME_2_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_1_INPUT}" "${GEAR_RAY_RED_DOOR_SWITCH_ON_FRAME_2_INPUT}" "${GEAR_RAY_WALL_TEXTURE_GENERATOR}"
    COMMENT "Generating packed 4bpp indexed-color wall texture"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            -c "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}"
            -o "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_WALL_TEXTURE_SOURCE}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_HEADER}"
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
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating packed static HUD weapon"
    VERBATIM
)

foreach(zombie_state IN ITEMS SHOT_01 SHOT_02 SHOT_DEAD CORPS)
    string(TOLOWER "${zombie_state}" zombie_state_lower)
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
    OUTPUT "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK1
            -c "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_SOURCE}"
            -o "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_SOURCE}"
            "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_HEADER}"
    COMMENT "Compiling generated static HUD weapon"
    VERBATIM
)

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
            "${GEAR_RAY_SPRITE_TEXTURE_GENERATOR}"
    COMMENT "Generating packed shooting HUD weapon"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            "-I${GEAR_RAY_GENERATED_DIR}"
            --constseg BANK1
            -c "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE}"
            -o "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_OBJECT}"
    DEPENDS "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_SOURCE}"
            "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_HEADER}"
    COMMENT "Compiling generated shooting HUD weapon"
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
    DEPENDS "${GEAR_RAY_WORLD_INTERACTIONS_SOURCE}" "${GEAR_RAY_WORLD_INTERACTIONS_HEADER}" "${GEAR_RAY_INTERACTION_TARGET_HEADER}" "${GEAR_RAY_RED_DOOR_SWITCH_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_WORKSHOP_MAP_HEADER}" "${GEAR_RAY_WORLD_OBJECTS_HEADER}" "${GEAR_RAY_WORLD_OBJECT_HEADER}" "${GEAR_RAY_DOOR_INSTANCES_HEADER}" "${GEAR_RAY_DOOR_STATES_HEADER}"
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
            --codeseg BANK1
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

add_custom_command(
    OUTPUT "${GEAR_RAY_IHX}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -o "${GEAR_RAY_IHX}"
            -mz80
            --no-std-crt0
            --data-loc 0xC000
            -Wl-b_BANK1=0x14000
            "${GEAR_RAY_CRT0}"
            "${GEAR_RAY_MAIN_OBJECT}"
            "${GEAR_RAY_CAMERA_OBJECT}"
            "${GEAR_RAY_RAYCASTER_OBJECT}"
            "${GEAR_RAY_PLAYER_OBJECT}"
            "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}"
            "${GEAR_RAY_WORLD_OBJECT}"
            "${GEAR_RAY_WORKSHOP_MAP_OBJECT}"
            "${GEAR_RAY_WORLD_OBJECTS_OBJECT}"
            "${GEAR_RAY_WORLD_SPRITE_OBJECT}"
            "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}"
            "${GEAR_RAY_ZOMBIE_AI_OBJECT}"
            "${GEAR_RAY_ENEMY_COLLISION_OBJECT}"
            "${GEAR_RAY_DOOR_INSTANCES_OBJECT}"
            "${GEAR_RAY_DOOR_STATES_OBJECT}"
            "${GEAR_RAY_INPUT_OBJECT}"
            "${GEAR_RAY_VIDEO_OBJECT}"
            "${GEAR_RAY_HUD_WEAPON_OBJECT}"
            "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}"
            "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
            "${GEAR_RAY_WALL_TEXTURES_OBJECT}"
            "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}"
            "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_OBJECT}"
            "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_OBJECT}"
            "${GEAR_RAY_SMSLIB_LIBRARY}"
            "${GEAR_RAY_STARTUP_LOGO_OBJECT}"
            "${GEAR_RAY_INTERACTION_RAY_OBJECT}"
            "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}"
            ${GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT}
    DEPENDS "${GEAR_RAY_MAIN_OBJECT}" "${GEAR_RAY_CAMERA_OBJECT}" "${GEAR_RAY_RAYCASTER_OBJECT}" "${GEAR_RAY_PLAYER_OBJECT}" "${GEAR_RAY_RED_DOOR_SWITCH_OBJECT}" "${GEAR_RAY_STARTUP_LOGO_OBJECT}" "${GEAR_RAY_INTERACTION_RAY_OBJECT}" "${GEAR_RAY_WORLD_INTERACTIONS_OBJECT}" "${GEAR_RAY_WORLD_OBJECT}" "${GEAR_RAY_WORKSHOP_MAP_OBJECT}" "${GEAR_RAY_WORLD_OBJECTS_OBJECT}" "${GEAR_RAY_WORLD_SPRITE_OBJECT}" "${GEAR_RAY_ZOMBIE_SHOOTING_OBJECT}" "${GEAR_RAY_ZOMBIE_AI_OBJECT}" "${GEAR_RAY_ENEMY_COLLISION_OBJECT}" "${GEAR_RAY_DOOR_INSTANCES_OBJECT}" "${GEAR_RAY_DOOR_STATES_OBJECT}" "${GEAR_RAY_INPUT_OBJECT}" "${GEAR_RAY_VIDEO_OBJECT}" "${GEAR_RAY_HUD_WEAPON_OBJECT}" "${GEAR_RAY_SPRITE_PROJECTION_OBJECT}" "${GEAR_RAY_RENDER_TEXTURES_OBJECT}" ${GEAR_RAY_RENDERER_PROFILE_LINK_OBJECT} "${GEAR_RAY_WALL_TEXTURES_OBJECT}" "${GEAR_RAY_GENERATED_SEGA_LOGO_OBJECT}" "${GEAR_RAY_GENERATED_WALL_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_SPRITE_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_01_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_02_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_ZOMBIE_SHOT_DEAD_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_ZOMBIE_CORPS_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_WEAPON_TEXTURE_OBJECT}" "${GEAR_RAY_GENERATED_WEAPON_SHOOT_TEXTURE_OBJECT}" "${GEAR_RAY_CRT0}" "${GEAR_RAY_SMSLIB_LIBRARY}"
    COMMENT "Linking GearRay for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ROM}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${GEAR_RAY_ROM_DIR}"
    COMMAND "${GEAR_RAY_MAKESMS_EXECUTABLE}" "${GEAR_RAY_IHX}" "${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_IHX}"
    COMMENT "Generating rom/${GEAR_RAY_ROM_FILENAME}"
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
add_dependencies(gear_ray_game gear_ray_engine gear_ray_validate_workshop
                 gear_ray_validate_zombie_shooting
                 gear_ray_validate_zombie_ai)

add_custom_target(gear_ray_info ALL
    COMMAND "${CMAKE_COMMAND}" -E echo "GearRay Game Gear ROM: ${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_ROM}"
    VERBATIM
)

cmake_minimum_required(VERSION 3.20)

# SDCC is driven explicitly below, so CMake does not need a host compiler.
project(gear_ray VERSION 0.1.0 LANGUAGES NONE)

set(GEAR_RAY_BUILD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Generated build output directory")
set(GEAR_RAY_DEVKITSMS_ROOT "D:/Tools/devkitSMS" CACHE PATH "Path to the local devkitSMS installation")
set(GEAR_RAY_MAKESMS_EXECUTABLE "${GEAR_RAY_DEVKITSMS_ROOT}/makesms/Windows/makesms.exe" CACHE FILEPATH "Path to makesms.exe")

find_program(GEAR_RAY_SDCC_EXECUTABLE NAMES sdcc DOC "Path to SDCC executable")
if(NOT GEAR_RAY_SDCC_EXECUTABLE)
    message(FATAL_ERROR "SDCC was not found on PATH.")
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
set(GEAR_RAY_PLAYER_SOURCE "${GEAR_RAY_GAME_DIR}/player.c")
set(GEAR_RAY_PLAYER_HEADER "${GEAR_RAY_GAME_DIR}/player.h")
set(GEAR_RAY_PLAYER_OBJECT "${CMAKE_BINARY_DIR}/player.rel")
set(GEAR_RAY_WORLD_SOURCE "${GEAR_RAY_GAME_DIR}/world.c")
set(GEAR_RAY_WORLD_HEADER "${GEAR_RAY_GAME_DIR}/world.h")
set(GEAR_RAY_WORLD_OBJECT "${CMAKE_BINARY_DIR}/world.rel")
set(GEAR_RAY_INPUT_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input.c")
set(GEAR_RAY_INPUT_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/input.h")
set(GEAR_RAY_INPUT_OBJECT "${CMAKE_BINARY_DIR}/input.rel")
set(GEAR_RAY_VIDEO_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.c")
set(GEAR_RAY_VIDEO_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/video.h")
set(GEAR_RAY_VIDEO_OBJECT "${CMAKE_BINARY_DIR}/video.rel")
set(GEAR_RAY_RENDER_TEXTURES_SOURCE "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/render_textures.c")
set(GEAR_RAY_RENDER_TEXTURES_HEADER "${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}/render_textures.h")
set(GEAR_RAY_RENDER_TEXTURES_OBJECT "${CMAKE_BINARY_DIR}/render_textures.rel")
set(GEAR_RAY_IHX "${CMAKE_BINARY_DIR}/GearRay.ihx")
set(GEAR_RAY_ROM_DIR "${CMAKE_SOURCE_DIR}/rom")
set(GEAR_RAY_ROM "${GEAR_RAY_ROM_DIR}/GearRay.gg")

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
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_MAIN_SOURCE}"
            -o "${GEAR_RAY_MAIN_OBJECT}"
    DEPENDS "${GEAR_RAY_MAIN_SOURCE}" "${GEAR_RAY_CAMERA_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_PLAYER_HEADER}" "${GEAR_RAY_VIDEO_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/main.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RAYCASTER_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            -c "${GEAR_RAY_RAYCASTER_SOURCE}"
            -o "${GEAR_RAY_RAYCASTER_OBJECT}"
    DEPENDS "${GEAR_RAY_RAYCASTER_SOURCE}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_CAMERA_HEADER}" "${GEAR_RAY_WORLD_HEADER}"
    COMMENT "Compiling engine/render/raycaster.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_CAMERA_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
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
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_WORLD_SOURCE}"
            -o "${GEAR_RAY_WORLD_OBJECT}"
    DEPENDS "${GEAR_RAY_WORLD_SOURCE}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/world.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_VIDEO_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_VIDEO_SOURCE}"
            -o "${GEAR_RAY_VIDEO_OBJECT}"
    DEPENDS "${GEAR_RAY_VIDEO_SOURCE}" "${GEAR_RAY_VIDEO_HEADER}" "${GEAR_RAY_RENDER_TEXTURES_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling platform/game_gear/video.c"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            "-I${GEAR_RAY_RENDER_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_RENDER_TEXTURES_SOURCE}"
            -o "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
    DEPENDS "${GEAR_RAY_RENDER_TEXTURES_SOURCE}" "${GEAR_RAY_RENDER_TEXTURES_HEADER}" "${GEAR_RAY_RAYCASTER_HEADER}" "${GEAR_RAY_WORLD_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling platform/game_gear/render_textures.c"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_PLAYER_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            "-I${GEAR_RAY_GAME_GEAR_PLATFORM_DIR}"
            "-I${GEAR_RAY_GAME_DIR}"
            --peep-file "${GEAR_RAY_SMSLIB_INCLUDE}/peep-rules.txt"
            -c "${GEAR_RAY_PLAYER_SOURCE}"
            -o "${GEAR_RAY_PLAYER_OBJECT}"
    DEPENDS "${GEAR_RAY_PLAYER_SOURCE}" "${GEAR_RAY_PLAYER_HEADER}" "${GEAR_RAY_INPUT_HEADER}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/player.c for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_INPUT_OBJECT}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -mz80
            -DTARGET_GG
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
    OUTPUT "${GEAR_RAY_IHX}"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}"
            -o "${GEAR_RAY_IHX}"
            -mz80
            --no-std-crt0
            --data-loc 0xC000
            "${GEAR_RAY_CRT0}"
            "${GEAR_RAY_MAIN_OBJECT}"
            "${GEAR_RAY_CAMERA_OBJECT}"
            "${GEAR_RAY_RAYCASTER_OBJECT}"
            "${GEAR_RAY_PLAYER_OBJECT}"
            "${GEAR_RAY_WORLD_OBJECT}"
            "${GEAR_RAY_INPUT_OBJECT}"
            "${GEAR_RAY_VIDEO_OBJECT}"
            "${GEAR_RAY_RENDER_TEXTURES_OBJECT}"
            "${GEAR_RAY_SMSLIB_LIBRARY}"
    DEPENDS "${GEAR_RAY_MAIN_OBJECT}" "${GEAR_RAY_CAMERA_OBJECT}" "${GEAR_RAY_RAYCASTER_OBJECT}" "${GEAR_RAY_PLAYER_OBJECT}" "${GEAR_RAY_WORLD_OBJECT}" "${GEAR_RAY_INPUT_OBJECT}" "${GEAR_RAY_VIDEO_OBJECT}" "${GEAR_RAY_RENDER_TEXTURES_OBJECT}" "${GEAR_RAY_CRT0}" "${GEAR_RAY_SMSLIB_LIBRARY}"
    COMMENT "Linking GearRay for Game Gear"
    VERBATIM
)

add_custom_command(
    OUTPUT "${GEAR_RAY_ROM}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${GEAR_RAY_ROM_DIR}"
    COMMAND "${GEAR_RAY_MAKESMS_EXECUTABLE}" "${GEAR_RAY_IHX}" "${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_IHX}"
    COMMENT "Generating rom/GearRay.gg"
    VERBATIM
)

# Preserve the existing project target structure while making the game target real.
add_custom_target(gear_ray_engine)
add_custom_target(gear_ray_game ALL DEPENDS "${GEAR_RAY_ROM}")
add_dependencies(gear_ray_game gear_ray_engine)

add_custom_target(gear_ray_info ALL
    COMMAND "${CMAKE_COMMAND}" -E echo "GearRay Game Gear ROM: ${GEAR_RAY_ROM}"
    DEPENDS "${GEAR_RAY_ROM}"
    VERBATIM
)

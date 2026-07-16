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
set(GEAR_RAY_MAIN_SOURCE "${CMAKE_SOURCE_DIR}/game/main.c")
set(GEAR_RAY_MAIN_OBJECT "${CMAKE_BINARY_DIR}/main.rel")
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
            --sdcccall 0
            -DTARGET_GG
            "-I${GEAR_RAY_SMSLIB_INCLUDE}"
            -c "${GEAR_RAY_MAIN_SOURCE}"
            -o "${GEAR_RAY_MAIN_OBJECT}"
    # Current SDCC records sdcccall(0), while the ABI-0 devkit archive predates
    # that metadata field. Normalize the tag so ASlink accepts the compatible objects.
    COMMAND powershell -NoProfile -Command
            "(Get-Content -Raw -LiteralPath '${GEAR_RAY_MAIN_OBJECT}').Replace('O -mz80 sdcccall(0)', 'O -mz80') | Set-Content -NoNewline -LiteralPath '${GEAR_RAY_MAIN_OBJECT}' -Encoding ascii"
    DEPENDS "${GEAR_RAY_MAIN_SOURCE}" "${GEAR_RAY_SMSLIB_INCLUDE}/SMSlib.h"
    COMMENT "Compiling game/main.c for Game Gear"
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
            "${GEAR_RAY_SMSLIB_LIBRARY}"
    DEPENDS "${GEAR_RAY_MAIN_OBJECT}" "${GEAR_RAY_CRT0}" "${GEAR_RAY_SMSLIB_LIBRARY}"
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

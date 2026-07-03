cmake_minimum_required(VERSION 3.20)

# GearRay uses CMake as the main build entry point.
#
# LANGUAGES NONE is intentional for this foundation step. The project does not
# require a host C compiler yet. SDCC and devkitSMS are detected below so the
# local Game Gear toolchain is validated before real source targets are added.
project(gear_ray VERSION 0.1.0 LANGUAGES NONE)

# Keep generated files out of the source tree. build.bat configures this same
# path so beginners see one predictable build folder.
set(GEAR_RAY_BUILD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Generated build output directory")

# This option documents the missing ROM packaging stage without pretending it
# exists. It is OFF by default and there are no commands that call ihx2sms.exe.
option(GEAR_RAY_ENABLE_ROM_PACKAGING "Enable future Game Gear ROM packaging steps" OFF)

set(GEAR_RAY_DEVKITSMS_ROOT "D:/Tools/devkitSMS" CACHE PATH "Path to the local devkitSMS installation")
set(GEAR_RAY_MAKESMS_EXECUTABLE "${GEAR_RAY_DEVKITSMS_ROOT}/makesms/Windows/makesms.exe" CACHE FILEPATH "Path to makesms.exe")
set(GEAR_RAY_IHX2SMS_EXECUTABLE "${GEAR_RAY_DEVKITSMS_ROOT}/ihx2sms/Windows/ihx2sms.exe" CACHE FILEPATH "Path to ihx2sms.exe")

# Folder guide for contributors:
# - engine/: reusable raycasting engine code and low-level Game Gear helpers.
# - game/: sample game logic that calls into the engine.
# - assets/: original art, maps, palettes, sound data, and conversion sources.
# - source/: early scratch source kept out of the build until the toolchain is chosen.
# - tools/: helper scripts and future asset conversion utilities.
# - docs/: notes, explanations, and build documentation.

message(STATUS "Configuring GearRay ${PROJECT_VERSION}")
message(STATUS "Build directory: ${GEAR_RAY_BUILD_DIR}")
message(STATUS "ROM packaging enabled: ${GEAR_RAY_ENABLE_ROM_PACKAGING}")
message(STATUS "No Game Gear ROM is produced by this foundation build.")

find_program(GEAR_RAY_SDCC_EXECUTABLE NAMES sdcc DOC "Path to SDCC executable")
if(NOT GEAR_RAY_SDCC_EXECUTABLE)
    message(FATAL_ERROR
        "SDCC was not found on PATH. "
        "Install SDCC and make sure sdcc.exe is available from your terminal."
    )
endif()
message(STATUS "SDCC found: ${GEAR_RAY_SDCC_EXECUTABLE}")

if(NOT IS_DIRECTORY "${GEAR_RAY_DEVKITSMS_ROOT}")
    message(FATAL_ERROR
        "devkitSMS was not found at '${GEAR_RAY_DEVKITSMS_ROOT}'. "
        "Install devkitSMS at D:/Tools/devkitSMS or configure GEAR_RAY_DEVKITSMS_ROOT."
    )
endif()
message(STATUS "devkitSMS found: ${GEAR_RAY_DEVKITSMS_ROOT}")

if(NOT EXISTS "${GEAR_RAY_MAKESMS_EXECUTABLE}")
    message(FATAL_ERROR
        "makesms.exe was not found at '${GEAR_RAY_MAKESMS_EXECUTABLE}'. "
        "Expected default path: D:/Tools/devkitSMS/makesms/Windows/makesms.exe"
    )
endif()
message(STATUS "makesms found: ${GEAR_RAY_MAKESMS_EXECUTABLE}")

if(NOT EXISTS "${GEAR_RAY_IHX2SMS_EXECUTABLE}")
    message(FATAL_ERROR
        "ihx2sms.exe was not found at '${GEAR_RAY_IHX2SMS_EXECUTABLE}'. "
        "Expected default path: D:/Tools/devkitSMS/ihx2sms/Windows/ihx2sms.exe"
    )
endif()
message(STATUS "ihx2sms found: ${GEAR_RAY_IHX2SMS_EXECUTABLE}")

# gear_ray_info is a friendly status target. It is part of the default build so
# running either 'cmake --build build' or 'build.bat' gives useful feedback.
add_custom_target(gear_ray_info ALL
    COMMAND ${CMAKE_COMMAND} -E echo "GearRay CMake foundation is configured."
    COMMAND ${CMAKE_COMMAND} -E echo "Targets: gear_ray_info, gear_ray_engine, gear_ray_game"
    COMMAND ${CMAKE_COMMAND} -E echo "No ROM generation is configured yet."
    VERBATIM
)

# gear_ray_engine is a placeholder for the reusable raycasting engine. It does
# not compile source files yet because the Game Gear C/Z80 toolchain has not
# been selected.
add_custom_target(gear_ray_engine
    COMMAND ${CMAKE_COMMAND} -E echo "gear_ray_engine placeholder: add engine sources after the toolchain is chosen."
    VERBATIM
)

# gear_ray_game is a placeholder for the sample game layer. It depends on the
# engine placeholder to show the intended build order without producing output.
add_custom_target(gear_ray_game
    COMMAND ${CMAKE_COMMAND} -E echo "gear_ray_game placeholder: add game sources after the engine target is real."
    VERBATIM
)
add_dependencies(gear_ray_game gear_ray_engine)

# Keep the future packaging branch explicit. This prevents accidental reliance
# on ihx2sms.exe while leaving a clear hook for the later implementation.
if(GEAR_RAY_ENABLE_ROM_PACKAGING)
    message(FATAL_ERROR
        "ROM packaging is not implemented yet. "
        "Do not enable GEAR_RAY_ENABLE_ROM_PACKAGING until the converter/toolchain is documented."
    )
endif()

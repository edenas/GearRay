cmake_minimum_required(VERSION 3.20)

# GearRay uses CMake as the main build entry point.
#
# LANGUAGES NONE is intentional for this foundation step. The project does not
# require a host C compiler, SDCC, devkitSMS, or a ROM converter yet. When the
# Game Gear toolchain is chosen, this can become LANGUAGES C and real source
# files can be attached to the targets below.
project(GearRay VERSION 0.1.0 LANGUAGES NONE)

# Keep generated files out of the source tree. build.bat configures this same
# path so beginners see one predictable build folder.
set(GEARRAY_BUILD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Generated build output directory")

# This option documents the missing ROM packaging stage without pretending it
# exists. It is OFF by default and there are no commands that call ihx2sms.exe.
option(GEARRAY_ENABLE_ROM_PACKAGING "Enable future Game Gear ROM packaging steps" OFF)

# Folder guide for contributors:
# - engine/: reusable raycasting engine code and low-level Game Gear helpers.
# - game/: sample game logic that calls into the engine.
# - assets/: original art, maps, palettes, sound data, and conversion sources.
# - source/: early scratch source kept out of the build until the toolchain is chosen.
# - tools/: helper scripts and future asset conversion utilities.
# - docs/: notes, explanations, and build documentation.

message(STATUS "Configuring GearRay ${PROJECT_VERSION}")
message(STATUS "Build directory: ${GEARRAY_BUILD_DIR}")
message(STATUS "ROM packaging enabled: ${GEARRAY_ENABLE_ROM_PACKAGING}")
message(STATUS "No Game Gear ROM is produced by this foundation build.")

# gearray-info is a friendly status target. It is part of the default build so
# running either 'cmake --build build' or 'build.bat' gives useful feedback.
add_custom_target(gearray-info ALL
    COMMAND ${CMAKE_COMMAND} -E echo "GearRay CMake foundation is configured."
    COMMAND ${CMAKE_COMMAND} -E echo "Targets: gearray-info, gearray-engine, gearray-game"
    COMMAND ${CMAKE_COMMAND} -E echo "No ROM generation is configured yet."
    VERBATIM
)

# gearray-engine is a placeholder for the reusable raycasting engine. It does
# not compile source files yet because the Game Gear C/Z80 toolchain has not
# been selected.
add_custom_target(gearray-engine
    COMMAND ${CMAKE_COMMAND} -E echo "gearray-engine placeholder: add engine sources after the toolchain is chosen."
    VERBATIM
)

# gearray-game is a placeholder for the sample game layer. It depends on the
# engine placeholder to show the intended build order without producing output.
add_custom_target(gearray-game
    COMMAND ${CMAKE_COMMAND} -E echo "gearray-game placeholder: add game sources after the engine target is real."
    VERBATIM
)
add_dependencies(gearray-game gearray-engine)

# Keep the future packaging branch explicit. This prevents accidental reliance
# on ihx2sms.exe while leaving a clear hook for the later implementation.
if(GEARRAY_ENABLE_ROM_PACKAGING)
    message(FATAL_ERROR
        "ROM packaging is not implemented yet. "
        "Do not enable GEARRAY_ENABLE_ROM_PACKAGING until the converter/toolchain is documented."
    )
endif()

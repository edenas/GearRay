cmake_minimum_required(VERSION 3.20)

# GearRay is a Sega Game Gear raycasting engine project. This CMake file is a
# beginner-friendly starting point and build checklist, not a complete ROM
# pipeline yet.
project(GearRay LANGUAGES C)

# Folder purposes:
# - engine/: reusable raycasting engine code and low-level Game Gear helpers.
# - game/: sample game logic that calls into the engine.
# - assets/: original art, maps, palettes, sound data, and conversion sources.
# - tools/: helper scripts and future asset conversion utilities.
# - docs/: notes, explanations, and build documentation.
# - build/: generated local build output.

set(GEARRAY_ROM_NAME "gearray" CACHE STRING "Base name for generated ROM files")

message(STATUS "Configuring GearRay")
message(STATUS "This is a starter build file. No ROM is produced yet.")
message(STATUS "TODO: choose and document the Game Gear Z80 toolchain.")
message(STATUS "TODO: add engine/game sources once they exist.")
message(STATUS "TODO: add asset conversion steps from tools/ and assets/.")
message(STATUS "TODO: add ROM packaging without assuming ihx2sms.exe exists.")

add_custom_target(gearray-info ALL
    COMMAND ${CMAKE_COMMAND} -E echo "GearRay project foundation configured."
    COMMAND ${CMAKE_COMMAND} -E echo "Next: install/document a Game Gear toolchain, then add sources."
    VERBATIM
)

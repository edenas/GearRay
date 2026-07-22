@echo off
echo GearRay renderer-profiling build launcher
echo.

cmake -S . -B build-profile -G Ninja ^
    -DGEARRAY_PROFILE_RENDERER=ON ^
    -DGEAR_RAY_ROM_FILENAME=GearRay-profile.gg
if errorlevel 1 exit /b 1

cmake --build build-profile
if errorlevel 1 exit /b 1

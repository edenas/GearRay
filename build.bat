@echo off
echo GearRay CMake build launcher
echo.

cmake -S . -B build -G Ninja ^
    -DGEARRAY_PROFILE_RENDERER=OFF ^
    -DGEAR_RAY_ROM_FILENAME=GearRay.gg
if errorlevel 1 exit /b 1

cmake --build build
if errorlevel 1 exit /b 1

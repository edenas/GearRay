@echo off
echo GearRay CMake build launcher
echo.

cmake -S . -B build -G Ninja
if errorlevel 1 exit /b 1

cmake --build build
if errorlevel 1 exit /b 1
@echo off
setlocal

rem GearRay Windows build launcher.
rem CMake is the main build system; this file only keeps the Windows workflow
rem beginner-friendly by running the two CMake commands in the right order.
rem It intentionally does not call SDCC, devkitSMS, ihx2sms.exe, or any ROM
rem packaging tool.

echo GearRay CMake build launcher
echo.

where cmake >nul 2>nul
if errorlevel 1 (
    echo CMake was not found on PATH.
    echo Install CMake, then run build.bat again.
    exit /b 1
)

cmake -S . -B build
if errorlevel 1 exit /b 1

cmake --build build
if errorlevel 1 exit /b 1

echo.
echo GearRay foundation build completed.
echo No Game Gear ROM was generated yet.

endlocal

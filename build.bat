@echo off
<<<<<<< HEAD
setlocal

rem GearRay Windows build helper.
rem This script is intentionally simple while the Game Gear toolchain is still
rem being chosen. It does not assume ihx2sms.exe or any specific compiler
rem exists yet.

echo GearRay build helper
echo.

where cmake >nul 2>nul
if errorlevel 1 (
    echo CMake was not found on PATH.
    echo.
    echo TODO: Install CMake or document the final Game Gear build toolchain.
    echo TODO: Choose the compiler/converter flow before producing ROM files.
    exit /b 1
)

if not exist build mkdir build

cmake -S . -B build
if errorlevel 1 exit /b 1

cmake --build build
if errorlevel 1 exit /b 1

echo.
echo Build foundation completed.
echo TODO: Add Game Gear compiler steps after the toolchain is selected.
echo TODO: Add ROM packaging later; ihx2sms.exe is not required yet.

endlocal
=======
set DEVKITSMS=D:\Tools\devkitSMS

if not exist build mkdir build
if not exist rom mkdir rom

sdcc -c -mz80 ^
-I"%DEVKITSMS%\SMSlib\src" ^
-o build\main.rel ^
source\main.c

sdcc -mz80 --no-std-crt0 ^
"%DEVKITSMS%\crt0\crt0_sms.rel" ^
build\main.rel ^
-L"%DEVKITSMS%\SMSlib\lib" ^
-lSMSlib ^
-o build\wolfgear.ihx

"%DEVKITSMS%\ihx2sms\ihx2sms.exe" build\wolfgear.ihx rom\wolfgear.gg

pause
>>>>>>> 830f9d25e45daac45bd0faf416a942fd29ba4927

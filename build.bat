@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 exit /b 1
echo GearRay Release build

cmake -S . -B build/release -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DGEARRAY_PROFILE_RENDERER=OFF ^
    -DGEAR_RAY_ROM_FILENAME=GearRay.gg ^
    "-DGEAR_RAY_ROM_DIR=%CD%/rom"
if errorlevel 1 goto failed

cmake --build build/release
if errorlevel 1 goto failed
popd
exit /b 0
:failed
popd
exit /b 1

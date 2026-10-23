@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 exit /b 1
echo GearRay diagnostic profiling build

cmake -S . -B build/profile -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DGEARRAY_PROFILE_RENDERER=ON ^
    -DGEAR_RAY_ROM_FILENAME=GearRay-profile.gg ^
    "-DGEAR_RAY_ROM_DIR=%CD%/build/profile/rom"
if errorlevel 1 goto failed

cmake --build build/profile
if errorlevel 1 goto failed
popd
exit /b 0
:failed
popd
exit /b 1

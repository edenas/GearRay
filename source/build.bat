@echo off
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
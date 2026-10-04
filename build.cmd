@echo off
rem Build of the SAPI-1 port: build\bomber.com (CP/M) and build\bomber.hex (Intel HEX, from 0100h).
rem PASMO can be set in the environment, default E:\SAPI_GIT\Tools\pasmo-0.5.3\pasmo.exe.
setlocal
cd /d "%~dp0"
if "%PASMO%"=="" set PASMO=E:\SAPI_GIT\Tools\pasmo-0.5.3\pasmo.exe
if not exist build mkdir build
python tools\make_tables.py || exit /b 1
pushd sapi
"%PASMO%" --bin bomber_sapi.asm ..\build\bomber.com ..\build\bomber.sym || (popd & exit /b 1)
"%PASMO%" --hex bomber_sapi.asm ..\build\bomber.hex || (popd & exit /b 1)
popd
for %%f in (build\bomber.com) do set SIZE=%%~zf
set /a PAGES=(SIZE+255)/256
echo build\bomber.com: %SIZE% bytes, in CP/M: SAVE %PAGES% BOMBER.COM

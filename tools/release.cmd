@echo off
rem Release package: builds the game and makes build\SAPI-Bomberman-<VERSION>.zip
rem (BOMBER.COM, bomber.hex, README.md, CHANGELOG.md). The version is also in CHANGELOG.md.
setlocal
set VERSION=1.0.0
cd /d "%~dp0.."
call "%~dp0..\build.cmd" || exit /b 1
set PKG=build\SAPI-Bomberman-%VERSION%
if exist "%PKG%" rmdir /s /q "%PKG%"
mkdir "%PKG%"
copy /y build\bomber.com "%PKG%\BOMBER.COM" >nul
copy /y build\bomber.hex "%PKG%\bomber.hex" >nul
copy /y README.md "%PKG%\README.md" >nul
copy /y CHANGELOG.md "%PKG%\CHANGELOG.md" >nul
if exist "%PKG%.zip" del "%PKG%.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%PKG%\*' -DestinationPath '%PKG%.zip'" || exit /b 1
echo %PKG%.zip

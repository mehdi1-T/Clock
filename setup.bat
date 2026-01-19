@echo off
REM -------------------------------
REM Setup Clock Shortcut for EXE
REM -------------------------------

echo Creating desktop shortcut for Clock...
echo.

REM Get the folder of this bat file
set "FOLDER=%~dp0"
set "EXE=%FOLDER%dist\main.exe"

REM Check if the EXE exists
if not exist "%EXE%" (
    echo ERROR: "%EXE%" not found!
    echo Please make sure main.exe is in the dist folder.
    pause
    exit /b 1
)

REM Create desktop shortcut using PowerShell (single line)
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ShortcutPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Clock.lnk'); if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath -Force }; $shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut($ShortcutPath); $shortcut.TargetPath = '%EXE%'; $shortcut.WorkingDirectory = [System.IO.Path]::GetDirectoryName('%EXE%'); $shortcut.IconLocation = '%EXE%'; $shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! Shortcut created on your Desktop, but dont forget be focus.
) else (
    echo.
    echo ERROR: Failed to create shortcut.
)

echo.
pause
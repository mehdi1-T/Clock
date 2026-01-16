@echo off
REM -------------------------------
REM Setup Clock Shortcut
REM -------------------------------

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3 first
    pause
    exit
)

REM Get the folder of this bat file
set FOLDER=%~dp0
set SCRIPT=%FOLDER%clock.py

REM Create desktop shortcut using PowerShell
powershell -Command ^
"$s=(New-Object -COM WScript.Shell).CreateShortcut('$env:USERPROFILE\Desktop\Clock.lnk'); ^
$s.TargetPath='python.exe'; ^
$s.Arguments='$SCRIPT'; ^
$s.WorkingDirectory='$FOLDER'; ^
$s.IconLocation='$SCRIPT'; ^
$s.Save()"

echo Shortcut created on your Desktop! 
pause

@echo off
REM Create a sibling clone of the Yaram Browser project and add run_clone.bat inside it
setlocal enabledelayedexpansion
set SRC=%~dp0
REM create destination in parent folder with random suffix to avoid collisions
for /f "tokens=*" %%R in ('echo %RANDOM%') do set RAND=%%R
set DEST=%~dp0..\Yaram_Browser_Clone_!RAND!
REM normalize to full path
pushd "%~dp0.."
set DEST_FULL=%cd%\Yaram_Browser_Clone_!RAND!
popd
if exist "%DEST_FULL%" rd /s /q "%DEST_FULL%"
mkdir "%DEST_FULL%"

echo Copying project files to "%DEST_FULL%" ...
xcopy "%SRC%*" "%DEST_FULL%\" /E /H /I /Y >nul

REM Create run_clone.bat inside the clone
set RUN_BAT=%DEST_FULL%\run_clone.bat
(
    echo @echo off
    echo cd /d "%DEST_FULL%"
    echo py yaram_browser.py
    echo pause
) > "%RUN_BAT%"

echo Clone created at: %DEST_FULL%
echo A launcher `run_clone.bat` was created inside the clone.
endlocal
pause

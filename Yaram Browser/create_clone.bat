@echo off
REM Create a fresh clone of the Yaram Browser project for testing
setlocal
set SRC=%~dp0
set DEST=%~dp0Yaram_Browser_Clone
if exist "%DEST%" rd /s /q "%DEST%"
mkdir "%DEST%"
echo Copying project files from "%SRC%" to "%DEST%" ...
xcopy "%SRC%*" "%DEST%\" /E /H /I /Y
echo Clone created at: %DEST%
endlocal
pause

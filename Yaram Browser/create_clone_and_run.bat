@echo off
REM Create a clone and immediately run the cloned browser for testing
setlocal
set SRC=%~dp0
set DEST=%~dp0Yaram_Browser_Clone
if exist "%DEST%" rd /s /q "%DEST%"
mkdir "%DEST%"
echo Copying project files from "%SRC%" to "%DEST%" ...
xcopy "%SRC%*" "%DEST%\" /E /H /I /Y
echo Starting cloned Yaram Browser...
pushd "%DEST%"
py yaram_browser.py
popd
endlocal

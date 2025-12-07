echo Starting Yaram Browser...
@echo off
REM Yaram Browser Starter
REM Reminder: New visitors will see the setup wizard on first run.
REM After completing setup, the wizard will not appear again for this user.

echo NOTE: On first run the Yaram setup wizard will appear for new users.
echo It will not show again after setup is completed for this user.

cd /d "%~dp0"
py yaram_browser.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting browser. Make sure Python and required packages are installed.
    pause
)

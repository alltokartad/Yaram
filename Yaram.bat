@echo off
title Yaram Control Panel
REM Yaram.bat - All-in-one control script for Yaram Browser
cd /d "%~dp0"

:menu
cls
echo ==========================
echo   Yaram Control Panel
echo ==========================
echo.
echo 1) Start Yaram Browser
echo 2) Run Setup Wizard
echo 3) Create/Update Desktop Launcher (Run Yaram Browser.bat)
echo 4) Create Sibling Clone (safe)
echo 5) Create Clone and Run
echo 6) Install dependencies (requirements.txt)
echo 7) Create project run.bat (run.bat)
echo 8) Exit
echo.
set /p choice=Choose an option [1-8]: 
if "%choice%"=="1" goto start_browser
if "%choice%"=="2" goto run_setup
if "%choice%"=="3" goto create_launcher
if "%choice%"=="4" goto create_clone
if "%choice%"=="5" goto create_clone_and_run
if "%choice%"=="6" goto install_deps
if "%choice%"=="7" goto create_runbat
if "%choice%"=="8" goto end
goto menu

:start_browser
echo Starting Yaram Browser...
py yaram_browser.py
echo Returned with exit code %ERRORLEVEL%
pause
goto menu

:run_setup
echo Launching Setup Wizard...
py setup_wizard.py
echo Setup wizard finished (or was closed).
pause
goto menu

:create_launcher
set desktop=%USERPROFILE%\Desktop
set target=%desktop%\Run Yaram Browser.bat
echo Creating Desktop launcher at %target%
if exist "%target%" (
  set /p overwrite=Launcher exists. Overwrite? (y/N): 
  if /I not "%overwrite%"=="y" (
    echo Keeping existing launcher.
    pause
    goto menu
  )
)
(
  echo @echo off
  echo cd /d "%~dp0"
  echo py yaram_browser.py
  echo pause
) > "%target%"
echo Desktop launcher written to %target%
pause
goto menu

:create_clone
echo Creating a safe sibling clone...
set rand=%RANDOM%
pushd "%~dp0.."
+set destfull=%cd%\Yaram_Browser_Clone_%rand%
+popd
if exist "%destfull%" rd /s /q "%destfull%"
mkdir "%destfull%"
echo Copying files...
xcopy "%~dp0*" "%destfull%\" /E /H /I /Y
echo Clone created at: %destfull%
pause
goto menu

:create_clone_and_run
echo Creating clone and running the cloned browser...
set rand=%RANDOM%
pushd "%~dp0.."
+set destfull=%cd%\Yaram_Browser_Clone_%rand%
+popd
if exist "%destfull%" rd /s /q "%destfull%"
mkdir "%destfull%"
+echo Copying files...
xcopy "%~dp0*" "%destfull%\" /E /H /I /Y
echo Starting cloned browser from %destfull%
pushd "%destfull%"
+py yaram_browser.py
popd
pause
goto menu

:install_deps
if not exist "requirements.txt" (
  echo requirements.txt not found in project folder.
  pause
  goto menu
)
echo Installing dependencies from requirements.txt (this uses pip)
py -m pip install -r requirements.txt
echo Done. Returned %ERRORLEVEL%
pause
goto menu

:create_runbat
echo Creating project run.bat in project folder...
set runpath=%~dp0run.bat
(
  echo @echo off
  echo REM Yaram Browser Starter
  echo echo NOTE: On first run the Yaram setup wizard will appear for new users.
  echo cd /d "%~dp0"
  echo py yaram_browser.py
  echo if %%ERRORLEVEL%% NEQ 0 (
  echo     echo.
  echo     echo Error starting browser. Make sure Python and required packages are installed.
  echo     pause
  echo )
) > "%runpath%"
echo Created %runpath%
pause
goto menu

:end
echo Goodbye.
exit /b 0


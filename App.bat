@echo off
:: Windows CLI Menu Wrapper for Dependency Check & Execution

:: Check for Python installation
echo Checking if Python is installed...
python --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    start https://www.python.org/downloads/
    echo Please install Python and rerun this script.
    exit /b
)

:: Check for required Python packages
echo Checking for required Python packages...

:: openrouteservice (ensure full install for exception module)
python -c "import openrouteservice; from openrouteservice import exceptions" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo openrouteservice or its submodules are missing. Installing now...
    pip install --upgrade openrouteservice
)

:: pandas
python -c "import pandas" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo pandas is missing. Installing now...
    pip install pandas
)

:: tqdm
python -c "import tqdm" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo tqdm is missing. Installing now...
    pip install tqdm
)

:: requests
python -c "import requests" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo requests is missing. Installing now...
    pip install requests
)

:: Menu for the user to select actions
:MENU
cls
echo ===========================
echo Select an option:
echo ===========================
echo 1. Run the OpenRouteService Distance Calculation
echo 2. Reset Progress Data (not export)
echo 3. View Help
echo 4. Exit
echo ===========================
set /p option=Choose an option (1/2/3/4):

:: Process the menu selection
IF "%option%"=="1" goto RUN_SCRIPT
IF "%option%"=="2" goto RESET_DATA
IF "%option%"=="3" goto HELP
IF "%option%"=="4" exit
goto MENU

:RUN_SCRIPT
cls
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
echo Running the OpenRouteService distance calculation...
python script.py %TIMESTAMP%
echo Distance calculation completed. Check the export folder for output.
pause
goto MENU

:RESET_DATA
cls
echo Resetting data (this will delete previous progress tracking but not exports)...
del /q data\*.json
del /q data\*.csv
echo Done. You may rerun the calculation from scratch.
pause
goto MENU

:HELP
cls
echo ===========================
echo Help:
echo ===========================
echo 1. This tool helps you calculate motorcycle route distances.
echo 2. It checks and installs required Python dependencies.
echo 3. Option 1 runs the calculator and auto-generates a timestamped export.
echo 4. Option 2 resets only the progress data (pairs, skips), not the final export.
echo 5. Make sure towns.json exists in the working folder.
pause
goto MENU

@echo off
:: Windows CLI Menu Wrapper for Dependency Check & Execution

:: Check for Python installation
echo Checking if Python is installed...
cmd /c python --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    start https://www.python.org/downloads/
    echo Please install Python and rerun this script.
    pause
    exit
)

:: Check for required Python packages
echo Checking for required Python packages...

:: openrouteservice
cmd /c python -m pip show openrouteservice >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo openrouteservice is not installed. Installing now...
    cmd /c pip install --upgrade openrouteservice
    echo Please wait while openrouteservice is being installed...
    pause
)

:: pandas
cmd /c python -m pip show pandas >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo pandas is not installed. Installing now...
    cmd /c pip install pandas
    echo Please wait while pandas is being installed...
    pause
)

:: tqdm
cmd /c python -m pip show tqdm >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo tqdm is not installed. Installing now...
    cmd /c pip install tqdm
    echo Please wait while tqdm is being installed...
    pause
)

:: requests
cmd /c python -m pip show requests >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo requests is not installed. Installing now...
    cmd /c pip install requests
    echo Please wait while requests is being installed...
    pause
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
echo Running the OpenRouteService distance calculation...
cmd /c python script.py
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
echo 1. This script checks and installs required Python dependencies.
echo 3. Option 1 runs the calculator.
echo 4. Option 2 resets only the progress data (pairs, skips), not the final export.
echo 5. Ensure you have a valid OpenRouteService API key in config.json.
echo 6. The script has an auto save every succesful route calcualation.
echo 7. You can continue the progress if it's interupted or terminated.
echo 7. Make sure coordinates.json exists in the working folder.
pause
goto MENU

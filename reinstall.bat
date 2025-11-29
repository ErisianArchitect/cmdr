@echo OFF
:: Attempts to run command that requires elevated privileges.
sudo run -E python -m pip install --force-reinstall "%~dp0\."
if errorlevel 1 (
    echo There was an error installing `cmdr`.
    exit /b %errorlevel%
)
if "%1"=="--wait" (
    pause
)
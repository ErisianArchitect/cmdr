@echo OFF
:: Run pip install with elevated privileges so that it doesn't get installed in appdata.
sudo run -E python -m pip install --force-reinstall "%~dp0\."
if errorlevel 1 (
    echo There was an error installing `cmdr`.
    exit /b %errorlevel%
)
if "%1"=="/w" (
    pause
)
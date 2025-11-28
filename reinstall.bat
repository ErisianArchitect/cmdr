@echo OFF
:: Attempts to run command that requires elevated privileges.
net session >nul 2>&1
if errorlevel 1 (
    powershell -NoProfile -Command "Start-Process '%~f0' -WorkingDirectory '%~dp0' -Verb RunAs -Wait"
    exit /b
)
cd /d "%~dp0"
python -m pip uninstall cmdr -y
python -m pip install .
pause
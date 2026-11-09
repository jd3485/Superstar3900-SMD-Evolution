@echo off
setlocal
cd /d "%~dp0\..\..\.."
python -B "03_Verifiche\V5.4\run_native_v54.py" --output "REPORT_NATIVE_V5.4"
echo.
echo I report si trovano in REPORT_NATIVE_V5.4. Anche un esito senza errori non autorizza la produzione.
pause

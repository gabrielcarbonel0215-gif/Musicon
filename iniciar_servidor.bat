@echo off
title Music Hub - Servidor Local
echo ======================================================
echo    Iniciando Music Hub (Descargador Completo de M4A)
echo ======================================================
echo.
echo Abriendo aplicacion en tu navegador...
start http://localhost:8000

"C:\Users\Abeli\AppData\Local\Python\pythoncore-3.14-64\python.exe" server.py
if %ERRORLEVEL% NEQ 0 (
    python server.py
)
pause

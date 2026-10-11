@echo off
title Subir a GitHub - Musicon
echo ======================================================
echo           Subiendo proyecto a GitHub: Musicon
echo ======================================================
echo.
echo Repositorio: https://github.com/gabrielcarbonel0215-gif/Musicon.git
echo.
echo Subiendo archivos...
echo (Si aparece una ventana para iniciar sesion en GitHub, autorizala en tu navegador)
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================
    echo     EXITO: Tu proyecto se ha subido a GitHub!
    echo     URL: https://github.com/gabrielcarbonel0215-gif/Musicon
    echo ======================================================
) else (
    echo.
    echo Ocurrio un inconveniente al subir. Comprueba tu conexion o permisos.
)

echo.
pause

@echo off
chcp 65001 > nul

cd %~dp0

cd scripts

cls

python sorteo_por_apellidos.py

@echo ¡Muchas gracias por usar nuestro programa!

pause
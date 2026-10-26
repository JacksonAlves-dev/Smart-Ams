@echo off
cd /d "%~dp0"
title Smart AMS - Agente L1

echo ========================================================
echo            Smart AMS - Agente de Suporte L1
echo ========================================================
echo Iniciando aplicacao local...

if exist "runtime\pythonw.exe" (
    start "" "runtime\pythonw.exe" iniciar_smartams.pyw
) else (
    start "" pythonw iniciar_smartams.pyw
)

echo O Smart AMS abrira no seu navegador em instantes.
ping 127.0.0.1 -n 3 >nul
exit


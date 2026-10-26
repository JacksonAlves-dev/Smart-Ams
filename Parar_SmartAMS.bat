@echo off
cd /d "%~dp0"
title Encerrar Smart AMS

echo ========================================================
echo             Encerrando o Smart AMS
echo ========================================================
echo Localizando processos na porta 8501...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo Smart AMS encerrado com sucesso.
ping 127.0.0.1 -n 3 >nul
exit


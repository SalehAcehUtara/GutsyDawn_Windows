@echo off
title Gutsy Dawn - Live Debugger
echo =======================================
echo Mengawasi dan menjalankan Gutsy Dawn...
echo =======================================
cd /d "%~dp0"
python intip.py
echo.
echo Membuka file log hasil rekaman...
start notepad "..\log all.txt"
pause

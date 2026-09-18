@echo off
title Soulbekbot - Tizim Holati Tekshiruvi
color 0A
cd /d "%~dp0"
echo ============================================================
echo   SOULBEKBOT DIAGNOSTIKA VA HOLATNI TEKSHIRISH
echo ============================================================
echo.
call venv\Scripts\python.exe check_status.py
echo.
pause

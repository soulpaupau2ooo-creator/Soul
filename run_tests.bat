@echo off
title Soulbekbot - Unit Testlar
color 0B
cd /d "%~dp0"
echo ============================================================
echo   SOULBEKBOT - BARCHA UNIT TESTLARNI ISHGA TUSHIRISH
echo ============================================================
echo.
call venv\Scripts\python.exe -m unittest discover tests
echo.
pause

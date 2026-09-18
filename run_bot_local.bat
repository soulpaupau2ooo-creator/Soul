@echo off
title Soulbekbot - Lokal Polling Rejimi
color 0E
cd /d "%~dp0"
echo ============================================================
echo   SOULBEKBOT - LOKAL ISHGA TUSHIRISH (POLLING)
echo ============================================================
echo.
echo   DIQQAT: Render bulutida bot 24/7 webhook orqali ishlab turibdi.
echo   Agar botni lokal ishga tushirsangiz, u Render webhookini
echo   vaqtincha to'xtatib, kompyuteringizdan xabarlarni qabul qiladi.
echo.
echo   To'xtatish uchun: Ctrl + C bosing.
echo.
set USE_WEBHOOK=false
call venv\Scripts\python.exe bot.py
pause

@echo off
title College Event Management & Recommendation System
echo ========================================================
echo Starting College Event Management System
echo ========================================================
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
python run_servers.py
pause

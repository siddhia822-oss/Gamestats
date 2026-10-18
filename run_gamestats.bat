@echo off
title GameStats Frontend Setup
cd /d "%~dp0"
echo.
echo ========================================
echo       GAMESTATS FRONTEND LAUNCHER
echo ========================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Please install Python 3.10 or newer from https://www.python.org/downloads/
  echo During installation, tick "Add Python to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating a Python virtual environment...
  py -m venv .venv
)
echo Installing required libraries...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Library installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)
echo.
echo Starting GameStats in your browser...
".venv\Scripts\python.exe" -m streamlit run app.py
pause

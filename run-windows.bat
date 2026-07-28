@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  arch-bot Windows launcher
echo ========================================

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo .env file created.
  echo Add your tokens and Discord IDs, then run this file again.
  start "" notepad ".env"
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  where py >nul 2>&1
  if errorlevel 1 (
    echo Python 3.11 or newer is required.
    pause
    exit /b 1
  )
  py -3 -m venv ".venv"
  if errorlevel 1 (
    pause
    exit /b 1
  )
)

".venv\Scripts\python.exe" -c "import discord, openai, dotenv" >nul 2>&1
if errorlevel 1 (
  echo Installing required packages...
  ".venv\Scripts\python.exe" -m pip install .
  if errorlevel 1 (
    echo Package installation failed.
    pause
    exit /b 1
  )
)

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
echo.
echo Starting bot server. Close this window or press Ctrl+C to stop.
echo.
".venv\Scripts\python.exe" -m arch_bot.main

set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo Bot server stopped. Exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%

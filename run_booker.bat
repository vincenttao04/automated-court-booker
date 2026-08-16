@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" main.py >> logs\run.log 2>&1
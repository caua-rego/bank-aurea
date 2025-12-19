@echo off
REM Windows/Generic Start Script Placeholder
echo Starting Backend...
start python run.py
echo Starting Frontend...
cd frontend
start npx ng serve

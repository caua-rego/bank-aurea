#!/bin/bash
# Bank Aurea Unified Startup

# Trap Ctrl+C to kill both
trap "kill 0" EXIT

echo "Starting Backend (Port 5001)..."
python3 run.py &

echo "Starting Frontend (Port 4200)..."
cd frontend
npx ng serve &

wait

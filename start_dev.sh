#!/bin/bash
# Bank Aurea Unified Startup
set -e

# Trap Ctrl+C to kill both
trap "kill 0" EXIT

export FLASK_APP=run.py
export FLASK_CONFIG=${FLASK_CONFIG:-development}

echo "Applying database migrations..."
flask db upgrade

echo "Starting Backend (Port 5001)..."
python3 run.py &

echo "Starting Frontend (Port 4200)..."
cd frontend
npx ng serve &

wait

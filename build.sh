#!/bin/bash

set -e

echo "Starting Backend on port 8000..."
source venv/bin/activate

uvicorn main:app --reload &
BACK_PID=$!

cd frontend || exit
echo "Starting Frontend (React on port 3000)..."
npm start &

wait $BACK_PID

#!/bin/bash
# Start Backend directly using the conda environment
cd backend
echo "Starting Backend on Port 8001..."
../opt/homebrew/Caskroom/miniconda/base/envs/cut-agent/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
# Falls back to conda run if direct path fails (based on user path structure in logs)
# conda run -n cut-agent uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

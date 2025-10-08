#!/bin/bash
# SERP-Master API Startup Script

cd ~/serp-master/backend
source venv/bin/activate
echo "Starting SERP-Master API on port 8000..."
python -m app.main

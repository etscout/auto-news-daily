#!/bin/bash
# Start the Daily Auto News web UI

cd "$(dirname "$0")"

echo "🚗 Starting Daily Auto News Web UI..."
echo "📝 Login: caleb / autonews2026"
echo "🌐 Open: http://localhost:5000"
echo ""

python3 web.py

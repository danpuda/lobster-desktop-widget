#!/bin/bash
cd "$(dirname "$0")/src"
python3 server.py &
sleep 1
echo "Open http://localhost:8765 in browser"

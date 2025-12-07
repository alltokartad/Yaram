#!/bin/bash

# Yaram Browser Startup Script

echo "Starting Yaram Browser..."
python yaram_browser.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error starting browser. Make sure Python and required packages are installed."
    exit 1
fi

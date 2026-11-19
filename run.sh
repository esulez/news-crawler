#!/bin/bash

# News Crawler Run Script

echo "Starting News Crawler..."
echo "========================"

# Create data directory if it doesn't exist
mkdir -p data

# Install dependencies if not already installed
if [ ! -f "requirements_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch requirements_installed
    echo "Dependencies installed."
fi

# Run the application
python main.py "$@"

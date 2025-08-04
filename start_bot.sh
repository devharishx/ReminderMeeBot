#!/bin/bash

# ReminderBot Startup Script

echo "🤖 Starting ReminderBot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Run the bot
echo "🚀 Launching ReminderBot..."
python bot.py 
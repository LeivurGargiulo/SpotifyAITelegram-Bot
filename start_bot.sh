#!/bin/bash

# Telegram Music Recommendation Bot Startup Script

echo "🎵 Starting Telegram Music Recommendation Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API keys (see .env.example)"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if all required variables are set
required_vars=("TELEGRAM_TOKEN" "SPOTIFY_CLIENT_ID" "SPOTIFY_CLIENT_SECRET" "OPENROUTER_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '   %s\n' "${missing_vars[@]}"
    echo "Please check your .env file"
    exit 1
fi

# Run setup test first
echo "🔍 Running setup test..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting the bot..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Start the bot
    python music_recommendation_bot.py
else
    echo "❌ Setup test failed. Please fix the issues before starting the bot."
    exit 1
fi
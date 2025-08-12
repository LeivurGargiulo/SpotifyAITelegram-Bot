#!/bin/bash

# Discord Music Bot Startup Script
# This script starts the Discord bot with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $python_version found"
}

# Check if required files exist
check_files() {
    local missing_files=()
    
    if [ ! -f "discord_music_bot.py" ]; then
        missing_files+=("discord_music_bot.py")
    fi
    
    if [ ! -f "requirements.txt" ]; then
        missing_files+=("requirements.txt")
    fi
    
    if [ ! -d "cogs" ]; then
        missing_files+=("cogs/")
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        print_error "Missing required files: ${missing_files[*]}"
        exit 1
    fi
    
    print_success "All required files found"
}

# Check environment variables
check_env() {
    local missing_vars=()
    
    if [ -z "$DISCORD_TOKEN" ]; then
        missing_vars+=("DISCORD_TOKEN")
    fi
    
    if [ -z "$SPOTIFY_CLIENT_ID" ]; then
        missing_vars+=("SPOTIFY_CLIENT_ID")
    fi
    
    if [ -z "$SPOTIFY_CLIENT_SECRET" ]; then
        missing_vars+=("SPOTIFY_CLIENT_SECRET")
    fi
    
    if [ -z "$OPENROUTER_API_KEY" ]; then
        missing_vars+=("OPENROUTER_API_KEY")
    fi
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing environment variables: ${missing_vars[*]}"
        print_warning "Please set these variables in your .env file or environment"
        exit 1
    fi
    
    print_success "All environment variables are set"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if pip3 install -r requirements.txt; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Create logs directory
setup_logs() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
        print_success "Created logs directory"
    fi
}

# Start the bot
start_bot() {
    print_status "Starting Discord Music Bot..."
    print_status "Press Ctrl+C to stop the bot"
    
    # Run the bot
    python3 discord_music_bot.py
}

# Main execution
main() {
    echo "=========================================="
    echo "    Discord Music Bot Startup Script"
    echo "=========================================="
    echo ""
    
    print_status "Checking prerequisites..."
    check_python
    check_files
    
    print_status "Checking environment variables..."
    check_env
    
    print_status "Setting up environment..."
    install_dependencies
    setup_logs
    
    echo ""
    print_success "All checks passed! Starting bot..."
    echo ""
    
    start_bot
}

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env file"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run main function
main "$@"
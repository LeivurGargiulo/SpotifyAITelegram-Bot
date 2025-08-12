#!/bin/bash

# Optimized Discord Bot Startup Script
# Production-ready with monitoring and error handling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_NAME="Optimized Discord Music Bot"
LOG_FILE="discord_bot.log"
PID_FILE="bot.pid"
MAX_RESTARTS=5
RESTART_DELAY=30

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to check if bot is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1  # Not running
}

# Function to stop the bot
stop_bot() {
    print_status "Stopping $BOT_NAME..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            sleep 5
            if ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Bot didn't stop gracefully, force killing..."
                kill -9 "$PID"
            fi
        fi
        rm -f "$PID_FILE"
    fi
    print_success "Bot stopped successfully"
}

# Function to start the bot
start_bot() {
    print_status "Starting $BOT_NAME..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "optimized_discord_bot.py" ]; then
        print_error "optimized_discord_bot.py not found"
        exit 1
    fi
    
    # Check environment variables
    required_vars=("DISCORD_TOKEN" "SPOTIFY_CLIENT_ID" "SPOTIFY_CLIENT_SECRET" "OPENROUTER_API_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_error "Please set these variables in your environment or .env file"
        exit 1
    fi
    
    # Install/update dependencies
    print_status "Checking dependencies..."
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
    fi
    
    # Create log directory if it doesn't exist
    mkdir -p logs
    
    # Start the bot
    print_status "Launching bot..."
    nohup python3 optimized_discord_bot.py > "logs/$LOG_FILE" 2>&1 &
    BOT_PID=$!
    echo $BOT_PID > "$PID_FILE"
    
    # Wait a moment and check if bot started successfully
    sleep 3
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        print_success "$BOT_NAME started successfully (PID: $BOT_PID)"
        print_status "Logs are being written to logs/$LOG_FILE"
        return 0
    else
        print_error "Failed to start $BOT_NAME"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to monitor the bot
monitor_bot() {
    local restart_count=0
    
    while [ $restart_count -lt $MAX_RESTARTS ]; do
        if ! check_running; then
            print_warning "Bot is not running, attempting restart ($((restart_count + 1))/$MAX_RESTARTS)"
            
            if start_bot; then
                restart_count=0  # Reset counter on successful start
            else
                restart_count=$((restart_count + 1))
                if [ $restart_count -lt $MAX_RESTARTS ]; then
                    print_warning "Waiting $RESTART_DELAY seconds before next restart attempt..."
                    sleep $RESTART_DELAY
                fi
            fi
        fi
        
        # Check bot health every 30 seconds
        sleep 30
        
        if check_running; then
            PID=$(cat "$PID_FILE")
            # Check if bot is responsive (you can add more health checks here)
            if ! ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Bot process died, will restart on next cycle"
            fi
        fi
    done
    
    print_error "Maximum restart attempts reached. Bot failed to start properly."
    exit 1
}

# Function to show bot status
show_status() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_success "$BOT_NAME is running (PID: $PID)"
        
        # Show recent logs
        if [ -f "logs/$LOG_FILE" ]; then
            print_status "Recent log entries:"
            tail -n 10 "logs/$LOG_FILE"
        fi
    else
        print_warning "$BOT_NAME is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "logs/$LOG_FILE" ]; then
        tail -f "logs/$LOG_FILE"
    else
        print_error "Log file not found"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the bot"
    echo "  stop      Stop the bot"
    echo "  restart   Restart the bot"
    echo "  status    Show bot status and recent logs"
    echo "  logs      Show live logs"
    echo "  monitor   Start bot with automatic restart monitoring"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start the bot once"
    echo "  $0 monitor    # Start with automatic restart on failure"
    echo "  $0 status     # Check if bot is running"
}

# Main script logic
case "${1:-help}" in
    start)
        if check_running; then
            print_warning "$BOT_NAME is already running"
            exit 0
        fi
        start_bot
        ;;
    stop)
        if ! check_running; then
            print_warning "$BOT_NAME is not running"
            exit 0
        fi
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    monitor)
        print_status "Starting $BOT_NAME with monitoring..."
        if check_running; then
            print_warning "$BOT_NAME is already running"
            exit 0
        fi
        start_bot
        monitor_bot
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
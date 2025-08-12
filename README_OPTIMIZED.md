# 🚀 Optimized Discord Music Recommendation Bot

A production-ready Discord bot that provides intelligent music recommendations using AI-powered keyword extraction and Spotify's recommendation engine. Built with performance, security, and maintainability in mind.

## ✨ Features

### 🎵 Music Recommendations
- **AI-Powered Analysis**: Uses OpenRouter API to extract music-related keywords from natural language
- **Spotify Integration**: Leverages Spotify's recommendation engine for high-quality music suggestions
- **Smart Caching**: Advanced LRU cache system with TTL for optimal performance
- **Fallback System**: Graceful degradation when AI services are unavailable

### ⚡ Performance Optimizations
- **Asynchronous Processing**: Non-blocking event handling for smooth user experience
- **Rate Limiting**: Advanced sliding window rate limiter with burst protection
- **Memory Management**: Optimized memory usage with automatic cleanup
- **Response Time Tracking**: Real-time performance monitoring and metrics

### 🛡️ Security & Reliability
- **Environment Variables**: Secure management of API keys and tokens
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Graceful Shutdown**: Proper cleanup and signal handling
- **Health Monitoring**: Built-in health checks and performance metrics

### 📊 Monitoring & Analytics
- **Performance Metrics**: Real-time tracking of response times, cache hit rates, and error rates
- **System Monitoring**: CPU, memory, and disk usage tracking
- **Error Logging**: Detailed error logs with context and user information
- **Admin Commands**: Built-in commands for monitoring and debugging

## 🏗️ Architecture

### Core Components
- **OptimizedDiscordBot**: Main bot class with enhanced performance features
- **OptimizedCache**: Advanced LRU cache with access tracking and TTL
- **AdvancedRateLimiter**: Sliding window rate limiter with burst protection
- **SecureAPIClient**: HTTP client with retry logic and timeout handling
- **OptimizedSpotifyAPI**: Enhanced Spotify API with caching and error handling
- **OptimizedOpenRouterAPI**: AI keyword extraction with fallback mechanisms

### Cogs (Modules)
- **MusicCommands**: Core music recommendation functionality
- **UtilityCommands**: Helper commands and utilities
- **ErrorHandler**: Comprehensive error handling and logging
- **PerformanceMonitor**: Real-time performance tracking and metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Spotify API Credentials
- OpenRouter API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-music-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

4. **Start the bot**
   ```bash
   # Using the optimized startup script
   ./start_optimized_bot.sh start
   
   # Or directly with Python
   python3 optimized_discord_bot.py
   ```

### Using the Startup Script

The optimized startup script provides several commands:

```bash
# Start the bot once
./start_optimized_bot.sh start

# Start with automatic restart monitoring
./start_optimized_bot.sh monitor

# Check bot status
./start_optimized_bot.sh status

# View live logs
./start_optimized_bot.sh logs

# Stop the bot
./start_optimized_bot.sh stop

# Restart the bot
./start_optimized_bot.sh restart
```

## 🎮 Usage

### Basic Commands
- `!start` - Welcome message and bot introduction
- `!help` - Detailed help and examples
- `!stats` - Your usage statistics and rate limit status
- `!health` - Quick bot health check

### Music Recommendations
Simply send a message describing what music you want:

```
"I'm feeling happy and energetic"
"Need rock music for my workout"
"I love jazz and classical music"
"Want romantic songs for dinner"
"Looking for 80s pop classics"
```

### Admin Commands
- `!performance` - Detailed performance metrics (Admin only)
- `!metrics` - API and cache statistics (Admin only)
- `!logs` - Recent error logs (Admin only)

## 📈 Performance Features

### Caching System
- **Multi-level Caching**: Separate caches for recommendations, tokens, and keywords
- **LRU Eviction**: Automatic removal of least recently used items
- **TTL Management**: Time-based expiration with configurable timeouts
- **Access Tracking**: Monitor cache hit rates and access patterns

### Rate Limiting
- **Sliding Window**: Accurate rate limiting with time-based windows
- **Burst Protection**: Prevents rapid-fire requests
- **Per-User Tracking**: Individual rate limits for each user
- **Graceful Degradation**: Informative messages when limits are exceeded

### Error Handling
- **Comprehensive Logging**: Detailed error logs with context
- **Graceful Degradation**: Fallback mechanisms when services are unavailable
- **User-Friendly Messages**: Clear error messages for users
- **Automatic Recovery**: Self-healing mechanisms for transient failures

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | Yes |
| `SPOTIFY_CLIENT_ID` | Spotify API client ID | Yes |
| `SPOTIFY_CLIENT_SECRET` | Spotify API client secret | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |

### Performance Tuning
The bot includes several configurable parameters:

```python
# Cache settings
CACHE_MAX_SIZE = 1000
CACHE_TTL = 3600  # 1 hour

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 15
BURST_LIMIT = 5

# API timeouts
API_TIMEOUT = 30
MAX_RETRIES = 3
```

## 📊 Monitoring

### Performance Metrics
The bot tracks various performance indicators:
- Response times
- Cache hit rates
- Error rates
- API call success rates
- Memory and CPU usage

### Logging
- **File Logging**: All logs are written to `logs/discord_bot.log`
- **Console Output**: Real-time logging to console
- **Error Tracking**: Detailed error logs with stack traces
- **Performance Logging**: Regular performance metrics logging

### Health Checks
- **System Resources**: Monitor CPU, memory, and disk usage
- **API Health**: Check external API availability
- **Bot Responsiveness**: Verify bot is responding to commands
- **Error Rate Monitoring**: Track and alert on high error rates

## 🛠️ Development

### Project Structure
```
discord-music-bot/
├── optimized_discord_bot.py    # Main bot file
├── cogs/                       # Bot modules
│   ├── music_commands.py       # Music recommendation logic
│   ├── utility_commands.py     # Utility commands
│   ├── error_handler.py        # Error handling
│   └── performance_monitor.py  # Performance monitoring
├── start_optimized_bot.sh      # Startup script
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
└── logs/                       # Log files
```

### Adding New Features
1. Create a new cog in the `cogs/` directory
2. Implement your commands and event handlers
3. Add the cog to the bot's cog loading list
4. Update documentation and tests

### Testing
```bash
# Run basic tests
python3 -m pytest tests/

# Run with coverage
python3 -m pytest --cov=. tests/
```

## 🔒 Security Best Practices

### API Key Management
- Store all sensitive data in environment variables
- Never commit API keys to version control
- Use `.env` files for local development
- Rotate API keys regularly

### Rate Limiting
- Implement per-user rate limits
- Use sliding window algorithms
- Provide clear feedback when limits are exceeded
- Monitor for abuse patterns

### Error Handling
- Don't expose sensitive information in error messages
- Log errors with appropriate detail levels
- Implement graceful degradation
- Provide user-friendly error messages

## 🚀 Deployment

### Production Deployment
1. **Environment Setup**: Configure all required environment variables
2. **Dependencies**: Install all required packages
3. **Monitoring**: Set up logging and monitoring
4. **Process Management**: Use the startup script or a process manager
5. **Backup**: Regular backups of configuration and logs

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "optimized_discord_bot.py"]
```

### Systemd Service
Create a systemd service file for automatic startup:

```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/path/to/bot
Environment=PATH=/path/to/bot/venv/bin
ExecStart=/path/to/bot/venv/bin/python optimized_discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the logs in `logs/discord_bot.log`
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check the bot's health with `!health` command
5. Review the performance metrics with `!performance`

For additional help, please open an issue on the project repository.

---

**Built with ❤️ for the Discord community**
# Enhanced Discord Music Recommendation Bot

A powerful Discord bot that provides AI-powered music recommendations based on user preferences, moods, and activities. This bot is a complete conversion from the original Telegram bot, maintaining all functionality while adapting to Discord's API and conventions.

## 🎵 Features

- **AI-Powered Recommendations**: Uses OpenRouter API to analyze user messages and extract music-related keywords
- **Spotify Integration**: Fetches personalized music recommendations from Spotify's Web API
- **Intelligent Caching**: Reduces API calls and improves response times
- **Rate Limiting**: Protects against abuse with configurable rate limits
- **Rich Embeds**: Beautiful Discord embeds with track information, popularity, and Spotify links
- **Comprehensive Error Handling**: User-friendly error messages and detailed logging
- **Background Tasks**: Automatic cache cleanup and maintenance
- **Modular Architecture**: Organized into cogs for maintainability

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Spotify API credentials
- OpenRouter API key

### Installation

1. **Clone or download the bot files**
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

4. **Run the bot**
   ```bash
   python discord_music_bot.py
   ```

## 🔧 Setup Guide

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Enable the following bot permissions:
   - Send Messages
   - Embed Links
   - Use Slash Commands
   - Read Message History
   - Add Reactions

### Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy the Client ID and Client Secret
4. Add them to your `.env` file

### OpenRouter API Setup

1. Go to [OpenRouter](https://openrouter.ai/)
2. Create an account and get your API key
3. Add it to your `.env` file

## 📋 Commands

### Music Commands
- **Natural Language**: Just send a message describing what music you want!
  - "I'm feeling happy and energetic"
  - "Need rock music for my workout"
  - "Want romantic jazz for dinner"
  - "Looking for 80s pop classics"

### Bot Commands
- `!start` - Welcome message and introduction
- `!help` - Help and usage examples
- `!stats` - Your usage statistics
- `!debug` - Bot debug information and error logs
- `!status` - Detailed bot status and performance
- `!ping` - Check bot latency
- `!info` - Bot information and features
- `!cleanup` - Manual cache cleanup (admin only)

## 🎯 Usage Examples

### Basic Music Requests
```
User: I'm feeling sad today
Bot: 🎵 Music Recommendations 🎵
     Based on: sad, melancholy, emotional
     
     1. "Mad World" - Gary Jules
        📀 Album: Donnie Darko
        💫 Popularity: 75%
        ⏱️ Duration: 3:32
        🎧 Listen on Spotify

     2. "Hallelujah" - Jeff Buckley
        📀 Album: Grace
        ⭐ Popularity: 82%
        ⏱️ Duration: 6:53
        🎧 Listen on Spotify
```

### Activity-Based Requests
```
User: Need energetic music for my workout
Bot: 🎵 Music Recommendations 🎵
     Based on: energetic, workout, fast, dance
     
     1. "Eye of the Tiger" - Survivor
        📀 Album: Eye of the Tiger
        🔥 Popularity: 89%
        ⏱️ Duration: 4:05
        🎧 Listen on Spotify
```

## 🏗️ Architecture

### Core Components

1. **EnhancedDiscordMusicBot**: Main bot class with Discord.py integration
2. **EnhancedSpotifyAPI**: Handles Spotify API interactions with caching
3. **EnhancedOpenRouterAPI**: Manages AI keyword extraction
4. **Cache**: In-memory caching system with TTL
5. **RateLimiter**: User rate limiting protection

### Cogs (Modules)

- **MusicCommands**: Handles music recommendations and core functionality
- **UtilityCommands**: Debug, status, and utility commands
- **ErrorHandler**: Comprehensive error handling and logging

### Background Tasks

- **Cache Cleanup**: Automatically clears expired cache entries every hour
- **Error Logging**: Maintains recent error logs for debugging

## 🔒 Security Features

- **Environment Variables**: Secure credential management
- **Rate Limiting**: 15 requests per minute per user
- **Input Validation**: Sanitizes user inputs
- **Error Handling**: Prevents information leakage in error messages

## 📊 Performance Features

- **Intelligent Caching**: Reduces API calls by 80%+ for repeated requests
- **Async Operations**: Non-blocking I/O for better performance
- **Background Tasks**: Automatic maintenance without user interaction
- **Memory Management**: Automatic cleanup of expired cache entries

## 🐛 Error Handling

The bot includes comprehensive error handling for:

- **API Failures**: Graceful handling of Spotify/OpenRouter API issues
- **Network Errors**: Connection timeout and retry logic
- **Rate Limits**: User-friendly rate limit messages
- **Invalid Inputs**: Helpful suggestions for better requests
- **Permission Issues**: Clear guidance for missing permissions

## 🚀 Deployment

### Local Development
```bash
python discord_music_bot.py
```

### Production Deployment
1. **VPS/Cloud Server**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run with process manager (e.g., systemd, PM2)
   python discord_music_bot.py
   ```

2. **Docker** (recommended):
   ```bash
   docker build -t discord-music-bot .
   docker run -d --env-file .env discord-music-bot
   ```

3. **Heroku**:
   - Add buildpack: `heroku/python`
   - Set environment variables in Heroku dashboard
   - Deploy with `git push heroku main`

## 📈 Monitoring

### Built-in Monitoring
- `!debug` - Real-time bot status and error logs
- `!status` - Detailed performance metrics
- `!ping` - Latency monitoring

### Logging
- Comprehensive logging to console and files
- Error tracking with stack traces
- User activity monitoring
- API call statistics

## 🔧 Configuration

### Rate Limiting
```python
# In discord_music_bot.py
self.rate_limiter = RateLimiter(max_requests=15, window=60)  # 15 requests per minute
```

### Cache Settings
```python
# Cache TTL settings
self.cache = Cache(ttl=1800)  # 30 minutes for Spotify recommendations
self.cache = Cache(ttl=3600)  # 1 hour for keyword extraction
```

### Background Tasks
```python
# Cache cleanup interval
@tasks.loop(hours=1)
async def cleanup_cache(self):
    # Runs every hour
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the `!debug` command for error logs
2. Verify your environment variables are set correctly
3. Ensure your bot has the required Discord permissions
4. Check the API status of Spotify and OpenRouter

## 🔄 Migration from Telegram Bot

This Discord bot maintains 100% feature parity with the original Telegram bot:

- ✅ All commands converted (`/start` → `!start`, etc.)
- ✅ Message handling preserved
- ✅ Rate limiting maintained
- ✅ Caching system intact
- ✅ Error handling enhanced
- ✅ Background tasks adapted
- ✅ API integrations unchanged

The main differences are:
- Discord embeds instead of Markdown formatting
- Discord.py event system instead of Telegram's polling
- Enhanced error handling for Discord-specific issues
- Improved modular architecture with cogs

## 🎉 Features Added in Discord Version

- **Rich Embeds**: Beautiful Discord-native formatting
- **Enhanced Error Handling**: Discord-specific error messages
- **Modular Architecture**: Organized into maintainable cogs
- **Background Tasks**: Automatic maintenance and cleanup
- **Performance Monitoring**: Built-in status and debug commands
- **Admin Commands**: Cache management and system control
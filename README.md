# 🎵 Telegram Music Recommendation Bot

A smart Telegram bot that recommends music based on your mood, situation, or preferences using Spotify Web API and OpenRouter AI for natural language understanding.

## ✨ Features

- **AI-Powered Analysis**: Uses OpenRouter AI to understand your music preferences from natural language
- **Spotify Integration**: Gets personalized music recommendations from Spotify's vast library
- **Smart Keyword Extraction**: Automatically extracts genres, moods, activities, and preferences from your messages
- **Rich Recommendations**: Returns 5 curated tracks with song title, artist, album, and direct Spotify links
- **Async Architecture**: Built with modern async/await patterns for optimal performance
- **Comprehensive Error Handling**: Graceful handling of API failures and unexpected inputs
- **Detailed Logging**: Full logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- Spotify Developer Account
- OpenRouter API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd music-recommendation-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   # Telegram Bot Token (get from @BotFather)
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   
   # Spotify API Credentials (get from Spotify Developer Dashboard)
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   
   # OpenRouter API Key (get from openrouter.ai)
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the bot**
   ```bash
   python music_recommendation_bot.py
   ```

## 🔧 Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token and add it to your `.env` file

### 2. Set up Spotify Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details:
   - App name: "Music Recommendation Bot"
   - App description: "Telegram bot for music recommendations"
   - Redirect URI: `http://localhost:8888/callback` (for now)
5. Copy the Client ID and Client Secret to your `.env` file

### 3. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Go to your API keys section
4. Create a new API key
5. Copy the key to your `.env` file

## 📱 Usage Examples

Once the bot is running, users can interact with it like this:

### Basic Usage
```
User: "I'm feeling sad today"
Bot: 🎵 Music Recommendations 🎵
     Based on: sad
     
     1. **Someone Like You** - Adele
        Album: 21
        Listen on Spotify: [link]
     
     2. **Mad World** - Gary Jules
        Album: Donnie Darko
        Listen on Spotify: [link]
     ...

User: "Need energetic music for my workout"
Bot: 🎵 Music Recommendations 🎵
     Based on: energetic, workout
     
     1. **Eye of the Tiger** - Survivor
        Album: Eye of the Tiger
        Listen on Spotify: [link]
     ...
```

### More Examples
- "I love jazz and classical music"
- "Want some rock music for driving"
- "Need calm music for studying"
- "Looking for romantic songs"
- "I'm in a party mood"

## 🏗️ Architecture

The bot is built with a modular architecture:

- **`MusicRecommendationBot`**: Main bot class handling Telegram interactions
- **`SpotifyAPI`**: Handles Spotify authentication and recommendations
- **`OpenRouterAPI`**: Manages AI-powered keyword extraction
- **`Track`**: Data class for representing music tracks

### Key Components

1. **Natural Language Processing**: OpenRouter AI analyzes user messages to extract music-related keywords
2. **Music Recommendation Engine**: Spotify API provides personalized recommendations based on extracted keywords
3. **Response Formatting**: Clean, readable responses with direct Spotify links
4. **Error Handling**: Comprehensive error handling for all API interactions

## 🔍 How It Works

1. **User sends a message** describing their music preferences
2. **OpenRouter AI analyzes** the message and extracts relevant keywords (genres, moods, activities)
3. **Keywords are processed** and mapped to Spotify's recommendation parameters
4. **Spotify API returns** 5 personalized track recommendations
5. **Bot formats and sends** the recommendations with direct Spotify links

## 🛠️ Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Your Telegram bot token | ✅ |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID | ✅ |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter API key | ✅ |

### Customization

You can customize the bot by modifying:

- **Recommendation limit**: Change the `limit` parameter in `get_recommendations()`
- **Market region**: Modify the `market` parameter for different regions
- **AI model**: Change the OpenRouter model in the payload
- **Response format**: Modify the `_format_recommendations()` method

## 🐛 Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all environment variables are set in your `.env` file
   - Check that the file is in the correct location

2. **"Spotify authentication failed"**
   - Verify your Spotify Client ID and Secret are correct
   - Check that your Spotify app is properly configured

3. **"OpenRouter API request failed"**
   - Verify your OpenRouter API key is valid
   - Check your API usage limits

4. **"No recommendations found"**
   - Try more specific keywords
   - Check if the keywords are supported in the genre mapping

### Debugging

The bot includes comprehensive logging. Check the console output for detailed error messages and debugging information.

## 🚀 Deployment

### Local Development
```bash
python music_recommendation_bot.py
```

### Production Deployment

For production deployment, consider:

1. **Environment Management**: Use proper environment variable management
2. **Process Management**: Use tools like `systemd`, `supervisor`, or `pm2`
3. **Logging**: Set up proper log rotation and monitoring
4. **Security**: Ensure API keys are properly secured

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "music_recommendation_bot.py"]
```

## 🔮 Future Improvements

Here are some potential enhancements for the bot:

### High Priority
- **User Authentication**: Add Spotify OAuth for personalized recommendations
- **Caching**: Implement recommendation caching to reduce API calls
- **Rate Limiting**: Add rate limiting to prevent abuse
- **User Preferences**: Store user preferences for better recommendations

### Medium Priority
- **Audio Previews**: Integrate Spotify audio previews
- **Playlist Creation**: Allow users to create playlists from recommendations
- **Multiple Languages**: Add support for multiple languages
- **Advanced Filtering**: Add filters for release year, popularity, etc.

### Low Priority
- **Social Features**: Share recommendations with friends
- **Music History**: Track user listening history
- **Analytics**: Add usage analytics and insights
- **Web Interface**: Create a web dashboard for bot management

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information

---

**Happy listening! 🎶**
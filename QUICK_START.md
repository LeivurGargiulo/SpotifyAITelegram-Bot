# 🚀 Quick Start Guide - Discord Music Bot

Get your Discord Music Bot running in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Spotify API credentials
- OpenRouter API key

## ⚡ Quick Setup

### 1. Get Your API Keys

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application → Bot → Copy Token

**Spotify API:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create App → Copy Client ID and Client Secret

**OpenRouter API:**
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up → Get API Key

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your keys
nano .env
```

Fill in your `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 3. Install & Run

**Option A: Direct Python**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python discord_music_bot.py
```

**Option B: Using Startup Script**
```bash
# Make script executable
chmod +x start_discord_bot.sh

# Run with automatic setup
./start_discord_bot.sh
```

**Option C: Docker**
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.discord.yml up -d
```

### 4. Invite Bot to Server

1. Go to your Discord Application → OAuth2 → URL Generator
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
4. Copy the generated URL and open it in browser
5. Select your server and authorize

## 🎵 Test Your Bot

Once the bot is running, try these commands in your Discord server:

```
!start          # Welcome message
!help           # Help and examples
!ping           # Check if bot is responsive
```

Then try asking for music:
```
I'm feeling happy and energetic
Need rock music for my workout
Want romantic jazz for dinner
```

## 🔧 Troubleshooting

### Bot Not Responding?
- Check if bot is online in Discord
- Verify bot has correct permissions
- Check console for error messages

### API Errors?
- Verify all API keys are correct in `.env`
- Check if APIs are working (Spotify, OpenRouter)
- Use `!debug` command to check API status

### Permission Issues?
- Ensure bot has these permissions:
  - Send Messages
  - Embed Links
  - Read Message History
  - Use Slash Commands

## 📚 Next Steps

- Read `README_DISCORD.md` for detailed documentation
- Check `CONVERSION_SUMMARY.md` for technical details
- Run `python test_discord_bot.py` to test all components
- Customize bot settings in the code

## 🆘 Need Help?

1. Check the `!debug` command for error logs
2. Verify your environment variables
3. Check API status and credentials
4. Review the comprehensive documentation

---

**🎉 You're all set! Your Discord Music Bot is ready to recommend amazing music!**
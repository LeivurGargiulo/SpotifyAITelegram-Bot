"""
Configuration file for the Optimized Discord Music Bot
Centralized settings for easy customization and maintenance.
"""

import os
from typing import Dict, Any

class BotConfig:
    """Centralized configuration for the Discord bot."""
    
    # Bot Settings
    BOT_NAME = "Optimized Discord Music Bot"
    COMMAND_PREFIX = "!"
    MAX_MESSAGES = 10000  # Discord.py message cache size
    
    # Performance Settings
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
    SPOTIFY_CACHE_TTL = int(os.getenv('SPOTIFY_CACHE_TTL', 1800))  # 30 minutes
    OPENROUTER_CACHE_TTL = int(os.getenv('OPENROUTER_CACHE_TTL', 3600))  # 1 hour
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 15))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # seconds
    BURST_LIMIT = int(os.getenv('BURST_LIMIT', 5))
    BURST_WINDOW = int(os.getenv('BURST_WINDOW', 10))  # seconds
    
    # API Settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = float(os.getenv('RETRY_DELAY', 1.0))
    
    # Spotify Settings
    SPOTIFY_MARKET = os.getenv('SPOTIFY_MARKET', 'US')
    SPOTIFY_RECOMMENDATION_LIMIT = int(os.getenv('SPOTIFY_RECOMMENDATION_LIMIT', 5))
    
    # OpenRouter Settings
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'gpt-3.5-turbo')
    OPENROUTER_MAX_TOKENS = int(os.getenv('OPENROUTER_MAX_TOKENS', 100))
    OPENROUTER_TEMPERATURE = float(os.getenv('OPENROUTER_TEMPERATURE', 0.3))
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/discord_bot.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Background Task Intervals
    CACHE_CLEANUP_INTERVAL = int(os.getenv('CACHE_CLEANUP_INTERVAL', 3600))  # 1 hour
    PRESENCE_UPDATE_INTERVAL = int(os.getenv('PRESENCE_UPDATE_INTERVAL', 300))  # 5 minutes
    METRICS_LOG_INTERVAL = int(os.getenv('METRICS_LOG_INTERVAL', 600))  # 10 minutes
    PERFORMANCE_MONITOR_INTERVAL = int(os.getenv('PERFORMANCE_MONITOR_INTERVAL', 60))  # 1 minute
    
    # User Experience Settings
    TYPING_INDICATOR_TIMEOUT = int(os.getenv('TYPING_INDICATOR_TIMEOUT', 30))
    USER_COOLDOWN = float(os.getenv('USER_COOLDOWN', 2.0))  # seconds
    MAX_ERROR_LOGS = int(os.getenv('MAX_ERROR_LOGS', 100))
    MAX_PERFORMANCE_HISTORY = int(os.getenv('MAX_PERFORMANCE_HISTORY', 1000))
    
    # Embed Colors
    EMBED_COLORS = {
        'success': 0x00ff00,  # Green
        'error': 0xff0000,    # Red
        'warning': 0xffaa00,  # Orange
        'info': 0x0099ff,     # Blue
        'music': 0x1db954,    # Spotify Green
        'performance': 0x7289da  # Discord Blurple
    }
    
    # Genre Mappings for Spotify
    GENRE_MAPPINGS = {
        'rock': 'rock',
        'pop': 'pop',
        'jazz': 'jazz',
        'classical': 'classical',
        'electronic': 'electronic',
        'hip-hop': 'hip-hop',
        'rap': 'hip-hop',
        'country': 'country',
        'blues': 'blues',
        'reggae': 'reggae',
        'folk': 'folk',
        'metal': 'metal',
        'punk': 'punk',
        'indie': 'indie',
        'alternative': 'alternative',
        'r&b': 'r-n-b',
        'soul': 'soul',
        'funk': 'funk',
        'disco': 'disco',
        'house': 'house',
        'techno': 'techno',
        'trance': 'trance',
        'ambient': 'ambient',
        'lofi': 'lofi',
        'chill': 'chill',
        'energetic': 'dance',
        'party': 'dance',
        'romantic': 'romance',
        'sad': 'sad',
        'happy': 'happy',
        'calm': 'calm',
        'relaxing': 'relaxing'
    }
    
    # Audio Feature Keywords
    AUDIO_FEATURE_KEYWORDS = {
        'energy': {
            'high': ['energetic', 'upbeat', 'fast', 'dance', 'party', 'workout'],
            'low': ['calm', 'relaxing', 'chill', 'sleep', 'study']
        },
        'valence': {
            'high': ['happy', 'joyful', 'cheerful', 'upbeat'],
            'low': ['sad', 'melancholy', 'depressing']
        },
        'tempo': {
            'high': ['fast', 'energetic', 'workout', 'dance'],
            'low': ['slow', 'calm', 'relaxing']
        }
    }
    
    # Fallback Keywords for Simple Analysis
    FALLBACK_KEYWORDS = {
        'moods': ['happy', 'sad', 'energetic', 'calm', 'romantic', 'melancholy'],
        'genres': ['rock', 'pop', 'jazz', 'classical', 'electronic', 'hip-hop', 'country'],
        'activities': ['workout', 'study', 'party', 'sleep', 'driving', 'running']
    }
    
    @classmethod
    def get_spotify_params(cls) -> Dict[str, Any]:
        """Get Spotify API parameters."""
        return {
            'limit': cls.SPOTIFY_RECOMMENDATION_LIMIT,
            'market': cls.SPOTIFY_MARKET
        }
    
    @classmethod
    def get_openrouter_params(cls) -> Dict[str, Any]:
        """Get OpenRouter API parameters."""
        return {
            'model': cls.OPENROUTER_MODEL,
            'max_tokens': cls.OPENROUTER_MAX_TOKENS,
            'temperature': cls.OPENROUTER_TEMPERATURE
        }
    
    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            'max_requests': cls.MAX_REQUESTS_PER_MINUTE,
            'window': cls.RATE_LIMIT_WINDOW,
            'burst_limit': cls.BURST_LIMIT,
            'burst_window': cls.BURST_WINDOW
        }
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            'max_size': cls.CACHE_MAX_SIZE,
            'ttl': cls.CACHE_TTL,
            'spotify_ttl': cls.SPOTIFY_CACHE_TTL,
            'openrouter_ttl': cls.OPENROUTER_CACHE_TTL
        }
    
    @classmethod
    def validate_environment(cls) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = [
            'DISCORD_TOKEN',
            'SPOTIFY_CLIENT_ID',
            'SPOTIFY_CLIENT_SECRET',
            'OPENROUTER_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration for debugging."""
        print("=== Bot Configuration ===")
        print(f"Bot Name: {cls.BOT_NAME}")
        print(f"Command Prefix: {cls.COMMAND_PREFIX}")
        print(f"Cache Max Size: {cls.CACHE_MAX_SIZE}")
        print(f"Cache TTL: {cls.CACHE_TTL}s")
        print(f"Rate Limit: {cls.MAX_REQUESTS_PER_MINUTE} requests per {cls.RATE_LIMIT_WINDOW}s")
        print(f"API Timeout: {cls.API_TIMEOUT}s")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("========================")

# Create a global config instance
config = BotConfig()
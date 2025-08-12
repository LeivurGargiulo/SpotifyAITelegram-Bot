#!/usr/bin/env python3
"""
Enhanced Discord Music Recommendation Bot
Converted from Telegram bot with all functionality intact.
"""

import os
import logging
import asyncio
import json
import time
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import hashlib
from datetime import datetime, timedelta

import aiohttp
import discord
from discord.ext import commands, tasks

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class Track:
    """Represents a music track with its details."""
    title: str
    artist: str
    spotify_url: str
    album: str = ""
    popularity: int = 0
    duration_ms: int = 0
    preview_url: Optional[str] = None

class Cache:
    """Simple in-memory cache for recommendations and tokens."""
    
    def __init__(self, ttl: int = 3600):  # 1 hour default TTL
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[any]:
        """Get value from cache if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: any) -> None:
        """Set value in cache with current timestamp."""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limits."""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < self.window]
        
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        return False
    
    def get_remaining(self, user_id: int) -> int:
        """Get remaining requests for user."""
        now = time.time()
        user_requests = self.requests[user_id]
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < self.window]
        return max(0, self.max_requests - len(user_requests))

class EnhancedSpotifyAPI:
    """Enhanced Spotify API with better keyword processing and caching."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0
        self.cache = Cache(ttl=1800)  # 30 minutes for recommendations
    
    async def _get_access_token(self) -> str:
        """Get Spotify access token with caching."""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            'grant_type': 'client_credentials'
        }
        auth_headers = {
            'Authorization': f'Basic {self._get_basic_auth()}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data, headers=auth_headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data['access_token']
                    self.token_expiry = time.time() + data['expires_in'] - 60  # Buffer
                    return self.access_token
                else:
                    raise Exception(f"Failed to get Spotify token: {response.status}")
    
    def _get_basic_auth(self) -> str:
        """Get basic auth string for Spotify."""
        import base64
        auth_string = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(auth_string.encode()).decode()
    
    async def get_recommendations(self, keywords: List[str]) -> List[Track]:
        """Get music recommendations based on keywords."""
        # Create cache key from keywords
        cache_key = hashlib.md5(','.join(sorted(keywords)).encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached recommendations for keywords: {keywords}")
            return cached_result
        
        try:
            access_token = await self._get_access_token()
            
            # Build seed parameters from keywords
            seed_genres, seed_artists, seed_tracks = await self._extract_seeds(keywords, access_token)
            
            # Build recommendation parameters
            params = {
                'limit': 5,
                'market': 'US'
            }
            
            if seed_genres:
                params['seed_genres'] = ','.join(seed_genres[:5])
            if seed_artists:
                params['seed_artists'] = ','.join(seed_artists[:5])
            if seed_tracks:
                params['seed_tracks'] = ','.join(seed_tracks[:5])
            
            # Add audio features based on keywords
            audio_features = self._get_audio_features_from_keywords(keywords)
            params.update(audio_features)
            
            # Make recommendation request
            url = "https://api.spotify.com/v1/recommendations"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for track_data in data.get('tracks', []):
                            track = Track(
                                title=track_data['name'],
                                artist=track_data['artists'][0]['name'],
                                spotify_url=track_data['external_urls']['spotify'],
                                album=track_data['album']['name'],
                                popularity=track_data['popularity'],
                                duration_ms=track_data['duration_ms'],
                                preview_url=track_data.get('preview_url')
                            )
                            tracks.append(track)
                        
                        # Cache the result
                        self.cache.set(cache_key, tracks)
                        return tracks
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify API error: {response.status} - {error_text}")
                        raise Exception(f"Spotify API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
    
    async def _extract_seeds(self, keywords: List[str], access_token: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract seed genres, artists, and tracks from keywords."""
        seed_genres = []
        seed_artists = []
        seed_tracks = []
        
        # Common genre mappings
        genre_mappings = {
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
        
        # Extract genres from keywords
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for word, genre in genre_mappings.items():
                if word in keyword_lower and genre not in seed_genres:
                    seed_genres.append(genre)
                    break
        
        return seed_genres[:5], seed_artists[:5], seed_tracks[:5]
    
    def _get_audio_features_from_keywords(self, keywords: List[str]) -> Dict[str, float]:
        """Get audio features based on keywords."""
        features = {}
        keywords_lower = [k.lower() for k in keywords]
        
        # Energy mapping
        if any(word in keywords_lower for word in ['energetic', 'upbeat', 'fast', 'dance', 'party', 'workout']):
            features['target_energy'] = 0.8
            features['min_energy'] = 0.6
        elif any(word in keywords_lower for word in ['calm', 'relaxing', 'chill', 'sleep', 'study']):
            features['target_energy'] = 0.3
            features['max_energy'] = 0.5
        
        # Valence (happiness) mapping
        if any(word in keywords_lower for word in ['happy', 'joyful', 'cheerful', 'upbeat']):
            features['target_valence'] = 0.8
            features['min_valence'] = 0.6
        elif any(word in keywords_lower for word in ['sad', 'melancholy', 'depressing']):
            features['target_valence'] = 0.3
            features['max_valence'] = 0.5
        
        # Tempo mapping
        if any(word in keywords_lower for word in ['fast', 'energetic', 'workout', 'dance']):
            features['target_tempo'] = 140
            features['min_tempo'] = 120
        elif any(word in keywords_lower for word in ['slow', 'calm', 'relaxing']):
            features['target_tempo'] = 80
            features['max_tempo'] = 100
        
        return features

class EnhancedOpenRouterAPI:
    """Enhanced OpenRouter API for keyword extraction."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = Cache(ttl=3600)  # 1 hour cache for keyword extraction
    
    async def extract_music_keywords(self, user_message: str) -> List[str]:
        """Extract music-related keywords from user message using AI."""
        # Create cache key from message
        cache_key = hashlib.md5(user_message.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached keywords for message: {user_message[:50]}...")
            return cached_result
        
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://discord-music-bot.com',
                'X-Title': 'Discord Music Bot'
            }
            
            prompt = f"""
            Extract music-related keywords from this user message. Focus on:
            - Moods and emotions (happy, sad, energetic, calm, romantic, etc.)
            - Music genres (rock, pop, jazz, classical, electronic, etc.)
            - Activities (workout, study, party, sleep, driving, etc.)
            - Time periods (80s, 90s, 2000s, etc.)
            - Seasons or occasions (summer, winter, christmas, etc.)
            
            User message: "{user_message}"
            
            Return only the keywords as a comma-separated list, no explanations.
            Maximum 10 keywords.
            """
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100,
                'temperature': 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        content = await response.json()
                        try:
                            keywords_text = content['choices'][0]['message']['content'].strip()
                            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                            
                            # Cache the result
                            self.cache.set(cache_key, keywords)
                            return keywords
                        except (KeyError, IndexError):
                            logger.warning(f"Unexpected response format: {content}")
                            return []
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise

class EnhancedDiscordMusicBot(commands.Bot):
    """Enhanced Discord bot with all Telegram bot functionality converted."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll create our own help command
        )
        
        # Initialize APIs and utilities
        self.spotify_api = EnhancedSpotifyAPI(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        self.openrouter_api = EnhancedOpenRouterAPI(
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
        self.rate_limiter = RateLimiter(max_requests=15, window=60)  # 15 requests per minute
        self.user_stats = defaultdict(int)
        self.start_time = datetime.now()
        self.error_logs = []
        
        # Load cogs
        try:
            self.load_extension('cogs.music_commands')
            self.load_extension('cogs.utility_commands')
            self.load_extension('cogs.error_handler')
            logger.info("All cogs loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cogs: {e}")
        
        # Start background tasks
        self.cleanup_cache.start()
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up Discord Music Bot...")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="!help for music recommendations"
        )
        await self.change_presence(activity=activity)
    
    @tasks.loop(hours=1)
    async def cleanup_cache(self):
        """Background task to clean up expired cache entries."""
        logger.info("Running cache cleanup...")
        self.spotify_api.cache.clear()
        self.openrouter_api.cache.clear()
        logger.info("Cache cleanup completed")
    
    @cleanup_cache.before_loop
    async def before_cleanup_cache(self):
        """Wait until the bot is ready before starting the cleanup task."""
        await self.wait_until_ready()

async def main():
    """Main function to run the Discord bot."""
    # Check required environment variables
    required_env_vars = ['DISCORD_TOKEN', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set all required environment variables before running the bot.")
        print("Required variables:")
        print("- DISCORD_TOKEN: Your Discord bot token")
        print("- SPOTIFY_CLIENT_ID: Spotify API client ID")
        print("- SPOTIFY_CLIENT_SECRET: Spotify API client secret")
        print("- OPENROUTER_API_KEY: OpenRouter API key")
        return
    
    # Initialize and run the bot
    bot = EnhancedDiscordMusicBot()
    
    try:
        logger.info("Starting Enhanced Discord Music Recommendation Bot...")
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
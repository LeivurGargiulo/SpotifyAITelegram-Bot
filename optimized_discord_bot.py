#!/usr/bin/env python3
"""
Optimized Discord Music Recommendation Bot
Production-ready with enhanced performance, security, and maintainability.
"""

import os
import logging
import asyncio
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import signal
import sys

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure comprehensive logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Type aliases for better code readability
UserID = int
GuildID = int
CacheKey = str
APIResponse = Dict[str, Any]

@dataclass
class Track:
    """Represents a music track with comprehensive details."""
    title: str
    artist: str
    spotify_url: str
    album: str = ""
    popularity: int = 0
    duration_ms: int = 0
    preview_url: Optional[str] = None
    release_date: Optional[str] = None
    genres: List[str] = None
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary for serialization."""
        return asdict(self)

@dataclass
class CacheEntry:
    """Cache entry with metadata for better cache management."""
    value: Any
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0.0

class OptimizedCache:
    """Advanced in-memory cache with LRU eviction and access tracking."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[CacheKey, CacheEntry] = {}
        self.access_order = deque()
        self._lock = asyncio.Lock()
    
    async def get(self, key: CacheKey) -> Optional[Any]:
        """Get value from cache with access tracking."""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                now = time.time()
                
                # Check if entry is expired
                if now - entry.timestamp > self.ttl:
                    await self._remove_entry(key)
                    return None
                
                # Update access metadata
                entry.access_count += 1
                entry.last_accessed = now
                
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.value
            return None
    
    async def set(self, key: CacheKey, value: Any) -> None:
        """Set value in cache with size management."""
        async with self._lock:
            now = time.time()
            
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                timestamp=now,
                access_count=1,
                last_accessed=now
            )
            
            self.cache[key] = entry
            self.access_order.append(key)
    
    async def _remove_entry(self, key: CacheKey) -> None:
        """Remove entry from cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.access_order:
            lru_key = self.access_order.popleft()
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self.cache.clear()
            self.access_order.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_entries = len(self.cache)
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            avg_accesses = total_accesses / total_entries if total_entries > 0 else 0
            
            return {
                'total_entries': total_entries,
                'max_size': self.max_size,
                'utilization': total_entries / self.max_size,
                'total_accesses': total_accesses,
                'avg_accesses_per_entry': avg_accesses
            }

class AdvancedRateLimiter:
    """Advanced rate limiter with sliding window and per-user tracking."""
    
    def __init__(self, max_requests: int = 15, window: int = 60, burst_limit: int = 5):
        self.max_requests = max_requests
        self.window = window
        self.burst_limit = burst_limit
        self.requests: Dict[UserID, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, user_id: UserID) -> bool:
        """Check if user is within rate limits with burst protection."""
        async with self._lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove old requests outside the window
            while user_requests and now - user_requests[0] > self.window:
                user_requests.popleft()
            
            # Check burst limit
            if len(user_requests) >= self.burst_limit:
                time_since_first = now - user_requests[0]
                if time_since_first < 10:  # Burst window of 10 seconds
                    return False
            
            # Check regular rate limit
            if len(user_requests) < self.max_requests:
                user_requests.append(now)
                return True
            return False
    
    async def get_remaining(self, user_id: UserID) -> int:
        """Get remaining requests for user."""
        async with self._lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove old requests
            while user_requests and now - user_requests[0] > self.window:
                user_requests.popleft()
            
            return max(0, self.max_requests - len(user_requests))
    
    async def get_user_stats(self, user_id: UserID) -> Dict[str, Any]:
        """Get detailed stats for a user."""
        async with self._lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove old requests
            while user_requests and now - user_requests[0] > self.window:
                user_requests.popleft()
            
            return {
                'requests_in_window': len(user_requests),
                'remaining_requests': max(0, self.max_requests - len(user_requests)),
                'window_reset_time': now + self.window,
                'is_rate_limited': len(user_requests) >= self.max_requests
            }

class SecureAPIClient:
    """Secure API client with retry logic, timeout handling, and error recovery."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic."""
        if not self.session:
            raise RuntimeError("APIClient not initialized. Use async context manager.")
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status < 500 or attempt == self.max_retries - 1:
                        return response
                    
                    # Retry on server errors
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise aiohttp.ClientError("Max retries exceeded")

class OptimizedSpotifyAPI:
    """Optimized Spotify API with enhanced caching and error handling."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        self.cache = OptimizedCache(ttl=1800)  # 30 minutes for recommendations
        self.token_cache = OptimizedCache(ttl=3500)  # Token cache with buffer
        self._token_lock = asyncio.Lock()
    
    async def _get_access_token(self) -> str:
        """Get Spotify access token with thread-safe caching."""
        async with self._token_lock:
            # Check cache first
            cached_token = await self.token_cache.get('spotify_token')
            if cached_token:
                return cached_token
            
            # Get new token
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {'grant_type': 'client_credentials'}
            auth_headers = {'Authorization': f'Basic {self._get_basic_auth()}'}
            
            async with SecureAPIClient() as client:
                async with client.request('POST', auth_url, data=auth_data, headers=auth_headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        token = data['access_token']
                        
                        # Cache token with buffer time
                        await self.token_cache.set('spotify_token', token)
                        return token
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify token error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get Spotify token: {response.status}")
    
    def _get_basic_auth(self) -> str:
        """Get basic auth string for Spotify."""
        import base64
        auth_string = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(auth_string.encode()).decode()
    
    async def get_recommendations(self, keywords: List[str]) -> List[Track]:
        """Get music recommendations with enhanced caching and error handling."""
        # Create cache key from sorted keywords for consistency
        cache_key = hashlib.md5(','.join(sorted(keywords)).encode()).hexdigest()
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for keywords: {keywords[:3]}...")
            return cached_result
        
        try:
            access_token = await self._get_access_token()
            
            # Build recommendation parameters
            params = await self._build_recommendation_params(keywords, access_token)
            
            # Make recommendation request
            url = "https://api.spotify.com/v1/recommendations"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with SecureAPIClient() as client:
                async with client.request('GET', url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = self._parse_tracks(data.get('tracks', []))
                        
                        # Cache the result
                        await self.cache.set(cache_key, tracks)
                        logger.info(f"Generated recommendations for keywords: {keywords[:3]}...")
                        return tracks
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify API error: {response.status} - {error_text}")
                        raise Exception(f"Spotify API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
    
    async def _build_recommendation_params(self, keywords: List[str], access_token: str) -> Dict[str, Any]:
        """Build recommendation parameters from keywords."""
        params = {'limit': 5, 'market': 'US'}
        
        # Extract seeds from keywords
        seed_genres, seed_artists, seed_tracks = await self._extract_seeds(keywords, access_token)
        
        if seed_genres:
            params['seed_genres'] = ','.join(seed_genres[:5])
        if seed_artists:
            params['seed_artists'] = ','.join(seed_artists[:5])
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks[:5])
        
        # Add audio features
        audio_features = self._get_audio_features_from_keywords(keywords)
        params.update(audio_features)
        
        return params
    
    def _parse_tracks(self, tracks_data: List[Dict[str, Any]]) -> List[Track]:
        """Parse track data into Track objects."""
        tracks = []
        for track_data in tracks_data:
            track = Track(
                title=track_data['name'],
                artist=track_data['artists'][0]['name'],
                spotify_url=track_data['external_urls']['spotify'],
                album=track_data['album']['name'],
                popularity=track_data['popularity'],
                duration_ms=track_data['duration_ms'],
                preview_url=track_data.get('preview_url'),
                release_date=track_data['album'].get('release_date')
            )
            tracks.append(track)
        return tracks
    
    async def _extract_seeds(self, keywords: List[str], access_token: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract seed genres, artists, and tracks from keywords."""
        # Genre mappings (simplified for performance)
        genre_mappings = {
            'rock': 'rock', 'pop': 'pop', 'jazz': 'jazz', 'classical': 'classical',
            'electronic': 'electronic', 'hip-hop': 'hip-hop', 'rap': 'hip-hop',
            'country': 'country', 'blues': 'blues', 'reggae': 'reggae',
            'folk': 'folk', 'metal': 'metal', 'punk': 'punk', 'indie': 'indie',
            'alternative': 'alternative', 'r&b': 'r-n-b', 'soul': 'soul',
            'funk': 'funk', 'disco': 'disco', 'house': 'house', 'techno': 'techno',
            'trance': 'trance', 'ambient': 'ambient', 'lofi': 'lofi',
            'chill': 'chill', 'energetic': 'dance', 'party': 'dance',
            'romantic': 'romance', 'sad': 'sad', 'happy': 'happy',
            'calm': 'calm', 'relaxing': 'relaxing'
        }
        
        seed_genres = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for word, genre in genre_mappings.items():
                if word in keyword_lower and genre not in seed_genres:
                    seed_genres.append(genre)
                    break
        
        return seed_genres[:5], [], []  # Simplified for performance
    
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
        
        # Valence mapping
        if any(word in keywords_lower for word in ['happy', 'joyful', 'cheerful', 'upbeat']):
            features['target_valence'] = 0.8
            features['min_valence'] = 0.6
        elif any(word in keywords_lower for word in ['sad', 'melancholy', 'depressing']):
            features['target_valence'] = 0.3
            features['max_valence'] = 0.5
        
        return features

class OptimizedOpenRouterAPI:
    """Optimized OpenRouter API with enhanced caching and error handling."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = OptimizedCache(ttl=3600)  # 1 hour cache
    
    async def extract_music_keywords(self, user_message: str) -> List[str]:
        """Extract music-related keywords with caching."""
        # Create cache key from message hash
        cache_key = hashlib.md5(user_message.encode()).hexdigest()
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for keyword extraction: {user_message[:30]}...")
            return cached_result
        
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://discord-music-bot.com',
                'X-Title': 'Discord Music Bot'
            }
            
            prompt = self._build_keyword_prompt(user_message)
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100,
                'temperature': 0.3
            }
            
            async with SecureAPIClient() as client:
                async with client.request('POST', url, json=data, headers=headers) as response:
                    if response.status == 200:
                        content = await response.json()
                        keywords = self._parse_keywords_response(content)
                        
                        # Cache the result
                        await self.cache.set(cache_key, keywords)
                        return keywords
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            # Return fallback keywords based on simple text analysis
            return self._fallback_keyword_extraction(user_message)
    
    def _build_keyword_prompt(self, user_message: str) -> str:
        """Build optimized prompt for keyword extraction."""
        return f"""
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
    
    def _parse_keywords_response(self, content: Dict[str, Any]) -> List[str]:
        """Parse keywords from API response."""
        try:
            keywords_text = content['choices'][0]['message']['content'].strip()
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            return keywords[:10]  # Limit to 10 keywords
        except (KeyError, IndexError) as e:
            logger.warning(f"Unexpected response format: {e}")
            return []
    
    def _fallback_keyword_extraction(self, user_message: str) -> List[str]:
        """Fallback keyword extraction using simple text analysis."""
        keywords = []
        message_lower = user_message.lower()
        
        # Simple keyword detection
        mood_keywords = ['happy', 'sad', 'energetic', 'calm', 'romantic', 'melancholy']
        genre_keywords = ['rock', 'pop', 'jazz', 'classical', 'electronic', 'hip-hop', 'country']
        activity_keywords = ['workout', 'study', 'party', 'sleep', 'driving', 'running']
        
        for keyword in mood_keywords + genre_keywords + activity_keywords:
            if keyword in message_lower:
                keywords.append(keyword)
        
        return keywords[:5]  # Return up to 5 keywords

class OptimizedDiscordBot(commands.Bot):
    """Optimized Discord bot with enhanced performance and reliability."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            max_messages=10000  # Optimize memory usage
        )
        
        # Initialize core components
        self._initialize_apis()
        self._initialize_utilities()
        self._initialize_metrics()
        
        # Load cogs
        self._load_cogs()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _initialize_apis(self):
        """Initialize API clients with proper error handling."""
        try:
            self.spotify_api = OptimizedSpotifyAPI(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
            self.openrouter_api = OptimizedOpenRouterAPI(
                api_key=os.getenv('OPENROUTER_API_KEY')
            )
            logger.info("API clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {e}")
            raise
    
    def _initialize_utilities(self):
        """Initialize utility components."""
        self.rate_limiter = AdvancedRateLimiter(max_requests=15, window=60)
        self.user_stats = defaultdict(int)
        self.start_time = datetime.now()
        self.error_logs = deque(maxlen=100)  # Keep last 100 errors
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_errors': 0,
            'avg_response_time': 0.0
        }
    
    def _initialize_metrics(self):
        """Initialize performance tracking."""
        self.request_times = deque(maxlen=1000)
        self.last_cleanup = time.time()
    
    def _load_cogs(self):
        """Load bot cogs with error handling."""
        cogs_to_load = [
            'cogs.music_commands',
            'cogs.utility_commands', 
            'cogs.error_handler',
            'cogs.performance_monitor'
        ]
        
        for cog in cogs_to_load:
            try:
                self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        self.cleanup_cache.start()
        self.update_presence.start()
        self.log_performance_metrics.start()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.close())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up Optimized Discord Music Bot...")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set initial presence
        await self._update_presence()
    
    @tasks.loop(hours=1)
    async def cleanup_cache(self):
        """Background task to clean up expired cache entries."""
        try:
            logger.info("Running cache cleanup...")
            await self.spotify_api.cache.clear()
            await self.openrouter_api.cache.clear()
            logger.info("Cache cleanup completed")
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    @tasks.loop(minutes=5)
    async def update_presence(self):
        """Update bot presence with current stats."""
        try:
            await self._update_presence()
        except Exception as e:
            logger.error(f"Presence update error: {e}")
    
    @tasks.loop(minutes=10)
    async def log_performance_metrics(self):
        """Log performance metrics periodically."""
        try:
            cache_stats = await self.spotify_api.cache.get_stats()
            logger.info(f"Performance metrics: {self.performance_metrics}")
            logger.info(f"Cache stats: {cache_stats}")
        except Exception as e:
            logger.error(f"Metrics logging error: {e}")
    
    async def _update_presence(self):
        """Update bot presence with current statistics."""
        total_requests = self.performance_metrics['total_requests']
        cache_hit_rate = (
            self.performance_metrics['cache_hits'] / 
            max(1, self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'])
        ) * 100
        
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"!help | {total_requests} requests | {cache_hit_rate:.1f}% cache"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler with enhanced logging."""
        error_msg = f"Command error in {ctx.guild.name if ctx.guild else 'DM'} by {ctx.author}: {str(error)}"
        logger.error(error_msg)
        
        # Add to error logs
        self.error_logs.append({
            'timestamp': datetime.now(),
            'error': str(error),
            'user': ctx.author.id,
            'guild': ctx.guild.id if ctx.guild else None,
            'command': ctx.command.name if ctx.command else None
        })
        
        # Update metrics
        self.performance_metrics['api_errors'] += 1
        
        # Let the error handler cog handle the rest
        await super().on_command_error(ctx, error)

async def main():
    """Main function with comprehensive error handling and validation."""
    # Validate environment variables
    required_env_vars = [
        'DISCORD_TOKEN', 
        'SPOTIFY_CLIENT_ID', 
        'SPOTIFY_CLIENT_SECRET', 
        'OPENROUTER_API_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set all required environment variables before running the bot.")
        return
    
    # Initialize and run the bot
    bot = OptimizedDiscordBot()
    
    try:
        logger.info("Starting Optimized Discord Music Recommendation Bot...")
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Critical error running bot: {e}")
        raise
    finally:
        logger.info("Shutting down bot...")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
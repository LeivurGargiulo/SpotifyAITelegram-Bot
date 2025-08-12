#!/usr/bin/env python3
"""
Enhanced Telegram Music Recommendation Bot
Advanced version with improved keyword processing, caching, and better error handling.
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

import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
        self.genre_cache = Cache(ttl=86400)  # 24 hours for genres
        
    async def _get_access_token(self) -> str:
        """Get Spotify access token using client credentials flow."""
        if self.access_token and asyncio.get_event_loop().time() < self.token_expiry:
            return self.access_token
            
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.token_expiry = asyncio.get_event_loop().time() + token_data['expires_in'] - 60
                    logger.info("Successfully obtained Spotify access token")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get Spotify token: {response.status} - {error_text}")
                    raise Exception(f"Spotify authentication failed: {response.status}")
    
    async def get_available_genres(self) -> List[str]:
        """Get list of available Spotify genres."""
        cache_key = "available_genres"
        cached_genres = self.cache.get(cache_key)
        if cached_genres:
            return cached_genres
        
        try:
            access_token = await self._get_access_token()
            headers = {'Authorization': f'Bearer {access_token}'}
            url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        genres = data.get('genres', [])
                        self.cache.set(cache_key, genres)
                        return genres
                    else:
                        logger.error(f"Failed to get genres: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting genres: {str(e)}")
            return []
    
    async def search_artists(self, query: str, limit: int = 5) -> List[str]:
        """Search for artists and return their Spotify IDs."""
        try:
            access_token = await self._get_access_token()
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'q': query,
                'type': 'artist',
                'limit': limit
            }
            url = "https://api.spotify.com/v1/search"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        artists = data.get('artists', {}).get('items', [])
                        return [artist['id'] for artist in artists]
                    else:
                        logger.error(f"Failed to search artists: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching artists: {str(e)}")
            return []
    
    async def get_recommendations(self, keywords: List[str], limit: int = 5) -> List[Track]:
        """Get music recommendations based on keywords with enhanced processing."""
        # Create cache key from keywords
        cache_key = hashlib.md5(','.join(sorted(keywords)).encode()).hexdigest()
        cached_tracks = self.cache.get(cache_key)
        if cached_tracks:
            logger.info("Returning cached recommendations")
            return cached_tracks
        
        try:
            access_token = await self._get_access_token()
            
            # Enhanced keyword processing
            seed_genres, seed_artists, seed_tracks = await self._enhanced_process_keywords(keywords)
            
            params = {
                'limit': limit,
                'market': 'US'
            }
            
            # Add seed parameters if available
            if seed_genres:
                params['seed_genres'] = ','.join(seed_genres[:5])
            if seed_artists:
                params['seed_artists'] = ','.join(seed_artists[:5])
            if seed_tracks:
                params['seed_tracks'] = ','.join(seed_tracks[:5])
            
            # Add audio features for better recommendations
            if any(keyword in ['energetic', 'upbeat', 'fast'] for keyword in keywords):
                params['target_energy'] = 0.8
                params['min_energy'] = 0.6
            elif any(keyword in ['calm', 'relaxing', 'chill'] for keyword in keywords):
                params['target_energy'] = 0.3
                params['max_energy'] = 0.5
            
            if any(keyword in ['happy', 'positive'] for keyword in keywords):
                params['target_valence'] = 0.8
                params['min_valence'] = 0.6
            elif any(keyword in ['sad', 'melancholic'] for keyword in keywords):
                params['target_valence'] = 0.3
                params['max_valence'] = 0.5
            
            headers = {'Authorization': f'Bearer {access_token}'}
            url = "https://api.spotify.com/v1/recommendations"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for track in data.get('tracks', []):
                            artists = ', '.join([artist['name'] for artist in track['artists']])
                            track_obj = Track(
                                title=track['name'],
                                artist=artists,
                                spotify_url=track['external_urls']['spotify'],
                                album=track['album']['name'],
                                popularity=track.get('popularity', 0),
                                duration_ms=track.get('duration_ms', 0),
                                preview_url=track.get('preview_url')
                            )
                            tracks.append(track_obj)
                        
                        # Cache the results
                        self.cache.set(cache_key, tracks)
                        logger.info(f"Successfully retrieved {len(tracks)} recommendations")
                        return tracks
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify API error: {response.status} - {error_text}")
                        raise Exception(f"Spotify API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting Spotify recommendations: {str(e)}")
            raise
    
    async def _enhanced_process_keywords(self, keywords: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Enhanced keyword processing with artist search and genre validation."""
        seed_genres = []
        seed_artists = []
        seed_tracks = []
        
        # Get available genres for validation
        available_genres = await self.get_available_genres()
        
        # Enhanced genre mapping
        genre_mapping = {
            'rock': 'rock',
            'pop': 'pop',
            'jazz': 'jazz',
            'classical': 'classical',
            'electronic': 'electronic',
            'hip hop': 'hip-hop',
            'hiphop': 'hip-hop',
            'country': 'country',
            'blues': 'blues',
            'reggae': 'reggae',
            'folk': 'folk',
            'r&b': 'r-n-b',
            'rnb': 'r-n-b',
            'soul': 'soul',
            'funk': 'funk',
            'disco': 'disco',
            'punk': 'punk',
            'metal': 'metal',
            'indie': 'indie',
            'alternative': 'alternative',
            'ambient': 'ambient',
            'chill': 'chill',
            'energetic': 'dance',
            'happy': 'pop',
            'sad': 'sad',
            'romantic': 'romance',
            'workout': 'workout',
            'party': 'party',
            'study': 'study',
            'sleep': 'sleep',
            'driving': 'road-trip',
            'road trip': 'road-trip',
            'summer': 'summer',
            'winter': 'winter',
            'christmas': 'christmas',
            'holiday': 'holiday'
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check genre mapping
            if keyword_lower in genre_mapping:
                mapped_genre = genre_mapping[keyword_lower]
                if mapped_genre in available_genres:
                    seed_genres.append(mapped_genre)
            
            # Check if it's a direct genre
            elif keyword_lower in available_genres:
                seed_genres.append(keyword_lower)
            
            # Try to find artists for the keyword
            elif len(keyword) > 2:  # Only search for keywords longer than 2 chars
                artist_ids = await self.search_artists(keyword, limit=1)
                if artist_ids:
                    seed_artists.extend(artist_ids)
        
        return seed_genres, seed_artists, seed_tracks

class EnhancedOpenRouterAPI:
    """Enhanced OpenRouter API with better prompt engineering."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def extract_music_keywords(self, user_message: str) -> List[str]:
        """Extract music-related keywords from user message using enhanced AI prompt."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/your-repo/music-bot',
                'X-Title': 'Enhanced Music Recommendation Bot'
            }
            
            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert music recommendation assistant. Extract music-related keywords from user messages with high precision.

Focus on extracting:
1. **Genres**: rock, pop, jazz, classical, electronic, hip-hop, country, blues, reggae, folk, r&b, soul, funk, disco, punk, metal, indie, alternative, ambient, etc.
2. **Moods**: happy, sad, energetic, calm, romantic, melancholic, upbeat, relaxing, exciting, peaceful, etc.
3. **Activities**: workout, study, party, sleep, driving, cooking, cleaning, meditation, etc.
4. **Time periods**: 80s, 90s, 2000s, 2010s, 2020s, etc.
5. **Specific artists/bands** (if clearly mentioned)
6. **Seasons/occasions**: summer, winter, christmas, holiday, etc.

Guidelines:
- Return ONLY a JSON array of relevant keywords (strings)
- Be specific but not overly granular
- If no clear music-related keywords found, return empty array []
- Don't include generic words like "music", "song", "listen"
- Normalize variations (e.g., "hip hop" → "hip-hop")

Examples:
- "I'm feeling sad and want some slow music" → ["sad", "slow"]
- "Need energetic rock for my workout" → ["energetic", "rock", "workout"]
- "I love jazz and classical from the 50s" → ["jazz", "classical", "50s"]
- "Just want some background music" → [] (too vague)
- "Looking for romantic songs for dinner" → ["romantic", "dinner"]"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 150
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content'].strip()
                        
                        try:
                            keywords = json.loads(content)
                            if isinstance(keywords, list):
                                # Filter out empty strings and normalize
                                keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
                                logger.info(f"Extracted keywords: {keywords}")
                                return keywords
                            else:
                                logger.warning(f"Unexpected response format: {content}")
                                return []
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON response: {content}")
                            return []
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise

class EnhancedMusicRecommendationBot:
    """Enhanced bot with caching, rate limiting, and better user experience."""
    
    def __init__(self):
        self.spotify_api = EnhancedSpotifyAPI(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        self.openrouter_api = EnhancedOpenRouterAPI(
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
        self.rate_limiter = RateLimiter(max_requests=15, window=60)  # 15 requests per minute
        self.user_stats = defaultdict(int)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with enhanced welcome message."""
        welcome_message = """
🎵 *Welcome to Enhanced Music Recommendation Bot!* 🎵

I'm your AI-powered music companion that understands your mood and preferences to recommend the perfect tracks!

*How to use me:*
• Tell me your mood: "I'm feeling sad today"
• Describe activities: "Need energetic music for my workout"
• Mention genres: "I love jazz and classical"
• Combine preferences: "Want romantic rock songs for driving"

*Examples:*
• "I'm feeling happy and energetic"
• "Need calm music for studying"
• "Looking for 80s rock classics"
• "Want some jazz for dinner"
• "Need party music for tonight"

*Features:*
✨ AI-powered mood analysis
🎯 Personalized recommendations
⚡ Fast response with caching
🔄 Rate limited (15 requests/minute)
📊 Track popularity and previews

Just send me a message describing what you're looking for! 🎶

*Commands:*
/start - Show this message
/stats - Show your usage statistics
/help - Get help and examples
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
🎵 *Music Recommendation Bot Help* 🎵

*How it works:*
1. I analyze your message using AI
2. Extract music-related keywords
3. Find perfect recommendations on Spotify
4. Send you 5 curated tracks

*What I understand:*
• **Moods**: happy, sad, energetic, calm, romantic, etc.
• **Genres**: rock, pop, jazz, classical, electronic, hip-hop, etc.
• **Activities**: workout, study, party, sleep, driving, etc.
• **Time periods**: 80s, 90s, 2000s, etc.
• **Seasons**: summer, winter, christmas, etc.

*Tips for better recommendations:*
• Be specific: "energetic rock for workout" vs "music"
• Combine preferences: "romantic jazz for dinner"
• Mention activities: "calm music for studying"
• Include time periods: "80s pop classics"

*Rate Limits:*
• 15 requests per minute per user
• Use /stats to check your usage

Need more help? Just ask! 🎶
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command to show user statistics."""
        user_id = update.effective_user.id
        requests_made = self.user_stats[user_id]
        remaining = self.rate_limiter.get_remaining(user_id)
        
        stats_message = f"""
📊 *Your Usage Statistics*

*Requests made:* {requests_made}
*Remaining this minute:* {remaining}/15

*Rate limit:* 15 requests per minute
*Reset time:* Every minute

Keep enjoying your music! 🎶
        """
        
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages with rate limiting and enhanced processing."""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received message from user {user_id}: {user_message}")
        
        # Check rate limiting
        if not self.rate_limiter.is_allowed(user_id):
            remaining_time = 60 - int(time.time() % 60)
            await update.message.reply_text(
                f"⏰ Rate limit exceeded! Please wait {remaining_time} seconds before making another request.\n\n"
                f"Limit: 15 requests per minute"
            )
            return
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Extract keywords using OpenRouter
            keywords = await self.openrouter_api.extract_music_keywords(user_message)
            
            if not keywords:
                await update.message.reply_text(
                    "🤔 I couldn't understand what kind of music you're looking for.\n\n"
                    "*Try being more specific:*\n"
                    "• \"I'm feeling happy and want upbeat music\"\n"
                    "• \"Need rock music for my workout\"\n"
                    "• \"I love jazz and classical music\"\n"
                    "• \"Want romantic songs for dinner\"\n\n"
                    "Use /help for more examples!"
                )
                return
            
            # Get music recommendations from Spotify
            tracks = await self.spotify_api.get_recommendations(keywords)
            
            if not tracks:
                await update.message.reply_text(
                    "😔 Sorry, I couldn't find any music recommendations based on your request.\n\n"
                    "*Try these suggestions:*\n"
                    "• Be more specific about genres or moods\n"
                    "• Mention activities or situations\n"
                    "• Use /help to see examples"
                )
                return
            
            # Update user statistics
            self.user_stats[user_id] += 1
            
            # Format and send recommendations
            response = self._format_enhanced_recommendations(tracks, keywords)
            await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
            
            logger.info(f"Successfully sent recommendations to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            await update.message.reply_text(
                "😞 Sorry, I encountered an error while processing your request.\n\n"
                "This might be due to:\n"
                "• Temporary API issues\n"
                "• Network connectivity problems\n\n"
                "Please try again in a moment!"
            )
    
    def _format_enhanced_recommendations(self, tracks: List[Track], keywords: List[str]) -> str:
        """Format track recommendations with enhanced information."""
        keywords_text = ', '.join(keywords)
        
        response = f"🎵 *Music Recommendations* 🎵\n\n"
        response += f"*Based on:* {keywords_text}\n\n"
        
        for i, track in enumerate(tracks, 1):
            # Add popularity indicator
            popularity_emoji = "🔥" if track.popularity > 70 else "⭐" if track.popularity > 40 else "💫"
            
            response += f"{i}. **{track.title}** - {track.artist}\n"
            response += f"   📀 Album: {track.album}\n"
            response += f"   {popularity_emoji} Popularity: {track.popularity}%\n"
            
            # Add duration if available
            if track.duration_ms:
                duration_min = track.duration_ms // 60000
                duration_sec = (track.duration_ms % 60000) // 1000
                response += f"   ⏱️ Duration: {duration_min}:{duration_sec:02d}\n"
            
            response += f"   🎧 [Listen on Spotify]({track.spotify_url})\n\n"
        
        response += "🎶 *Enjoy your music!*\n"
        response += f"💡 *Tip:* Use /stats to check your usage"
        
        return response
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😞 Sorry, something went wrong. Please try again later!\n\n"
                "If the problem persists, please contact support."
            )

async def main():
    """Main function to run the enhanced bot."""
    # Check required environment variables
    required_env_vars = ['TELEGRAM_TOKEN', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set all required environment variables before running the bot.")
        print("See .env.example for reference.")
        return
    
    # Initialize enhanced bot
    bot = EnhancedMusicRecommendationBot()
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Enhanced Music Recommendation Bot...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
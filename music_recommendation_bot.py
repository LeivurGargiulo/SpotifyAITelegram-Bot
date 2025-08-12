#!/usr/bin/env python3
"""
Telegram Music Recommendation Bot
Uses Spotify Web API and OpenRouter AI to recommend music based on user mood/situation.
"""

import os
import logging
import asyncio
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

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

class SpotifyAPI:
    """Handles Spotify API interactions."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0
        
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
                    self.token_expiry = asyncio.get_event_loop().time() + token_data['expires_in'] - 60  # Buffer
                    logger.info("Successfully obtained Spotify access token")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get Spotify token: {response.status} - {error_text}")
                    raise Exception(f"Spotify authentication failed: {response.status}")
    
    async def get_recommendations(self, keywords: List[str], limit: int = 5) -> List[Track]:
        """Get music recommendations based on keywords."""
        try:
            access_token = await self._get_access_token()
            
            # Convert keywords to seed parameters for Spotify
            seed_genres, seed_artists, seed_tracks = self._process_keywords(keywords)
            
            params = {
                'limit': limit,
                'market': 'US'  # You can make this configurable
            }
            
            # Add seed parameters if available
            if seed_genres:
                params['seed_genres'] = ','.join(seed_genres[:5])  # Spotify allows max 5 seeds
            if seed_artists:
                params['seed_artists'] = ','.join(seed_artists[:5])
            if seed_tracks:
                params['seed_tracks'] = ','.join(seed_tracks[:5])
            
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
                                album=track['album']['name']
                            )
                            tracks.append(track_obj)
                        
                        logger.info(f"Successfully retrieved {len(tracks)} recommendations")
                        return tracks
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify API error: {response.status} - {error_text}")
                        raise Exception(f"Spotify API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting Spotify recommendations: {str(e)}")
            raise
    
    def _process_keywords(self, keywords: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Process keywords into Spotify seed parameters."""
        # This is a simplified implementation
        # In a production system, you might want to use Spotify's genre/artist/track search APIs
        # to convert natural language keywords into actual Spotify IDs
        
        seed_genres = []
        seed_artists = []
        seed_tracks = []
        
        # Map common keywords to Spotify genres
        genre_mapping = {
            'rock': 'rock',
            'pop': 'pop',
            'jazz': 'jazz',
            'classical': 'classical',
            'electronic': 'electronic',
            'hip hop': 'hip-hop',
            'country': 'country',
            'blues': 'blues',
            'reggae': 'reggae',
            'folk': 'folk',
            'r&b': 'r-n-b',
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
            'sleep': 'sleep'
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in genre_mapping:
                seed_genres.append(genre_mapping[keyword_lower])
        
        return seed_genres, seed_artists, seed_tracks

class OpenRouterAPI:
    """Handles OpenRouter AI interactions for natural language understanding."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def extract_music_keywords(self, user_message: str) -> List[str]:
        """Extract music-related keywords from user message using OpenRouter AI."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/your-repo/music-bot',  # Replace with your repo
                'X-Title': 'Music Recommendation Bot'
            }
            
            payload = {
                "model": "anthropic/claude-3-haiku",  # Using Claude for better understanding
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a music recommendation assistant. Extract music-related keywords from user messages.
                        
                        Focus on:
                        - Genres (rock, pop, jazz, classical, electronic, hip-hop, etc.)
                        - Moods (happy, sad, energetic, calm, romantic, etc.)
                        - Activities (workout, study, party, sleep, driving, etc.)
                        - Artists or bands (if mentioned)
                        - Time periods or eras (80s, 90s, etc.)
                        
                        Return ONLY a JSON array of relevant keywords (strings), nothing else.
                        If no clear music-related keywords are found, return an empty array [].
                        
                        Examples:
                        - "I'm feeling sad today" → ["sad"]
                        - "Need some rock music for my workout" → ["rock", "workout"]
                        - "I love jazz and classical" → ["jazz", "classical"]
                        - "Just want some background music" → [] (too vague)"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 100
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

class MusicRecommendationBot:
    """Main bot class that handles Telegram interactions and music recommendations."""
    
    def __init__(self):
        self.spotify_api = SpotifyAPI(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        self.openrouter_api = OpenRouterAPI(
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🎵 *Welcome to Music Recommendation Bot!* 🎵

I can recommend music based on your mood, situation, or preferences. Just tell me what you're looking for!

*Examples:*
• "I'm feeling sad today"
• "Need energetic music for my workout"
• "I love jazz and classical"
• "Want some rock music for driving"
• "Need calm music for studying"

*How it works:*
1. I analyze your message using AI
2. Extract music-related keywords
3. Find perfect recommendations on Spotify
4. Send you 5 great tracks to try!

Just send me a message describing what kind of music you want! 🎶
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages and provide music recommendations."""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received message from user {user_id}: {user_message}")
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Extract keywords using OpenRouter
            keywords = await self.openrouter_api.extract_music_keywords(user_message)
            
            if not keywords:
                await update.message.reply_text(
                    "I couldn't understand what kind of music you're looking for. "
                    "Could you please be more specific? For example:\n"
                    "• \"I'm feeling happy and want some upbeat music\"\n"
                    "• \"Need rock music for my workout\"\n"
                    "• \"I love jazz and classical music\""
                )
                return
            
            # Get music recommendations from Spotify
            tracks = await self.spotify_api.get_recommendations(keywords)
            
            if not tracks:
                await update.message.reply_text(
                    "Sorry, I couldn't find any music recommendations based on your request. "
                    "Try describing your mood or the type of music you're looking for!"
                )
                return
            
            # Format and send recommendations
            response = self._format_recommendations(tracks, keywords)
            await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
            
            logger.info(f"Successfully sent recommendations to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            await update.message.reply_text(
                "Sorry, I encountered an error while processing your request. "
                "Please try again in a moment!"
            )
    
    def _format_recommendations(self, tracks: List[Track], keywords: List[str]) -> str:
        """Format track recommendations into a readable message."""
        keywords_text = ', '.join(keywords)
        
        response = f"🎵 *Music Recommendations* 🎵\n\n"
        response += f"Based on: *{keywords_text}*\n\n"
        
        for i, track in enumerate(tracks, 1):
            response += f"{i}. **{track.title}** - {track.artist}\n"
            response += f"   Album: {track.album}\n"
            response += f"   [Listen on Spotify]({track.spotify_url})\n\n"
        
        response += "Enjoy your music! 🎶"
        return response
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. Please try again later!"
            )

async def main():
    """Main function to run the bot."""
    # Check required environment variables
    required_env_vars = ['TELEGRAM_TOKEN', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set all required environment variables before running the bot.")
        return
    
    # Initialize bot
    bot = MusicRecommendationBot()
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Music Recommendation Bot...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
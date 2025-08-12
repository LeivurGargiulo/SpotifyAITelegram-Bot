#!/usr/bin/env python3
"""
Test suite for Discord Music Bot
Tests all major components and functionality.
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
import logging

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import bot components
from discord_music_bot import (
    Track, Cache, RateLimiter, EnhancedSpotifyAPI, 
    EnhancedOpenRouterAPI, EnhancedDiscordMusicBot
)

# Configure logging for tests
logging.basicConfig(level=logging.ERROR)

class TestTrack(unittest.TestCase):
    """Test Track dataclass."""
    
    def test_track_creation(self):
        """Test creating a Track object."""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            spotify_url="https://open.spotify.com/track/test",
            album="Test Album",
            popularity=75,
            duration_ms=180000,
            preview_url="https://example.com/preview.mp3"
        )
        
        self.assertEqual(track.title, "Test Song")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.spotify_url, "https://open.spotify.com/track/test")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.popularity, 75)
        self.assertEqual(track.duration_ms, 180000)
        self.assertEqual(track.preview_url, "https://example.com/preview.mp3")

class TestCache(unittest.TestCase):
    """Test Cache class."""
    
    def setUp(self):
        """Set up test cache."""
        self.cache = Cache(ttl=60)  # 1 minute TTL
    
    def test_cache_set_get(self):
        """Test setting and getting values from cache."""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        self.assertEqual(result, "test_value")
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        self.cache.set("test_key", "test_value")
        
        # Simulate time passing by manually setting an old timestamp
        self.cache.cache["test_key"] = ("test_value", 0)  # Very old timestamp
        
        result = self.cache.get("test_key")
        self.assertIsNone(result)
    
    def test_cache_clear(self):
        """Test clearing the cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.assertEqual(len(self.cache.cache), 2)
        
        self.cache.clear()
        self.assertEqual(len(self.cache.cache), 0)

class TestRateLimiter(unittest.TestCase):
    """Test RateLimiter class."""
    
    def setUp(self):
        """Set up test rate limiter."""
        self.rate_limiter = RateLimiter(max_requests=3, window=60)
    
    def test_rate_limiter_allowed(self):
        """Test rate limiter allows requests within limits."""
        user_id = 12345
        
        # First 3 requests should be allowed
        self.assertTrue(self.rate_limiter.is_allowed(user_id))
        self.assertTrue(self.rate_limiter.is_allowed(user_id))
        self.assertTrue(self.rate_limiter.is_allowed(user_id))
        
        # 4th request should be denied
        self.assertFalse(self.rate_limiter.is_allowed(user_id))
    
    def test_rate_limiter_remaining(self):
        """Test getting remaining requests."""
        user_id = 12345
        
        # Initially should have 3 remaining
        self.assertEqual(self.rate_limiter.get_remaining(user_id), 3)
        
        # After one request, should have 2 remaining
        self.rate_limiter.is_allowed(user_id)
        self.assertEqual(self.rate_limiter.get_remaining(user_id), 2)

class TestEnhancedSpotifyAPI(unittest.TestCase):
    """Test EnhancedSpotifyAPI class."""
    
    def setUp(self):
        """Set up test Spotify API."""
        self.spotify_api = EnhancedSpotifyAPI(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
    
    def test_audio_features_from_keywords(self):
        """Test audio features extraction from keywords."""
        # Test energetic keywords
        energetic_keywords = ["energetic", "upbeat", "workout"]
        features = self.spotify_api._get_audio_features_from_keywords(energetic_keywords)
        
        self.assertIn('target_energy', features)
        self.assertEqual(features['target_energy'], 0.8)
        self.assertIn('target_tempo', features)
        self.assertEqual(features['target_tempo'], 140)
        
        # Test calm keywords
        calm_keywords = ["calm", "relaxing", "study"]
        features = self.spotify_api._get_audio_features_from_keywords(calm_keywords)
        
        self.assertIn('target_energy', features)
        self.assertEqual(features['target_energy'], 0.3)
        self.assertIn('target_tempo', features)
        self.assertEqual(features['target_tempo'], 80)
    
    def test_extract_seeds(self):
        """Test seed extraction from keywords."""
        keywords = ["rock", "energetic", "80s"]
        seed_genres, seed_artists, seed_tracks = asyncio.run(
            self.spotify_api._extract_seeds(keywords, "test_token")
        )
        
        # Should extract rock genre
        self.assertIn("rock", seed_genres)

class TestEnhancedOpenRouterAPI(unittest.TestCase):
    """Test EnhancedOpenRouterAPI class."""
    
    def setUp(self):
        """Set up test OpenRouter API."""
        self.openrouter_api = EnhancedOpenRouterAPI(api_key="test_api_key")
    
    @patch('aiohttp.ClientSession.post')
    async def test_extract_music_keywords_success(self, mock_post):
        """Test successful keyword extraction."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'happy, energetic, pop, upbeat'
                }
            }]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        keywords = await self.openrouter_api.extract_music_keywords("I'm feeling happy and energetic")
        
        self.assertEqual(len(keywords), 4)
        self.assertIn("happy", keywords)
        self.assertIn("energetic", keywords)
        self.assertIn("pop", keywords)
        self.assertIn("upbeat", keywords)
    
    @patch('aiohttp.ClientSession.post')
    async def test_extract_music_keywords_failure(self, mock_post):
        """Test keyword extraction failure."""
        # Mock failed response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with self.assertRaises(Exception):
            await self.openrouter_api.extract_music_keywords("test message")

class TestEnhancedDiscordMusicBot(unittest.TestCase):
    """Test EnhancedDiscordMusicBot class."""
    
    def setUp(self):
        """Set up test bot."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'DISCORD_TOKEN': 'test_token',
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'OPENROUTER_API_KEY': 'test_api_key'
        }):
            self.bot = EnhancedDiscordMusicBot()
    
    def test_bot_initialization(self):
        """Test bot initialization."""
        self.assertIsNotNone(self.bot.spotify_api)
        self.assertIsNotNone(self.bot.openrouter_api)
        self.assertIsNotNone(self.bot.rate_limiter)
        self.assertEqual(self.bot.command_prefix, '!')
    
    def test_user_stats(self):
        """Test user statistics tracking."""
        user_id = 12345
        
        # Initially should be 0
        self.assertEqual(self.bot.user_stats[user_id], 0)
        
        # Increment stats
        self.bot.user_stats[user_id] += 1
        self.assertEqual(self.bot.user_stats[user_id], 1)
        
        # Increment again
        self.bot.user_stats[user_id] += 1
        self.assertEqual(self.bot.user_stats[user_id], 2)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'DISCORD_TOKEN': 'test_token',
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'OPENROUTER_API_KEY': 'test_api_key'
        }):
            self.bot = EnhancedDiscordMusicBot()
    
    def test_complete_workflow(self):
        """Test complete workflow from message to recommendation."""
        # This would test the complete flow from user message
        # to keyword extraction to Spotify recommendations
        # In a real test, this would involve mocking all external APIs
        pass

def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTrack,
        TestCache,
        TestRateLimiter,
        TestEnhancedSpotifyAPI,
        TestEnhancedOpenRouterAPI,
        TestEnhancedDiscordMusicBot,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*50}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running Discord Music Bot Tests...")
    print("="*50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
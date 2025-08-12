#!/usr/bin/env python3
"""
Test script to verify the setup of the Telegram Music Recommendation Bot.
This script checks environment variables and tests API connections.
"""

import os
import asyncio
import aiohttp
import json
from typing import List

async def test_spotify_connection(client_id: str, client_secret: str) -> bool:
    """Test Spotify API connection."""
    try:
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ Spotify API connection successful")
                    print(f"   Token expires in: {token_data['expires_in']} seconds")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Spotify API connection failed: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Spotify API connection error: {str(e)}")
        return False

async def test_openrouter_connection(api_key: str) -> bool:
    """Test OpenRouter API connection."""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/test/music-bot',
            'X-Title': 'Test Music Bot'
        }
        
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {
                    "role": "user",
                    "content": "Extract music keywords from: I love rock music"
                }
            ],
            "max_tokens": 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ OpenRouter API connection successful")
                    print(f"   Model used: {data.get('model', 'unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ OpenRouter API connection failed: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ OpenRouter API connection error: {str(e)}")
        return False

def test_telegram_token(token: str) -> bool:
    """Test Telegram bot token format."""
    try:
        # Basic format validation
        if not token or ':' not in token:
            print("❌ Invalid Telegram token format")
            return False
        
        parts = token.split(':')
        if len(parts) != 2:
            print("❌ Invalid Telegram token format")
            return False
        
        bot_id, bot_hash = parts
        if not bot_id.isdigit() or len(bot_hash) < 10:
            print("❌ Invalid Telegram token format")
            return False
        
        print("✅ Telegram token format looks valid")
        return True
    except Exception as e:
        print(f"❌ Telegram token validation error: {str(e)}")
        return False

async def test_music_recommendation(client_id: str, client_secret: str) -> bool:
    """Test a simple music recommendation."""
    try:
        # Get access token
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data) as response:
                if response.status != 200:
                    return False
                
                token_data = await response.json()
                access_token = token_data['access_token']
                
                # Test recommendations API
                headers = {'Authorization': f'Bearer {access_token}'}
                params = {
                    'seed_genres': 'rock',
                    'limit': 1,
                    'market': 'US'
                }
                
                async with session.get(
                    "https://api.spotify.com/v1/recommendations",
                    params=params,
                    headers=headers
                ) as rec_response:
                    if rec_response.status == 200:
                        data = await rec_response.json()
                        tracks = data.get('tracks', [])
                        if tracks:
                            track = tracks[0]
                            print("✅ Music recommendation test successful")
                            print(f"   Sample track: {track['name']} by {track['artists'][0]['name']}")
                            return True
                        else:
                            print("❌ No tracks returned in recommendation test")
                            return False
                    else:
                        print(f"❌ Recommendation API test failed: {rec_response.status}")
                        return False
    except Exception as e:
        print(f"❌ Music recommendation test error: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🎵 Telegram Music Recommendation Bot - Setup Test")
    print("=" * 50)
    
    # Check environment variables
    required_vars = {
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
        'SPOTIFY_CLIENT_ID': os.getenv('SPOTIFY_CLIENT_ID'),
        'SPOTIFY_CLIENT_SECRET': os.getenv('SPOTIFY_CLIENT_SECRET'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY')
    }
    
    print("\n📋 Environment Variables Check:")
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"✅ {var_name}: {'*' * (len(var_value) - 8) + var_value[-8:] if len(var_value) > 8 else '*' * len(var_value)}")
        else:
            print(f"❌ {var_name}: NOT SET")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set all required environment variables before running the bot.")
        return
    
    print("\n🔗 API Connection Tests:")
    
    # Test Telegram token
    telegram_ok = test_telegram_token(required_vars['TELEGRAM_TOKEN'])
    
    # Test Spotify API
    spotify_ok = await test_spotify_connection(
        required_vars['SPOTIFY_CLIENT_ID'],
        required_vars['SPOTIFY_CLIENT_SECRET']
    )
    
    # Test OpenRouter API
    openrouter_ok = await test_openrouter_connection(required_vars['OPENROUTER_API_KEY'])
    
    # Test music recommendation
    recommendation_ok = False
    if spotify_ok:
        recommendation_ok = await test_music_recommendation(
            required_vars['SPOTIFY_CLIENT_ID'],
            required_vars['SPOTIFY_CLIENT_SECRET']
        )
    
    print("\n📊 Test Summary:")
    print(f"   Telegram Token: {'✅' if telegram_ok else '❌'}")
    print(f"   Spotify API: {'✅' if spotify_ok else '❌'}")
    print(f"   OpenRouter API: {'✅' if openrouter_ok else '❌'}")
    print(f"   Music Recommendations: {'✅' if recommendation_ok else '❌'}")
    
    all_tests_passed = telegram_ok and spotify_ok and openrouter_ok and recommendation_ok
    
    if all_tests_passed:
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("Run 'python music_recommendation_bot.py' to start the bot.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above and fix them before running the bot.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
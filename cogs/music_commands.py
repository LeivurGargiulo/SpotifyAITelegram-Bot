"""
Optimized Music Commands Cog
Handles all music recommendation functionality with enhanced performance and error handling.
"""

import discord
from discord.ext import commands
import logging
import time
import asyncio
from typing import List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class MusicCommands(commands.Cog):
    """Music recommendation commands and message handling with performance optimization."""
    
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = defaultdict(float)
        self.processing_users = set()
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Handle !start command with enhanced welcome message."""
        welcome_embed = discord.Embed(
            title="🎵 Welcome to Enhanced Music Recommendation Bot! 🎵",
            description="I'm your AI-powered music companion that understands your mood and preferences to recommend the perfect tracks!",
            color=discord.Color.green()
        )
        
        welcome_embed.add_field(
            name="How to use me:",
            value="• Tell me your mood: \"I'm feeling sad today\"\n"
                  "• Describe activities: \"Need energetic music for my workout\"\n"
                  "• Mention genres: \"I love jazz and classical\"\n"
                  "• Combine preferences: \"Want romantic rock songs for driving\"",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Examples:",
            value="• \"I'm feeling happy and energetic\"\n"
                  "• \"Need calm music for studying\"\n"
                  "• \"Looking for 80s rock classics\"\n"
                  "• \"Want some jazz for dinner\"\n"
                  "• \"Need party music for tonight\"",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Features:",
            value="✨ AI-powered mood analysis\n"
                  "🎯 Personalized recommendations\n"
                  "⚡ Fast response with caching\n"
                  "🔄 Rate limited (15 requests/minute)\n"
                  "📊 Track popularity and previews",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Commands:",
            value="`!start` - Show this message\n"
                  "`!stats` - Show your usage statistics\n"
                  "`!help` - Get help and examples\n"
                  "`!debug` - Bot status and error logs",
            inline=False
        )
        
        welcome_embed.set_footer(text="Just send me a message describing what you're looking for! 🎶")
        
        await ctx.send(embed=welcome_embed)
        logger.info(f"User {ctx.author.id} started the bot")
        
        # Update metrics
        self.bot.performance_metrics['total_requests'] += 1
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Handle !help command."""
        help_embed = discord.Embed(
            title="🎵 Music Recommendation Bot Help 🎵",
            color=discord.Color.blue()
        )
        
        help_embed.add_field(
            name="How it works:",
            value="1. I analyze your message using AI\n"
                  "2. Extract music-related keywords\n"
                  "3. Find perfect recommendations on Spotify\n"
                  "4. Send you 5 curated tracks",
            inline=False
        )
        
        help_embed.add_field(
            name="What I understand:",
            value="**Moods**: happy, sad, energetic, calm, romantic, etc.\n"
                  "**Genres**: rock, pop, jazz, classical, electronic, hip-hop, etc.\n"
                  "**Activities**: workout, study, party, sleep, driving, etc.\n"
                  "**Time periods**: 80s, 90s, 2000s, etc.\n"
                  "**Seasons**: summer, winter, christmas, etc.",
            inline=False
        )
        
        help_embed.add_field(
            name="Tips for better recommendations:",
            value="• Be specific: \"energetic rock for workout\" vs \"music\"\n"
                  "• Combine preferences: \"romantic jazz for dinner\"\n"
                  "• Mention activities: \"calm music for studying\"\n"
                  "• Include time periods: \"80s pop classics\"",
            inline=False
        )
        
        help_embed.add_field(
            name="Rate Limits:",
            value="• 15 requests per minute per user\n"
                  "• Use `!stats` to check your usage",
            inline=False
        )
        
        help_embed.set_footer(text="Need more help? Just ask! 🎶")
        
        await ctx.send(embed=help_embed)
    
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        """Handle !stats command to show user statistics."""
        user_id = ctx.author.id
        requests_made = self.bot.user_stats[user_id]
        user_stats = await self.bot.rate_limiter.get_user_stats(user_id)
        
        stats_embed = discord.Embed(
            title="📊 Your Usage Statistics",
            color=discord.Color.gold()
        )
        
        stats_embed.add_field(
            name="Total Requests Made",
            value=str(requests_made),
            inline=True
        )
        
        stats_embed.add_field(
            name="Requests This Minute",
            value=f"{user_stats['requests_in_window']}/15",
            inline=True
        )
        
        stats_embed.add_field(
            name="Remaining Requests",
            value=f"{user_stats['remaining_requests']}/15",
            inline=True
        )
        
        stats_embed.add_field(
            name="Rate Limit Status",
            value="🟢 Active" if not user_stats['is_rate_limited'] else "🔴 Limited",
            inline=True
        )
        
        stats_embed.add_field(
            name="Reset Time",
            value=f"<t:{int(user_stats['window_reset_time'])}:R>",
            inline=True
        )
        
        # Add performance metrics
        avg_response_time = self.bot.performance_metrics.get('avg_response_time', 0)
        stats_embed.add_field(
            name="Average Response Time",
            value=f"{avg_response_time:.2f}s",
            inline=True
        )
        
        stats_embed.set_footer(text="Keep enjoying your music! 🎶")
        
        # Update metrics
        self.bot.performance_metrics['total_requests'] += 1
        
        await ctx.send(embed=stats_embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages with optimized rate limiting and processing."""
        # Ignore bot messages and commands
        if message.author.bot or message.content.startswith('!'):
            return
        
        user_message = message.content
        user_id = message.author.id
        
        # Prevent duplicate processing
        if user_id in self.processing_users:
            return
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.user_cooldowns[user_id] < 2:  # 2 second cooldown
            return
        
        logger.info(f"Received message from user {user_id}: {user_message}")
        
        # Check rate limiting with async method
        if not await self.bot.rate_limiter.is_allowed(user_id):
            user_stats = await self.bot.rate_limiter.get_user_stats(user_id)
            remaining_time = int(user_stats['window_reset_time'] - current_time)
            
            rate_limit_embed = discord.Embed(
                title="⏰ Rate Limit Exceeded!",
                description=f"Please wait {remaining_time} seconds before making another request.\n\n"
                           f"Limit: 15 requests per minute\n"
                           f"Your requests: {user_stats['requests_in_window']}/15",
                color=discord.Color.red()
            )
            await message.reply(embed=rate_limit_embed)
            return
        
        # Mark user as processing
        self.processing_users.add(user_id)
        self.user_cooldowns[user_id] = current_time
        
        # Send typing indicator
        async with message.channel.typing():
            start_time = time.time()
            try:
                # Update metrics
                self.bot.performance_metrics['total_requests'] += 1
                
                # Extract keywords using OpenRouter
                keywords = await self.bot.openrouter_api.extract_music_keywords(user_message)
                
                if not keywords:
                    self.bot.performance_metrics['cache_misses'] += 1
                    no_keywords_embed = discord.Embed(
                        title="🤔 I couldn't understand what kind of music you're looking for.",
                        description="**Try being more specific:**\n"
                                  "• \"I'm feeling happy and want upbeat music\"\n"
                                  "• \"Need rock music for my workout\"\n"
                                  "• \"I love jazz and classical music\"\n"
                                  "• \"Want romantic songs for dinner\"\n\n"
                                  "Use `!help` for more examples!",
                        color=discord.Color.orange()
                    )
                    await message.reply(embed=no_keywords_embed)
                    return
                
                # Get music recommendations from Spotify
                tracks = await self.bot.spotify_api.get_recommendations(keywords)
                
                if not tracks:
                    self.bot.performance_metrics['cache_misses'] += 1
                    no_tracks_embed = discord.Embed(
                        title="😔 Sorry, I couldn't find any music recommendations based on your request.",
                        description="**Try these suggestions:**\n"
                                  "• Be more specific about genres or moods\n"
                                  "• Mention activities or situations\n"
                                  "• Use `!help` to see examples",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=no_tracks_embed)
                    return
                
                # Update user statistics and metrics
                self.bot.user_stats[user_id] += 1
                self.bot.performance_metrics['cache_hits'] += 1
                
                # Calculate response time
                response_time = time.time() - start_time
                self.bot.request_times.append(response_time)
                
                # Update average response time
                if self.bot.request_times:
                    self.bot.performance_metrics['avg_response_time'] = sum(self.bot.request_times) / len(self.bot.request_times)
                
                # Format and send recommendations
                response_embed = self._format_enhanced_recommendations(tracks, keywords, response_time)
                await message.reply(embed=response_embed)
                
                logger.info(f"Successfully sent recommendations to user {user_id} in {response_time:.2f}s")
                
            except Exception as e:
                self.bot.performance_metrics['api_errors'] += 1
                logger.error(f"Error processing message for user {user_id}: {str(e)}")
                error_embed = discord.Embed(
                    title="😞 Sorry, I encountered an error while processing your request.",
                    description="This might be due to:\n"
                              "• Temporary API issues\n"
                              "• Network connectivity problems\n\n"
                              "Please try again in a moment!",
                    color=discord.Color.red()
                )
                await message.reply(embed=error_embed)
            finally:
                # Remove user from processing set
                self.processing_users.discard(user_id)
    
    def _format_enhanced_recommendations(self, tracks: List, keywords: List[str], response_time: float = 0.0) -> discord.Embed:
        """Format track recommendations with enhanced information and performance metrics."""
        keywords_text = ', '.join(keywords)
        
        embed = discord.Embed(
            title="🎵 Music Recommendations 🎵",
            description=f"**Based on:** {keywords_text}",
            color=discord.Color.green()
        )
        
        for i, track in enumerate(tracks, 1):
            # Add popularity indicator
            popularity_emoji = "🔥" if track.popularity > 70 else "⭐" if track.popularity > 40 else "💫"
            
            # Format duration if available
            duration_text = ""
            if track.duration_ms:
                duration_min = track.duration_ms // 60000
                duration_sec = (track.duration_ms % 60000) // 1000
                duration_text = f"⏱️ Duration: {duration_min}:{duration_sec:02d}\n"
            
            field_value = f"📀 Album: {track.album}\n"
            field_value += f"{popularity_emoji} Popularity: {track.popularity}%\n"
            field_value += duration_text
            field_value += f"🎧 [Listen on Spotify]({track.spotify_url})"
            
            embed.add_field(
                name=f"{i}. {track.title} - {track.artist}",
                value=field_value,
                inline=False
            )
        
        footer_text = "🎶 Enjoy your music! 💡 Tip: Use !stats to check your usage"
        if response_time > 0:
            footer_text += f" | ⚡ Response time: {response_time:.2f}s"
        embed.set_footer(text=footer_text)
        
        return embed

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(MusicCommands(bot))
"""
Music Commands Cog
Handles all music recommendation functionality converted from Telegram bot.
"""

import discord
from discord.ext import commands
import logging
import time
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

class MusicCommands(commands.Cog):
    """Music recommendation commands and message handling."""
    
    def __init__(self, bot):
        self.bot = bot
    
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
        remaining = self.bot.rate_limiter.get_remaining(user_id)
        
        stats_embed = discord.Embed(
            title="📊 Your Usage Statistics",
            color=discord.Color.gold()
        )
        
        stats_embed.add_field(
            name="Requests made",
            value=str(requests_made),
            inline=True
        )
        
        stats_embed.add_field(
            name="Remaining this minute",
            value=f"{remaining}/15",
            inline=True
        )
        
        stats_embed.add_field(
            name="Rate limit",
            value="15 requests per minute",
            inline=True
        )
        
        stats_embed.add_field(
            name="Reset time",
            value="Every minute",
            inline=True
        )
        
        stats_embed.set_footer(text="Keep enjoying your music! 🎶")
        
        await ctx.send(embed=stats_embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages with rate limiting and enhanced processing."""
        # Ignore bot messages and commands
        if message.author.bot or message.content.startswith('!'):
            return
        
        user_message = message.content
        user_id = message.author.id
        
        logger.info(f"Received message from user {user_id}: {user_message}")
        
        # Check rate limiting
        if not self.bot.rate_limiter.is_allowed(user_id):
            remaining_time = 60 - int(time.time() % 60)
            rate_limit_embed = discord.Embed(
                title="⏰ Rate Limit Exceeded!",
                description=f"Please wait {remaining_time} seconds before making another request.\n\n"
                           f"Limit: 15 requests per minute",
                color=discord.Color.red()
            )
            await message.reply(embed=rate_limit_embed)
            return
        
        # Send typing indicator
        async with message.channel.typing():
            try:
                # Extract keywords using OpenRouter
                keywords = await self.bot.openrouter_api.extract_music_keywords(user_message)
                
                if not keywords:
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
                
                # Update user statistics
                self.bot.user_stats[user_id] += 1
                
                # Format and send recommendations
                response_embed = self._format_enhanced_recommendations(tracks, keywords)
                await message.reply(embed=response_embed)
                
                logger.info(f"Successfully sent recommendations to user {user_id}")
                
            except Exception as e:
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
    
    def _format_enhanced_recommendations(self, tracks: List, keywords: List[str]) -> discord.Embed:
        """Format track recommendations with enhanced information."""
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
        
        embed.set_footer(text="🎶 Enjoy your music! 💡 Tip: Use !stats to check your usage")
        
        return embed

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(MusicCommands(bot))
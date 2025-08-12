"""
Utility Commands Cog
Handles debug, status, and other utility commands.
"""

import discord
from discord.ext import commands
import logging
import psutil
import platform
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class UtilityCommands(commands.Cog):
    """Utility commands for bot management and debugging."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='debug')
    async def debug_command(self, ctx):
        """Handle !debug command that returns bot uptime, version, and recent error logs."""
        # Calculate uptime
        uptime = datetime.now() - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get bot stats
        total_users = sum(len(guild.members) for guild in self.bot.guilds)
        total_guilds = len(self.bot.guilds)
        
        # Get recent error logs (last 10)
        recent_errors = self.bot.error_logs[-10:] if self.bot.error_logs else []
        
        debug_embed = discord.Embed(
            title="🔧 Bot Debug Information",
            color=discord.Color.blue()
        )
        
        debug_embed.add_field(
            name="Bot Status",
            value=f"🟢 Online\n"
                  f"⏱️ Uptime: {uptime_str}\n"
                  f"🏓 Latency: {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        debug_embed.add_field(
            name="System Info",
            value=f"🖥️ CPU: {cpu_percent}%\n"
                  f"💾 Memory: {memory_percent}%\n"
                  f"🐍 Python: {platform.python_version()}",
            inline=True
        )
        
        debug_embed.add_field(
            name="Bot Stats",
            value=f"👥 Users: {total_users:,}\n"
                  f"🏠 Guilds: {total_guilds}\n"
                  f"📊 Commands: {len(self.bot.commands)}",
            inline=True
        )
        
        debug_embed.add_field(
            name="API Status",
            value=f"🎵 Spotify: {'🟢' if self.bot.spotify_api.access_token else '🔴'}\n"
                  f"🤖 OpenRouter: {'🟢' if self.bot.openrouter_api.api_key else '🔴'}\n"
                  f"💾 Cache: {len(self.bot.spotify_api.cache.cache)} items",
            inline=True
        )
        
        # Add recent errors if any
        if recent_errors:
            error_text = "\n".join([f"• {error[:100]}..." for error in recent_errors[-5:]])
            debug_embed.add_field(
                name="Recent Errors (Last 5)",
                value=error_text if len(error_text) < 1024 else error_text[:1021] + "...",
                inline=False
            )
        else:
            debug_embed.add_field(
                name="Recent Errors",
                value="✅ No recent errors",
                inline=False
            )
        
        debug_embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        debug_embed.timestamp = datetime.now()
        
        await ctx.send(embed=debug_embed)
        logger.info(f"Debug command used by {ctx.author.id}")
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Handle !status command for detailed bot status."""
        # Calculate uptime
        uptime = datetime.now() - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]
        
        # Get detailed system info
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get bot performance stats
        total_commands = sum(self.bot.user_stats.values())
        active_users = len([uid for uid, count in self.bot.user_stats.items() if count > 0])
        
        status_embed = discord.Embed(
            title="📊 Detailed Bot Status",
            color=discord.Color.green()
        )
        
        status_embed.add_field(
            name="Performance",
            value=f"⚡ Total Commands: {total_commands:,}\n"
                  f"👤 Active Users: {active_users}\n"
                  f"🔄 Rate Limit Hits: {sum(1 for user_requests in self.bot.rate_limiter.requests.values() if len(user_requests) >= 15)}",
            inline=True
        )
        
        status_embed.add_field(
            name="System Resources",
            value=f"🖥️ CPU Cores: {cpu_count}\n"
                  f"💾 RAM Used: {memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB\n"
                  f"💿 Disk Free: {disk.free // (1024**3):.1f}GB",
            inline=True
        )
        
        status_embed.add_field(
            name="Cache Status",
            value=f"🎵 Spotify Cache: {len(self.bot.spotify_api.cache.cache)} items\n"
                  f"🤖 OpenRouter Cache: {len(self.bot.openrouter_api.cache.cache)} items\n"
                  f"⏰ Last Cleanup: {self.bot.cleanup_cache.next_iteration.strftime('%H:%M:%S') if self.bot.cleanup_cache.next_iteration else 'N/A'}",
            inline=True
        )
        
        status_embed.add_field(
            name="Uptime",
            value=f"🕐 Started: {self.bot.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                  f"⏱️ Running: {uptime_str}\n"
                  f"🔄 Next Cleanup: {self.bot.cleanup_cache.next_iteration.strftime('%H:%M:%S') if self.bot.cleanup_cache.next_iteration else 'N/A'}",
            inline=True
        )
        
        status_embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        status_embed.timestamp = datetime.now()
        
        await ctx.send(embed=status_embed)
        logger.info(f"Status command used by {ctx.author.id}")
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Handle !ping command for latency check."""
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Determine latency status
        if latency < 100:
            status = "🟢 Excellent"
            color = discord.Color.green()
        elif latency < 200:
            status = "🟡 Good"
            color = discord.Color.gold()
        elif latency < 500:
            status = "🟠 Fair"
            color = discord.Color.orange()
        else:
            status = "🔴 Poor"
            color = discord.Color.red()
        
        ping_embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms\n**Status:** {status}",
            color=color
        )
        
        ping_embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=ping_embed)
        logger.info(f"Ping command used by {ctx.author.id} - Latency: {latency}ms")
    
    @commands.command(name='info')
    async def info_command(self, ctx):
        """Handle !info command for bot information."""
        info_embed = discord.Embed(
            title="ℹ️ Bot Information",
            description="Enhanced Discord Music Recommendation Bot\n"
                       "Converted from Telegram bot with all functionality intact.",
            color=discord.Color.blue()
        )
        
        info_embed.add_field(
            name="Version",
            value="2.0.0 (Discord Edition)",
            inline=True
        )
        
        info_embed.add_field(
            name="Library",
            value=f"discord.py {discord.__version__}",
            inline=True
        )
        
        info_embed.add_field(
            name="Python",
            value=platform.python_version(),
            inline=True
        )
        
        info_embed.add_field(
            name="Features",
            value="🎵 AI-powered music recommendations\n"
                  "⚡ Intelligent caching system\n"
                  "🔄 Rate limiting protection\n"
                  "📊 User statistics tracking\n"
                  "🔧 Comprehensive error handling",
            inline=False
        )
        
        info_embed.add_field(
            name="APIs Used",
            value="🎵 Spotify Web API\n"
                  "🤖 OpenRouter AI API\n"
                  "📱 Discord Gateway API",
            inline=False
        )
        
        info_embed.add_field(
            name="Commands",
            value="`!start` - Welcome message\n"
                  "`!help` - Help and examples\n"
                  "`!stats` - Your usage statistics\n"
                  "`!debug` - Bot debug information\n"
                  "`!status` - Detailed status\n"
                  "`!ping` - Latency check\n"
                  "`!info` - This information",
            inline=False
        )
        
        info_embed.set_footer(text="Just send me a message describing what music you want! 🎶")
        
        await ctx.send(embed=info_embed)
        logger.info(f"Info command used by {ctx.author.id}")
    
    @commands.command(name='cleanup')
    @commands.has_permissions(administrator=True)
    async def cleanup_command(self, ctx):
        """Handle !cleanup command for manual cache cleanup (admin only)."""
        try:
            # Clear all caches
            self.bot.spotify_api.cache.clear()
            self.bot.openrouter_api.cache.clear()
            
            cleanup_embed = discord.Embed(
                title="🧹 Cache Cleanup Complete",
                description="All caches have been cleared successfully.",
                color=discord.Color.green()
            )
            
            cleanup_embed.add_field(
                name="Cleared Caches",
                value="🎵 Spotify API cache\n🤖 OpenRouter API cache",
                inline=False
            )
            
            await ctx.send(embed=cleanup_embed)
            logger.info(f"Manual cache cleanup performed by admin {ctx.author.id}")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Cleanup Failed",
                description=f"An error occurred during cleanup: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
            logger.error(f"Cache cleanup failed: {str(e)}")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(UtilityCommands(bot))
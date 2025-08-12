"""
Performance Monitor Cog
Tracks bot performance, memory usage, and provides detailed metrics.
"""

import discord
from discord.ext import commands, tasks
import logging
import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor(commands.Cog):
    """Performance monitoring and metrics collection."""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        self.performance_history = deque(maxlen=1000)  # Keep last 1000 measurements
        self.command_times = {}
        self.error_counts = defaultdict(int)
        self.api_call_times = deque(maxlen=100)
        
        # Start monitoring tasks
        self.monitor_performance.start()
        self.cleanup_old_data.start()
    
    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.monitor_performance.cancel()
        self.cleanup_old_data.cancel()
    
    @tasks.loop(minutes=1)
    async def monitor_performance(self):
        """Monitor system performance and bot metrics."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get bot metrics
            bot_metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024),
                'guild_count': len(self.bot.guilds),
                'user_count': len(self.bot.users),
                'latency_ms': self.bot.latency * 1000,
                'total_requests': self.bot.performance_metrics['total_requests'],
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'error_rate': self._calculate_error_rate()
            }
            
            self.performance_history.append(bot_metrics)
            
            # Log if performance is poor
            if cpu_percent > 80 or memory.percent > 80:
                logger.warning(f"High resource usage - CPU: {cpu_percent}%, Memory: {memory.percent}%")
                
        except Exception as e:
            logger.error(f"Error monitoring performance: {e}")
    
    @tasks.loop(hours=1)
    async def cleanup_old_data(self):
        """Clean up old performance data."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.performance_history = deque(
                [entry for entry in self.performance_history if entry['timestamp'] > cutoff_time],
                maxlen=1000
            )
            logger.info("Cleaned up old performance data")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.bot.performance_metrics['cache_hits'] + self.bot.performance_metrics['cache_misses']
        return (self.bot.performance_metrics['cache_hits'] / total * 100) if total > 0 else 0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate."""
        total_requests = self.bot.performance_metrics['total_requests']
        total_errors = self.bot.performance_metrics['api_errors']
        return (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    @commands.command(name='performance')
    @commands.has_permissions(administrator=True)
    async def performance_command(self, ctx):
        """Show detailed performance metrics."""
        try:
            # Get current metrics
            current = self.performance_history[-1] if self.performance_history else {}
            
            embed = discord.Embed(
                title="🤖 Bot Performance Metrics",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # System metrics
            embed.add_field(
                name="🖥️ System Resources",
                value=f"**CPU:** {current.get('cpu_percent', 0):.1f}%\n"
                      f"**Memory:** {current.get('memory_percent', 0):.1f}% "
                      f"({current.get('memory_used_mb', 0):.0f} MB)\n"
                      f"**Disk:** {current.get('disk_percent', 0):.1f}% "
                      f"({current.get('disk_free_gb', 0):.1f} GB free)",
                inline=False
            )
            
            # Bot metrics
            embed.add_field(
                name="🤖 Bot Statistics",
                value=f"**Guilds:** {current.get('guild_count', 0)}\n"
                      f"**Users:** {current.get('user_count', 0)}\n"
                      f"**Latency:** {current.get('latency_ms', 0):.1f}ms\n"
                      f"**Uptime:** {self._format_uptime()}",
                inline=True
            )
            
            # Performance metrics
            embed.add_field(
                name="📊 Performance",
                value=f"**Total Requests:** {current.get('total_requests', 0)}\n"
                      f"**Cache Hit Rate:** {current.get('cache_hit_rate', 0):.1f}%\n"
                      f"**Error Rate:** {current.get('error_rate', 0):.1f}%\n"
                      f"**API Errors:** {self.bot.performance_metrics['api_errors']}",
                inline=True
            )
            
            # Performance status
            status = self._get_performance_status(current)
            embed.add_field(
                name="📈 Status",
                value=status,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in performance command: {e}")
            await ctx.send("❌ Error retrieving performance metrics.")
    
    def _format_uptime(self) -> str:
        """Format bot uptime."""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def _get_performance_status(self, metrics: Dict[str, Any]) -> str:
        """Get performance status based on metrics."""
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)
        error_rate = metrics.get('error_rate', 0)
        
        if cpu > 80 or memory > 80 or error_rate > 10:
            return "🔴 **Poor** - High resource usage or error rate"
        elif cpu > 60 or memory > 60 or error_rate > 5:
            return "🟡 **Fair** - Moderate resource usage"
        else:
            return "🟢 **Good** - Optimal performance"
    
    @commands.command(name='metrics')
    @commands.has_permissions(administrator=True)
    async def metrics_command(self, ctx):
        """Show detailed API and cache metrics."""
        try:
            # Get cache stats
            spotify_cache_stats = await self.bot.spotify_api.cache.get_stats()
            openrouter_cache_stats = await self.bot.openrouter_api.cache.get_stats()
            
            embed = discord.Embed(
                title="📊 Detailed Metrics",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Spotify cache stats
            embed.add_field(
                name="🎵 Spotify Cache",
                value=f"**Entries:** {spotify_cache_stats['total_entries']}/{spotify_cache_stats['max_size']}\n"
                      f"**Utilization:** {spotify_cache_stats['utilization']:.1%}\n"
                      f"**Total Accesses:** {spotify_cache_stats['total_accesses']}\n"
                      f"**Avg Accesses:** {spotify_cache_stats['avg_accesses_per_entry']:.1f}",
                inline=True
            )
            
            # OpenRouter cache stats
            embed.add_field(
                name="🤖 OpenRouter Cache",
                value=f"**Entries:** {openrouter_cache_stats['total_entries']}/{openrouter_cache_stats['max_size']}\n"
                      f"**Utilization:** {openrouter_cache_stats['utilization']:.1%}\n"
                      f"**Total Accesses:** {openrouter_cache_stats['total_accesses']}\n"
                      f"**Avg Accesses:** {openrouter_cache_stats['avg_accesses_per_entry']:.1f}",
                inline=True
            )
            
            # Rate limiter stats
            user_stats = await self.bot.rate_limiter.get_user_stats(ctx.author.id)
            embed.add_field(
                name="⏱️ Rate Limiter",
                value=f"**Your Requests:** {user_stats['requests_in_window']}/15\n"
                      f"**Remaining:** {user_stats['remaining_requests']}\n"
                      f"**Reset Time:** <t:{int(user_stats['window_reset_time'])}:R>\n"
                      f"**Limited:** {'Yes' if user_stats['is_rate_limited'] else 'No'}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in metrics command: {e}")
            await ctx.send("❌ Error retrieving detailed metrics.")
    
    @commands.command(name='health')
    async def health_command(self, ctx):
        """Quick health check of the bot."""
        try:
            # Quick health check
            latency = self.bot.latency * 1000
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Determine health status
            if latency < 100 and memory_percent < 70 and cpu_percent < 70:
                status = "🟢 Healthy"
                color = discord.Color.green()
            elif latency < 200 and memory_percent < 85 and cpu_percent < 85:
                status = "🟡 Warning"
                color = discord.Color.yellow()
            else:
                status = "🔴 Critical"
                color = discord.Color.red()
            
            embed = discord.Embed(
                title="🏥 Bot Health Check",
                description=status,
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📊 Quick Stats",
                value=f"**Latency:** {latency:.1f}ms\n"
                      f"**Memory:** {memory_percent:.1f}%\n"
                      f"**CPU:** {cpu_percent:.1f}%\n"
                      f"**Guilds:** {len(self.bot.guilds)}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in health command: {e}")
            await ctx.send("❌ Error performing health check.")
    
    @commands.command(name='logs')
    @commands.has_permissions(administrator=True)
    async def logs_command(self, ctx, count: int = 10):
        """Show recent error logs."""
        try:
            if not self.bot.error_logs:
                await ctx.send("✅ No error logs found.")
                return
            
            # Get recent logs
            recent_logs = list(self.bot.error_logs)[-count:]
            
            embed = discord.Embed(
                title=f"📋 Recent Error Logs (Last {len(recent_logs)})",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            for i, log in enumerate(recent_logs[-5:], 1):  # Show last 5 logs
                timestamp = log['timestamp'].strftime('%H:%M:%S')
                error = log['error'][:100] + "..." if len(log['error']) > 100 else log['error']
                embed.add_field(
                    name=f"Error {i} ({timestamp})",
                    value=f"**Error:** {error}\n**User:** <@{log['user']}>\n**Guild:** {log['guild'] or 'DM'}",
                    inline=False
                )
            
            if len(recent_logs) > 5:
                embed.set_footer(text=f"And {len(recent_logs) - 5} more errors...")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in logs command: {e}")
            await ctx.send("❌ Error retrieving logs.")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(PerformanceMonitor(bot))
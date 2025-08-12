"""
Error Handler Cog
Provides comprehensive error handling and logging for the Discord bot.
"""

import discord
from discord.ext import commands
import logging
import traceback
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    """Global error handler for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler for command errors."""
        # Log the error
        error_msg = f"Command error in {ctx.guild.name if ctx.guild else 'DM'} by {ctx.author}: {str(error)}"
        logger.error(error_msg)
        
        # Add to bot's error logs
        self.bot.error_logs.append(error_msg)
        if len(self.bot.error_logs) > 100:  # Keep only last 100 errors
            self.bot.error_logs = self.bot.error_logs[-100:]
        
        # Handle different types of errors
        if isinstance(error, commands.CommandNotFound):
            await self._handle_command_not_found(ctx)
        elif isinstance(error, commands.MissingPermissions):
            await self._handle_missing_permissions(ctx, error)
        elif isinstance(error, commands.BotMissingPermissions):
            await self._handle_bot_missing_permissions(ctx, error)
        elif isinstance(error, commands.CommandOnCooldown):
            await self._handle_command_cooldown(ctx, error)
        elif isinstance(error, commands.MissingRequiredArgument):
            await self._handle_missing_argument(ctx, error)
        elif isinstance(error, commands.BadArgument):
            await self._handle_bad_argument(ctx, error)
        elif isinstance(error, commands.NoPrivateMessage):
            await self._handle_no_private_message(ctx)
        elif isinstance(error, commands.PrivateMessageOnly):
            await self._handle_private_message_only(ctx)
        elif isinstance(error, commands.DisabledCommand):
            await self._handle_disabled_command(ctx)
        elif isinstance(error, commands.CommandInvokeError):
            await self._handle_command_invoke_error(ctx, error)
        else:
            await self._handle_unknown_error(ctx, error)
    
    async def _handle_command_not_found(self, ctx):
        """Handle command not found errors."""
        embed = discord.Embed(
            title="❌ Command Not Found",
            description="The command you're looking for doesn't exist.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Available Commands",
            value="`!start` - Welcome message\n"
                  "`!help` - Help and examples\n"
                  "`!stats` - Your usage statistics\n"
                  "`!debug` - Bot debug information\n"
                  "`!status` - Detailed status\n"
                  "`!ping` - Latency check\n"
                  "`!info` - Bot information",
            inline=False
        )
        
        embed.add_field(
            name="Music Recommendations",
            value="Just send me a message describing what music you want!\n"
                  "Examples: \"I'm feeling happy\", \"Need rock for workout\"",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_missing_permissions(self, ctx, error):
        """Handle missing permissions errors."""
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Required Permissions",
            value=", ".join(error.missing_permissions),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_bot_missing_permissions(self, ctx, error):
        """Handle bot missing permissions errors."""
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description="I don't have the required permissions to perform this action.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Required Permissions",
            value=", ".join(error.missing_permissions),
            inline=False
        )
        
        embed.add_field(
            name="Solution",
            value="Ask a server administrator to grant me the required permissions.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_command_cooldown(self, ctx, error):
        """Handle command cooldown errors."""
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"This command is on cooldown. Please wait {error.retry_after:.1f} seconds.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Cooldown Info",
            value=f"Rate limit: {error.cooldown.rate} uses per {error.cooldown.per} seconds",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_missing_argument(self, ctx, error):
        """Handle missing argument errors."""
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"The command `{ctx.command}` is missing a required argument.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Missing Argument",
            value=f"`{error.param.name}`",
            inline=False
        )
        
        embed.add_field(
            name="Usage",
            value=f"`{ctx.prefix}{ctx.command} {ctx.command.signature}`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_bad_argument(self, ctx, error):
        """Handle bad argument errors."""
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description="One or more arguments provided are invalid.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Error",
            value=str(error),
            inline=False
        )
        
        embed.add_field(
            name="Usage",
            value=f"`{ctx.prefix}{ctx.command} {ctx.command.signature}`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_no_private_message(self, ctx):
        """Handle no private message errors."""
        embed = discord.Embed(
            title="❌ Command Not Available in DMs",
            description="This command can only be used in a server, not in private messages.",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_private_message_only(self, ctx):
        """Handle private message only errors."""
        embed = discord.Embed(
            title="❌ Command Only Available in DMs",
            description="This command can only be used in private messages.",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_disabled_command(self, ctx):
        """Handle disabled command errors."""
        embed = discord.Embed(
            title="❌ Command Disabled",
            description="This command is currently disabled.",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_command_invoke_error(self, ctx, error):
        """Handle command invoke errors."""
        original_error = error.original
        
        # Log the full error
        logger.error(f"Command invoke error: {str(original_error)}")
        logger.error(traceback.format_exc())
        
        # Create error embed
        embed = discord.Embed(
            title="❌ Command Error",
            description="An error occurred while executing the command.",
            color=discord.Color.red()
        )
        
        # Add error details if it's a known error type
        if isinstance(original_error, asyncio.TimeoutError):
            embed.add_field(
                name="Error Type",
                value="Timeout Error - The operation took too long to complete.",
                inline=False
            )
        elif isinstance(original_error, ConnectionError):
            embed.add_field(
                name="Error Type",
                value="Connection Error - Unable to connect to external services.",
                inline=False
            )
        else:
            embed.add_field(
                name="Error Type",
                value=f"{type(original_error).__name__}: {str(original_error)}",
                inline=False
            )
        
        embed.add_field(
            name="What to do",
            value="• Try again in a few moments\n"
                  "• Check if the service is working\n"
                  "• Contact support if the problem persists",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _handle_unknown_error(self, ctx, error):
        """Handle unknown errors."""
        # Log the full error
        logger.error(f"Unknown error: {str(error)}")
        logger.error(traceback.format_exc())
        
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred. Please try again later.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Error Details",
            value=f"Type: {type(error).__name__}\nMessage: {str(error)}",
            inline=False
        )
        
        embed.add_field(
            name="What to do",
            value="• Try the command again\n"
                  "• Check if the bot is working properly\n"
                  "• Contact support if the problem persists",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        """Handle errors in event listeners."""
        logger.error(f"Error in event {event_method}: {args} {kwargs}")
        logger.error(traceback.format_exc())
        
        # Add to bot's error logs
        error_msg = f"Event error in {event_method}: {args}"
        self.bot.error_logs.append(error_msg)
        if len(self.bot.error_logs) > 100:
            self.bot.error_logs = self.bot.error_logs[-100:]
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Log successful command usage."""
        logger.info(f"Command used: {ctx.command} by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Log successful command completion."""
        logger.info(f"Command completed: {ctx.command} by {ctx.author}")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(ErrorHandler(bot))
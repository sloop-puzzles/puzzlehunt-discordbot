import logging
from typing import Optional

import discord
from discord.ext import commands

from bot.store import MissingPuzzleError, PuzzleJsonDb, PuzzleData, GuildSettingsDb

logger = logging.getLogger(__name__)

"""
Base cog class which holds some common code for all of the cogs in this application.
"""


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # if isinstance(error, commands.errors.CheckFailure):
        #     await ctx.send('You do not have the correct role for this command.')
        await ctx.send(f":exclamation: **{type(error).__name__}**" + "\n" + str(error))


    async def check_is_bot_channel(self, ctx) -> bool:
        """Check if command was sent to bot channel configured in settings"""
        settings = GuildSettingsDb.get_cached(ctx.guild.id)
        if not settings.discord_bot_channel:
            # If no channel is designated, then all channels are fine
            # to listen to commands.
            return True

        if ctx.channel.name == settings.discord_bot_channel:
            # Channel name matches setting (note, channel name might not be unique)
            return True

        await ctx.send(f":exclamation: Most bot commands should be sent to #{settings.discord_bot_channel}")
        return False

    def get_puzzle_data_from_channel(self, channel) -> Optional[PuzzleData]:
        """Extract puzzle data based on the channel name and category name

        Looks up the corresponding JSON data
        """
        if not channel.category:
            return None

        guild = channel.guild
        guild_id = guild.id
        round_id = channel.category.id
        round_name = channel.category.name
        puzzle_id = channel.id
        puzzle_name = channel.name
        settings = GuildSettingsDb.get_cached(guild_id)
        hunt_id = settings.category_mapping[channel.category.id]

        if round_name.startswith(self.get_solved_puzzle_category(settings.hunt_settings[hunt_id].hunt_name)):
            round_id = "*"
        try:
            return PuzzleJsonDb.get(guild_id, puzzle_id, round_id, hunt_id)
        except MissingPuzzleError:
            # Not the cleanest, just try to guess the original category id
            # A DB would be useful here, then can directly query on solved_channel_id ..
            logger.error(
                f"Unable to retrieve puzzle={puzzle_id} round={round_id} {round_name}/{puzzle_name}"
            )
            return None


class GeneralAppError(RuntimeError):
    pass

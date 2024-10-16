""" Google Drive integration for puzzle organization

This is a separate cog so that Google Drive integration
can be easily disabled; simply omit this file.
"""

import datetime
import logging
import string
import traceback
from typing import Optional

import discord
from discord.ext import commands, tasks
import gspread_asyncio
import gspread_formatting
import pytz

from bot.base_cog import BaseCog
from bot.utils import urls
from bot.store import GuildSettingsDb, GuildSettings, MissingPuzzleError, PuzzleData, PuzzleJsonDb
from bot.utils.gdrive import get_or_create_folder, rename_file
from bot.utils.gsheet import create_spreadsheet, copy_spreadsheet, get_manager
from bot.utils.appscript import create_project, add_javascript
from bot.utils.gsheet_nexus import update_nexus

logger = logging.getLogger(__name__)


class GoogleSheets(BaseCog):
    agcm = get_manager()

    def __init__(self, bot):
        self.bot = bot
        self.refresh_nexus.start()

    def cap_name(self, name):
        """Capitalize name for easy comprehension"""
        return string.capwords(name.replace("-", " "))

    async def create_nexus_spreadsheet(self, text_channel: discord.TextChannel, hunt_name: str):
        guild_id = text_channel.guild.id
        settings = GuildSettingsDb.get(guild_id)
        folder_name = self.cap_name(hunt_name)
        if not settings.drive_parent_id:
            return
        try:
            hunt_folder = await get_or_create_folder(
                name= folder_name, parent_id=settings.drive_parent_id,
            )

            hunt_folder_id = hunt_folder["id"]
            spreadsheet = await create_spreadsheet(agcm=self.agcm, title="Nexus", folder_id=hunt_folder_id)
            url = urls.spreadsheet_url(spreadsheet.id)
            embed = discord.Embed(
                description=f":ladder: :dog: I've created a spreadsheet for you at {url} Check out the `Quick Links` tab for more info!"
            )
            await text_channel.send(embed=embed)
        except Exception as exc:
            logger.exception(f"Unable to create nexus spreadsheet for {hunt_name}")
            await text_channel.send(f":exclamation: Unable to create nexus spreadsheet for {hunt_name}: {exc}")
            return

        return (spreadsheet, hunt_folder)


    async def create_puzzle_spreadsheet(self, text_channel: discord.TextChannel, puzzle: PuzzleData):
        guild_id = text_channel.guild.id
        name = self.cap_name(puzzle.name)
        round_name = self.cap_name(puzzle.round_name)
        if name == "meta":
            # Distinguish metas between different rounds
            name = f"{name} ({round_name})"

        settings = GuildSettingsDb.get(guild_id)
        hunt_settings = settings.hunt_settings[puzzle.hunt_id]
        if not hunt_settings.drive_parent_id:
            return

        try:
            # create drive folder if needed
            round_folder = await get_or_create_folder(
                name=round_name, parent_id=hunt_settings.drive_parent_id
            )
            round_folder_id = round_folder["id"]

            if settings.drive_starter_sheet_id:
                spreadsheet = await copy_spreadsheet(agcm=self.agcm, source_id=settings.drive_starter_sheet_id, title=name, folder_id=round_folder_id)
                await self.clear_spreadsheet(spreadsheet)
            else:
                spreadsheet = await create_spreadsheet(agcm=self.agcm, title=name, folder_id=round_folder_id)
            puzzle.google_folder_id = round_folder_id
            puzzle.google_sheet_id = spreadsheet.id
            PuzzleJsonDb.commit(puzzle)

            # inform spreadsheet creation
            puzzle_url = puzzle.hunt_url
            sheet_url = urls.spreadsheet_url(spreadsheet.id)
            emoji = GuildSettingsDb.get_cached(guild_id).discord_bot_emoji
            embed = discord.Embed(
                description=
                f"{emoji} I've created a spreadsheet for you at {sheet_url}. "
                f"Check out the `Quick Links` tab for more info! "
                # NOTE: This next sentence might be better elsewhere, for now easy enough to add message here.
                f"I've assumed the puzzle page is {puzzle_url}, use `!link` to update if needed."
            )
            await text_channel.send(embed=embed)

            # add some helpful links
            await self.add_quick_links_worksheet(spreadsheet, puzzle, settings)

            # add the additional helpers
            #  proj = await create_project(spreadsheet.id)
            #  await add_javascript(proj["scriptId"])

        except Exception as exc:
            logger.exception(f"Unable to create spreadsheet for {round_name}/{name}")
            await text_channel.send(f":exclamation: Unable to create spreadsheet for {round_name}/{name}: {exc}")
            #  traceback.print_exc()
            return

        return spreadsheet

    async def clear_spreadsheet(self, spreadsheet: gspread_asyncio.AsyncioGspreadSpreadsheet):
        await spreadsheet.add_worksheet("Sheet 1", 1000, 26, index=0)

        body = {
            "requests": [{
                "deleteSheet": {
                    "sheetId": ws.id
                }
            } for ws in await spreadsheet.worksheets() if ws.title != "Sheet 1"]
        }

        await spreadsheet.batch_update(body)

    def update_cell_row(self, cell_range, row: int, key: str, value: str):
        """Update key-value row cell contents; row starts from 1"""
        cell_range[(row - 1) * 2].value = key
        cell_range[(row - 1) * 2 + 1].value = value

    async def add_quick_links_worksheet(
        self, spreadsheet: gspread_asyncio.AsyncioGspreadSpreadsheet, puzzle: PuzzleData, settings: GuildSettings
    ):
        worksheet = await spreadsheet.add_worksheet(title="Quick Links", rows=10, cols=2)
        cell_range = await worksheet.range(1, 1, 10, 2)

        hunt_settings = settings.hunt_settings[puzzle.hunt_id]

        self.update_cell_row(cell_range, 1, "Hunt URL", puzzle.hunt_url)
        self.update_cell_row(cell_range, 2, "Drive folder", urls.drive_folder_url(puzzle.google_folder_id))
        nexus_url = urls.spreadsheet_url(hunt_settings.drive_nexus_sheet_id) if hunt_settings.drive_nexus_sheet_id else ""
        self.update_cell_row(cell_range, 3, "Nexus", nexus_url)
        resources_url = urls.spreadsheet_url(settings.drive_resources_id) if settings.drive_resources_id else ""
        self.update_cell_row(cell_range, 4, "Resources", resources_url)
        self.update_cell_row(cell_range, 5, "Discord channel mention", puzzle.channel_mention)
        self.update_cell_row(
            cell_range, 6, "Reminders", "Please create a new worksheet if you're making large changes (e.g. re-sorting)"
        )
        self.update_cell_row(cell_range, 7, "", "You can use Ctrl+Alt+M to leave a comment on a cell")
        await worksheet.update_cells(cell_range)

        # Not async
        gspread_formatting.set_column_width(worksheet.ws, "B", 1000)

    async def archive_puzzle_spreadsheet(self, puzzle: PuzzleData) -> dict:
        def archive_puzzle_name(sheet_name):
            if "SOLVED" in sheet_name:
                return sheet_name
            return f"[SOLVED: {puzzle.solution}] {sheet_name}"

        return await rename_file(puzzle.google_sheet_id, name_lambda=archive_puzzle_name)

    @tasks.loop(seconds=60.0)
    async def refresh_nexus(self):
        """Ref: https://discordpy.readthedocs.io/en/latest/ext/tasks/"""
        for guild in self.bot.guilds:
            settings = GuildSettingsDb.get_cached(guild.id)
            for key, hs in settings.hunt_settings.items():
                if hs.drive_nexus_sheet_id and hs.end_time is None:
                    puzzles = PuzzleJsonDb.get_all(guild.id, key)
                    await update_nexus(agcm=self.agcm, file_id=hs.drive_nexus_sheet_id, puzzles=puzzles)

    @refresh_nexus.before_loop
    async def before_refreshing_nexus(self):
        await self.bot.wait_until_ready()
        print("Ready to start updating nexus spreadsheet")


async def setup(bot):
    # Comment this out if google-drive-related package are not installed!
    await bot.add_cog(GoogleSheets(bot))


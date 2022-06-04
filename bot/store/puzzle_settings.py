from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HuntSettings:
    hunt_url_sep: str = "-"         # Separator in the puzzle url, e.g. - for https://./puzzle/foo-bar
    hunt_name: str = ""
    hunt_url: str = ""
    drive_nexus_sheet_id: str = ""  # Refer to gsheet_nexus.py
    drive_parent_id: str = ""       # ID of root drive folder

@dataclass_json
@dataclass
class GuildSettings:
    guild_id: int
    guild_name: str = ""
    discord_bot_channel: str = ""   # Channel to listen for bot commands
    discord_bot_emoji: str = ":ladder: :dog:"  # Short description string or emoji for bot messages
    discord_use_voice_channels: int = 1  # Whether to create voice channels for puzzles
    drive_parent_id: str = ""
    drive_resources_id: str = ""    # Document with resources links, etc
    hunt_settings: Dict[str, HuntSettings] = field(default_factory=dict)
    category_mapping: Dict[int, str] = field(default_factory=dict)


class _GuildSettingsDb:
    @classmethod
    def get(cls, guild_id: int) -> GuildSettings:
        pass

    @classmethod
    def get_cached(cls, guild_id: int) -> GuildSettings:
        pass

    @classmethod
    def commit(cls, settings: GuildSettings):
        pass

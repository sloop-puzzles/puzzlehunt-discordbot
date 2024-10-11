import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dataclasses_json import dataclass_json
from google.cloud import datastore


@dataclass_json
@dataclass
class HuntSettings:
    hunt_id: int = 0
    guild_id: int = 0
    hunt_url_sep: str = "-"         # Separator in the puzzle url, e.g. - for https://./puzzle/foo-bar
    hunt_name: str = ""
    hunt_url: str = ""
    hunt_puzzle_prefix: str = "puzzle"
    drive_nexus_sheet_id: str = ""  # Refer to gsheet_nexus.py
    drive_parent_id: str = ""       # ID of root drive folder
    role_id: int = 0
    end_time: Optional[datetime.datetime] = None             # End time of the hunt
    start_time: Optional[datetime.datetime] = None           # Start time of the hunt

    def to_entity(self, client: datastore.Client):
        key = client.key('Hunt', self.hunt_id, 'Guild', self.guild_id)
        entity = datastore.Entity(key)
        entity['hunt_url_sep'] = self.hunt_url_sep
        entity['hunt_name'] = self.hunt_name
        entity['hunt_url'] = self.hunt_url
        entity['drive_nexus_sheet_id'] = self.drive_nexus_sheet_id
        entity['drive_parent_id'] = self.drive_parent_id
        entity['role_id'] = self.role_id
        entity['start_time'] = self.start_time
        entity['end_time'] = self.end_time
        return entity

    @classmethod
    def from_entity(cls, entity: datastore.Entity):
        hunt = HuntSettings()

        hunt.hunt_id = entity.key.id_or_name
        hunt.guild_id = entity.parent.id_or_name
        hunt.hunt_url_sep = entity['hunt_url_sep']
        hunt.hunt_name = entity['hunt_name']
        hunt.hunt_url = entity['hunt_url']
        hunt.drive_nexus_sheet_id = entity['drive_nexus_sheet_id']
        hunt.drive_parent_id = entity['drive_parent_id']
        hunt.role_id = entity['role_id']
        hunt.start_time = entity['start_time']
        hunt.end_time = entity['end_time']
        return hunt



@dataclass_json
@dataclass
class GuildSettings:
    guild_id: int
    guild_name: str = ""
    discord_bot_channel: str = ""   # Channel to listen for bot commands
    discord_bot_emoji: str = ":ladder: :dog:"  # Short description string or emoji for bot messages
    discord_use_voice_channels: bool = False  # Whether to create voice channels for puzzles
    drive_parent_id: str = ""
    drive_resources_id: str = ""    # Document with resources links, etc
    hunt_settings: Dict[int, HuntSettings] = field(default_factory=dict)
    category_mapping: Dict[int, int] = field(default_factory=dict)
    past_hunts_category_id: int = 0
    drive_starter_sheet_id: str = ""

    def to_entity(self, client: datastore.Client):
        key = client.key('Guild', self.guild_id)
        entity = datastore.Entity(key)
        entity['guild_name'] = self.guild_name
        entity['discord_bot_channel'] = self.discord_bot_channel
        entity['discord_bot_emoji'] = self.discord_bot_emoji
        entity['discord_use_voice_channels'] = self.discord_use_voice_channels
        entity['drive_parent_id'] = self.drive_parent_id
        entity['drive_resources_id'] = self.drive_resources_id
        entity['past_hunts_category_id'] = self.past_hunts_category_id
        entity['sheet_tempalte_id'] = self.drive_starter_sheet_id
        return entity

    @classmethod
    def from_entity(cls, entity: datastore.Entity):
        guild = GuildSettings

        guild.guild_id = entity.key.id_or_name
        guild.guild_name = entity['guild_name']
        guild.discord_bot_channel = entity['discord_bot_channel']
        guild.discord_bot_emoji = entity['discord_bot_emoji']
        guild.discord_use_voice_channels = entity['discord_use_voice_channels']
        guild.drive_parent_id = entity['drive_parent_id']
        guild.drive_resources_id = entity['drive_resources_id']
        guild.past_hunts_category_id = entity['past_hunts_category_id']
        guild.puzzle_template_id = entity['drive_starter_sheet_id']

        return guild


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


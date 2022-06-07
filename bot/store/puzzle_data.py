from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from google.cloud import datastore
import datetime
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class MissingPuzzleError(RuntimeError):
    pass

@dataclass_json
@dataclass
class PuzzleData:
    name: str
    hunt_name: str=""
    hunt_id: str = 0
    round_name: str = ""
    round_id: int = 0  # round = category channel
    guild_id: int = 0
    #  guild_name: str = ""
    channel_id: int = 0
    channel_mention: str = ""
    voice_channel_id: int = 0
    hunt_url: str = ""
    google_sheet_id: str = ""
    google_folder_id: str = ""
    status: str = ""
    solution: str = ""
    priority: str = ""
    puzzle_type: str = ""
    notes: List[str] = field(default_factory=list)
    start_time: Optional[datetime.datetime] = None
    solve_time: Optional[datetime.datetime] = None
    archive_time: Optional[datetime.datetime] = None

    def to_entity(self, client: datastore.Client):
        key = client.key('Guild', self.guild_id, 'Hunt', self.hunt_id, 'Round', self.round_id, 'Puzzle', self.channel_id)
        entity = datastore.Entity(key)
        entity['name'] = self.name
        entity['hunt_name'] =  self.hunt_name
        entity['round_name'] = self.round_name
        entity['channel_mention'] = self.channel_mention
        entity['voice_channel_id'] = self.voice_channel_id
        entity['hunt_url'] = self.hunt_url
        entity['google_sheet_id'] = self.google_sheet_id
        entity['google_folder_id'] = self.google_folder_id
        entity['status'] = self.status
        entity['solution'] = self.solution
        entity['priority'] = self.priority
        entity['puzzle_type'] = self.puzzle_type
        entity['notes'] = self.notes
        entity['start_time'] = self.start_time
        entity['solve_time'] = self.solve_time
        entity['archive_time'] = self.archive_time
        return entity

    @classmethod
    def from_entity(cls, entity: datastore.Entity):
        puz = PuzzleData()
        key = entity.key
        round_key = key.parent
        hunt_key = round_key.parent
        guild_key = hunt_key.parent

        puz.channel_id = key.id_or_name
        puz.round_id = round_key.id_or_name
        puz.hunt_id = hunt_key.id_or_name
        puz.guild_id = guild_key.id_or_name
        puz.name = entity['name']
        puz.hunt_name = entity['hunt_name']
        puz.round_name = entity['round_name']
        puz.channel_mention = entity['channel_mention']
        puz.voice_channel_id = entity['voice_channel_id']
        puz.hunt_url = entity['hunt_url']
        puz.google_sheet_id = entity['google_sheet_id']
        puz.google_folder_id = entity['google_folder_id']
        puz.status = entity['status']
        puz.solution = entity['solution']
        puz.priority = entity['priority']
        puz.puzzle_type = entity['puzzle_type']
        puz.notes = entity['notes']
        puz.start_time = entity['start_time']
        puz.solve_time = entity['solve_time']
        puz.archive_time = entity['archive_time']
        return puz

    @classmethod
    def sort_by_round_start(cls, puzzles: list) -> list:
        """Return list of PuzzleData objects sorted by start of round time

        Groups puzzles in the same round together, and sorts puzzles within round
        by start_time.
        """
        round_start_times = {}

        for puzzle in puzzles:
            if puzzle.start_time is None:
                continue

            start_time = puzzle.start_time.timestamp()  # epoch time
            round_start_time = round_start_times.get(puzzle.round_name)
            if round_start_time is None or start_time < round_start_time:
                round_start_times[puzzle.round_name] = start_time

        return sorted(puzzles, key=lambda p: (round_start_times.get(p.round_name, 0), p.start_time or 0))

class _PuzzleJsonDb:
    def commit(self, puzzle_data):
        pass
    def delete(self, puzzle_data):
        pass
    def get(self, guild_id, puzzle_id, round_id, hunt_id) -> PuzzleData:
        pass
    def get_all(self, guild_id, hunt_id="*") -> List[PuzzleData]:
        pass
    def get_solved_puzzles_to_archive(self, guild_id, now=None, include_meta=False, minutes=5) -> List[PuzzleData]:
        pass
    def aggregate_json(self) -> dict:
        pass

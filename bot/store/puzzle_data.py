from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
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
    hunt_name: str
    round_name: str
    round_id: int = 0  # round = category channel
    guild_id: int = 0
    guild_name: str = ""
    channel_id: int = 0
    channel_mention: str = ""
    voice_channel_id: int = 0
    # archive_channel_id: str = ""
    archive_channel_mention: str = ""
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
    def get(self, guild_id, puzzle_id, round_id, hunt_name) -> PuzzleData:
        pass
    def get_all(self, guild_id, hunt_name="*") -> List[PuzzleData]:
        pass
    def get_all(self, guild_id, hunt_name="*") -> List[PuzzleData]:
        pass
    def get_solved_puzzles_to_archive(self, guild_id, now=None, include_meta=False, minutes=5) -> List[PuzzleData]:
        pass
    def aggregate_json(self) -> dict:
        pass

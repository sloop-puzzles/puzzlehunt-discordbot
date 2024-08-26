import datetime
import errno
import json
import logging
from pathlib import Path
from typing import List

import pytz
from .puzzle_data import _PuzzleJsonDb, PuzzleData
from .puzzle_settings import _GuildSettingsDb, GuildSettings

logger = logging.getLogger(__name__)
class FilePuzzleJsonDb(_PuzzleJsonDb):
    def __init__(self, dir_path: Path):
        self.dir_path = dir_path

    def puzzle_path(self, puzzle, round_id=None, hunt_id=None, guild_id=None) -> Path:
        """Store puzzle metadata to the path `guild/category/puzzle.json`

        Use unique ASCII ids (e.g. the discord id snowflakes) for each part of the
        path, to avoid potential shenanigans with unicode handling.

        Note:
            For convenience, with the Google Drive cog, the relative path
            to the puzzle metadata file will be saved in a column in the nexus
            spreadsheet.
        """
        if isinstance(puzzle, PuzzleData):
            puzzle_id = puzzle.channel_id
            round_id = puzzle.round_id
            guild_id = puzzle.guild_id
            hunt_id = puzzle.hunt_id
        elif isinstance(puzzle, (int, str)):
            puzzle_id = puzzle
            if round_id is None or guild_id is None or hunt_id is None:
                raise ValueError(f"round_id / guild_id not passed for puzzle {puzzle}")
        else:
            raise ValueError(f"Unknown puzzle type: {type(puzzle)} for {puzzle}")
        # TODO: Database would be better here .. who wants to sort through puzzle metadata by these ids?
        return (self.dir_path / str(guild_id) / str(hunt_id) / str(round_id) / str(puzzle_id)).with_suffix(".json")

    def commit(self, puzzle_data):
        """Update puzzle metadata file"""
        puzzle_path = self.puzzle_path(puzzle_data)
        puzzle_path.parent.parent.mkdir(exist_ok=True)
        puzzle_path.parent.mkdir(exist_ok=True)
        with puzzle_path.open("w") as fp:
            fp.write(puzzle_data.to_json(indent=4))

    def delete(self, puzzle_data):
        puzzle_path = self.puzzle_path(puzzle_data)
        try:
            puzzle_path.unlink()
        except IOError:
            pass

    def get(self, guild_id, puzzle_id, round_id, hunt_id) -> PuzzleData:
        try:
            path = self.puzzle_path(puzzle_id, hunt_id=hunt_id, round_id=round_id, guild_id=guild_id)
            p = next(self.dir_path.rglob(f"{guild_id}/{hunt_id}/*/{puzzle_id}.json")) if "*" in str(path) else path
            with p.open() as fp:
                return PuzzleData.from_json(fp.read())
        except (IOError, OSError) as exc:
            # can also just catch FileNotFoundError
            if exc.errno == errno.ENOENT:
                raise MissingPuzzleError(f"Unable to find puzzle {puzzle_id} for {round_id}")
            raise


    def get_all(self, guild_id, hunt_id="*") -> List[PuzzleData]:
        paths = self.dir_path.rglob(f"{guild_id}/{hunt_id}/*/*.json")
        puzzle_datas = []
        for path in paths:
            try:
                with path.open() as fp:
                    puzzle_datas.append(PuzzleData.from_json(fp.read()))
            except Exception:
                logger.exception(f"Unable to load puzzle data from {path}")
        return PuzzleData.sort_by_round_start(puzzle_datas)

    def get_solved_puzzles_to_archive(self, guild_id, now=None, include_meta=False, minutes=5) -> List[PuzzleData]:
        """Returns list of all solved but unarchived puzzles"""
        all_puzzles = self.get_all(guild_id)
        now = now or datetime.datetime.now(tz=pytz.UTC)
        puzzles_to_archive = []
        for puzzle in all_puzzles:
            if puzzle.archive_time is not None:
                # already archived
                continue
            if puzzle.name == "meta" and not include_meta:
                # we usually do not want to archive meta channels, only do manually
                continue
            if puzzle.status == "solved" and puzzle.solve_time is not None:
                # found a solved puzzle
                if now - puzzle.solve_time > datetime.timedelta(minutes=minutes):
                    # enough time has passed, archive the channel
                    puzzles_to_archive.append(puzzle)
        return puzzles_to_archive

    def aggregate_json(self) -> dict:
        """Aggregate all puzzle metadata into a single JSON object, for convenience

        Might be handy with a JSON viewer such as `IPython.display.JSON`.
        """
        paths = self.dir_path.rglob(f"*/*.json")
        result = {}
        for path in paths:
            relpath = path.relative_to(self.dir_path)
            with path.open() as fp:
                result[str(relpath)] = json.load(fp)
        return result

class FileGuildSettingsDb():
    def __init__(self, dir_path: Path):
        self.dir_path = dir_path
        self.cached_settings = {}

    def get(self, guild_id: int) -> GuildSettings:
        settings_path = self.dir_path / str(guild_id) / "settings.json"
        if settings_path.exists():
            with settings_path.open() as fp:
                settings = GuildSettings.from_json(fp.read())
        else:
            # Populate empty settings file
            settings = GuildSettings(guild_id=guild_id)
            self.commit(settings)
        return settings

    def get_cached(self, guild_id: int) -> GuildSettings:
        if guild_id in self.cached_settings:
            return self.cached_settings[guild_id]
        settings = self.get(guild_id)
        self.cached_settings[guild_id] = settings
        return settings

    def commit(self, settings: GuildSettings):
        settings_path = self.dir_path / str(settings.guild_id) / "settings.json"
        settings_path.parent.parent.mkdir(exist_ok=True)
        settings_path.parent.mkdir(exist_ok=True)
        with settings_path.open("w") as fp:
            fp.write(settings.to_json(indent=4))
        self.cached_settings[settings.guild_id] = settings

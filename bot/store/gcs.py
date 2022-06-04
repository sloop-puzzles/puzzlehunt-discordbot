class GCSPuzzleJsonDb(_PuzzleJsonDb):
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

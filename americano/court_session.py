from typing import List, Optional

from pydantic import BaseModel, Field


class CourtSession(BaseModel):
    n_players_each_team: int = Field()
    teamA: List[str] = Field()
    teamB: List[str] = Field()
    n_game_points: int = Field()
    score_team_A: Optional[int] = Field(default=None)
    score_team_B: Optional[int] = Field(default=None)

    @property
    def finished(self) -> bool:
        return self.score_team_A is not None and self.score_team_B is not None

    def add_score(
        self,
        score_team_A: Optional[int] = None,
        score_team_B: Optional[int] = None,
    ):
        if score_team_A is not None:
            self.score_team_A = score_team_A
        if score_team_B is not None:
            self.score_team_B = score_team_B

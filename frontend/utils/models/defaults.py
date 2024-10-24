from pydantic import BaseModel, Field


class GameSessionDefaults(BaseModel):
    n_courts: int = Field(default=3)
    n_game_points: int = Field(default=24)
    n_court_players: list[int] = Field(default=[2])
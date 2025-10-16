from pydantic import BaseModel, Field


class GameSessionDefaults(BaseModel):
    n_courts: int = Field(default=3)
    n_game_points: int = Field(default=24)
    n_court_players: list[int] = Field(default=[2])
    use_default_game_points: bool = Field(default=True)
    override_resting_points: bool = Field(default=False)
    resting_points_manual: int = Field(default=0)
    allow_negative_player_scores: bool = Field(default=False)
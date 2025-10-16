"""Game session schemas for API validation."""

from typing import Optional

from pydantic import BaseModel, Field


class CourtConfig(BaseModel):
    """Configuration for a single court."""

    n_players_each_team: int = Field(..., ge=1)


class GameSessionCreate(BaseModel):
    """Schema for creating a game session."""

    n_courts: int = Field(..., ge=1)
    court_configs: list[CourtConfig] = Field(
        ..., description="Configuration for each court"
    )
    n_game_points: Optional[int] = Field(None, ge=1)
    resting_points: Optional[float] = Field(None, ge=0)


class GameSessionResponse(BaseModel):
    """Schema for game session responses."""

    id: int
    tournament_id: int
    n_courts: int
    n_game_points: Optional[int]
    resting_points: Optional[float]
    finished: bool
    status: str  # 'pending', 'in_progress', or 'completed'
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }


class CourtSessionResponse(BaseModel):
    """Schema for court session responses."""

    id: int
    game_session_id: int
    court_index: int
    n_players_each_team: int
    score_team_a: Optional[int]
    score_team_b: Optional[int]
    team_a_players: list[int] = []  # Player IDs
    team_b_players: list[int] = []  # Player IDs

    model_config = {
        "from_attributes": True,
    }

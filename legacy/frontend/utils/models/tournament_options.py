from pydantic import BaseModel, Field


class TournamentOptions(BaseModel):
    mix_tournament: bool = Field(default=False)

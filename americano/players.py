import json
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field

from americano.models.enums import Gender


class Player(BaseModel):
    id: int = Field()
    name: str = Field()
    gender: Optional[Gender] = Field()
    score: int | float = Field(default=0)
    games_played: int = Field(default=0)

    def print(self):
        print(f"Name: {self.name}, Score: {self.score}, Games Played: {self.games_played}")  # noqa E501


class PlayerList(BaseModel):
    players: List[Player] = Field(default_factory=list)
    next_id: int = Field(default=1)

    def add_player(self, name: str) -> Player:
        # Check if name is empty
        if not name:
            raise ValueError("Player name cannot be empty")

        # Check if player already exists
        for player in self.players:
            if player.name == name:
                raise ValueError(f"Player {name} already exists")

        player = Player(id=self.next_id, name=name)
        self.players.append(player)
        self.next_id += 1
        return player

    def add_players(self, names: List[str]) -> List[Player]:
        players = [Player(id=self.next_id + i, name=name) for i, name in enumerate(names)]  # noqa E501
        self.players.extend(players)
        self.next_id += len(names)
        return players

    def remove_player(self, player_id: int) -> Optional[Player]:
        for i, player in enumerate(self.players):
            if player.id == player_id:
                return self.players.pop(i)
        return None

    def remove_player_by_name(self, name: str) -> Optional[Player]:
        for i, player in enumerate(self.players):
            if player.name == name:
                return self.players.pop(i)
        return None

    def get_player_by_name(self, name: str) -> Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return None

    def add_game_result_to_player(self):
        pass

    def save_players(self, filename: str):
        with open(filename, 'w') as f:
            json.dump([player.dict() for player in self.players], f)

    def load_players(self, filename: str):
        with open(filename) as f:
            player_data = json.load(f)
        self.players = [Player(**data) for data in player_data]
        self.next_id = max(player.id for player in self.players) + 1

    def get_names(self):
        return [player.name for player in self.players]

    def get_player_scores(self):
        return [player.score for player in self.players]

    def get_player_games_played(self):
        return [player.games_played for player in self.players]

    def print(self):
        for player in self.players:
            player.print()

    def to_pandas(self):
        return pd.DataFrame([player.model_dump() for player in self.players])

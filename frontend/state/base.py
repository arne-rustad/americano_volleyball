from abc import ABC, abstractmethod
from typing import Optional

from americano.game_session import GameSession
from americano.players import PlayerList
from frontend.utils.models.defaults import GameSessionDefaults
from frontend.utils.models.tournament_options import TournamentOptions


class State(ABC):
    @abstractmethod
    def set_players(self, players: PlayerList) -> None:
        pass

    @abstractmethod
    def get_players(self) -> PlayerList:
        pass

    @abstractmethod
    def delete_players(self) -> None:
        pass

    @abstractmethod
    def set_game_session(self, game_session: GameSession) -> None:
        pass

    @abstractmethod
    def get_game_session(self) -> Optional[GameSession]:
        pass

    @abstractmethod
    def delete_game_session(self) -> None:
        pass

    @abstractmethod
    def set_defaults(self, defaults: GameSessionDefaults) -> None:
        pass

    @abstractmethod
    def get_defaults(self) -> GameSessionDefaults:
        pass

    @abstractmethod
    def delete_defaults(self) -> None:
        pass

    @abstractmethod
    def set_tournament_options(self, options: TournamentOptions) -> None:
        pass

    @abstractmethod
    def get_tournament_options(self) -> Optional[TournamentOptions]:
        pass

    @abstractmethod
    def delete_tournament_options(self) -> None:
        pass

    @abstractmethod
    def end_tournament(self) -> None:
        pass

    @abstractmethod
    def restart_tournament(self) -> None:
        pass

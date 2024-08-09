from pydantic import BaseModel, Field
from typing import List, Optional
from .players import PlayerList, Player


class CourtSession(BaseModel):
    n_players_each_team: int = Field()
    teamA: List[Player] = Field()
    teamB: List[Player] = Field()
    n_game_points: int = Field()
    score_team_A: Optional[int] = Field(default=None)
    score_team_B: Optional[int] = Field(default=None)

    @property
    def finished(self) -> bool:
        return self.score_team_A is not None and self.score_team_B is not None

    def add_score(self, score_team_A: Optional[int] = None, score_team_B: Optional[int] = None):  # noqa E501
        if score_team_A is not None:
            self.score_team_A = score_team_A
        if score_team_B is not None:
            self.score_team_B = score_team_B

    def add_score_to_players(self):
        assert self.finished

        for player in self.teamA:
            player.games_played += 1
            player.score += self.score_team_A
        for player in self.teamB:
            player.games_played += 1
            player.score += self.score_team_B


class GameSession(BaseModel):
    n_courts: int = Field()
    n_game_points: int = Field()
    court_sessions: List[CourtSession] = Field(default_factory=list)
    players: PlayerList = Field()
    score_added_to_players: bool = Field(default=False)

    def update_session_score(self, court_index: int, score_team_A: int = None, score_team_B: int = None):  # noqa E501
        if score_team_A is None and score_team_B is None:
            return ValueError("Both team scores cannot be None")

        elif score_team_A is None:
            score_team_A = self.n_game_points - score_team_B
        elif score_team_B is None:
            score_team_B = self.n_game_points - score_team_A

        if 0 <= court_index < len(self.court_sessions):
            self.court_sessions[court_index].add_score(score_team_A, score_team_B)  # noqa E501

    def add_court_session(
        self,
        n_players_each_team: int,
        teamA: List[Player],
        teamB: List[Player]
    ):
        court_session = CourtSession(n_players_each_team=n_players_each_team, teamA=teamA, teamB=teamB, n_game_points=self.n_game_points)  # noqa E501
        self.court_sessions.append(court_session)

    def create_court_sessions(self, n_players_each_team: list):
        assert len(n_players_each_team) == self.n_courts

        self.court_sessions = []

        drawn_players = self.players.draw_players(n = 2 * sum(n_players_each_team))  # noqa E501

        used_players = 0
        for n_players in n_players_each_team:
            teamA = drawn_players[used_players:used_players + 2*n_players:2]
            teamB = drawn_players[used_players+1:used_players + 2*n_players:2]
            used_players += n_players * 2
            self.add_court_session(n_players_each_team=n_players, teamA=teamA, teamB=teamB)  # noqa E501

    @property
    def finished(self) -> bool:
        return all(session.finished for session in self.court_sessions)

    def add_score_to_players(self, override: bool = False):

        if self.score_added_to_players and not override:
            print("Score already added to players and override = False. Skipping...")  # noqa E501

        if not self.finished:
            return ValueError("Cannot add score to players until all sessions are finished")  # noqa E501

        for session in self.court_sessions:
            session.add_score_to_players()

        self.score_added_to_players = True

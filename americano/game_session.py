from random import shuffle
from typing import List

from pydantic import BaseModel, Field

from americano.court_session import CourtSession
from americano.player_manager import PlayerManager

from .players import PlayerList


class GameSession(BaseModel):
    n_courts: int = Field()
    n_game_points: int = Field()
    court_sessions: List[CourtSession] = Field(default_factory=list)
    score_added_to_players: bool = Field(default=False)

    def update_session_score(
        self,
        court_index: int,
        score_team_A: int = None,
        score_team_B: int = None,
    ):
        if score_team_A is None and score_team_B is None:
            raise ValueError("Both team scores cannot be None")
        
        assert 0 <= court_index < len(self.court_sessions) # Make sure the court index is valid  # noqa E501

        if score_team_A is not None:
            self.court_sessions[court_index].score_team_A = score_team_A
        
        if score_team_B is not None:
            self.court_sessions[court_index].score_team_B = score_team_B
        
        if self.n_game_points is not None:
            if self.court_sessions[court_index].score_team_A is None:
                self.court_sessions[court_index].score_team_A = self.n_game_points - score_team_B  # noqa E501
            elif self.court_sessions[court_index].score_team_B is None:
                self.court_sessions[court_index].score_team_B = self.n_game_points - score_team_A  # noqa E501


    def add_court_session(
        self,
        n_players_each_team: int,
        teamA: List[str],
        teamB: List[str],
    ):
        court_session = CourtSession(
            n_players_each_team=n_players_each_team,
            teamA=teamA,
            teamB=teamB,
            n_game_points=self.n_game_points,
        )
        self.court_sessions.append(court_session)

    def create_court_sessions(
        self,
        n_players_each_team: list[int],
        players: PlayerList,
        mix_tournament: bool = False,
    ):
        assert len(n_players_each_team) == self.n_courts

        self.court_sessions = []

        player_manager = PlayerManager(player_list=players)
        drawn_players = player_manager.draw_player_names(
            n=2 * sum(n_players_each_team),
            mix_tournament=mix_tournament,
        )
        if mix_tournament:
            used_players = 0
            for n_players in n_players_each_team:
                teamA = []
                teamB = []
                current_players = drawn_players[
                    used_players : used_players + 2 * n_players
                ]
                groups = []
                for i in range(len(current_players) // 4):
                    groups.append(current_players[i * 4 : (i + 1) * 4])
                if len(current_players) % 4 > 0:
                    groups.append(
                        current_players[len(current_players) // 4 * 4 :]
                    )
                for group in groups:
                    if len(group) == 4:
                        teamA.extend([group[0], group[3]])
                        teamB.extend([group[1], group[2]])
                    elif len(group) == 2:
                        shuffle(group)
                        teamA.append(group[0])
                        teamB.append(group[1])
                    else:
                        raise ValueError(
                            f"Invalid group size: {len(group)}. Group size should always be 2 or 4."  # noqa E501
                        )
                used_players += 2 * n_players
                self.add_court_session(
                    n_players_each_team=n_players, teamA=teamA, teamB=teamB
                )

        else:
            used_players = 0
            for n_players in n_players_each_team:
                teamA = drawn_players[
                    used_players : used_players + 2 * n_players : 2
                ]
                teamB = drawn_players[
                    used_players + 1 : used_players + 2 * n_players : 2
                ]
                used_players += n_players * 2
                self.add_court_session(
                    n_players_each_team=n_players, teamA=teamA, teamB=teamB
                )

    @property
    def finished(self) -> bool:
        return all(session.finished for session in self.court_sessions)

    def add_score_to_players(self, override: bool = False):
        if self.score_added_to_players and not override:
            print(
                "Score already added to players and override = False. Skipping..."  # noqa E501
            )

        if not self.finished:
            return ValueError(
                "Cannot add score to players until all sessions are finished"
            )

        for session in self.court_sessions:
            session.add_score_to_players()

        self.score_added_to_players = True

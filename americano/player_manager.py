from americano.court_session import CourtSession
from americano.models.enums import Gender
from americano.players import Player, PlayerList


class PlayerManager:
    def __init__(self, player_list: PlayerList):
        self.player_list = player_list

    def draw_players(
        self, n: int, mix_tournament: bool = False
    ) -> list[Player]:
        if n > len(self.player_list.players):
            raise ValueError("Cannot draw more players than available")
        elif n < 0:
            raise ValueError("Cannot draw a negative number of players")
        if n % 2 != 0:
            raise ValueError("Cannot draw an odd number of players (yet)")

        # Sort players by score, descending. We do this first to make the sorting easier to test.  # noqa E501
        players_drawn = sorted(
            self.player_list.players,
            key=lambda x: x.score,
            reverse=True,
        )

        # Sort players by games played, ascending
        players_drawn = sorted(
            self.player_list.players,
            key=lambda x: x.games_played,
            reverse=False,
        )

        # If mix tournament, return first one man, then one woman, then one man, etc.  # noqa E501
        if mix_tournament:
            male_players = [
                p for p in players_drawn if p.gender == Gender.MALE
            ]
            female_players = [
                p for p in players_drawn if p.gender == Gender.FEMALE
            ]

            n_male_to_select = min(n // 2, len(male_players))
            n_female_to_select = min(n // 2, len(female_players))

            # Handle case where we don't have enough players of one gender.
            # We have earlier verified that there are at least n players,
            # thus we can safely add the difference to the other gender.
            if n_male_to_select < n // 2:
                n_female_to_select += n // 2 - n_male_to_select
            elif n_female_to_select < n // 2:
                n_male_to_select += n // 2 - n_female_to_select

            selected_male_players = male_players[:n_male_to_select]
            selected_female_players = female_players[:n_female_to_select]

            # Reorder players by points
            selected_male_players = sorted(
                selected_male_players, key=lambda x: x.score, reverse=True
            )
            selected_female_players = sorted(
                selected_female_players, key=lambda x: x.score, reverse=True
            )

            # Merge lists, alternating between male and female
            selected_players = []
            male_index = 0
            female_index = 0
            i = 0

            while len(selected_players) < n:
                if i % 2 == 0:  # Even index, pick male
                    if male_index < len(selected_male_players):
                        selected_players.append(
                            selected_male_players[male_index]
                        )
                        male_index += 1
                    elif female_index < len(selected_female_players):
                        selected_players.append(
                            selected_female_players[female_index]
                        )
                        female_index += 1
                    else:
                        break  # No more players to pick
                else:  # Odd index, pick female
                    if female_index < len(selected_female_players):
                        selected_players.append(
                            selected_female_players[female_index]
                        )
                        female_index += 1
                    elif male_index < len(selected_male_players):
                        selected_players.append(
                            selected_male_players[male_index]
                        )
                        male_index += 1
                    else:
                        break  # No more players to pick
                i += 1

            return selected_players
        # If not mix tournament, just return the first n players
        else:
            players_drawn = players_drawn[:n]
            return sorted(players_drawn, key=lambda x: x.score, reverse=True)

    def draw_player_names(
        self, n: int, mix_tournament: bool = False
    ) -> list[str]:
        return [
            player.name
            for player in self.draw_players(n=n, mix_tournament=mix_tournament)
        ]

    @classmethod
    def _update_player_score_single_court(
        cls, players: PlayerList, court_session: CourtSession
    ):
        assert court_session.finished

        for player_name in court_session.teamA:
            player = players.get_player_by_name(player_name)
            player.games_played += 1
            player.score += court_session.score_team_A

        for player_name in court_session.teamB:
            player = players.get_player_by_name(player_name)
            player.games_played += 1
            player.score += court_session.score_team_B

    def update_player_scores(
        self, court_sessions: list[CourtSession], resting_points: int = 0
    ):
        for session in court_sessions:
            self._update_player_score_single_court(
                players=self.player_list, court_session=session
            )

        if resting_points > 0:
            players_playing = [
                player_name
                for session in court_sessions
                for player_name in session.teamA + session.teamB
            ]
            players_not_playing = [
                player_name
                for player_name in self.player_list.get_names()
                if player_name not in players_playing
            ]
            for player_name in players_not_playing:
                player = self.player_list.get_player_by_name(player_name)
                player.score += resting_points

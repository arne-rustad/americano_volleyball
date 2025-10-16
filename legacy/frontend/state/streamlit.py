from typing import Optional

import streamlit as st

from americano.game_session import GameSession
from americano.players import PlayerList
from frontend.state.base import State
from frontend.utils.models.defaults import GameSessionDefaults
from frontend.utils.models.tournament_options import TournamentOptions


class StreamlitState(State):
    def set_players(self, players: PlayerList) -> None:
        """Set the players in Streamlit session_state."""
        st.session_state["players"] = players.model_dump_json()

    def get_players(self) -> PlayerList:
        """Get the players from Streamlit session_state."""
        if "players" not in st.session_state:
            st.session_state["players"] = PlayerList().model_dump_json()
        return PlayerList.model_validate_json(st.session_state["players"])

    def delete_players(self) -> None:
        """Delete the players from Streamlit session_state."""
        st.session_state.pop("players", None)

    def set_game_session(self, game_session: GameSession) -> None:
        """Set the game session in Streamlit session_state."""
        st.session_state["game_session"] = game_session.model_dump_json()

    def get_game_session(self) -> Optional[GameSession]:
        """Get the game session from Streamlit session_state."""
        if "game_session" not in st.session_state:
            return None
        return GameSession.model_validate_json(st.session_state["game_session"])

    def delete_game_session(self) -> None:
        """Delete the game session from Streamlit session_state."""
        st.session_state.pop("game_session", None)

    def set_defaults(self, defaults: GameSessionDefaults) -> None:
        """Set the game session defaults in Streamlit session_state."""
        st.session_state["defaults"] = defaults.model_dump_json()

    def get_defaults(self) -> GameSessionDefaults:
        """Get the game session defaults from Streamlit session_state."""
        if "defaults" not in st.session_state:
            st.session_state["defaults"] = GameSessionDefaults().model_dump_json()  # noqa E501
        return GameSessionDefaults.model_validate_json(st.session_state["defaults"])  # noqa E501

    def delete_defaults(self) -> None:
        """Delete the defaults from Streamlit session_state."""
        st.session_state.pop("defaults", None)

    def set_tournament_options(self, options: TournamentOptions) -> None:
        """Set the tournament options in Streamlit session_state."""
        st.session_state["tournament_options"] = options.model_dump_json()

    def get_tournament_options(self) -> Optional[TournamentOptions]:
        """Get the tournament options from Streamlit session_state."""
        if "tournament_options" not in st.session_state:
            return None
        return TournamentOptions.model_validate_json(
            st.session_state["tournament_options"]
        )

    def delete_tournament_options(self) -> None:
        """Delete the tournament options from Streamlit session_state."""
        st.session_state.pop("tournament_options", None)

    def end_tournament(self) -> None:
        """Clear tournament-related data from Streamlit session_state."""
        self.delete_players()
        self.delete_tournament_options()
        self.delete_game_session()
        self.delete_defaults()

from typing import Optional

import streamlit as st

from americano.game_session import GameSession
from americano.players import PlayerList
from frontend.utils.models.defaults import GameSessionDefaults
from frontend.utils.models.tournament_options import TournamentOptions


def update_players_state(players: PlayerList) -> None: 
    st.session_state["players"] = players.model_dump_json()

def get_players_from_state() -> PlayerList:
    if st.session_state.get("players") is None:
        st.session_state["players"] = PlayerList().model_dump_json()
    players = PlayerList.model_validate_json(st.session_state["players"])
    return players

# Game session state
def get_game_session_state() -> GameSession:
    if st.session_state.get("game_session") is None:
        return None
    return GameSession.model_validate_json(
        st.session_state.get("game_session")
    )

def update_game_session_state(game_session: GameSession) -> None:
    st.session_state["game_session"] = game_session.model_dump_json()

def delete_game_session_state() -> None:
    if st.session_state.get("game_session") is not None:
        del st.session_state["game_session"]

# Number of players in each court
def get_game_session_defaults() -> GameSessionDefaults:
    if st.session_state.get("game_session_defaults") is None:
        game_session_defaults = GameSessionDefaults().model_dump_json()
        st.session_state["game_session_defaults"] = game_session_defaults
    game_session_defaults = GameSessionDefaults.model_validate_json(
        st.session_state["game_session_defaults"]
    )
    return game_session_defaults

def update_game_session_defaults(game_session_defaults) -> None:
    st.session_state["game_session_defaults"] = game_session_defaults.model_dump_json()  # noqa E501

def get_tournament_options() -> Optional[TournamentOptions]:
    if st.session_state.get("tournament_options") is None:
        return None
    return TournamentOptions.model_validate_json(
        st.session_state["tournament_options"]
    )

def update_tournament_options(tournament_options: Optional[TournamentOptions]) -> None:  # noqa E501
    if tournament_options is None:
        del st.session_state["tournament_options"]
    else:
        st.session_state["tournament_options"] = tournament_options.model_dump_json()  # noqa E501

def end_tournament() -> None:
    if st.session_state.get("players") is not None:
        del st.session_state["players"]
    if st.session_state.get("tournament_options") is not None:
        del st.session_state["tournament_options"]
    if st.session_state.get("game_session") is not None:
        del st.session_state["game_session"]

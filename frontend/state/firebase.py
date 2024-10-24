from typing import Optional

import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

from americano.game_session import GameSession
from americano.players import PlayerList
from frontend.utils.models.defaults import GameSessionDefaults
from frontend.utils.models.tournament_options import TournamentOptions


class FirestoreState:
    def __init__(self, user_id: str):
        """Initialize with a unique user ID."""
        self.user_id = user_id  # Used to identify the user's data in Firestore

        # Initialize Firebase app
        if not firebase_admin._apps:
            # Retrieve the service account key JSON from Streamlit secrets
            firebase_config = st.secrets["firebase"]

            # Initialize the app with a service account, granting admin privileges  # noqa E501
            cred = credentials.Certificate(dict(firebase_config))
            firebase_admin.initialize_app(cred)

        # Get a reference to the Firestore service
        self.db = firestore.client()
        self.user_doc_ref = self.db.collection("default").document(self.user_id)
        self.data_ref = self.user_doc_ref.collection("data")

    # Players
    def set_players(self, players: PlayerList) -> None:
        """Set the players in Firestore."""
        data = players.model_dump()
        self._set_data('players', data)

    def get_players(self) -> PlayerList:
        """Get the players from Firestore."""
        data = self._get_data('players')
        if data is not None:
            return PlayerList.model_validate(data)
        else:
            return PlayerList()

    def delete_players(self) -> None:
        """Delete the players from Firestore."""
        self._delete_data('players')

    # Game Session
    def set_game_session(self, game_session: GameSession) -> None:
        """Set the game session in Firestore."""
        data = game_session.model_dump()
        self._set_data('game_session', data)

    def get_game_session(self) -> Optional[GameSession]:
        """Get the game session from Firestore."""
        data = self._get_data('game_session')
        if data is not None:
            return GameSession.model_validate(data)
        else:
            return None

    def delete_game_session(self) -> None:
        """Delete the game session from Firestore."""
        self._delete_data('game_session')

    # Defaults
    def set_defaults(self, defaults: GameSessionDefaults) -> None:
        """Set the game session defaults in Firestore."""
        data = defaults.model_dump()
        self._set_data('defaults', data)

    def get_defaults(self) -> GameSessionDefaults:
        """Get the game session defaults from Firestore."""
        data = self._get_data('defaults')
        if data is not None:
            return GameSessionDefaults.model_validate(data)
        else:
            return GameSessionDefaults()

    def delete_defaults(self) -> None:
        """Delete the defaults from Firestore."""
        self._delete_data('defaults')

    # Tournament Options
    def set_tournament_options(self, options: TournamentOptions) -> None:
        """Set the tournament options in Firestore."""
        data = options.model_dump()
        self._set_data('tournament_options', data)

    def get_tournament_options(self) -> Optional[TournamentOptions]:
        """Get the tournament options from Firestore."""
        data = self._get_data('tournament_options')
        if data is not None:
            return TournamentOptions.model_validate(data)
        else:
            return None

    def delete_tournament_options(self) -> None:
        """Delete the tournament options from Firestore."""
        self._delete_data('tournament_options')

    # End Tournament
    def end_tournament(self) -> None:
        """Clear tournament-related data from Firestore."""
        self.delete_players()
        self.delete_tournament_options()
        self.delete_game_session()
        self.delete_defaults()
    
    def restart_tournament(self) -> None:
        """Reset the scores and games played for all players."""
        players = self.get_players()
        for player in players.players:
            player.score = 0
            player.games_played = 0
        self.set_players(players)

    # Internal helper methods
    def _set_data(self, key: str, data: dict) -> None:
        """Set data in Firestore under the user's document."""
        doc_ref = self.data_ref.document(key)
        try:
            doc_ref.set(data)
        except Exception as e:
            st.error(f"Error setting {key}: {e}")

    def _get_data(self, key: str) -> Optional[dict]:
        """Get data from Firestore under the user's document."""
        doc_ref = self.data_ref.document(key)
        try:
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            st.error(f"Error getting {key}: {e}")
            return None

    def _delete_data(self, key: str) -> None:
        """Delete data from Firestore under the user's document."""
        doc_ref = self.data_ref.document(key)
        try:
            doc_ref.delete()
        except Exception as e:
            st.error(f"Error deleting {key}: {e}")
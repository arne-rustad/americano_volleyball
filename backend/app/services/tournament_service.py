"""Tournament management service."""

from fastapi import HTTPException

from app.database import supabase


class TournamentService:
    """Handles tournament-level operations."""

    @staticmethod
    async def reset_tournament(tournament_id: int) -> dict:
        """Reset a tournament by clearing scores and deleting game sessions.

        This will:
        1. Reset all player scores to 0
        2. Reset all player games_played to 0
        3. Delete all game sessions and related data
        4. Clear current_game_session_id from tournament

        Args:
            tournament_id: ID of the tournament to reset

        Returns:
            Success message dict with reset statistics

        Raises:
            HTTPException: If tournament not found
        """
        # Validate tournament exists
        tournament = TournamentService._get_tournament(tournament_id)

        # Get all players for stats
        players = TournamentService._get_all_players(tournament_id)
        player_count = len(players)

        # Reset all player scores and games_played to 0
        for player in players:
            supabase.table("players").update(
                {"score": 0, "games_played": 0}
            ).eq("id", player["id"]).execute()

        # Get all game sessions for this tournament
        game_sessions = TournamentService._get_all_game_sessions(
            tournament_id
        )
        session_count = len(game_sessions)

        # Clear tournament's current_game_session_id FIRST
        # (must do this before deleting sessions due to foreign key constraint)
        supabase.table("tournaments").update(
            {"current_game_session_id": None}
        ).eq("id", tournament_id).execute()

        # Delete all game sessions and related data
        for session in game_sessions:
            await TournamentService._delete_game_session_cascade(
                session["id"]
            )

        return {
            "message": "Tournament reset successfully",
            "tournament_id": tournament_id,
            "tournament_name": tournament["name"],
            "players_reset": player_count,
            "sessions_deleted": session_count,
        }

    # Helper methods

    @staticmethod
    def _get_tournament(tournament_id: int) -> dict:
        """Get tournament by ID."""
        tournament_response = (
            supabase.table("tournaments")
            .select("*")
            .eq("id", tournament_id)
            .execute()
        )
        if not tournament_response.data:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return tournament_response.data[0]

    @staticmethod
    def _get_all_players(tournament_id: int) -> list[dict]:
        """Get all players for a tournament (active and inactive)."""
        players_response = (
            supabase.table("players")
            .select("*")
            .eq("tournament_id", tournament_id)
            .execute()
        )
        return players_response.data or []

    @staticmethod
    def _get_all_game_sessions(tournament_id: int) -> list[dict]:
        """Get all game sessions for a tournament."""
        sessions_response = (
            supabase.table("game_sessions")
            .select("*")
            .eq("tournament_id", tournament_id)
            .execute()
        )
        return sessions_response.data or []

    @staticmethod
    async def _delete_game_session_cascade(session_id: int):
        """Delete a game session and all related data."""
        # Get all courts
        courts_response = (
            supabase.table("court_sessions")
            .select("*")
            .eq("game_session_id", session_id)
            .execute()
        )

        # Delete court_players for all courts
        for court in courts_response.data:
            supabase.table("court_players").delete().eq(
                "court_session_id", court["id"]
            ).execute()

        # Delete court_sessions
        supabase.table("court_sessions").delete().eq(
            "game_session_id", session_id
        ).execute()

        # Delete game_session
        supabase.table("game_sessions").delete().eq(
            "id", session_id
        ).execute()


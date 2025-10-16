"""Game session completion and scoring service."""

from fastapi import HTTPException

from app.database import supabase


class GameCompletionService:
    """Handles game session completion and score updates."""

    @staticmethod
    async def complete_session(session_id: int) -> dict:
        """Complete a game session and update all player scores.

        Args:
            session_id: ID of the game session to complete

        Returns:
            Completed game session dict

        Raises:
            HTTPException: If session not found, already completed,
                or missing scores
        """
        # Get game session
        session = GameCompletionService._get_session(session_id)

        # Check if already completed
        if session["status"] == "completed":
            raise HTTPException(
                status_code=400, detail="Game session already completed"
            )

        # Get all courts with players
        courts = GameCompletionService._get_courts_with_players(session_id)

        # Validate all courts have scores
        GameCompletionService._validate_all_scores_entered(courts)

        # Calculate score updates for each player
        player_score_updates, playing_player_ids = (
            GameCompletionService._calculate_player_score_updates(courts)
        )

        # Update player scores
        await GameCompletionService._update_player_scores(
            player_score_updates
        )

        # Award resting points to non-playing players
        if session["resting_points"] and session["resting_points"] > 0:
            await GameCompletionService._award_resting_points(
                session["tournament_id"],
                playing_player_ids,
                session["resting_points"],
            )

        # Mark session as complete
        completed_session = GameCompletionService._mark_session_complete(
            session_id
        )

        return completed_session

    # Helper methods

    @staticmethod
    def _get_session(session_id: int) -> dict:
        """Get game session by ID."""
        session_response = (
            supabase.table("game_sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        if not session_response.data:
            raise HTTPException(
                status_code=404, detail="Game session not found"
            )
        return session_response.data[0]

    @staticmethod
    def _get_courts_with_players(session_id: int) -> list[dict]:
        """Get all courts with their players."""
        courts_response = (
            supabase.table("court_sessions")
            .select("*, court_players(*)")
            .eq("game_session_id", session_id)
            .execute()
        )
        return courts_response.data

    @staticmethod
    def _validate_all_scores_entered(courts: list[dict]):
        """Validate that all courts have scores entered."""
        for court in courts:
            if (
                court["score_team_a"] is None
                or court["score_team_b"] is None
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Court {court['court_index']} is missing scores",
                )

    @staticmethod
    def _calculate_player_score_updates(
        courts: list[dict],
    ) -> tuple[dict, set]:
        """Calculate score updates for each player.

        Returns:
            Tuple of (player_score_updates dict, playing_player_ids set)
        """
        player_score_updates = {}
        playing_player_ids = set()

        for court in courts:
            for court_player in court["court_players"]:
                player_id = court_player["player_id"]
                playing_player_ids.add(player_id)

                if player_id not in player_score_updates:
                    player_score_updates[player_id] = {
                        "score_add": 0,
                        "games_add": 0,
                    }

                if court_player["team"] == "A":
                    player_score_updates[player_id]["score_add"] += court[
                        "score_team_a"
                    ]
                else:  # Team B
                    player_score_updates[player_id]["score_add"] += court[
                        "score_team_b"
                    ]

                player_score_updates[player_id]["games_add"] += 1

        return player_score_updates, playing_player_ids

    @staticmethod
    async def _update_player_scores(score_updates: dict):
        """Update player scores in database."""
        for player_id, updates in score_updates.items():
            # Get current player data
            player_response = (
                supabase.table("players")
                .select("*")
                .eq("id", player_id)
                .execute()
            )
            player = player_response.data[0]

            # Update with new scores
            supabase.table("players").update(
                {
                    "score": player["score"] + updates["score_add"],
                    "games_played": player["games_played"]
                    + updates["games_add"],
                }
            ).eq("id", player_id).execute()

    @staticmethod
    async def _award_resting_points(
        tournament_id: int, playing_player_ids: set, resting_points: float
    ):
        """Award resting points to non-playing players."""
        # Get all players in tournament
        all_players_response = (
            supabase.table("players")
            .select("*")
            .eq("tournament_id", tournament_id)
            .execute()
        )

        # Award resting points to non-playing players (active or inactive)
        for player in all_players_response.data:
            if player["id"] not in playing_player_ids:
                supabase.table("players").update(
                    {"score": player["score"] + resting_points}
                ).eq("id", player["id"]).execute()

    @staticmethod
    def _mark_session_complete(session_id: int) -> dict:
        """Mark session as completed in database."""
        completed_session_response = (
            supabase.table("game_sessions")
            .update({"status": "completed", "finished": True})
            .eq("id", session_id)
            .execute()
        )
        return completed_session_response.data[0]


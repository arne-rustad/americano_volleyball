"""Player swapping service for game sessions."""

from fastapi import HTTPException

from app.database import supabase
from app.schemas.game_session import PlayerSwapRequest


class PlayerSwapService:
    """Handles player position swaps in game sessions."""

    @staticmethod
    async def swap_players(
        session_id: int, swap_data: PlayerSwapRequest
    ) -> dict:
        """Swap two players in a game session.

        Handles three cases:
        1. Both players are playing - swap their positions
        2. One playing, one resting - substitute player
        3. Both resting - invalid, raises exception

        Args:
            session_id: ID of the game session
            swap_data: Player swap request with player IDs

        Returns:
            Success message dict

        Raises:
            HTTPException: If validation fails or invalid swap
        """
        # Get and validate session
        session = PlayerSwapService._get_session(session_id)

        # Check if session allows swaps
        courts = PlayerSwapService._get_courts(session_id)
        PlayerSwapService._validate_session_allows_swaps(session, courts)

        # Validate both players exist and are active
        PlayerSwapService._validate_players_exist_and_active(
            session["tournament_id"],
            swap_data.player1_id,
            swap_data.player2_id,
        )

        # Get player assignments in this game session
        court_session_ids = [court["id"] for court in courts]
        player1_assignment = PlayerSwapService._get_player_assignment(
            swap_data.player1_id, court_session_ids
        )
        player2_assignment = PlayerSwapService._get_player_assignment(
            swap_data.player2_id, court_session_ids
        )

        # Execute appropriate swap based on player states
        await PlayerSwapService._execute_swap(
            player1_assignment,
            player2_assignment,
            swap_data.player1_id,
            swap_data.player2_id,
        )

        return {"message": "Players swapped successfully"}

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
    def _get_courts(session_id: int) -> list[dict]:
        """Get all courts for a game session."""
        courts_response = (
            supabase.table("court_sessions")
            .select("*")
            .eq("game_session_id", session_id)
            .execute()
        )
        return courts_response.data

    @staticmethod
    def _validate_session_allows_swaps(session: dict, courts: list[dict]):
        """Validate session status and scores allow swaps."""
        if session["status"] == "completed":
            raise HTTPException(
                status_code=400,
                detail="Cannot swap players in completed game session",
            )

        has_scores = any(
            court["score_team_a"] is not None
            or court["score_team_b"] is not None
            for court in courts
        )

        if has_scores:
            raise HTTPException(
                status_code=400,
                detail="Cannot swap players after scores have been entered",
            )

    @staticmethod
    def _validate_players_exist_and_active(
        tournament_id: int, player1_id: int, player2_id: int
    ):
        """Validate both players exist in tournament and are active."""
        players_response = (
            supabase.table("players")
            .select("*")
            .eq("tournament_id", tournament_id)
            .in_("id", [player1_id, player2_id])
            .eq("is_active", True)
            .execute()
        )

        if len(players_response.data) != 2:
            raise HTTPException(
                status_code=404,
                detail="One or both players not found or not active in this tournament",
            )

    @staticmethod
    def _get_player_assignment(
        player_id: int, court_session_ids: list[int]
    ) -> dict | None:
        """Get player's court assignment if they're playing."""
        player_response = (
            supabase.table("court_players")
            .select("*")
            .eq("player_id", player_id)
            .in_("court_session_id", court_session_ids)
            .execute()
        )
        return player_response.data[0] if player_response.data else None

    @staticmethod
    async def _execute_swap(
        assignment1: dict | None,
        assignment2: dict | None,
        player1_id: int,
        player2_id: int,
    ):
        """Execute the appropriate swap based on player states."""
        # Case 1: Both players are playing - swap their positions
        if assignment1 and assignment2:
            await PlayerSwapService._swap_both_playing(
                assignment1, assignment2
            )

        # Case 2: Player 1 playing, Player 2 resting - swap them
        elif assignment1 and not assignment2:
            await PlayerSwapService._swap_playing_with_resting(
                assignment1, player2_id
            )

        # Case 3: Player 2 playing, Player 1 resting - swap them
        elif assignment2 and not assignment1:
            await PlayerSwapService._swap_playing_with_resting(
                assignment2, player1_id
            )

        # Case 4: Both players are resting - invalid
        else:
            raise HTTPException(
                status_code=400, detail="Cannot swap two resting players"
            )

    @staticmethod
    async def _swap_both_playing(assignment1: dict, assignment2: dict):
        """Swap two playing players' positions."""
        # Update player 1 to player 2's position
        supabase.table("court_players").update(
            {
                "court_session_id": assignment2["court_session_id"],
                "team": assignment2["team"],
            }
        ).eq("id", assignment1["id"]).execute()

        # Update player 2 to player 1's position
        supabase.table("court_players").update(
            {
                "court_session_id": assignment1["court_session_id"],
                "team": assignment1["team"],
            }
        ).eq("id", assignment2["id"]).execute()

    @staticmethod
    async def _swap_playing_with_resting(
        playing_assignment: dict, resting_player_id: int
    ):
        """Swap a playing player with a resting player."""
        # Create assignment for resting player (now playing)
        supabase.table("court_players").insert(
            {
                "court_session_id": playing_assignment["court_session_id"],
                "player_id": resting_player_id,
                "team": playing_assignment["team"],
            }
        ).execute()

        # Remove assignment for playing player (now resting)
        supabase.table("court_players").delete().eq(
            "id", playing_assignment["id"]
        ).execute()


"""Game session creation and management service."""

from fastapi import HTTPException

from americano.player_manager import PlayerManager
from americano.players import Player as AmericanoPlayer, PlayerList
from app.database import supabase
from app.schemas.game_session import CourtSessionResponse, GameSessionCreate


class GameSessionService:
    """Handles game session creation, retrieval, and deletion."""

    @staticmethod
    async def create_session(
        tournament_id: int, session_data: GameSessionCreate
    ) -> dict:
        """Create a new game session with player assignments.

        Args:
            tournament_id: ID of the tournament
            session_data: Game session configuration

        Returns:
            Created game session dict

        Raises:
            HTTPException: If tournament not found or not enough players
        """
        # Validate tournament exists
        tournament = GameSessionService._get_tournament(tournament_id)

        # Get active players
        active_players = GameSessionService._get_active_players(tournament_id)

        # Validate enough players
        total_players_needed = sum(
            config.n_players_each_team * 2
            for config in session_data.court_configs
        )
        if total_players_needed > len(active_players):
            raise HTTPException(
                status_code=400,
                detail=f"Not enough players. Need {total_players_needed}, "
                f"have {len(active_players)}",
            )

        # Create game session record
        game_session = GameSessionService._create_game_session_record(
            tournament_id, session_data
        )
        game_session_id = game_session["id"]

        # Draw players using PlayerManager
        drawn_players = GameSessionService._draw_players(
            active_players, total_players_needed, tournament["is_mix_tournament"]
        )

        # Create courts and assign players
        GameSessionService._create_courts_and_assign_players(
            game_session_id, session_data, drawn_players, tournament
        )

        # Update tournament's current game session
        supabase.table("tournaments").update(
            {"current_game_session_id": game_session_id}
        ).eq("id", tournament_id).execute()

        return game_session

    @staticmethod
    async def get_court_sessions(session_id: int) -> list[CourtSessionResponse]:
        """Get all courts in a game session with player assignments.

        Args:
            session_id: ID of the game session

        Returns:
            List of court session response objects
        """
        courts_response = (
            supabase.table("court_sessions")
            .select("*, court_players(*)")
            .eq("game_session_id", session_id)
            .order("court_index")
            .execute()
        )

        result = []
        for court in courts_response.data:
            team_a_players = [
                cp["player_id"]
                for cp in court["court_players"]
                if cp["team"] == "A"
            ]
            team_b_players = [
                cp["player_id"]
                for cp in court["court_players"]
                if cp["team"] == "B"
            ]

            court_data = CourtSessionResponse(
                id=court["id"],
                game_session_id=court["game_session_id"],
                court_index=court["court_index"],
                n_players_each_team=court["n_players_each_team"],
                score_team_a=court["score_team_a"],
                score_team_b=court["score_team_b"],
                team_a_players=team_a_players,
                team_b_players=team_b_players,
            )
            result.append(court_data)

        return result

    @staticmethod
    async def delete_session(session_id: int) -> dict:
        """Delete a pending game session with all related data.

        Args:
            session_id: ID of the game session to delete

        Returns:
            Success message dict

        Raises:
            HTTPException: If session not found, not pending, or has scores
        """
        # Get session and validate it exists
        session = GameSessionService._get_session(session_id)

        # Validate session is pending
        if session["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete game session with status "
                f"'{session['status']}'. Only pending sessions can be deleted.",
            )

        # Get courts and check for scores
        courts = GameSessionService._get_courts(session_id)
        if GameSessionService._has_any_scores(courts):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete game session with scores entered",
            )

        # Delete cascade: court_players -> court_sessions -> game_session
        for court in courts:
            supabase.table("court_players").delete().eq(
                "court_session_id", court["id"]
            ).execute()

        supabase.table("court_sessions").delete().eq(
            "game_session_id", session_id
        ).execute()

        supabase.table("game_sessions").delete().eq("id", session_id).execute()

        # Clear tournament's current_game_session_id if this was current
        GameSessionService._clear_tournament_current_session(
            session["tournament_id"], session_id
        )

        return {"message": "Game session deleted successfully"}

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
    def _get_active_players(tournament_id: int) -> list[dict]:
        """Get all active players for a tournament."""
        players_response = (
            supabase.table("players")
            .select("*")
            .eq("tournament_id", tournament_id)
            .eq("is_active", True)
            .execute()
        )
        if not players_response.data:
            raise HTTPException(
                status_code=400,
                detail="No active players available for this tournament",
            )
        return players_response.data

    @staticmethod
    def _create_game_session_record(
        tournament_id: int, session_data: GameSessionCreate
    ) -> dict:
        """Create game session database record."""
        game_session_response = (
            supabase.table("game_sessions")
            .insert(
                {
                    "tournament_id": tournament_id,
                    "n_courts": session_data.n_courts,
                    "n_game_points": session_data.n_game_points,
                    "resting_points": session_data.resting_points,
                    "status": "pending",
                }
            )
            .execute()
        )
        return game_session_response.data[0]

    @staticmethod
    def _draw_players(
        players_data: list[dict], n_players: int, is_mix: bool
    ) -> list[AmericanoPlayer]:
        """Draw players using PlayerManager."""
        americano_players = PlayerList(
            players=[
                AmericanoPlayer(
                    id=p["id"],
                    name=p["name"],
                    gender=p["gender"],
                    score=p["score"],
                    games_played=p["games_played"],
                )
                for p in players_data
            ]
        )

        player_manager = PlayerManager(player_list=americano_players)
        return player_manager.draw_players(n=n_players, mix_tournament=is_mix)

    @staticmethod
    def _create_courts_and_assign_players(
        game_session_id: int,
        session_data: GameSessionCreate,
        drawn_players: list[AmericanoPlayer],
        tournament: dict,
    ):
        """Create court sessions and assign players to teams."""
        player_idx = 0
        for court_idx, config in enumerate(session_data.court_configs):
            n_players = config.n_players_each_team

            # Create court session
            court_session_response = (
                supabase.table("court_sessions")
                .insert(
                    {
                        "game_session_id": game_session_id,
                        "court_index": court_idx,
                        "n_players_each_team": n_players,
                    }
                )
                .execute()
            )
            court_session_id = court_session_response.data[0]["id"]

            # Assign players to teams
            team_a, team_b = GameSessionService._assign_teams(
                drawn_players[player_idx : player_idx + 2 * n_players],
                n_players,
                tournament["is_mix_tournament"],
            )

            # Save team assignments
            court_player_inserts = []
            for player in team_a:
                court_player_inserts.append(
                    {
                        "court_session_id": court_session_id,
                        "player_id": player.id,
                        "team": "A",
                    }
                )
            for player in team_b:
                court_player_inserts.append(
                    {
                        "court_session_id": court_session_id,
                        "player_id": player.id,
                        "team": "B",
                    }
                )

            supabase.table("court_players").insert(
                court_player_inserts
            ).execute()

            player_idx += 2 * n_players

    @staticmethod
    def _assign_teams(
        court_players: list[AmericanoPlayer], n_players: int, is_mix: bool
    ) -> tuple[list[AmericanoPlayer], list[AmericanoPlayer]]:
        """Assign players to Team A and Team B."""
        if is_mix:
            # Mix tournament: group in sets of 4
            team_a = []
            team_b = []
            groups = []
            for i in range(len(court_players) // 4):
                groups.append(court_players[i * 4 : (i + 1) * 4])
            if len(court_players) % 4 > 0:
                groups.append(court_players[len(court_players) // 4 * 4 :])

            for group in groups:
                if len(group) == 4:
                    team_a.extend([group[0], group[3]])
                    team_b.extend([group[1], group[2]])
                elif len(group) == 2:
                    team_a.append(group[0])
                    team_b.append(group[1])
            return team_a, team_b
        else:
            # Regular tournament: alternate players
            return court_players[::2], court_players[1::2]

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
    def _has_any_scores(courts: list[dict]) -> bool:
        """Check if any court has scores entered."""
        return any(
            court["score_team_a"] is not None
            or court["score_team_b"] is not None
            for court in courts
        )

    @staticmethod
    def _clear_tournament_current_session(
        tournament_id: int, session_id: int
    ):
        """Clear tournament's current_game_session_id if it matches."""
        if tournament_id:
            tournament_response = (
                supabase.table("tournaments")
                .select("*")
                .eq("id", tournament_id)
                .single()
                .execute()
            )
            if (
                tournament_response.data
                and tournament_response.data.get("current_game_session_id")
                == session_id
            ):
                supabase.table("tournaments").update(
                    {"current_game_session_id": None}
                ).eq("id", tournament_id).execute()


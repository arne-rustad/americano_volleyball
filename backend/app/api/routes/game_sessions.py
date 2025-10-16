"""Game session API endpoints - Complex logic only."""

from fastapi import APIRouter, HTTPException

from americano.player_manager import PlayerManager
from americano.players import Player as AmericanoPlayer, PlayerList
from app.database import supabase
from app.schemas.game_session import (
    GameSessionCreate,
    GameSessionResponse,
    CourtSessionResponse,
)

router = APIRouter()


@router.post(
    "/tournaments/{tournament_id}/game-sessions",
    response_model=GameSessionResponse,
    status_code=201,
)
async def create_game_session(
    tournament_id: int,
    session_data: GameSessionCreate,
):
    """Create a new game session and draw players for courts.
    
    This endpoint uses the PlayerManager to intelligently draw players
    based on their scores, games played, and gender (for mix tournaments).
    """
    # Check tournament exists
    tournament_response = (
        supabase.table("tournaments")
        .select("*")
        .eq("id", tournament_id)
        .execute()
    )
    if not tournament_response.data:
        raise HTTPException(status_code=404, detail="Tournament not found")

    tournament = tournament_response.data[0]

    # Get all active players (inactive players are excluded from drawing)
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

    # Convert database players to Americano PlayerList
    americano_players = PlayerList(
        players=[
            AmericanoPlayer(
                id=p["id"],
                name=p["name"],
                gender=p["gender"],
                score=p["score"],
                games_played=p["games_played"],
            )
            for p in players_response.data
        ]
    )

    # Calculate total players needed
    total_players_needed = sum(
        config.n_players_each_team * 2
        for config in session_data.court_configs
    )

    if total_players_needed > len(americano_players.players):
        raise HTTPException(
            status_code=400,
            detail=f"Not enough players. Need {total_players_needed}, "
            f"have {len(americano_players.players)}",
        )

    # Create game session
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

    game_session = game_session_response.data[0]
    game_session_id = game_session["id"]

    # Use PlayerManager to draw players
    player_manager = PlayerManager(player_list=americano_players)
    drawn_players = player_manager.draw_players(
        n=total_players_needed,
        mix_tournament=tournament["is_mix_tournament"],
    )

    # Create court sessions with drawn players
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

        court_session = court_session_response.data[0]
        court_session_id = court_session["id"]

        # Assign players to teams
        # For mix tournament, use the mix assignment logic
        if tournament["is_mix_tournament"]:
            court_players = drawn_players[
                player_idx : player_idx + 2 * n_players
            ]
            team_a = []
            team_b = []

            # Group players in sets of 4 (or 2 if odd)
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
        else:
            # Regular tournament: alternate players
            court_players = drawn_players[
                player_idx : player_idx + 2 * n_players
            ]
            team_a = court_players[::2]  # Even indices
            team_b = court_players[1::2]  # Odd indices

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

        # Bulk insert court players
        supabase.table("court_players").insert(court_player_inserts).execute()

        player_idx += 2 * n_players

    # Update tournament's current game session
    supabase.table("tournaments").update(
        {"current_game_session_id": game_session_id}
    ).eq("id", tournament_id).execute()

    return GameSessionResponse(**game_session)


@router.get(
    "/game-sessions/{session_id}/courts",
    response_model=list[CourtSessionResponse],
)
async def get_court_sessions(session_id: int):
    """Get all courts in a game session with player assignments."""
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


@router.post(
    "/game-sessions/{session_id}/complete",
    response_model=GameSessionResponse,
)
async def complete_game_session(session_id: int):
    """Complete game session and update player scores.
    
    This endpoint:
    1. Validates all courts have scores
    2. Updates player scores atomically
    3. Awards resting points to non-playing players
    4. Marks session as complete
    """
    # Get game session
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

    session = session_response.data[0]

    if session["status"] == "completed":
        raise HTTPException(
            status_code=400, detail="Game session already completed"
        )

    # Get all courts with players
    courts_response = (
        supabase.table("court_sessions")
        .select("*, court_players(*)")
        .eq("game_session_id", session_id)
        .execute()
    )

    # Check all courts have scores
    for court in courts_response.data:
        if court["score_team_a"] is None or court["score_team_b"] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Court {court['court_index']} is missing scores",
            )

    # Collect score updates for each player
    player_score_updates = {}
    playing_player_ids = set()

    for court in courts_response.data:
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

    # Update player scores (use RPC for atomic updates)
    for player_id, updates in player_score_updates.items():
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

    # Handle resting players (all players who didn't play, including inactive)
    if session["resting_points"] and session["resting_points"] > 0:
        # Get all players in this tournament
        all_players_response = (
            supabase.table("players")
            .select("*")
            .eq("tournament_id", session["tournament_id"])
            .execute()
        )

        # Award resting points to all non-playing players (active or inactive)
        for player in all_players_response.data:
            if player["id"] not in playing_player_ids:
                supabase.table("players").update(
                    {"score": player["score"] + session["resting_points"]}
                ).eq("id", player["id"]).execute()

    # Mark session as complete
    completed_session_response = (
        supabase.table("game_sessions")
        .update({"status": "completed", "finished": True})
        .eq("id", session_id)
        .execute()
    )

    return GameSessionResponse(**completed_session_response.data[0])

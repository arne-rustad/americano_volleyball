"""Game session API endpoints - Thin route handlers."""

from fastapi import APIRouter

from app.schemas.game_session import (
    CourtSessionResponse,
    GameSessionCreate,
    GameSessionResponse,
    PlayerSwapRequest,
)
from app.services import (
    GameCompletionService,
    GameSessionAnalysisService,
    GameSessionService,
    PlayerSwapService,
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
    result = await GameSessionService.create_session(
        tournament_id, session_data
    )
    return GameSessionResponse(**result)


@router.get(
    "/game-sessions/{session_id}/courts",
    response_model=list[CourtSessionResponse],
)
async def get_court_sessions(session_id: int):
    """Get all courts in a game session with player assignments."""
    return await GameSessionService.get_court_sessions(session_id)


@router.get("/game-sessions/{session_id}/repetition-analysis")
async def get_repetition_analysis(session_id: int):
    """Analyze team and matchup repetitions for a game session.

    Compares this session against all completed sessions in the same
    tournament to identify repeated team combinations and matchups.
    """
    return await GameSessionAnalysisService.analyze_repetitions(session_id)


@router.post("/game-sessions/{session_id}/swap-players")
async def swap_players(session_id: int, swap_data: PlayerSwapRequest):
    """Swap two players in a game session.

    This allows manual adjustment of player assignments after session creation
    but before any scores are entered. Supports:
    - Swapping two playing players
    - Swapping a playing player with a resting player
    """
    return await PlayerSwapService.swap_players(session_id, swap_data)


@router.delete("/game-sessions/{session_id}")
async def delete_game_session(session_id: int):
    """Delete a pending game session.

    Only allows deletion of game sessions that haven't started yet
    (status = 'pending' and no scores entered).
    """
    return await GameSessionService.delete_session(session_id)


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
    result = await GameCompletionService.complete_session(session_id)
    return GameSessionResponse(**result)

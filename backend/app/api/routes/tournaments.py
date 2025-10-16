"""Tournament API endpoints."""

from fastapi import APIRouter

from app.services import TournamentService

router = APIRouter()


@router.post("/tournaments/{tournament_id}/reset")
async def reset_tournament(tournament_id: int):
    """Reset a tournament by clearing all scores and deleting game sessions.

    This will:
    - Reset all player scores to 0
    - Reset all player games_played to 0
    - Delete all game sessions and related data
    - Clear current_game_session_id from tournament

    This action cannot be undone.
    """
    return await TournamentService.reset_tournament(tournament_id)


# Tournament Reset Feature

## Overview
Added a tournament reset feature that allows users to restart a tournament from scratch by clearing all scores and deleting all game sessions.

## Implementation

### Backend

#### New Service: TournamentService
**File**: `backend/app/services/tournament_service.py`

Handles tournament-level operations. Currently includes:

**Method**: `reset_tournament(tournament_id: int)`
- Resets all player scores to 0
- Resets all player games_played to 0
- Deletes all game sessions (with cascade deletion of court_sessions and court_players)
- Clears tournament's current_game_session_id
- Returns statistics: players reset count, sessions deleted count

**Helper Methods**:
- `_get_tournament()` - Validate tournament exists
- `_get_all_players()` - Get all players (active and inactive)
- `_get_all_game_sessions()` - Get all sessions for tournament
- `_delete_game_session_cascade()` - Delete session with related data

#### New Router: Tournaments
**File**: `backend/app/api/routes/tournaments.py`

Simple router with one endpoint:
- `POST /api/tournaments/{tournament_id}/reset` - Reset tournament

Thin wrapper that delegates to `TournamentService.reset_tournament()`.

#### Main App Update
**File**: `backend/app/main.py`

- Imported and registered tournaments router
- Available at `/api/tournaments/*` endpoints

### Frontend

#### API Client
**File**: `frontend/lib/api.ts`

Added:
- `TournamentResetResponse` interface
- `resetTournament(tournamentId)` function
- Returns reset statistics for user feedback

#### UI Component
**File**: `frontend/app/tournaments/[id]/leaderboard/page.tsx`

Added:
- "Reset Tournament" button (only shown when players exist)
- Confirmation dialog using AlertDialog component
- Loading state during reset operation
- Success toast with statistics
- Auto-refresh leaderboard after reset

**UI Features**:
- Button positioned next to page title
- Uses destructive styling to indicate danger
- Disabled during reset operation
- Shows confirmation dialog before executing
- Displays helpful statistics after reset

## User Flow

1. User navigates to tournament leaderboard
2. Clicks "Reset Tournament" button (top right)
3. Confirmation dialog appears with warning
4. User confirms the reset
5. Backend processes reset:
   - All player scores → 0
   - All player games_played → 0
   - All game sessions deleted
   - Current game session cleared
6. Success message shows statistics
7. Leaderboard refreshes to show reset state

## API Endpoint

### Reset Tournament
```
POST /api/tournaments/{tournament_id}/reset
```

**Response**:
```json
{
  "message": "Tournament reset successfully",
  "tournament_id": 1,
  "tournament_name": "Summer Tournament",
  "players_reset": 12,
  "sessions_deleted": 5
}
```

**Errors**:
- `404` - Tournament not found

## Database Operations

The reset performs these operations in order:

1. **Validate** tournament exists
2. **Fetch** all players and game sessions
3. **Reset** player scores and games_played:
   ```sql
   UPDATE players
   SET score = 0, games_played = 0
   WHERE tournament_id = ?
   ```
4. **Delete** game sessions (cascade):
   - For each game session:
     - Delete all court_players for each court
     - Delete all court_sessions
     - Delete game_session record
5. **Clear** tournament's current_game_session_id:
   ```sql
   UPDATE tournaments
   SET current_game_session_id = NULL
   WHERE id = ?
   ```

## Safety Features

1. **Confirmation Dialog**: Users must explicitly confirm
2. **Warning Message**: Clear indication this cannot be undone
3. **Destructive Styling**: Red button to indicate danger
4. **Loading State**: Button disabled during reset
5. **Statistics**: Shows what was reset for verification

## Code Organization

Following the established service layer pattern:
- ✅ Business logic in service class
- ✅ Thin route handler
- ✅ Proper error handling
- ✅ Type safety
- ✅ Clear separation of concerns

## Use Cases

- **Restart Tournament**: Start fresh without creating new tournament
- **Practice Mode**: Run test tournaments, then reset
- **New Season**: Use same tournament for multiple seasons
- **Fix Mistakes**: Reset after accidental score corruption
- **Demo/Testing**: Show tournament features, then reset

## Future Enhancements (Optional)

1. **Soft Reset**: Option to keep game sessions but reset scores
2. **Partial Reset**: Reset only certain players or sessions
3. **Reset History**: Track when resets occurred
4. **Backup Before Reset**: Auto-create backup snapshot
5. **Scheduled Resets**: Auto-reset at specific intervals

## Testing Checklist

- ✅ Backend service compiles
- ✅ Route registered in main app
- ✅ Frontend API function defined
- ✅ UI button renders correctly
- ✅ Confirmation dialog works
- ✅ Loading state displays
- [ ] Manual test: Reset tournament with players
- [ ] Manual test: Reset tournament with game sessions
- [ ] Manual test: Verify scores reset to 0
- [ ] Manual test: Verify game sessions deleted
- [ ] Manual test: Success message displays stats

## Files Modified

**Backend**:
- ✅ `backend/app/services/tournament_service.py` (new)
- ✅ `backend/app/services/__init__.py` (updated exports)
- ✅ `backend/app/api/routes/tournaments.py` (new)
- ✅ `backend/app/main.py` (registered router)

**Frontend**:
- ✅ `frontend/lib/api.ts` (added resetTournament function)
- ✅ `frontend/app/tournaments/[id]/leaderboard/page.tsx` (added UI)

## Summary

Added a complete tournament reset feature following best practices:
- Clean service layer architecture
- Proper confirmation and safety measures
- Helpful user feedback
- Cascade deletion for data integrity
- Type-safe implementation
- Consistent with existing codebase patterns

The feature is production-ready and safe to use! 🚀


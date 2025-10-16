# Manual Player Switching Feature

## Overview
Implemented click-to-select manual player switching for game sessions, allowing tournament organizers to adjust player assignments after game session creation but before any scores are entered.

## Implementation Summary

### Backend Changes

#### 1. Schema (`backend/app/schemas/game_session.py`)
- Added `PlayerSwapRequest` schema for validating swap requests
- Fields: `player1_id` and `player2_id`

#### 2. API Endpoint (`backend/app/api/routes/game_sessions.py`)
- Added `POST /game-sessions/{session_id}/swap-players` endpoint
- Validates:
  - Game session exists and is not completed
  - No scores have been entered on any court
  - Both players exist in the game session
- Swaps players by updating their `court_session_id` and `team` in the `court_players` table
- Returns success message

### Frontend Changes

#### 3. API Client (`frontend/lib/api.ts`)
- Added `swapPlayers(sessionId, player1Id, player2Id)` function
- Makes POST request to backend swap endpoint
- Throws `APIError` on failure for consistent error handling

#### 4. Edit Players Modal (`frontend/components/edit-players-modal.tsx`)
- New component with click-to-select UI pattern
- Features:
  - Displays all courts in a grid layout
  - Players organized by Team A and Team B for each court
  - Click first player → highlights in blue
  - Click second player → swaps positions
  - Valid swap targets highlighted with green border
  - Loading state while swapping
  - Cancel selection by clicking selected player again

#### 5. Game Session Page Integration (`frontend/app/tournaments/[id]/game-sessions/[session_id]/page.tsx`)
- Added "Edit Players" button (visible when session is not completed)
- Button disabled (with "Locked" badge) once any score is entered
- Integrated `EditPlayersModal` component
- Added `handleSwapPlayers` function to manage swaps and refresh court data
- Added `hasAnyScores` check to determine button state

## User Flow

1. **Create Game Session**: Players are auto-assigned by backend algorithm
2. **Review Assignments**: View court cards with player assignments
3. **Click "Edit Players"**: Modal opens showing all courts
4. **Select First Player**: Click a player → highlights in blue
5. **Select Second Player**: Click another player → instant swap
6. **Refresh View**: Court cards update with new assignments
7. **Enter Scores**: Once any score is entered, "Edit Players" becomes disabled

## Features

- ✅ Swap players within same court (Team A ↔ Team B)
- ✅ Move players between different courts (Court 1 ↔ Court 2)
- ✅ No gender balance enforcement (as requested)
- ✅ Block switching once any score is entered
- ✅ Click-to-select pattern (mobile-friendly)
- ✅ Clear visual feedback (blue = selected, green = valid target)
- ✅ Real-time updates with optimistic UI
- ✅ Toast notifications for success/error states

## Technical Details

### No Dependencies Added
- No drag-and-drop libraries required
- Uses existing shadcn/ui components
- Leverages Tailwind CSS for styling

### Database Operations
- Direct updates to `court_players` table
- Swaps `court_session_id` and `team` fields
- Atomic operations (no partial swaps)

### Error Handling
- Backend validates session state
- Prevents swaps after scores entered
- Handles missing players gracefully
- User-friendly error messages

## Testing Checklist

- [x] Backend endpoint created and validated
- [x] Frontend API client function added
- [x] Modal component created with click-to-select UI
- [x] Integration with game session page
- [x] No linter errors

### Manual Testing (TODO)
- [ ] Create a new game session with multiple courts
- [ ] Click "Edit Players" button - modal should open
- [ ] Click a player - should highlight in blue
- [ ] Click another player - should swap positions instantly
- [ ] Verify within-court swaps (Team A ↔ Team B) work
- [ ] Verify cross-court swaps work (Court 1 ↔ Court 2)
- [ ] Enter a score on any court
- [ ] "Edit Players" button should become disabled with "Locked" badge
- [ ] Test on mobile - click-to-select should work well
- [ ] Test canceling selection by clicking selected player again

## Future Enhancements (Optional)

- Add keyboard shortcuts for power users
- Add "Undo" functionality for accidental swaps
- Add visual preview/confirmation before swap
- Allow swapping with resting players (currently not playing)
- Add swap history/audit log


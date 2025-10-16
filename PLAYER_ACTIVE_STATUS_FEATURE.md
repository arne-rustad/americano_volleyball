# Player Active/Inactive Status Feature

## Overview

Players can now be marked as **active** or **inactive**. Inactive players will not be drawn for new game sessions and will not receive resting points.

## Use Cases

- Player is injured and needs to sit out
- Player needs a break but wants to stay in the tournament
- Temporary absence (bathroom, phone call, etc.)
- Managing player rotation

## Implementation Details

### Database

**Migration**: `add_is_active_to_players`

Added `is_active` column to `players` table:
- Type: `BOOLEAN`
- Default: `true`
- NOT NULL

All existing players were automatically set to active.

### Backend Changes

**File**: `backend/app/api/routes/game_sessions.py`

1. **Player Drawing** (Line 43-55):
   - Only active players are fetched when creating game sessions
   - Query includes `.eq("is_active", True)`
   - Error message updated to "No active players available"

2. **Resting Points** (Line 330-346):
   - **All players** who didn't play receive resting points (including inactive)
   - Inactive players are still part of the tournament
   - They just can't be drawn for new games

### Frontend Changes

**File**: `frontend/app/tournaments/[id]/players/page.tsx`

1. **Status Column**:
   - New "Status" column in the players table
   - Shows active/inactive status with icons
   - Active: Green button with ✓ icon
   - Inactive: Outline button with ✗ icon

2. **Toggle Function**:
   - Click status button to toggle between active/inactive
   - Toast notification confirms the change
   - Realtime update via Supabase subscription

3. **Visual Feedback**:
   - Inactive players shown with 60% opacity
   - Clear visual distinction in the table

4. **Icons Used**:
   - `UserCheck`: Active player
   - `UserX`: Inactive player

### TypeScript Types

Updated `frontend/lib/database.types.ts`:
- `players.Row.is_active: boolean`
- `players.Insert.is_active?: boolean` (optional, defaults to true)
- `players.Update.is_active?: boolean` (optional)

## User Experience

### Activating/Deactivating a Player

1. Go to tournament → Players tab
2. Find the player in the table
3. Click their status button (Active/Inactive)
4. Status toggles immediately with confirmation toast

### What Happens When Inactive

**During Game Session Creation**:
- Inactive players are excluded from player drawing
- Will not be assigned to any court
- Game session can still be created if enough active players exist

**During Game Session Completion**:
- Inactive players **DO** receive resting points (they're still in the tournament)
- Their score increases by resting points if they didn't play
- Their games_played stat remains unchanged
- They stay competitive even while inactive

### Visual Indicators

- **Active players**: Full opacity, green "Active" button
- **Inactive players**: 60% opacity, gray "Inactive" button

## Testing

### Manual Test Steps

1. ✅ Create a tournament with several players
2. ✅ Mark one player as inactive
3. ✅ Verify inactive player appears grayed out
4. ✅ Start a new game session
5. ✅ Verify inactive player is not drawn
6. ✅ Complete the game session with resting points
7. ✅ Verify inactive player DID receive resting points
8. ✅ Reactivate the player
9. ✅ Verify player appears normal again
10. ✅ Start another game session
11. ✅ Verify reactivated player can be drawn

### Edge Cases Handled

- ✅ All players inactive → Error: "No active players available"
- ✅ Not enough active players → Error with count mismatch
- ✅ Player becomes inactive mid-tournament → Stats preserved
- ✅ Realtime updates → Status changes propagate immediately

## Design Decisions

### Why `is_active` instead of `is_benched`?

- **Positive framing**: Default state is `true` (active)
- **Clear semantics**: Active means "can play", inactive means "can't play"
- **Professional terminology**: Works in any sports context
- **Simple boolean**: Easy to reason about and query

### Why DO inactive players get resting points?

- **Still in tournament**: Inactive doesn't mean "removed" - they're just not playing
- **Fairness**: Prevents them from falling behind while injured/absent
- **Temporary status**: Makes it easier to return to play without big score gap
- **Player retention**: Encourages players to stay in tournament even during breaks

### Why allow toggling vs permanent state?

- **Flexibility**: Players might return from injury, bathroom break, etc.
- **No deletion needed**: Don't have to remove/re-add players
- **History preserved**: Stats remain even when inactive
- **Easy recovery**: One click to rejoin the tournament

## Future Enhancements (Not Implemented)

- [ ] Add "reason" field for inactive status (injured, absent, etc.)
- [ ] Show inactive count in player summary
- [ ] Filter to show only active/inactive players
- [ ] Warn when creating game with few active players
- [ ] History log of status changes
- [ ] Bulk activate/deactivate players

## Files Modified

### Database
- New migration: `supabase/migrations/..._add_is_active_to_players.sql`

### Backend
- `backend/app/api/routes/game_sessions.py` (2 changes)

### Frontend
- `frontend/lib/database.types.ts` (TypeScript types updated)
- `frontend/app/tournaments/[id]/players/page.tsx` (status column, toggle function)

## Summary

This feature provides flexible player management without requiring deletion or re-creation of player records. It maintains tournament integrity by excluding inactive players from game drawing while **still awarding them resting points** to keep them competitive. This allows players to take breaks without falling behind, encouraging retention and smooth re-entry when they return to active status.

**Result**: Clean, intuitive UX with robust backend validation! 🎉


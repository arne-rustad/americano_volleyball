# Swap with Resting Players Feature

## Overview
Extended the manual player switching feature to allow swapping playing players with active resting players (on the bench). This gives tournament organizers complete flexibility to substitute players during a game session before any scores are entered.

## Implementation Summary

### Backend Changes

#### 1. Enhanced Swap Logic (`backend/app/api/routes/game_sessions.py`)
Updated the `/game-sessions/{session_id}/swap-players` endpoint to handle three cases:

**Case 1: Both players are playing** (original behavior)
- Swaps their court assignments and teams
- Updates both `court_players` records

**Case 2: One playing, one resting** (new)
- Creates a new `court_players` record for the resting player
- Assigns them to the playing player's court and team
- Deletes the playing player's `court_players` record

**Case 3: Both players are resting** (invalid)
- Returns 400 error - cannot swap two resting players

**Additional Validations:**
- Verifies both players exist in the tournament
- Checks both players are active (`is_active = true`)
- Maintains all existing score and status checks

### Frontend Changes

#### 2. Edit Players Modal (`frontend/components/edit-players-modal.tsx`)
Enhanced to show and interact with resting players:

**New Props:**
- `restingPlayers`: Array of active players not currently playing

**New State:**
- `selectedRestingPlayer`: Tracks selected resting player

**New Handlers:**
- `handleRestingPlayerClick`: Handles clicking on resting players
- Enhanced `handlePlayerClick`: Clears resting selection when clicking playing players

**UI Additions:**
- "Resting Players (On Bench)" section below court cards
- Grid layout showing all active resting players
- Same click-to-select pattern with visual feedback
- Updated description text explaining both swap types

**Visual Feedback:**
- Blue highlight for selected player (playing or resting)
- Green border for valid swap targets
- Clear status message showing selection type

#### 3. Game Session Page (`frontend/app/tournaments/[id]/game-sessions/[session_id]/page.tsx`)
Added functionality to fetch and manage resting players:

**New State:**
- `restingPlayers`: Array of active players not in the game session

**New Function:**
- `fetchRestingPlayers()`: Fetches active players and filters out those currently playing

**Updated Functions:**
- `handleSwapPlayers`: Now refreshes both court sessions and resting players list after swap

**Data Flow:**
- Fetches all active players in tournament
- Fetches all playing player IDs from court sessions
- Filters to get resting players (active but not playing)
- Passes resting players to modal

## User Flow

### Swap Playing with Playing (existing)
1. Click a playing player → highlights blue
2. Click another playing player → instant swap

### Swap Playing with Resting (new)
1. Click a playing player → highlights blue
2. Click a resting player → instant swap (playing player moves to bench, resting player takes their spot)

### Select from Bench
1. Click a resting player → highlights blue
2. Click a playing player → instant swap

### Cancel Selection
- Click selected player again → deselects

## Features

- ✅ Swap playing player with resting player
- ✅ Only show active resting players
- ✅ Same click-to-select pattern for consistency
- ✅ Clear visual feedback for both player types
- ✅ Prevent swapping two resting players
- ✅ Real-time updates of both playing and resting lists
- ✅ Maintains all existing validations and safeguards
- ✅ Mobile-friendly grid layout for resting players

## Technical Details

### Database Operations
**Playing to Resting:**
- DELETE from `court_players` WHERE id = playing_player_assignment_id

**Resting to Playing:**
- INSERT into `court_players` (court_session_id, player_id, team)

**Both Playing:**
- UPDATE `court_players` (swap court_session_id and team)

### Validation Chain
1. Game session must exist
2. Session must be pending (not completed)
3. No scores entered on any court
4. Both players must exist in tournament
5. Both players must be active
6. At least one player must be playing (can't swap two resting)

### Performance
- Resting players fetched on modal open
- Minimal queries (2 selects + filtering in JS)
- Real-time refresh after swaps

## Example Scenarios

### Scenario 1: Injured Player
- Player 5 playing on Court 2, Team A
- Gets injured before game starts
- Click Player 5, click Player 12 (resting)
- Player 12 now on Court 2, Team A; Player 5 on bench

### Scenario 2: Balance Teams
- Courts assigned, but one court looks unbalanced
- Swap a strong player with a resting player
- Swap another player to rebalance

### Scenario 3: Late Arrival
- Player assigned to court but running late
- Swap them with another resting player
- When they arrive, swap back if needed

## Testing Checklist

- [x] Backend endpoint updated to handle three cases
- [x] Frontend modal shows resting players
- [x] Frontend fetches and filters resting players correctly
- [x] No linter errors

### Manual Testing (TODO)
- [ ] Create game session with 8 active players, 2 courts (4 playing, 4 resting)
- [ ] Open Edit Players modal - verify 4 resting players shown
- [ ] Swap a playing player with a resting player - both ways
- [ ] Verify lists update correctly after swap
- [ ] Verify cannot swap two resting players
- [ ] Verify inactive players don't appear in resting list
- [ ] Test on mobile - resting players grid should be responsive

## Future Enhancements (Optional)

- Show player stats (score, games played) in resting players list
- Add filter/search for resting players
- Show visual indicator if player was recently swapped
- Add "Quick Swap" button to automatically rotate resting players
- Add keyboard shortcuts for power users


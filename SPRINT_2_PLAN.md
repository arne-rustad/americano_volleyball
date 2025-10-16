# Sprint 2: Game Sessions

## Goal
Build the core game session functionality - create games, draw players into courts, input scores, and complete games with automatic score updates.

## Architecture
- **Frontend**: Next.js pages for game session UI
- **Backend**: FastAPI endpoints for complex logic (player drawing, score calculation)
- **Supabase**: Direct reads for display, backend handles writes

## Pages to Build

### 1. Game Sessions Tab
**File**: `frontend/app/tournaments/[id]/game-sessions/page.tsx`

Features:
- Add "Game Sessions" tab to tournament navigation
- Show list of all game sessions for tournament:
  - Status badge (Pending/In Progress/Completed)
  - Number of courts
  - Created date
  - Completed date (if finished)
  - Click → view/continue game session
- "Start New Game" button → `/tournaments/[id]/game-sessions/new`
- Empty state when no sessions

### 2. Start New Game Page
**File**: `frontend/app/tournaments/[id]/game-sessions/new/page.tsx`

Form to configure new game session:
- Number of courts (dropdown: 1-10)
- Points per game (input, default: 15)
- Resting points (input, default: 0, optional)
- Submit button → POST to backend API

**Backend Integration**:
```typescript
POST /api/tournaments/{tournament_id}/game-sessions
Body: {
  n_courts: number,
  n_game_points: number,
  resting_points?: number
}
Response: {
  game_session_id: number,
  court_sessions: [...court assignments with players...]
}
```

Success → Redirect to `/tournaments/[id]/game-sessions/[session_id]`

### 3. Active Game Session Page
**File**: `frontend/app/tournaments/[id]/game-sessions/[session_id]/page.tsx`

Features:
- Display all courts in a grid (responsive)
- Each court card shows:
  - Court number
  - Team A players (with names)
  - Team B players (with names)
  - Score inputs for Team A and Team B
  - Inline validation (scores must be numbers)
- "Complete Game Session" button (enabled when all scores entered)
- Back button to game sessions list

**Data**:
- Fetch court sessions: `supabase.from('court_sessions').select('*, court_players(*, players(*))').eq('game_session_id', sessionId)`
- Update scores: Direct Supabase update on court_sessions
- Complete game: POST to backend API

**Backend Integration**:
```typescript
POST /api/game-sessions/{session_id}/complete
Response: {
  updated_players: [...players with new scores...]
}
```

Success → Show toast, redirect to leaderboard with updated scores

## Components to Build

### CourtCard Component
**File**: `frontend/components/court-card.tsx`

Reusable card for displaying a single court:
- Court number header
- Team A section with player names
- Team B section with player names
- Score inputs (2 number inputs)
- Optional: Visual divider between teams

### GameSessionCard Component
**File**: `frontend/components/game-session-card.tsx`

Card for displaying a game session in the list:
- Status badge
- Session details
- Click handler

## Updates to Existing Components

### TournamentTabs
Add "Game Sessions" tab between "Players" and "Leaderboard"

## Backend Endpoints Already Built ✅

These are already implemented and tested:
1. `POST /api/tournaments/{tournament_id}/game-sessions` - Create session with player drawing
2. `POST /api/game-sessions/{session_id}/complete` - Complete session and update scores

## Implementation Steps

1. **Add Game Sessions tab** to tournament navigation
2. **Build Game Sessions list page** with empty state
3. **Build Start New Game form page**
4. **Build Active Game Session page** with court cards
5. **Build CourtCard component** for score input
6. **Test full flow**: Create → View → Input scores → Complete → Verify leaderboard updates

## Testing Checklist

- [ ] Can navigate to Game Sessions tab
- [ ] Empty state shows when no game sessions
- [ ] Can start a new game session with valid configuration
- [ ] Backend draws players correctly (uses PlayerManager logic)
- [ ] Court assignments display with correct teams
- [ ] Can input scores for all courts
- [ ] Validation prevents invalid scores
- [ ] Can complete game session
- [ ] Player scores update correctly after completion
- [ ] Leaderboard reflects new scores
- [ ] Can view past completed game sessions
- [ ] Status badges show correct states

## Files to Create

**Pages**:
- `frontend/app/tournaments/[id]/game-sessions/page.tsx`
- `frontend/app/tournaments/[id]/game-sessions/new/page.tsx`
- `frontend/app/tournaments/[id]/game-sessions/[session_id]/page.tsx`

**Components**:
- `frontend/components/court-card.tsx`
- `frontend/components/game-session-card.tsx`

**Updates**:
- `frontend/components/tournament-tabs.tsx` (add Game Sessions tab)

## Technical Notes

### Player Drawing Logic (Already in Backend)
The backend uses `americano.player_manager.draw_players()` which:
- Sorts players by score (lowest first)
- Balances games played
- Handles mix tournaments (ensures gender balance on courts)
- Manages odd numbers of players (creates resting)

### Score Update Logic (Already in Backend)
The backend calculates new scores based on:
- Point differential per game
- Resting points (if applicable)
- Updates all player records in one transaction

### State Management
- Game session status: `pending` → `in_progress` → `completed`
- Court sessions store scores (nullable until entered)
- Frontend validates all scores entered before allowing completion

## Out of Scope (Later Sprints)

- Real-time updates during active games (Sprint 3)
- Edit scores after completion (Sprint 3)
- Delete game sessions (Sprint 3)
- Advanced statistics (Sprint 4)

---

**This sprint brings the core tournament functionality to life!**


# Delete Pending Game Sessions Feature

## Overview
Implemented functionality to delete game sessions that are in "pending" status (not yet started or completed). This allows tournament organizers to remove game sessions that were created by mistake or need to be recreated.

## Implementation Summary

### Backend Changes

#### 1. API Endpoint (`backend/app/api/routes/game_sessions.py`)
- Added `DELETE /game-sessions/{session_id}` endpoint
- Validates:
  - Game session exists
  - Session status is "pending"
  - No scores have been entered (extra safety check)
- Deletion process:
  1. Deletes all `court_players` records for courts in the session
  2. Deletes all `court_sessions` records
  3. Deletes the `game_sessions` record
  4. Clears `current_game_session_id` from tournament if this was the current session
- Returns success message

### Frontend Changes

#### 2. API Client (`frontend/lib/api.ts`)
- Added `deleteGameSession(sessionId)` function
- Makes DELETE request to backend endpoint
- Throws `APIError` on failure for consistent error handling

#### 3. Game Session Page (`frontend/app/tournaments/[id]/game-sessions/[session_id]/page.tsx`)
- Added "Delete Session" button in header (visible only for pending sessions)
- Button styled with destructive variant (red)
- Added confirmation dialog using shadcn/ui `AlertDialog`
- Added `handleDeleteSession` function to manage deletion
- Redirects to game sessions list after successful deletion
- Shows loading state during deletion

#### 4. UI Components
- Added shadcn/ui `alert-dialog` component for confirmation dialog

## User Flow

1. **View Pending Session**: Navigate to a game session with "pending" status
2. **Click Delete**: Click the red "Delete Session" button in the header
3. **Confirm**: Confirmation dialog appears asking to confirm deletion
4. **Delete**: Click "Delete" button to confirm
5. **Redirect**: Automatically redirected to game sessions list with success message

## Features

- ✅ Delete button only visible for pending sessions
- ✅ Additional safety check: button hidden if any scores entered
- ✅ Confirmation dialog prevents accidental deletion
- ✅ Cascading deletion of related records (court_players, court_sessions)
- ✅ Clears tournament's current_game_session_id if needed
- ✅ Loading state during deletion
- ✅ Toast notifications for success/error states
- ✅ Proper error handling and user feedback

## Safety Features

### Backend Validation
1. **Status Check**: Only "pending" sessions can be deleted
2. **Score Check**: Double-checks that no scores have been entered
3. **Existence Check**: Validates session exists before attempting deletion
4. **Error Messages**: Clear error messages for all failure cases

### Frontend UX
1. **Conditional Display**: Button only shown when appropriate
2. **Confirmation Dialog**: Requires explicit confirmation
3. **Cannot Undo Warning**: Clear message that action is permanent
4. **Disabled During Action**: Prevents double-clicks
5. **Loading State**: Visual feedback during deletion

## Database Cleanup

The endpoint properly cleans up all related data:
```
court_players → deleted for all courts in session
court_sessions → deleted for session
game_sessions → deleted
tournaments.current_game_session_id → cleared if applicable
```

## Testing Checklist

- [x] Backend endpoint created and validated
- [x] Frontend API client function added
- [x] Delete button added to UI
- [x] Confirmation dialog implemented
- [x] No linter errors
- [x] shadcn/ui alert-dialog component added

### Manual Testing (TODO)
- [ ] Create a new game session (status = pending)
- [ ] Verify "Delete Session" button appears in header
- [ ] Click "Delete Session" - confirmation dialog should appear
- [ ] Click "Cancel" - dialog closes, session still exists
- [ ] Click "Delete Session" again, then "Delete" - session should be deleted
- [ ] Verify redirect to game sessions list
- [ ] Verify session no longer appears in list
- [ ] Try to delete a completed session - should not show delete button
- [ ] Try to delete a session with scores - should not show delete button (or backend should reject)

## Future Enhancements (Optional)

- Add "Undo" functionality (soft delete with restore option)
- Add delete option on game sessions list page (bulk actions)
- Add audit log for deleted sessions
- Add confirmation with session details in dialog
- Add keyboard shortcut for deletion (with confirmation)


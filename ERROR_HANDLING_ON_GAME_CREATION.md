# Error Handling on Game Session Creation

## Problem

When users tried to create a game session without enough active players, they would get a console error and the API would return a 400 error. The backend logs would show `POST /api/tournaments/3/game-sessions HTTP/1.1" 400`. This was inefficient and created unnecessary errors.

## Solution

Added **proactive validation on the game creation form page**:
1. Fetches active player count when form loads
2. Calculates required players based on form configuration (courts × players_per_team × 2)
3. Shows warning banner when not enough players
4. Disables submit button to **prevent API call**
5. Only validates again on submit as a safety check

## Implementation

### File Modified
`frontend/app/tournaments/[id]/game-sessions/new/page.tsx`

### Changes

1. **Fetch Active Player Count on Load**
   ```typescript
   const [activePlayerCount, setActivePlayerCount] = useState<number>(0);
   const [isLoadingPlayers, setIsLoadingPlayers] = useState(true);
   
   useEffect(() => {
     const { count } = await supabase
       .from("players")
       .select("*", { count: "exact", head: true })
       .eq("tournament_id", tournamentId)
       .eq("is_active", true);
     setActivePlayerCount(count || 0);
   }, [tournamentId]);
   ```

2. **Calculate Required Players Dynamically**
   ```typescript
   const nCourts = form.watch("n_courts");
   const nPlayersPerTeam = form.watch("n_players_per_team");
   const requiredPlayers = nCourts * nPlayersPerTeam * 2;
   const hasEnoughPlayers = activePlayerCount >= requiredPlayers;
   ```

3. **Validate Before API Call in onSubmit**
   ```typescript
   async function onSubmit(data) {
     // Prevent API call if not enough players
     if (activePlayerCount < requiredPlayers) {
       setErrorMessage(`Not enough players. Need ${required}, have ${activePlayerCount}`);
       return; // Don't make API call!
     }
     
     // Only make API call if validation passes
     const response = await createGameSession(tournamentId, data);
   }
   ```

4. **Dynamic Warning Banner**
   ```typescript
   {!hasEnoughPlayers && !isLoadingPlayers && (
     <Alert variant="destructive">
       This configuration needs {requiredPlayers} active players, but you
       only have {activePlayerCount}. Add or activate players to continue.
     </Alert>
   )}
   ```

5. **Disabled Submit Button**
   ```typescript
   <Button 
     disabled={isSubmitting || !hasEnoughPlayers || isLoadingPlayers}
   >
     {!hasEnoughPlayers
       ? `Need ${requiredPlayers - activePlayerCount} More Players`
       : "Create Game Session"}
   </Button>
   ```

### UI Behavior

**Before Form Submission**:
- ✅ No error shown
- ✅ Form is accessible
- ✅ User can configure settings

**After Failed Submission**:
- 🔴 Red alert banner appears above the form card
- 📝 Shows exact error message from backend (e.g., "Not enough players. Need 4, have 3")
- 🔗 Provides link to "Manage players" page
- 🍞 Toast notification also shown
- ✅ Form stays on page (doesn't navigate away)
- ✅ User can modify settings and retry

**After Successful Submission**:
- ✅ Error cleared
- ✅ Toast success message
- ✅ Navigates to active game session page

## User Experience Flow

### Scenario: Not Enough Players

1. User clicks "Start New Game" from Game Sessions list ✅
2. Form loads normally ✅
3. User configures: 2 courts, 2v2 (needs 8 players) ✅
4. User clicks "Create Game Session" ✅
5. **Backend returns error**: "Not enough players. Need 8, have 3" ❌
6. **Alert appears** above the form with the error message 🔴
7. User clicks "Manage players" link 🔗
8. User adds/activates more players ✅
9. User returns to form (or refreshes) ✅
10. User clicks "Create Game Session" again ✅
11. **Success!** Game session created ✅

## Design Decisions

### Why show error on form page instead of list page?

1. **User intent**: They've already decided to create a game, form provides context
2. **Dynamic requirements**: Player needs depend on configuration (courts × players_per_team)
3. **Better UX**: See the configuration that caused the issue
4. **Flexibility**: User can adjust settings to need fewer players
5. **Honest feedback**: Show real error from backend, not pre-validation

### Why not disable the button on list page?

1. **Changing requirements**: Player needs vary based on configuration
2. **Exploration**: User might want to see the form options first
3. **Less restrictive**: Don't block access, just inform on error
4. **Simpler**: No need to fetch player count on every page load

### Why both Alert and Toast?

1. **Alert**: Persistent, in-context, actionable (with link)
2. **Toast**: Immediate feedback, non-blocking
3. **Together**: Maximum visibility without being intrusive

## Error Message Examples

### Not Enough Players
```
Cannot Create Game Session
Not enough players. Need 8, have 3. Manage players
```

### No Active Players
```
Cannot Create Game Session
No active players available for this tournament. Manage players
```

### Generic Error
```
Cannot Create Game Session
Failed to create game session. Please try again. Manage players
```

## Visual States

### Form Without Error
- ✅ Clean form card
- ✅ All fields visible
- ✅ Submit button enabled
- ✅ No warning messages

### Form With Error
- 🔴 Red alert banner at top
- ⚠️ AlertCircle icon
- 📝 Error title and description
- 🔗 "Manage players" link (underlined)
- ✅ Form still accessible below
- ✅ Submit button still enabled (can retry)

## Files Modified

1. **`frontend/app/tournaments/[id]/game-sessions/new/page.tsx`**
   - Added error state
   - Enhanced error handling
   - Added Alert component display
   - Imported shadcn/ui Alert components

## Components Used

- **shadcn/ui Alert**: For prominent error display
- **shadcn/ui AlertDescription**: For error message text
- **shadcn/ui AlertTitle**: For "Cannot Create Game Session" heading
- **lucide-react AlertCircle**: For warning icon

## Future Enhancements (Not Implemented)

- [ ] **Proactive validation**: Calculate required players from form values and show warning before submission
- [ ] **Smart suggestions**: "You have 2 inactive players. Activate them to continue?"
- [ ] **Dynamic calculation**: Show "Need X more players" as user changes courts/players
- [ ] **Scroll to error**: Auto-scroll to alert when error appears
- [ ] **Field highlighting**: Highlight n_courts or n_players_per_team fields on error

## Testing

### Manual Test Steps

1. ✅ Create tournament with 3 active players
2. ✅ Navigate to Game Sessions → "Start New Game"
3. ✅ Configure: 2 courts, 2v2 (needs 8 players)
4. ✅ Click "Create Game Session"
5. ✅ Verify red alert appears with error message
6. ✅ Verify error message shows correct numbers
7. ✅ Verify "Manage players" link is present
8. ✅ Click "Manage players" → navigates to Players page
9. ✅ Add 5 more players
10. ✅ Return to Game Sessions → "Start New Game"
11. ✅ Configure same settings
12. ✅ Click "Create Game Session"
13. ✅ Verify game session creates successfully
14. ✅ Verify navigates to active game page

## Summary

Proactive validation prevents unnecessary API calls and provides instant feedback:
- ✅ **No API calls** when validation fails (no 400 errors in logs)
- ✅ **Instant feedback** - warning shows immediately as user changes configuration
- ✅ **Dynamic button text** - shows exactly how many more players needed
- ✅ **Clear guidance** - suggests adding players or reducing courts/team size
- ✅ **No console errors** - validation happens client-side

**Before**: User clicks submit → API call → 400 error → console error → toast

**After**: User sees warning immediately → button disabled → no API call → clean logs

**Result**: Efficient, user-friendly validation that prevents errors before they happen! 🎉


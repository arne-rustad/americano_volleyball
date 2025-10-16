"""Game session repetition analysis service."""

from fastapi import HTTPException

from app.database import supabase


class GameSessionAnalysisService:
    """Analyzes team and matchup repetitions in game sessions."""

    @staticmethod
    async def analyze_repetitions(session_id: int) -> dict:
        """Analyze how many teams and matchups repeat from previous sessions.

        Compares the current session against all completed sessions in the
        same tournament to identify repeated team combinations and matchups.

        Args:
            session_id: ID of the game session to analyze

        Returns:
            dict with summary stats and detailed breakdowns of repetitions

        Raises:
            HTTPException: If session not found
        """
        # Get current session and validate
        current_session = GameSessionAnalysisService._get_session(session_id)
        tournament_id = current_session["tournament_id"]

        # Get current session's teams and matchups
        current_teams, current_matchups = (
            await GameSessionAnalysisService._extract_session_data(
                session_id
            )
        )

        # Get all completed sessions from same tournament (excluding current)
        completed_sessions = (
            GameSessionAnalysisService._get_completed_sessions(
                tournament_id, exclude_session_id=session_id
            )
        )

        # If no history, return zeros
        if not completed_sessions:
            return {
                "total_teams": len(current_teams),
                "repeated_teams": 0,
                "total_matchups": len(current_matchups),
                "repeated_matchups": 0,
                "team_details": [],
                "matchup_details": [],
            }

        # Analyze repetitions
        team_analysis = await GameSessionAnalysisService._analyze_teams(
            current_teams, completed_sessions
        )

        matchup_analysis = await GameSessionAnalysisService._analyze_matchups(
            current_matchups, completed_sessions
        )

        return {
            "total_teams": len(current_teams),
            "repeated_teams": team_analysis["repeated_count"],
            "total_matchups": len(current_matchups),
            "repeated_matchups": matchup_analysis["repeated_count"],
            "team_details": team_analysis["details"],
            "matchup_details": matchup_analysis["details"],
        }

    # Helper methods

    @staticmethod
    def _get_session(session_id: int) -> dict:
        """Get game session by ID."""
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
        return session_response.data[0]

    @staticmethod
    def _get_completed_sessions(
        tournament_id: int, exclude_session_id: int
    ) -> list[dict]:
        """Get all completed sessions for tournament."""
        sessions_response = (
            supabase.table("game_sessions")
            .select("*")
            .eq("tournament_id", tournament_id)
            .eq("status", "completed")
            .neq("id", exclude_session_id)
            .execute()
        )
        return sessions_response.data or []

    @staticmethod
    async def _extract_session_data(
        session_id: int,
    ) -> tuple[list[dict], list[dict]]:
        """Extract teams and matchups from a session.

        Returns:
            Tuple of (teams_list, matchups_list)
            - teams_list: [{"court_index": 0, "team": "A", "player_ids": [1,2]}]
            - matchups_list: [{"court_index": 0, "team_a": [1,2], "team_b": [3,4]}]
        """
        # Get all courts with players
        courts_response = (
            supabase.table("court_sessions")
            .select("*, court_players(*)")
            .eq("game_session_id", session_id)
            .order("court_index")
            .execute()
        )

        teams = []
        matchups = []

        for court in courts_response.data:
            # Extract team A and team B
            team_a_players = sorted(
                [
                    cp["player_id"]
                    for cp in court["court_players"]
                    if cp["team"] == "A"
                ]
            )
            team_b_players = sorted(
                [
                    cp["player_id"]
                    for cp in court["court_players"]
                    if cp["team"] == "B"
                ]
            )

            # Add teams
            if team_a_players:
                teams.append(
                    {
                        "court_index": court["court_index"],
                        "team": "A",
                        "player_ids": team_a_players,
                    }
                )
            if team_b_players:
                teams.append(
                    {
                        "court_index": court["court_index"],
                        "team": "B",
                        "player_ids": team_b_players,
                    }
                )

            # Add matchup (both teams on same court)
            if team_a_players and team_b_players:
                matchups.append(
                    {
                        "court_index": court["court_index"],
                        "team_a_player_ids": team_a_players,
                        "team_b_player_ids": team_b_players,
                    }
                )

        return teams, matchups

    @staticmethod
    async def _analyze_teams(
        current_teams: list[dict], completed_sessions: list[dict]
    ) -> dict:
        """Analyze which teams are repeating from history."""
        repeated_count = 0
        details = []

        for team in current_teams:
            team_key = tuple(team["player_ids"])
            repeat_count = 0
            previous_session_ids = []

            # Check each completed session
            for session in completed_sessions:
                session_teams, _ = (
                    await GameSessionAnalysisService._extract_session_data(
                        session["id"]
                    )
                )

                # Check if this team appears in that session
                for hist_team in session_teams:
                    if tuple(hist_team["player_ids"]) == team_key:
                        repeat_count += 1
                        previous_session_ids.append(session["id"])
                        break

            if repeat_count > 0:
                repeated_count += 1
                details.append(
                    {
                        "court_index": team["court_index"],
                        "team": team["team"],
                        "player_ids": team["player_ids"],
                        "repeat_count": repeat_count,
                        "previous_session_ids": previous_session_ids,
                    }
                )

        return {"repeated_count": repeated_count, "details": details}

    @staticmethod
    async def _analyze_matchups(
        current_matchups: list[dict], completed_sessions: list[dict]
    ) -> dict:
        """Analyze which matchups are repeating from history."""
        repeated_count = 0
        details = []

        for matchup in current_matchups:
            # Create normalized matchup key (order independent)
            team_a = tuple(matchup["team_a_player_ids"])
            team_b = tuple(matchup["team_b_player_ids"])
            matchup_key = tuple(sorted([team_a, team_b]))

            repeat_count = 0
            previous_session_ids = []

            # Check each completed session
            for session in completed_sessions:
                _, session_matchups = (
                    await GameSessionAnalysisService._extract_session_data(
                        session["id"]
                    )
                )

                # Check if this matchup appears in that session
                for hist_matchup in session_matchups:
                    hist_team_a = tuple(hist_matchup["team_a_player_ids"])
                    hist_team_b = tuple(hist_matchup["team_b_player_ids"])
                    hist_matchup_key = tuple(sorted([hist_team_a, hist_team_b]))

                    if matchup_key == hist_matchup_key:
                        repeat_count += 1
                        previous_session_ids.append(session["id"])
                        break

            if repeat_count > 0:
                repeated_count += 1
                details.append(
                    {
                        "court_index": matchup["court_index"],
                        "team_a_player_ids": matchup["team_a_player_ids"],
                        "team_b_player_ids": matchup["team_b_player_ids"],
                        "repeat_count": repeat_count,
                        "previous_session_ids": previous_session_ids,
                    }
                )

        return {"repeated_count": repeated_count, "details": details}


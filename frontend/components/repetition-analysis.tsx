"use client";

import { useEffect, useState } from "react";
import { Info, ChevronDown, ChevronUp, Users } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { getRepetitionAnalysis, RepetitionAnalysis } from "@/lib/api";
import { createClient } from "@/lib/supabase";
import { Database } from "@/lib/database.types";

type Player = Database["public"]["Tables"]["players"]["Row"];

interface RepetitionAnalysisProps {
  sessionId: number;
  tournamentId: number;
}

export function RepetitionAnalysisComponent({
  sessionId,
  tournamentId,
}: RepetitionAnalysisProps) {
  const [analysis, setAnalysis] = useState<RepetitionAnalysis | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const supabase = createClient();

  useEffect(() => {
    fetchData();
  }, [sessionId, tournamentId]);

  async function fetchData() {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch analysis and players in parallel
      const [analysisData, playersData] = await Promise.all([
        getRepetitionAnalysis(sessionId),
        supabase
          .from("players")
          .select("*")
          .eq("tournament_id", tournamentId)
          .then((res) => res.data || []),
      ]);

      setAnalysis(analysisData);
      setPlayers(playersData);
    } catch (err: any) {
      console.error("Error fetching repetition analysis:", err);
      setError(err.message || "Failed to load repetition analysis");
    } finally {
      setIsLoading(false);
    }
  }

  function getPlayerNames(playerIds: number[]): string {
    return playerIds
      .map((id) => {
        const player = players.find((p) => p.id === id);
        return player?.name || `Player ${id}`;
      })
      .join(", ");
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-6">
          <div className="text-center text-muted-foreground">
            Analyzing repetitions...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!analysis) {
    return null;
  }

  const hasRepeats =
    analysis.repeated_teams > 0 || analysis.repeated_matchups > 0;
  const allNew = !hasRepeats;

  // Calculate percentages
  const teamRepeatPercent =
    analysis.total_teams > 0
      ? Math.round((analysis.repeated_teams / analysis.total_teams) * 100)
      : 0;
  const matchupRepeatPercent =
    analysis.total_matchups > 0
      ? Math.round((analysis.repeated_matchups / analysis.total_matchups) * 100)
      : 0;

  return (
    <Card className={allNew ? "border-green-200 bg-green-50/50" : ""}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-lg">Repetition Analysis</CardTitle>
          </div>
          {analysis.team_details.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="gap-1"
            >
              {showDetails ? (
                <>
                  Hide Details <ChevronUp className="h-4 w-4" />
                </>
              ) : (
                <>
                  Show Details <ChevronDown className="h-4 w-4" />
                </>
              )}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Team Repeats</div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">
                {analysis.repeated_teams}
              </span>
              <span className="text-muted-foreground">
                / {analysis.total_teams}
              </span>
              {teamRepeatPercent > 0 && (
                <Badge variant={teamRepeatPercent > 50 ? "default" : "secondary"}>
                  {teamRepeatPercent}%
                </Badge>
              )}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Matchup Repeats</div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">
                {analysis.repeated_matchups}
              </span>
              <span className="text-muted-foreground">
                / {analysis.total_matchups}
              </span>
              {matchupRepeatPercent > 0 && (
                <Badge
                  variant={matchupRepeatPercent > 50 ? "default" : "secondary"}
                >
                  {matchupRepeatPercent}%
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Message */}
        {allNew && (
          <Alert className="border-green-200 bg-green-50">
            <Users className="h-4 w-4" />
            <AlertTitle>All Fresh Combinations!</AlertTitle>
            <AlertDescription>
              No repeated teams or matchups from previous sessions. Great variety!
            </AlertDescription>
          </Alert>
        )}

        {/* Details Section */}
        {showDetails && hasRepeats && (
          <div className="space-y-4 pt-4 border-t">
            {/* Team Details */}
            {analysis.team_details.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm">Repeated Teams</h4>
                <div className="space-y-2">
                  {analysis.team_details.map((team, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-yellow-50 border border-yellow-200 rounded-md"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-medium text-sm">
                            Court {team.court_index + 1} - Team {team.team}
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {getPlayerNames(team.player_ids)}
                          </div>
                        </div>
                        <Badge variant="outline">
                          {team.repeat_count}x before
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Matchup Details */}
            {analysis.matchup_details.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm">Repeated Matchups</h4>
                <div className="space-y-2">
                  {analysis.matchup_details.map((matchup, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-orange-50 border border-orange-200 rounded-md"
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="font-medium text-sm">
                            Court {matchup.court_index + 1}
                          </div>
                          <div className="text-sm">
                            <div className="text-muted-foreground">Team A:</div>
                            <div className="ml-2">
                              {getPlayerNames(matchup.team_a_player_ids)}
                            </div>
                          </div>
                          <div className="text-sm">
                            <div className="text-muted-foreground">vs Team B:</div>
                            <div className="ml-2">
                              {getPlayerNames(matchup.team_b_player_ids)}
                            </div>
                          </div>
                        </div>
                        <Badge variant="outline">
                          {matchup.repeat_count}x before
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        {!allNew && (
          <div className="text-xs text-muted-foreground pt-2 border-t">
            <strong>Team repeats:</strong> Players have played together before.{" "}
            <strong>Matchup repeats:</strong> Same teams have faced each other
            before.
          </div>
        )}
      </CardContent>
    </Card>
  );
}


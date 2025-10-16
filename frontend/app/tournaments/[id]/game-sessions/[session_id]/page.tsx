"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, Loader2 } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CourtCard } from "@/components/court-card";
import { createClient } from "@/lib/supabase";
import { completeGameSession } from "@/lib/api";
import { Database } from "@/lib/database.types";
import { toast } from "sonner";

type GameSession = Database["public"]["Tables"]["game_sessions"]["Row"];
type CourtSession = Database["public"]["Tables"]["court_sessions"]["Row"];
type CourtPlayer = Database["public"]["Tables"]["court_players"]["Row"];
type Player = Database["public"]["Tables"]["players"]["Row"];

interface CourtSessionWithPlayers extends CourtSession {
  court_players: (CourtPlayer & { players: Player })[];
}

export default function ActiveGameSessionPage() {
  const params = useParams();
  const router = useRouter();
  const tournamentId = Number(params.id);
  const sessionId = Number(params.session_id);
  const supabase = createClient();

  const [gameSession, setGameSession] = useState<GameSession | null>(null);
  const [courtSessions, setCourtSessions] = useState<
    CourtSessionWithPlayers[]
  >([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    fetchGameSession();
    fetchCourtSessions();
  }, [sessionId]);

  async function fetchGameSession() {
    try {
      const { data, error } = await supabase
        .from("game_sessions")
        .select("*")
        .eq("id", sessionId)
        .single();

      if (error) throw error;
      setGameSession(data);
    } catch (error) {
      console.error("Error fetching game session:", error);
      toast.error("Failed to load game session");
    }
  }

  async function fetchCourtSessions() {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from("court_sessions")
        .select(
          `
          *,
          court_players (
            *,
            players (*)
          )
        `
        )
        .eq("game_session_id", sessionId)
        .order("court_index");

      if (error) throw error;

      setCourtSessions((data as any) || []);
    } catch (error) {
      console.error("Error fetching court sessions:", error);
      toast.error("Failed to load courts");
    } finally {
      setIsLoading(false);
    }
  }

  async function updateCourtScore(
    courtSessionId: number,
    team: "A" | "B",
    score: number
  ) {
    try {
      const field = team === "A" ? "score_team_a" : "score_team_b";
      const { error } = await supabase
        .from("court_sessions")
        .update({ [field]: score })
        .eq("id", courtSessionId);

      if (error) throw error;

      // Update local state
      setCourtSessions((prev) =>
        prev.map((court) =>
          court.id === courtSessionId ? { ...court, [field]: score } : court
        )
      );
    } catch (error) {
      console.error("Error updating score:", error);
      toast.error("Failed to update score");
    }
  }

  async function handleCompleteSession() {
    // Validate all scores are entered
    const allScoresEntered = courtSessions.every(
      (court) => court.score_team_a !== null && court.score_team_b !== null
    );

    if (!allScoresEntered) {
      toast.error("Please enter scores for all courts before completing");
      return;
    }

    setIsCompleting(true);

    try {
      await completeGameSession(sessionId);

      toast.success("Game session completed! Scores have been updated.");
      router.push(`/tournaments/${tournamentId}/game-sessions`);
    } catch (error) {
      console.error("Error completing game session:", error);
      toast.error("Failed to complete game session. Please try again.");
    } finally {
      setIsCompleting(false);
    }
  }

  function getStatusBadge(status: GameSession["status"]) {
    switch (status) {
      case "pending":
        return <Badge variant="outline">Pending</Badge>;
      case "in_progress":
        return <Badge variant="default">In Progress</Badge>;
      case "completed":
        return <Badge variant="secondary">Completed</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  }

  function getTeamPlayers(
    courtSession: CourtSessionWithPlayers,
    team: "A" | "B"
  ): Player[] {
    return courtSession.court_players
      .filter((cp) => cp.team === team)
      .map((cp) => cp.players);
  }

  const allScoresEntered = courtSessions.every(
    (court) => court.score_team_a !== null && court.score_team_b !== null
  );

  const isCompleted = gameSession?.status === "completed";

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <Link href={`/tournaments/${tournamentId}/game-sessions`}>
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Game Sessions
          </Button>
        </Link>
        {gameSession && getStatusBadge(gameSession.status)}
      </div>

      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">
          Game Session #{sessionId}
        </h1>
        {gameSession && (
          <div className="text-muted-foreground">
            {gameSession.n_courts} courts • {gameSession.n_game_points} points
            per game
          </div>
        )}
      </div>

      {courtSessions.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">
          No courts found for this game session
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {courtSessions.map((court) => (
              <CourtCard
                key={court.id}
                courtIndex={court.court_index}
                teamAPlayers={getTeamPlayers(court, "A")}
                teamBPlayers={getTeamPlayers(court, "B")}
                scoreTeamA={court.score_team_a}
                scoreTeamB={court.score_team_b}
                onScoreChange={(team, score) =>
                  updateCourtScore(court.id, team, score)
                }
                disabled={isCompleted}
              />
            ))}
          </div>

          {!isCompleted && (
            <div className="flex justify-center">
              <Button
                size="lg"
                onClick={handleCompleteSession}
                disabled={!allScoresEntered || isCompleting}
                className="gap-2"
              >
                {isCompleting ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Check className="h-5 w-5" />
                )}
                Complete Game Session
              </Button>
            </div>
          )}

          {isCompleted && (
            <div className="text-center py-6">
              <p className="text-lg text-muted-foreground">
                This game session has been completed.
              </p>
              <Link href={`/tournaments/${tournamentId}/leaderboard`}>
                <Button variant="outline" className="mt-4">
                  View Updated Leaderboard
                </Button>
              </Link>
            </div>
          )}
        </>
      )}
    </main>
  );
}


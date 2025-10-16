"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, Loader2, ArrowLeftRight, Trash2 } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CourtCard } from "@/components/court-card";
import { EditPlayersModal } from "@/components/edit-players-modal";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { createClient } from "@/lib/supabase";
import { completeGameSession, swapPlayers, deleteGameSession } from "@/lib/api";
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
  const [restingPlayers, setRestingPlayers] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchGameSession();
    fetchCourtSessions();
    fetchRestingPlayers();
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

  async function fetchRestingPlayers() {
    try {
      // Get all active players in the tournament
      const { data: allPlayers, error: playersError } = await supabase
        .from("players")
        .select("*")
        .eq("tournament_id", tournamentId)
        .eq("is_active", true);

      if (playersError) throw playersError;

      // Get players currently playing in this game session
      const { data: courtData, error: courtError } = await supabase
        .from("court_sessions")
        .select("court_players(player_id)")
        .eq("game_session_id", sessionId);

      if (courtError) throw courtError;

      // Extract playing player IDs
      const playingPlayerIds = new Set(
        courtData.flatMap((court: any) =>
          court.court_players.map((cp: any) => cp.player_id)
        )
      );

      // Filter out playing players to get resting players
      const resting = (allPlayers || []).filter(
        (player) => !playingPlayerIds.has(player.id)
      );

      setRestingPlayers(resting);
    } catch (error) {
      console.error("Error fetching resting players:", error);
      // Don't show error toast, just log - not critical
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
    } catch (error: any) {
      // Don't log to console - we're displaying it in the UI
      const message = error.message || "Failed to complete game session. Please try again.";
      toast.error(message);
    } finally {
      setIsCompleting(false);
    }
  }

  async function handleSwapPlayers(player1Id: number, player2Id: number) {
    try {
      await swapPlayers(sessionId, player1Id, player2Id);
      toast.success("Players swapped successfully");
      await fetchCourtSessions(); // Refresh court data
      await fetchRestingPlayers(); // Refresh resting players list
    } catch (error: any) {
      const message = error.message || "Failed to swap players";
      toast.error(message);
      throw error; // Re-throw so modal can handle it
    }
  }

  async function handleDeleteSession() {
    setIsDeleting(true);

    try {
      await deleteGameSession(sessionId);
      toast.success("Game session deleted successfully");
      router.push(`/tournaments/${tournamentId}/game-sessions`);
    } catch (error: any) {
      const message = error.message || "Failed to delete game session";
      toast.error(message);
      setIsDeleteDialogOpen(false);
    } finally {
      setIsDeleting(false);
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

  const hasAnyScores = courtSessions.some(
    (court) => court.score_team_a !== null || court.score_team_b !== null
  );

  const isCompleted = gameSession?.status === "completed";
  const isPending = gameSession?.status === "pending";

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
        <div className="flex items-center gap-3">
          {gameSession && getStatusBadge(gameSession.status)}
          {isPending && !hasAnyScores && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setIsDeleteDialogOpen(true)}
              className="gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Delete Session
            </Button>
          )}
        </div>
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
          {!isCompleted && (
            <div className="mb-4 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setIsEditModalOpen(true)}
                disabled={hasAnyScores}
                className="gap-2"
              >
                <ArrowLeftRight className="h-4 w-4" />
                Edit Players
                {hasAnyScores && (
                  <Badge variant="secondary" className="ml-2">
                    Locked
                  </Badge>
                )}
              </Button>
            </div>
          )}

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
                expectedGamePoints={gameSession?.n_game_points}
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

          <EditPlayersModal
            isOpen={isEditModalOpen}
            onClose={() => setIsEditModalOpen(false)}
            courtSessions={courtSessions}
            restingPlayers={restingPlayers}
            onSwap={handleSwapPlayers}
          />

          <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Game Session?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete this game session and all associated
                  court assignments. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteSession}
                  disabled={isDeleting}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  {isDeleting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </>
                  )}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </>
      )}
    </main>
  );
}


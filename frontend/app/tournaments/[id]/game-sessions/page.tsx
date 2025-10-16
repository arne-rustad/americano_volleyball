"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Plus, Trophy } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/empty-state";
import { createClient } from "@/lib/supabase";
import { Database } from "@/lib/database.types";
import { toast } from "sonner";

type GameSession = Database["public"]["Tables"]["game_sessions"]["Row"];

export default function GameSessionsPage() {
  const params = useParams();
  const tournamentId = Number(params.id);
  const supabase = createClient();

  const [gameSessions, setGameSessions] = useState<GameSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchGameSessions();
  }, [tournamentId]);

  async function fetchGameSessions() {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from("game_sessions")
        .select("*")
        .eq("tournament_id", tournamentId)
        .order("created_at", { ascending: false });

      if (error) throw error;

      setGameSessions(data || []);
    } catch (error) {
      console.error("Error fetching game sessions:", error);
      toast.error("Failed to load game sessions");
    } finally {
      setIsLoading(false);
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

  function formatDate(dateString: string | null) {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString();
  }

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Game Sessions</h1>
        <Link href={`/tournaments/${tournamentId}/game-sessions/new`}>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Start New Game
          </Button>
        </Link>
      </div>

      {gameSessions.length === 0 ? (
        <EmptyState
          icon={Trophy}
          title="No game sessions yet"
          description="Start your first game session to begin playing"
          action={
            <Link href={`/tournaments/${tournamentId}/game-sessions/new`}>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Start First Game
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="grid gap-4">
          {gameSessions.map((session) => (
            <Link
              key={session.id}
              href={`/tournaments/${tournamentId}/game-sessions/${session.id}`}
            >
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">
                      Game Session #{session.id}
                    </CardTitle>
                    {getStatusBadge(session.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Courts</div>
                      <div className="font-medium">{session.n_courts}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Points</div>
                      <div className="font-medium">
                        {session.n_game_points || "-"}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Created</div>
                      <div className="font-medium text-xs">
                        {formatDate(session.created_at)}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Completed</div>
                      <div className="font-medium text-xs">
                        {formatDate(session.completed_at)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}


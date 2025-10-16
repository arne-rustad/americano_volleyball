import Link from "next/link";
import { Plus, Trophy, Users, Calendar } from "lucide-react";
import { Navigation } from "@/components/navigation";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createClient } from "@/lib/supabase";
import { Database } from "@/lib/database.types";

type Tournament = Database["public"]["Tables"]["tournaments"]["Row"];

interface TournamentWithPlayerCount {
  id: number;
  name: string;
  is_mix_tournament: boolean;
  created_at: string;
  player_count: number;
}

export default async function Home() {
  const supabase = createClient();

  // Fetch tournaments
  const { data: tournamentsData, error } = await supabase
    .from("tournaments")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching tournaments:", error);
  }

  const tournaments = (tournamentsData || []) as Tournament[];

  // Fetch player counts for each tournament
  const tournamentsWithCounts: TournamentWithPlayerCount[] = await Promise.all(
    tournaments.map(async (tournament) => {
      const { count } = await supabase
        .from("players")
        .select("*", { count: "exact", head: true })
        .eq("tournament_id", tournament.id);

      return {
        id: tournament.id,
        name: tournament.name,
        is_mix_tournament: tournament.is_mix_tournament,
        created_at: tournament.created_at,
        player_count: count || 0,
      };
    })
  );

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="mb-12 text-center">
          <div className="flex justify-center mb-4">
            <Trophy className="h-16 w-16 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-4">Americano Volleyball</h1>
          <p className="text-lg text-muted-foreground mb-6 max-w-2xl mx-auto">
            Organize and manage your Americano volleyball tournaments with ease.
            Track players, scores, and create exciting matches.
          </p>
          <Link href="/tournaments/new">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Create New Tournament
            </Button>
          </Link>
        </div>

        {/* Tournaments List */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-6">Your Tournaments</h2>

          {!tournamentsWithCounts || tournamentsWithCounts.length === 0 ? (
            <EmptyState
              icon={Trophy}
              title="No tournaments yet"
              description="Get started by creating your first tournament"
              action={
                <Link href="/tournaments/new">
                  <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Create Tournament
                  </Button>
                </Link>
              }
            />
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {tournamentsWithCounts.map((tournament) => (
                <Link
                  key={tournament.id}
                  href={`/tournaments/${tournament.id}/leaderboard`}
                >
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-xl">
                          {tournament.name}
                        </CardTitle>
                        <Badge
                          variant={
                            tournament.is_mix_tournament
                              ? "default"
                              : "secondary"
                          }
                        >
                          {tournament.is_mix_tournament ? "Mix" : "Regular"}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm text-muted-foreground">
                        <div className="flex items-center gap-4 pt-2">
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            <span>{tournament.player_count} players</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>
                              {new Date(
                                tournament.created_at
                              ).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

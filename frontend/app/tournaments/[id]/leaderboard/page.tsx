"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Trophy, Medal, Users } from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/empty-state";
import { createClient } from "@/lib/supabase";
import { Database } from "@/lib/database.types";
import { toast } from "sonner";

type Player = Database["public"]["Tables"]["players"]["Row"];
type Tournament = Database["public"]["Tables"]["tournaments"]["Row"];

export default function LeaderboardPage() {
  const params = useParams();
  const tournamentId = Number(params.id);
  const supabase = createClient();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [tournamentId]);

  async function fetchData() {
    setIsLoading(true);
    try {
      const [tournamentRes, playersRes] = await Promise.all([
        supabase
          .from("tournaments")
          .select("*")
          .eq("id", tournamentId)
          .single(),
        supabase
          .from("players")
          .select("*")
          .eq("tournament_id", tournamentId)
          .order("score", { ascending: false })
          .order("name"),
      ]);

      if (tournamentRes.error) throw tournamentRes.error;
      if (playersRes.error) throw playersRes.error;

      setTournament(tournamentRes.data);
      setPlayers(playersRes.data || []);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load leaderboard");
    } finally {
      setIsLoading(false);
    }
  }

  function getRankBadge(rank: number) {
    if (rank === 1) {
      return (
        <Badge className="bg-yellow-500 hover:bg-yellow-600 gap-1">
          <Trophy className="h-3 w-3" />
          1st
        </Badge>
      );
    }
    if (rank === 2) {
      return (
        <Badge className="bg-gray-400 hover:bg-gray-500 gap-1">
          <Medal className="h-3 w-3" />
          2nd
        </Badge>
      );
    }
    if (rank === 3) {
      return (
        <Badge className="bg-amber-600 hover:bg-amber-700 gap-1">
          <Medal className="h-3 w-3" />
          3rd
        </Badge>
      );
    }
    return <span className="text-muted-foreground">{rank}</span>;
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
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Leaderboard</h1>
        <p className="text-muted-foreground mt-1">
          Current standings for {tournament?.name}
        </p>
      </div>

      {players.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No players yet"
          description="Add players to see the leaderboard"
        />
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Rank</TableHead>
                <TableHead>Player</TableHead>
                {tournament?.is_mix_tournament && (
                  <TableHead>Gender</TableHead>
                )}
                <TableHead className="text-right">Score</TableHead>
                <TableHead className="text-right">Games Played</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {players.map((player, index) => {
                const rank = index + 1;
                const isTopThree = rank <= 3;

                return (
                  <TableRow
                    key={player.id}
                    className={isTopThree ? "bg-muted/50" : ""}
                  >
                    <TableCell className="font-medium">
                      {getRankBadge(rank)}
                    </TableCell>
                    <TableCell className="font-medium">
                      {player.name}
                    </TableCell>
                    {tournament?.is_mix_tournament && (
                      <TableCell className="capitalize">
                        {player.gender || "-"}
                      </TableCell>
                    )}
                    <TableCell className="text-right font-semibold">
                      {player.score}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {player.games_played}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {players.length > 0 && (
        <div className="mt-4 text-sm text-muted-foreground text-center">
          Total Players: {players.length}
        </div>
      )}
    </main>
  );
}


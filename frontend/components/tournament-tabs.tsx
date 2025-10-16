"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface TournamentTabsProps {
  tournamentId: number;
}

export function TournamentTabs({ tournamentId }: TournamentTabsProps) {
  const pathname = usePathname();

  const getActiveTab = () => {
    if (pathname?.includes("players")) return "players";
    if (pathname?.includes("game-sessions")) return "game-sessions";
    if (pathname?.includes("leaderboard")) return "leaderboard";
    return "leaderboard";
  };

  return (
    <div className="border-b">
      <div className="container mx-auto px-4">
        <Tabs defaultValue={getActiveTab()}>
          <TabsList className="h-12 bg-transparent border-b-0 rounded-none">
            <Link href={`/tournaments/${tournamentId}/players`}>
              <TabsTrigger
                value="players"
                className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              >
                Players
              </TabsTrigger>
            </Link>
            <Link href={`/tournaments/${tournamentId}/game-sessions`}>
              <TabsTrigger
                value="game-sessions"
                className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              >
                Game Sessions
              </TabsTrigger>
            </Link>
            <Link href={`/tournaments/${tournamentId}/leaderboard`}>
              <TabsTrigger
                value="leaderboard"
                className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
              >
                Leaderboard
              </TabsTrigger>
            </Link>
          </TabsList>
        </Tabs>
      </div>
    </div>
  );
}


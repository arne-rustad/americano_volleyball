"use client";

import { useState } from "react";
import { Database } from "@/lib/database.types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeftRight } from "lucide-react";

type Player = Database["public"]["Tables"]["players"]["Row"];
type CourtSession = Database["public"]["Tables"]["court_sessions"]["Row"];
type CourtPlayer = Database["public"]["Tables"]["court_players"]["Row"];

interface CourtSessionWithPlayers extends CourtSession {
  court_players: (CourtPlayer & { players: Player })[];
}

interface PlayerPosition {
  playerId: number;
  playerName: string;
  courtSessionId: number;
  courtIndex: number;
  team: "A" | "B";
}

interface EditPlayersModalProps {
  isOpen: boolean;
  onClose: () => void;
  courtSessions: CourtSessionWithPlayers[];
  onSwap: (player1Id: number, player2Id: number) => Promise<void>;
}

export function EditPlayersModal({
  isOpen,
  onClose,
  courtSessions,
  onSwap,
}: EditPlayersModalProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerPosition | null>(null);
  const [isSwapping, setIsSwapping] = useState(false);

  // Extract all player positions
  const allPlayerPositions: PlayerPosition[] = courtSessions.flatMap((court) =>
    court.court_players.map((cp) => ({
      playerId: cp.player_id,
      playerName: cp.players.name,
      courtSessionId: court.id,
      courtIndex: court.court_index,
      team: cp.team as "A" | "B",
    }))
  );

  const handlePlayerClick = async (player: PlayerPosition) => {
    if (!selectedPlayer) {
      // First click: select player
      setSelectedPlayer(player);
    } else if (selectedPlayer.playerId === player.playerId) {
      // Click same player: deselect
      setSelectedPlayer(null);
    } else {
      // Second click: swap players
      setIsSwapping(true);
      try {
        await onSwap(selectedPlayer.playerId, player.playerId);
        setSelectedPlayer(null);
      } catch (error) {
        // Error is handled by parent component
      } finally {
        setIsSwapping(false);
      }
    }
  };

  const isPlayerSelected = (playerId: number) =>
    selectedPlayer?.playerId === playerId;

  const isValidSwapTarget = (playerId: number) =>
    selectedPlayer !== null && selectedPlayer.playerId !== playerId;

  const getPlayersForCourtTeam = (
    courtIndex: number,
    team: "A" | "B"
  ): PlayerPosition[] => {
    return allPlayerPositions.filter(
      (p) => p.courtIndex === courtIndex && p.team === team
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5" />
            Edit Player Assignments
          </DialogTitle>
          <DialogDescription>
            Click a player to select, then click another player to swap positions.
            {selectedPlayer && (
              <span className="block mt-2 text-primary font-medium">
                Selected: {selectedPlayer.playerName} - Click another player to swap
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 md:grid-cols-2">
          {courtSessions.map((court) => (
            <Card key={court.id}>
              <CardHeader>
                <CardTitle className="text-lg">Court {court.court_index + 1}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Team A */}
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-2">
                    Team A
                  </h4>
                  <div className="space-y-1">
                    {getPlayersForCourtTeam(court.court_index, "A").map((player) => (
                      <button
                        key={player.playerId}
                        onClick={() => handlePlayerClick(player)}
                        disabled={isSwapping}
                        className={`
                          w-full text-left px-3 py-2 rounded-md text-sm
                          transition-colors
                          ${isPlayerSelected(player.playerId)
                            ? "bg-primary text-primary-foreground"
                            : isValidSwapTarget(player.playerId)
                            ? "bg-green-50 border-2 border-green-500 hover:bg-green-100"
                            : "bg-secondary hover:bg-secondary/80"
                          }
                          ${isSwapping ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                        `}
                      >
                        {player.playerName}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Team B */}
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-2">
                    Team B
                  </h4>
                  <div className="space-y-1">
                    {getPlayersForCourtTeam(court.court_index, "B").map((player) => (
                      <button
                        key={player.playerId}
                        onClick={() => handlePlayerClick(player)}
                        disabled={isSwapping}
                        className={`
                          w-full text-left px-3 py-2 rounded-md text-sm
                          transition-colors
                          ${isPlayerSelected(player.playerId)
                            ? "bg-primary text-primary-foreground"
                            : isValidSwapTarget(player.playerId)
                            ? "bg-green-50 border-2 border-green-500 hover:bg-green-100"
                            : "bg-secondary hover:bg-secondary/80"
                          }
                          ${isSwapping ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                        `}
                      >
                        {player.playerName}
                      </button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSwapping}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}


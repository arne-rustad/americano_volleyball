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
  restingPlayers: Player[];
  onSwap: (player1Id: number, player2Id: number) => Promise<void>;
}

export function EditPlayersModal({
  isOpen,
  onClose,
  courtSessions,
  restingPlayers,
  onSwap,
}: EditPlayersModalProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerPosition | null>(null);
  const [selectedRestingPlayer, setSelectedRestingPlayer] = useState<number | null>(null);
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
    // Clear resting player selection if any
    if (selectedRestingPlayer) {
      setSelectedRestingPlayer(null);
    }

    if (!selectedPlayer) {
      // First click: select playing player
      setSelectedPlayer(player);
    } else if (selectedPlayer.playerId === player.playerId) {
      // Click same player: deselect
      setSelectedPlayer(null);
    } else {
      // Second click: swap two playing players
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

  const handleRestingPlayerClick = async (playerId: number) => {
    if (!selectedPlayer && !selectedRestingPlayer) {
      // First click: select resting player
      setSelectedRestingPlayer(playerId);
    } else if (selectedRestingPlayer === playerId) {
      // Click same resting player: deselect
      setSelectedRestingPlayer(null);
    } else if (selectedPlayer) {
      // Swap playing player with resting player
      setIsSwapping(true);
      try {
        await onSwap(selectedPlayer.playerId, playerId);
        setSelectedPlayer(null);
        setSelectedRestingPlayer(null);
      } catch (error) {
        // Error is handled by parent component
      } finally {
        setIsSwapping(false);
      }
    } else if (selectedRestingPlayer) {
      // Cannot swap two resting players
      // Just switch selection
      setSelectedRestingPlayer(playerId);
    }
  };

  const isPlayerSelected = (playerId: number) =>
    selectedPlayer?.playerId === playerId;

  const isRestingPlayerSelected = (playerId: number) =>
    selectedRestingPlayer === playerId;

  const isValidSwapTarget = (playerId: number) =>
    (selectedPlayer !== null && selectedPlayer.playerId !== playerId) ||
    selectedRestingPlayer !== null;

  const isValidRestingSwapTarget = (playerId: number) =>
    selectedPlayer !== null && selectedRestingPlayer !== playerId;

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
            You can also swap playing players with resting players.
            {selectedPlayer && (
              <span className="block mt-2 text-primary font-medium">
                Selected Playing: {selectedPlayer.playerName} - Click another player to swap
              </span>
            )}
            {selectedRestingPlayer && !selectedPlayer && (
              <span className="block mt-2 text-primary font-medium">
                Selected Resting: {restingPlayers.find(p => p.id === selectedRestingPlayer)?.name} - Click a playing player to swap
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

        {/* Resting Players */}
        {restingPlayers.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Resting Players (On Bench)</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {restingPlayers.map((player) => (
                <button
                  key={player.id}
                  onClick={() => handleRestingPlayerClick(player.id)}
                  disabled={isSwapping}
                  className={`
                    px-3 py-2 rounded-md text-sm
                    transition-colors
                    ${isRestingPlayerSelected(player.id)
                      ? "bg-primary text-primary-foreground"
                      : isValidRestingSwapTarget(player.id)
                      ? "bg-green-50 border-2 border-green-500 hover:bg-green-100"
                      : "bg-muted hover:bg-muted/80"
                    }
                    ${isSwapping ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                  `}
                >
                  {player.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSwapping}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}


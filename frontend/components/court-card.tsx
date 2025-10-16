import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Database } from "@/lib/database.types";

type Player = Database["public"]["Tables"]["players"]["Row"];

interface CourtCardProps {
  courtIndex: number;
  teamAPlayers: Player[];
  teamBPlayers: Player[];
  scoreTeamA: number | null;
  scoreTeamB: number | null;
  onScoreChange: (team: "A" | "B", score: number) => void;
  disabled?: boolean;
}

export function CourtCard({
  courtIndex,
  teamAPlayers,
  teamBPlayers,
  scoreTeamA,
  scoreTeamB,
  onScoreChange,
  disabled = false,
}: CourtCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Court {courtIndex + 1}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Team A */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm text-muted-foreground">
                Team A
              </h3>
              <div className="text-sm mt-1">
                {teamAPlayers.map((player) => (
                  <div key={player.id}>{player.name}</div>
                ))}
              </div>
            </div>
            <div className="w-20">
              <Label htmlFor={`court-${courtIndex}-team-a`} className="sr-only">
                Team A Score
              </Label>
              <Input
                id={`court-${courtIndex}-team-a`}
                type="number"
                min="0"
                value={scoreTeamA ?? ""}
                onChange={(e) =>
                  onScoreChange("A", Number(e.target.value) || 0)
                }
                placeholder="0"
                className="text-center text-lg font-bold"
                disabled={disabled}
              />
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-dashed" />

        {/* Team B */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm text-muted-foreground">
                Team B
              </h3>
              <div className="text-sm mt-1">
                {teamBPlayers.map((player) => (
                  <div key={player.id}>{player.name}</div>
                ))}
              </div>
            </div>
            <div className="w-20">
              <Label htmlFor={`court-${courtIndex}-team-b`} className="sr-only">
                Team B Score
              </Label>
              <Input
                id={`court-${courtIndex}-team-b`}
                type="number"
                min="0"
                value={scoreTeamB ?? ""}
                onChange={(e) =>
                  onScoreChange("B", Number(e.target.value) || 0)
                }
                placeholder="0"
                className="text-center text-lg font-bold"
                disabled={disabled}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


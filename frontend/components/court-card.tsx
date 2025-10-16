import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { AlertCircle } from "lucide-react";
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
  expectedGamePoints?: number | null;
}

export function CourtCard({
  courtIndex,
  teamAPlayers,
  teamBPlayers,
  scoreTeamA,
  scoreTeamB,
  onScoreChange,
  disabled = false,
  expectedGamePoints,
}: CourtCardProps) {
  // Calculate if scores match expected total
  const bothScoresSet = scoreTeamA !== null && scoreTeamB !== null;
  const totalScore = bothScoresSet ? (scoreTeamA || 0) + (scoreTeamB || 0) : null;
  const hasScoreMismatch = 
    expectedGamePoints && 
    totalScore !== null && 
    totalScore !== expectedGamePoints;
  
  const handleScoreChange = (team: "A" | "B", value: string) => {
    const score = Number(value) || 0;
    onScoreChange(team, score);
  };
  
  const handleScoreBlur = (team: "A" | "B", value: string) => {
    const score = Number(value) || 0;
    
    // Auto-calculate the other team's score if it's not set yet
    if (expectedGamePoints && score > 0) {
      if (team === "A" && scoreTeamB === null) {
        const calculatedScoreB = expectedGamePoints - score;
        if (calculatedScoreB >= 0) {
          onScoreChange("B", calculatedScoreB);
        }
      } else if (team === "B" && scoreTeamA === null) {
        const calculatedScoreA = expectedGamePoints - score;
        if (calculatedScoreA >= 0) {
          onScoreChange("A", calculatedScoreA);
        }
      }
    }
  };

  return (
    <Card className={hasScoreMismatch ? "border-yellow-500 border-2" : ""}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Court {courtIndex + 1}</CardTitle>
          {hasScoreMismatch && (
            <Badge variant="outline" className="gap-1 text-yellow-600 border-yellow-500">
              <AlertCircle className="h-3 w-3" />
              Total: {totalScore} / {expectedGamePoints}
            </Badge>
          )}
        </div>
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
                onChange={(e) => handleScoreChange("A", e.target.value)}
                onBlur={(e) => handleScoreBlur("A", e.target.value)}
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
                onChange={(e) => handleScoreChange("B", e.target.value)}
                onBlur={(e) => handleScoreBlur("B", e.target.value)}
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


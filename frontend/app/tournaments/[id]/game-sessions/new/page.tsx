"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { createGameSession } from "@/lib/api";
import { toast } from "sonner";

const gameSessionSchema = z.object({
  n_courts: z.number().min(1).max(10),
  n_players_per_team: z.number().min(1).max(4),
  n_game_points: z.number().min(1).max(100),
  resting_points: z.number().min(0).max(100).optional(),
});

type GameSessionFormData = z.infer<typeof gameSessionSchema>;

export default function NewGameSessionPage() {
  const params = useParams();
  const router = useRouter();
  const tournamentId = Number(params.id);
  const supabase = createClient();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activePlayerCount, setActivePlayerCount] = useState<number>(0);
  const [isLoadingPlayers, setIsLoadingPlayers] = useState(true);
  const [isLoadingDefaults, setIsLoadingDefaults] = useState(true);

  const form = useForm<GameSessionFormData>({
    resolver: zodResolver(gameSessionSchema),
    defaultValues: {
      n_courts: 2,
      n_players_per_team: 2,
      n_game_points: 24,
      resting_points: 12,
    },
  });

  // Fetch previous game session to use as defaults
  useEffect(() => {
    async function fetchPreviousGameSession() {
      setIsLoadingDefaults(true);
      try {
        const { data, error } = await supabase
          .from("game_sessions")
          .select("id, n_courts, n_game_points, resting_points")
          .eq("tournament_id", tournamentId)
          .order("created_at", { ascending: false })
          .limit(1)
          .single();

        if (data && !error) {
          // Fetch the first court session to get n_players_each_team
          const { data: courtData } = await supabase
            .from("court_sessions")
            .select("n_players_each_team")
            .eq("game_session_id", data.id)
            .limit(1)
            .single();

          // Set form values from previous session
          form.reset({
            n_courts: data.n_courts,
            n_players_per_team: courtData?.n_players_each_team || 2,
            n_game_points: data.n_game_points || 24,
            resting_points: data.resting_points || 12,
          });
        }
      } catch (error) {
        // No previous session or error - use defaults (already set)
        console.log("No previous game session found, using defaults");
      } finally {
        setIsLoadingDefaults(false);
      }
    }

    fetchPreviousGameSession();
  }, [tournamentId]);

  // Fetch active player count
  useEffect(() => {
    async function fetchActivePlayerCount() {
      setIsLoadingPlayers(true);
      try {
        const { count } = await supabase
          .from("players")
          .select("*", { count: "exact", head: true })
          .eq("tournament_id", tournamentId)
          .eq("is_active", true);
        
        setActivePlayerCount(count || 0);
      } catch (error) {
        console.error("Error fetching player count:", error);
      } finally {
        setIsLoadingPlayers(false);
      }
    }
    
    fetchActivePlayerCount();
  }, [tournamentId]);

  // Watch form values to calculate required players
  const nCourts = form.watch("n_courts");
  const nPlayersPerTeam = form.watch("n_players_per_team");
  const requiredPlayers = nCourts * nPlayersPerTeam * 2;
  const hasEnoughPlayers = !isLoadingPlayers && activePlayerCount >= requiredPlayers;
  
  // Handle game points blur - suggest resting points when user finishes editing
  const handleGamePointsBlur = (currentValue: number) => {
    const halfPoints = currentValue / 2;
    const currentRestingPoints = form.getValues("resting_points") || 0;
    
    // Only ask if the current resting points isn't already half
    if (currentRestingPoints !== halfPoints) {
      const shouldUpdate = window.confirm(
        `Would you like to set resting points to ${halfPoints} (half of ${currentValue} game points)?`
      );
      
      if (shouldUpdate) {
        form.setValue("resting_points", halfPoints);
      }
    }
  };

  async function onSubmit(data: GameSessionFormData) {
    // Validate player count before making API call
    const required = data.n_courts * data.n_players_per_team * 2;
    if (activePlayerCount < required) {
      const message = `Not enough players. Need ${required}, have ${activePlayerCount}`;
      setErrorMessage(message);
      toast.error(message);
      return; // Don't make API call
    }

    setIsSubmitting(true);
    setErrorMessage(null); // Clear previous errors

    try {
      // Build court configs array - all courts have same player count for MVP
      const court_configs = Array.from({ length: data.n_courts }, () => ({
        n_players_each_team: data.n_players_per_team,
      }));

      const response = await createGameSession(tournamentId, {
        n_courts: data.n_courts,
        court_configs,
        n_game_points: data.n_game_points,
        resting_points: data.resting_points,
      });

      toast.success("Game session created successfully!");
      router.push(
        `/tournaments/${tournamentId}/game-sessions/${response.id}`
      );
    } catch (error: any) {
      // Don't log to console - we're displaying it in the UI
      const message = error.message || "Failed to create game session. Please try again.";
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <Link href={`/tournaments/${tournamentId}/game-sessions`}>
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Game Sessions
          </Button>
        </Link>
      </div>

          {!hasEnoughPlayers && !isLoadingPlayers && !isLoadingDefaults && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Not Enough Active Players</AlertTitle>
              <AlertDescription>
                This configuration needs {requiredPlayers} active players, but you
                only have {activePlayerCount}.{" "}
                <Link
                  href={`/tournaments/${tournamentId}/players`}
                  className="underline font-medium"
                >
                  Add or activate players
                </Link>{" "}
                to continue, or reduce the number of courts/players per team.
              </AlertDescription>
            </Alert>
          )}

      {errorMessage && hasEnoughPlayers && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {errorMessage}{" "}
            <Link
              href={`/tournaments/${tournamentId}/players`}
              className="underline font-medium"
            >
              Manage players
            </Link>
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Start New Game Session</CardTitle>
          <CardDescription>
            Configure the settings for your next game round
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="n_courts"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Number of Courts *</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(Number(value))}
                      value={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select number of courts" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                          <SelectItem key={num} value={num.toString()}>
                            {num} {num === 1 ? "Court" : "Courts"}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      How many courts will be playing simultaneously
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="n_players_per_team"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Players Per Team *</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(Number(value))}
                      value={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select players per team" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {[1, 2, 3, 4].map((num) => (
                          <SelectItem key={num} value={num.toString()}>
                            {num}v{num}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      How many players on each team per court
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="n_game_points"
                render={({ field }) => {
                  const previousValue = useRef(field.value || 24);
                  
                  return (
                    <FormItem>
                      <FormLabel>Total Points Per Game *</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="24"
                          {...field}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (value !== "" && value !== "0") {
                              previousValue.current = Number(value);
                            }
                            field.onChange(value === "" ? "" : Number(value));
                          }}
                          onBlur={(e) => {
                            const value = e.target.value;
                            // If empty, restore to previous valid value
                            if (value === "" || value === "0") {
                              field.onChange(previousValue.current);
                            } else {
                              field.onChange(Number(value));
                            }
                            field.onBlur();
                            // Check if we should suggest resting points
                            const finalValue = Number(e.target.value || previousValue.current);
                            if (finalValue > 0) {
                              handleGamePointsBlur(finalValue);
                            }
                          }}
                        />
                      </FormControl>
                      <FormDescription>
                        Mexicano-style: Play exactly this many points (e.g., 24
                        points total, could be 12-12, 15-9, etc.)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  );
                }}
              />

              <FormField
                control={form.control}
                name="resting_points"
                render={({ field }) => {
                  const previousValue = useRef(field.value || 12);
                  
                  return (
                    <FormItem>
                      <FormLabel>Resting Points</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          step="0.5"
                          placeholder="12"
                          {...field}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (value !== "" && value !== "0") {
                              previousValue.current = Number(value);
                            }
                            field.onChange(value === "" ? "" : Number(value));
                          }}
                          onBlur={(e) => {
                            const value = e.target.value;
                            // If empty, restore to previous valid value
                            if (value === "" || value === "0") {
                              field.onChange(previousValue.current);
                            } else {
                              field.onChange(Number(value));
                            }
                            field.onBlur();
                          }}
                        />
                      </FormControl>
                      <FormDescription>
                        Points awarded to players not playing this round (typically
                        half of game points)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  );
                }}
              />

              <div className="flex gap-4 pt-4">
                <Button 
                  type="submit" 
                  disabled={isSubmitting || !hasEnoughPlayers || isLoadingPlayers || isLoadingDefaults} 
                  className="flex-1"
                >
                  {isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {isLoadingPlayers || isLoadingDefaults
                    ? "Loading..."
                    : !hasEnoughPlayers
                    ? `Need ${requiredPlayers - activePlayerCount} More Players`
                    : "Create Game Session"}
                </Button>
                <Link
                  href={`/tournaments/${tournamentId}/game-sessions`}
                  className="flex-1"
                >
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full"
                    disabled={isSubmitting}
                  >
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </main>
  );
}


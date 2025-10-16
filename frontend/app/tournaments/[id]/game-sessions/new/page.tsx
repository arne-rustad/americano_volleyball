"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { z } from "zod";

import { Button } from "@/components/ui/button";
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
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<GameSessionFormData>({
    resolver: zodResolver(gameSessionSchema),
    defaultValues: {
      n_courts: 2,
      n_players_per_team: 2,
      n_game_points: 24,
      resting_points: 12,
    },
  });

  // Watch for changes in game points and ask if user wants to update resting points
  const gamePoints = form.watch("n_game_points");
  const [previousGamePoints, setPreviousGamePoints] = useState(24);

  useEffect(() => {
    if (gamePoints && gamePoints !== previousGamePoints) {
      const halfPoints = gamePoints / 2;
      const currentRestingPoints = form.getValues("resting_points") || 0;
      
      // Only ask if the current resting points isn't already half
      if (currentRestingPoints !== halfPoints) {
        const shouldUpdate = window.confirm(
          `Game points changed to ${gamePoints}. Would you like to set resting points to ${halfPoints} (half of game points)?`
        );
        
        if (shouldUpdate) {
          form.setValue("resting_points", halfPoints);
        }
      }
      
      setPreviousGamePoints(gamePoints);
    }
  }, [gamePoints]);

  async function onSubmit(data: GameSessionFormData) {
    setIsSubmitting(true);

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
    } catch (error) {
      console.error("Error creating game session:", error);
      toast.error("Failed to create game session. Please try again.");
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
                      defaultValue={field.value.toString()}
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
                      defaultValue={field.value.toString()}
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
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Total Points Per Game *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="24"
                        {...field}
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>
                      Mexicano-style: Play exactly this many points (e.g., 24
                      points total, could be 12-12, 15-9, etc.)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="resting_points"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Resting Points</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.5"
                        placeholder="12"
                        {...field}
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>
                      Points awarded to players not playing this round (typically
                      half of game points)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-4 pt-4">
                <Button type="submit" disabled={isSubmitting} className="flex-1">
                  {isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Create Game Session
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


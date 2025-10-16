"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Plus, Pencil, Trash2, Users, UserCheck, UserX } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "@/components/empty-state";
import { createClient } from "@/lib/supabase";
import { playerSchema, PlayerFormData } from "@/lib/validations";
import { Database } from "@/lib/database.types";
import { toast } from "sonner";

type Player = Database["public"]["Tables"]["players"]["Row"];
type Tournament = Database["public"]["Tables"]["tournaments"]["Row"];

export default function PlayersPage() {
  const params = useParams();
  const tournamentId = Number(params.id);
  const supabase = createClient();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);
  const [deletingPlayer, setDeletingPlayer] = useState<Player | null>(null);

  const form = useForm<PlayerFormData>({
    resolver: zodResolver(playerSchema),
    defaultValues: {
      name: "",
      gender: undefined,
    },
  });

  useEffect(() => {
    fetchTournamentAndPlayers();
  }, [tournamentId]);

  async function fetchTournamentAndPlayers() {
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
          .order("name"),
      ]);

      if (tournamentRes.error) throw tournamentRes.error;
      if (playersRes.error) throw playersRes.error;

      setTournament(tournamentRes.data);
      setPlayers(playersRes.data || []);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load players");
    } finally {
      setIsLoading(false);
    }
  }

  function openAddDialog() {
    setEditingPlayer(null);
    form.reset({
      name: "",
      gender: undefined,
    });
    setIsDialogOpen(true);
  }

  function openEditDialog(player: Player) {
    setEditingPlayer(player);
    form.reset({
      name: player.name,
      gender: player.gender as "male" | "female" | undefined,
    });
    setIsDialogOpen(true);
  }

  function openDeleteDialog(player: Player) {
    setDeletingPlayer(player);
    setIsDeleteDialogOpen(true);
  }

  async function onSubmit(data: PlayerFormData) {
    try {
      if (editingPlayer) {
        // Update existing player
        const { error } = await supabase
          .from("players")
          .update({
            name: data.name,
            gender: data.gender || null,
          })
          .eq("id", editingPlayer.id);

        if (error) throw error;
        toast.success("Player updated successfully");
      } else {
        // Add new player
        const { error } = await supabase.from("players").insert([
          {
            tournament_id: tournamentId,
            name: data.name,
            gender: data.gender || null,
            score: 0,
            games_played: 0,
          },
        ]);

        if (error) throw error;
        toast.success("Player added successfully");
      }

      setIsDialogOpen(false);
      fetchTournamentAndPlayers();
    } catch (error) {
      console.error("Error saving player:", error);
      toast.error("Failed to save player");
    }
  }

  async function handleDelete() {
    if (!deletingPlayer) return;

    try {
      const { error } = await supabase
        .from("players")
        .delete()
        .eq("id", deletingPlayer.id);

      if (error) throw error;

      toast.success("Player deleted successfully");
      setIsDeleteDialogOpen(false);
      setDeletingPlayer(null);
      fetchTournamentAndPlayers();
    } catch (error) {
      console.error("Error deleting player:", error);
      toast.error("Failed to delete player");
    }
  }

  async function handleToggleActive(player: Player) {
    try {
      const { error } = await supabase
        .from("players")
        .update({ is_active: !player.is_active })
        .eq("id", player.id);

      if (error) throw error;

      toast.success(
        !player.is_active
          ? `${player.name} is now active`
          : `${player.name} is now inactive`
      );
      fetchTournamentAndPlayers();
    } catch (error) {
      console.error("Error toggling player status:", error);
      toast.error("Failed to update player status");
    }
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
        <h1 className="text-3xl font-bold">Players</h1>
        <Button onClick={openAddDialog} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Player
        </Button>
      </div>

      {players.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No players yet"
          description="Add players to start your tournament"
          action={
            <Button onClick={openAddDialog} className="gap-2">
              <Plus className="h-4 w-4" />
              Add First Player
            </Button>
          }
        />
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                {tournament?.is_mix_tournament && (
                  <TableHead>Gender</TableHead>
                )}
                <TableHead>Status</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Games Played</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {players.map((player) => (
                <TableRow key={player.id} className={!player.is_active ? "opacity-60" : ""}>
                  <TableCell className="font-medium">{player.name}</TableCell>
                  {tournament?.is_mix_tournament && (
                    <TableCell className="capitalize">
                      {player.gender || "-"}
                    </TableCell>
                  )}
                  <TableCell>
                    <Button
                      variant={player.is_active ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleToggleActive(player)}
                      className="gap-2"
                    >
                      {player.is_active ? (
                        <>
                          <UserCheck className="h-4 w-4" />
                          Active
                        </>
                      ) : (
                        <>
                          <UserX className="h-4 w-4" />
                          Inactive
                        </>
                      )}
                    </Button>
                  </TableCell>
                  <TableCell>{player.score}</TableCell>
                  <TableCell>{player.games_played}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDialog(player)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openDeleteDialog(player)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingPlayer ? "Edit Player" : "Add New Player"}
            </DialogTitle>
            <DialogDescription>
              {editingPlayer
                ? "Update player information"
                : "Add a new player to the tournament"}
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="Player name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {tournament?.is_mix_tournament && (
                <FormField
                  control={form.control}
                  name="gender"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Gender</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {editingPlayer ? "Update" : "Add"} Player
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Player</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {deletingPlayer?.name}? This
              action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </main>
  );
}


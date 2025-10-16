import { ReactNode } from "react";
import { Navigation } from "@/components/navigation";
import { TournamentTabs } from "@/components/tournament-tabs";
import { createClient } from "@/lib/supabase";
import { notFound } from "next/navigation";

export default async function TournamentLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supabase = createClient();

  const { data: tournament, error } = await supabase
    .from("tournaments")
    .select("id, name")
    .eq("id", id)
    .single();

  if (error || !tournament) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation tournamentName={tournament.name} />
      <TournamentTabs tournamentId={Number(id)} />
      {children}
    </div>
  );
}


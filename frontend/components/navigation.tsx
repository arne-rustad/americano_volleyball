"use client";

import Link from "next/link";
import { Trophy } from "lucide-react";

interface NavigationProps {
  tournamentName?: string;
}

export function Navigation({ tournamentName }: NavigationProps) {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold text-lg hover:opacity-80 transition-opacity"
        >
          <Trophy className="h-6 w-6" />
          <span>Americano Volleyball</span>
        </Link>

        {tournamentName && (
          <div className="text-sm text-muted-foreground font-medium">
            {tournamentName}
          </div>
        )}
      </div>
    </nav>
  );
}


'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export default function TestPage() {
  const [tournaments, setTournaments] = useState<any[]>([])
  const [players, setPlayers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        // Test: Fetch tournaments
        const { data: tournamentsData, error: tournamentsError } = await supabase
          .from('tournaments')
          .select('*')
          .order('created_at', { ascending: false })

        if (tournamentsError) throw tournamentsError

        // Test: Fetch players with scores
        const { data: playersData, error: playersError } = await supabase
          .from('players')
          .select('*')
          .order('score', { ascending: false })
          .limit(10)

        if (playersError) throw playersError

        setTournaments(tournamentsData || [])
        setPlayers(playersData || [])
        setLoading(false)
      } catch (err: any) {
        setError(err.message)
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <Card>
          <CardHeader>
            <CardTitle>Loading...</CardTitle>
          </CardHeader>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-4xl font-bold">Frontend Test Page</h1>

      <Card>
        <CardHeader>
          <CardTitle>✅ Connection Status</CardTitle>
          <CardDescription>Supabase connection is working!</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p>✅ TypeScript types loaded</p>
            <p>✅ Supabase client initialized</p>
            <p>✅ Database queries working</p>
            <p>✅ shadcn/ui components rendering</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tournaments ({tournaments.length})</CardTitle>
          <CardDescription>Latest tournaments from database</CardDescription>
        </CardHeader>
        <CardContent>
          {tournaments.length === 0 ? (
            <p className="text-muted-foreground">No tournaments found</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tournaments.map((tournament) => (
                  <TableRow key={tournament.id}>
                    <TableCell>{tournament.id}</TableCell>
                    <TableCell className="font-medium">{tournament.name}</TableCell>
                    <TableCell>
                      <Badge variant={tournament.is_mix_tournament ? 'default' : 'secondary'}>
                        {tournament.is_mix_tournament ? 'Mix' : 'Regular'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(tournament.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Players ({players.length})</CardTitle>
          <CardDescription>Sorted by score (descending)</CardDescription>
        </CardHeader>
        <CardContent>
          {players.length === 0 ? (
            <p className="text-muted-foreground">No players found</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Gender</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Games</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {players.map((player) => (
                  <TableRow key={player.id}>
                    <TableCell className="font-medium">{player.name}</TableCell>
                    <TableCell>
                      {player.gender && (
                        <Badge variant="outline">
                          {player.gender}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="font-bold">{player.score}</TableCell>
                    <TableCell className="text-muted-foreground">{player.games_played}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Environment Variables</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 font-mono text-sm">
            <p>✅ NEXT_PUBLIC_SUPABASE_URL: {process.env.NEXT_PUBLIC_SUPABASE_URL?.slice(0, 30)}...</p>
            <p>✅ NEXT_PUBLIC_SUPABASE_ANON_KEY: {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.slice(0, 30)}...</p>
            <p>✅ NEXT_PUBLIC_API_URL: {process.env.NEXT_PUBLIC_API_URL}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


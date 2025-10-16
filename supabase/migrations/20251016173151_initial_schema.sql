-- Initial schema for Americano Volleyball Tournament App
-- This matches the schema already deployed to production

-- Create tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    is_mix_tournament BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_tournaments_user_id ON tournaments(user_id);

-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    gender VARCHAR CHECK (gender IN ('male', 'female')),
    score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    games_played INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_players_tournament_id ON players(tournament_id);

-- Create game_sessions table
CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    n_courts INTEGER NOT NULL,
    n_game_points INTEGER,
    resting_points DOUBLE PRECISION,
    finished BOOLEAN NOT NULL DEFAULT FALSE,
    score_added_to_players BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_game_sessions_tournament_id ON game_sessions(tournament_id);

-- Create court_sessions table
CREATE TABLE IF NOT EXISTS court_sessions (
    id SERIAL PRIMARY KEY,
    game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    court_index INTEGER NOT NULL,
    n_players_each_team INTEGER NOT NULL,
    score_team_a INTEGER,
    score_team_b INTEGER
);

CREATE INDEX IF NOT EXISTS idx_court_sessions_game_session_id ON court_sessions(game_session_id);

-- Create court_players junction table
CREATE TABLE IF NOT EXISTS court_players (
    id SERIAL PRIMARY KEY,
    court_session_id INTEGER NOT NULL REFERENCES court_sessions(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    team VARCHAR NOT NULL CHECK (team IN ('A', 'B'))
);

CREATE INDEX IF NOT EXISTS idx_court_players_court_session_id ON court_players(court_session_id);
CREATE INDEX IF NOT EXISTS idx_court_players_player_id ON court_players(player_id);


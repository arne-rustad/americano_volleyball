-- Add timestamps and status improvements

-- Add timestamps for better tracking
ALTER TABLE players ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;

-- Add status enum for better state management
DO $$ BEGIN
    CREATE TYPE game_status AS ENUM ('pending', 'in_progress', 'completed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS status game_status DEFAULT 'pending';

-- Track current active session (optional but useful)
ALTER TABLE tournaments ADD COLUMN IF NOT EXISTS current_game_session_id INTEGER 
  REFERENCES game_sessions(id);

-- Remove redundant field
ALTER TABLE game_sessions DROP COLUMN IF EXISTS score_added_to_players;

-- Add index for status queries
CREATE INDEX IF NOT EXISTS idx_game_sessions_status ON game_sessions(status);


-- Seed data for local development and testing

-- Insert test tournament
INSERT INTO tournaments (name, is_mix_tournament, user_id) 
VALUES ('Test Tournament', false, 'test-user-123');

-- Insert test players
INSERT INTO players (tournament_id, name, gender, score, games_played) VALUES
(1, 'Alice', 'female', 0, 0),
(1, 'Bob', 'male', 0, 0),
(1, 'Charlie', 'male', 0, 0),
(1, 'Diana', 'female', 0, 0),
(1, 'Eve', 'female', 0, 0),
(1, 'Frank', 'male', 0, 0),
(1, 'Grace', 'female', 0, 0),
(1, 'Henry', 'male', 0, 0);

-- Insert a mix tournament for testing
INSERT INTO tournaments (name, is_mix_tournament, user_id) 
VALUES ('Mix Tournament Test', true, 'test-user-123');

-- Insert players for mix tournament  
INSERT INTO players (tournament_id, name, gender, score, games_played) VALUES
(2, 'Maria', 'female', 0, 0),
(2, 'John', 'male', 0, 0),
(2, 'Sarah', 'female', 0, 0),
(2, 'Mike', 'male', 0, 0),
(2, 'Emma', 'female', 0, 0),
(2, 'Tom', 'male', 0, 0);


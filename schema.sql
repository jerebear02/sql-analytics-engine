CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    conference TEXT NOT NULL,
    division TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    team_id INTEGER REFERENCES teams(id),
    position TEXT NOT NULL,
    age INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id),
    season_id INTEGER REFERENCES seasons(id),
    games INTEGER NOT NULL,
    points_per_game REAL NOT NULL,
    rebounds_per_game REAL NOT NULL,
    assists_per_game REAL NOT NULL,
    steals_per_game REAL NOT NULL,
    blocks_per_game REAL NOT NULL,
    fgm_per_game REAL NOT NULL,
    fga_per_game REAL NOT NULL,
    ftm_per_game REAL NOT NULL,
    fta_per_game REAL NOT NULL,
    minutes_per_game REAL NOT NULL,
    UNIQUE(player_id, season_id)
);

-- Indexes for query performance (good to highlight on GitHub)
CREATE INDEX IF NOT EXISTS idx_stats_player  ON stats(player_id);
CREATE INDEX IF NOT EXISTS idx_stats_season  ON stats(season_id);
CREATE INDEX IF NOT EXISTS idx_players_team  ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_pos   ON players(position);

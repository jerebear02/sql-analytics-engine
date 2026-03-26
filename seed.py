import sqlite3
import random

DB_PATH = "nba_analytics.db"

TEAMS = [
    ("Lakers",   "Los Angeles",   "West", "Pacific"),
    ("Celtics",  "Boston",        "East", "Atlantic"),
    ("Warriors", "Golden State",  "West", "Pacific"),
    ("Heat",     "Miami",         "East", "Southeast"),
    ("Nuggets",  "Denver",        "West", "Northwest"),
    ("Bucks",    "Milwaukee",     "East", "Central"),
    ("Suns",     "Phoenix",       "West", "Pacific"),
    ("76ers",    "Philadelphia",  "East", "Atlantic"),
    ("Clippers", "Los Angeles",   "West", "Pacific"),
    ("Nets",     "Brooklyn",      "East", "Atlantic"),
]

# (name, team_idx, position, age, base_ppg, base_rpg, base_apg)
PLAYERS = [
    ("LeBron James",           0, "SF", 39, 25.0, 7.5,  8.0),
    ("Anthony Davis",          0, "C",  31, 24.0, 12.0, 3.5),
    ("Austin Reaves",          0, "SG", 25, 15.5, 4.0,  5.0),
    ("Jayson Tatum",           1, "SF", 26, 27.0, 8.5,  4.5),
    ("Jaylen Brown",           1, "SG", 27, 22.0, 5.5,  3.5),
    ("Al Horford",             1, "C",  37, 10.5, 6.5,  2.5),
    ("Stephen Curry",          2, "PG", 36, 26.5, 4.5,  6.0),
    ("Klay Thompson",          2, "SG", 34, 17.5, 3.5,  2.5),
    ("Draymond Green",         2, "PF", 34,  9.0, 6.5,  6.5),
    ("Jimmy Butler",           3, "SF", 34, 21.0, 5.5,  5.0),
    ("Bam Adebayo",            3, "C",  26, 19.5, 10.0, 3.5),
    ("Tyler Herro",            3, "SG", 24, 20.0, 5.0,  4.5),
    ("Nikola Jokic",           4, "C",  29, 26.0, 12.0, 9.0),
    ("Jamal Murray",           4, "PG", 27, 21.0, 4.0,  6.5),
    ("Michael Porter Jr.",     4, "SF", 26, 17.0, 7.5,  2.0),
    ("Giannis Antetokounmpo",  5, "PF", 29, 30.0, 12.0, 6.0),
    ("Damian Lillard",         5, "PG", 33, 24.0, 4.5,  7.0),
    ("Khris Middleton",        5, "SF", 33, 15.0, 5.0,  5.0),
    ("Kevin Durant",           6, "SF", 35, 27.0, 6.5,  5.0),
    ("Devin Booker",           6, "SG", 27, 25.0, 4.5,  6.5),
    ("Jusuf Nurkic",           6, "C",  29, 12.5, 10.5, 2.5),
    ("Joel Embiid",            7, "C",  30, 33.0, 11.0, 5.5),
    ("Tyrese Maxey",           7, "PG", 23, 25.0, 3.5,  6.5),
    ("Kelly Oubre Jr.",        7, "SF", 28, 15.0, 4.5,  2.0),
    ("Kawhi Leonard",          8, "SF", 32, 22.0, 6.5,  3.5),
    ("Paul George",            8, "SF", 33, 21.0, 5.5,  4.5),
    ("Russell Westbrook",      8, "PG", 35, 11.5, 5.5,  8.0),
    ("Mikal Bridges",          9, "SF", 27, 22.0, 4.5,  3.5),
    ("Cam Thomas",             9, "SG", 22, 22.0, 3.5,  3.5),
    ("Ben Simmons",            9, "PG", 27, 10.0, 8.0,  6.0),
]


def jitter(val, pct=0.14):
    return round(max(0.5, val * random.uniform(1 - pct, 1 + pct)), 1)


def seed():
    random.seed(42)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Teams
    for t in TEAMS:
        cur.execute(
            "INSERT INTO teams (name, city, conference, division) VALUES (?,?,?,?)", t
        )

    team_ids = [r[0] for r in cur.execute("SELECT id FROM teams ORDER BY id").fetchall()]

    # Seasons
    for year in [2022, 2023, 2024]:
        cur.execute("INSERT INTO seasons (year) VALUES (?)", (year,))

    season_map = {
        r[1]: r[0]
        for r in cur.execute("SELECT id, year FROM seasons").fetchall()
    }

    # Players
    for p in PLAYERS:
        name, team_idx, pos, age, *_ = p
        cur.execute(
            "INSERT INTO players (name, team_id, position, age) VALUES (?,?,?,?)",
            (name, team_ids[team_idx], pos, age),
        )

    player_ids = [r[0] for r in cur.execute("SELECT id FROM players ORDER BY id").fetchall()]

    # Stats — simulate slight progression over 3 seasons
    for i, player in enumerate(PLAYERS):
        _, _, _, _, base_ppg, base_rpg, base_apg = player
        pid = player_ids[i]

        for year in [2022, 2023, 2024]:
            sid = season_map[year]
            trend = (year - 2022) * random.uniform(-0.4, 1.0)

            ppg = max(5.0, jitter(base_ppg + trend))
            rpg = max(1.0, jitter(base_rpg))
            apg = max(0.5, jitter(base_apg))
            spg = round(random.uniform(0.4, 2.2), 1)
            bpg = round(random.uniform(0.1, 2.0), 1)
            fgm = round(ppg / random.uniform(4.5, 5.5), 1)
            fga = round(fgm / random.uniform(0.40, 0.55), 1)
            ftm = round(random.uniform(1.5, 6.5), 1)
            fta = round(ftm / random.uniform(0.72, 0.92), 1)
            mpg = round(random.uniform(27, 37), 1)
            games = random.randint(52, 82)

            cur.execute(
                """INSERT INTO stats
                   (player_id, season_id, games, points_per_game, rebounds_per_game,
                    assists_per_game, steals_per_game, blocks_per_game,
                    fgm_per_game, fga_per_game, ftm_per_game, fta_per_game, minutes_per_game)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (pid, sid, games, ppg, rpg, apg, spg, bpg, fgm, fga, ftm, fta, mpg),
            )

    conn.commit()
    conn.close()
    print("✓ Database seeded.")


if __name__ == "__main__":
    seed()

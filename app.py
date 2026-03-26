"""
SQL Analytics Engine — Flask Backend
Showcases: Window Functions, CTEs, LAG/LEAD, NTILE, RANK, Indexes
Dataset:   NBA-style player stats across 3 seasons
"""

import os
import sqlite3

from flask import Flask, jsonify, render_template

app = Flask(__name__)
DB_PATH = "nba_analytics.db"


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with open("schema.sql") as f:
        conn.executescript(f.read())
    conn.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/top-scorers")
def top_scorers():
    """
    RANK() window function — ranks all players by PPG within each season.
    Returns top 10 for the latest season, including their career average.
    """
    conn = get_db()
    rows = conn.execute("""
        WITH ranked AS (
            SELECT
                p.name,
                p.position,
                t.name           AS team,
                s.year           AS season,
                st.points_per_game,
                RANK() OVER (
                    PARTITION BY s.year
                    ORDER BY st.points_per_game DESC
                )                AS rank,
                ROUND(
                    AVG(st.points_per_game) OVER (PARTITION BY p.id), 1
                )                AS career_avg
            FROM stats   st
            JOIN players p  ON st.player_id  = p.id
            JOIN teams   t  ON p.team_id     = t.id
            JOIN seasons s  ON st.season_id  = s.id
        )
        SELECT * FROM ranked
        WHERE rank <= 10 AND season = (SELECT MAX(year) FROM seasons)
        ORDER BY rank
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/yoy-improvement")
def yoy_improvement():
    """
    LAG() window function — compares each player's PPG to the previous season.
    Highlights the biggest year-over-year jumps.
    """
    conn = get_db()
    rows = conn.execute("""
        WITH season_stats AS (
            SELECT
                p.name,
                p.position,
                t.name                  AS team,
                s.year,
                st.points_per_game,
                st.assists_per_game,
                LAG(st.points_per_game) OVER (
                    PARTITION BY p.id ORDER BY s.year
                )                       AS prev_ppg,
                LAG(st.assists_per_game) OVER (
                    PARTITION BY p.id ORDER BY s.year
                )                       AS prev_apg
            FROM stats   st
            JOIN players p ON st.player_id = p.id
            JOIN teams   t ON p.team_id    = t.id
            JOIN seasons s ON st.season_id = s.id
        )
        SELECT
            name, position, team, year,
            points_per_game                             AS ppg,
            prev_ppg,
            ROUND(points_per_game - prev_ppg, 1)        AS ppg_change,
            ROUND(assists_per_game - prev_apg, 1)       AS apg_change
        FROM season_stats
        WHERE prev_ppg IS NOT NULL
          AND year = (SELECT MAX(year) FROM seasons)
        ORDER BY ppg_change DESC
        LIMIT 15
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/efficiency")
def efficiency():
    """
    CTE + NTILE() — computes a classic NBA efficiency rating, then buckets
    players into percentile deciles using NTILE(10).
    Formula: PTS + REB + AST + STL + BLK – missed FG – missed FT
    """
    conn = get_db()
    rows = conn.execute("""
        WITH eff AS (
            SELECT
                p.name,
                p.position,
                t.name  AS team,
                s.year,
                ROUND(
                    st.points_per_game
                    + st.rebounds_per_game
                    + st.assists_per_game
                    + st.steals_per_game
                    + st.blocks_per_game
                    - (st.fga_per_game - st.fgm_per_game)
                    - (st.fta_per_game - st.ftm_per_game),
                    1
                )       AS efficiency,
                st.points_per_game   AS ppg,
                st.rebounds_per_game AS rpg,
                st.assists_per_game  AS apg,
                NTILE(10) OVER (
                    ORDER BY st.points_per_game
                           + st.rebounds_per_game
                           + st.assists_per_game
                )       AS decile
            FROM stats   st
            JOIN players p ON st.player_id = p.id
            JOIN teams   t ON p.team_id    = t.id
            JOIN seasons s ON st.season_id = s.id
            WHERE s.year = (SELECT MAX(year) FROM seasons)
        )
        SELECT *, decile * 10 AS percentile
        FROM eff
        ORDER BY efficiency DESC
        LIMIT 15
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/team-breakdown")
def team_breakdown():
    """
    Nested CTEs + RANK() OVER PARTITION — aggregates team stats,
    then ranks each team within its conference by offensive output.
    """
    conn = get_db()
    rows = conn.execute("""
        WITH team_agg AS (
            SELECT
                t.name          AS team,
                t.conference,
                s.year,
                COUNT(DISTINCT p.id)            AS roster_size,
                ROUND(AVG(st.points_per_game),1) AS avg_ppg,
                ROUND(AVG(st.assists_per_game),1) AS avg_apg,
                ROUND(AVG(st.rebounds_per_game),1) AS avg_rpg,
                ROUND(MAX(st.points_per_game),1)   AS star_ppg
            FROM stats   st
            JOIN players p ON st.player_id = p.id
            JOIN teams   t ON p.team_id    = t.id
            JOIN seasons s ON st.season_id = s.id
            WHERE s.year = (SELECT MAX(year) FROM seasons)
            GROUP BY t.id, s.year
        ),
        conf_ranked AS (
            SELECT *,
                RANK() OVER (
                    PARTITION BY conference
                    ORDER BY avg_ppg DESC
                ) AS conf_rank
            FROM team_agg
        )
        SELECT * FROM conf_ranked
        ORDER BY avg_ppg DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/consistent-performers")
def consistent_performers():
    """
    Multi-season CTE — finds players with 2+ seasons of 15+ PPG
    and sorts by lowest PPG range (most consistent at the top).
    """
    conn = get_db()
    rows = conn.execute("""
        WITH career AS (
            SELECT
                p.name,
                p.position,
                t.name                              AS team,
                COUNT(s.id)                         AS seasons_played,
                ROUND(AVG(st.points_per_game),  1)  AS avg_ppg,
                ROUND(MIN(st.points_per_game),  1)  AS min_ppg,
                ROUND(MAX(st.points_per_game),  1)  AS max_ppg,
                ROUND(MAX(st.points_per_game)
                      - MIN(st.points_per_game), 1) AS ppg_range,
                ROUND(AVG(st.assists_per_game), 1)  AS avg_apg,
                ROUND(AVG(st.rebounds_per_game),1)  AS avg_rpg
            FROM stats   st
            JOIN players p ON st.player_id = p.id
            JOIN teams   t ON p.team_id    = t.id
            JOIN seasons s ON st.season_id = s.id
            GROUP BY p.id
            HAVING seasons_played >= 2
        )
        SELECT * FROM career
        WHERE avg_ppg >= 15
        ORDER BY ppg_range ASC, avg_ppg DESC
        LIMIT 12
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Initializing database...")
        init_db()
        from seed import seed
        seed()
    app.run(debug=True)

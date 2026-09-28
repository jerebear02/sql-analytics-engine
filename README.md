# SQL Analytics Engine

A Flask + SQLite analytics dashboard showcasing advanced SQL on NBA-style player data across 3 seasons.

Built to demonstrate SQL depth for software engineering portfolios.

---

## SQL Concepts Demonstrated

| Feature | Query |
|---|---|
| `RANK()` window function | Top scorers ranked within each season |
| `LAG()` window function | Year-over-year PPG comparison |
| `NTILE(10)` | Percentile bucketing for efficiency |
| Nested CTEs | Team conference rankings |
| `PARTITION BY` | Per-player and per-conference grouping |
| Multi-season aggregation + `HAVING` | Consistent performers filter |
| Indexes | `idx_stats_player`, `idx_stats_season`, `idx_players_team` |

---

## Setup

**1. Clone and install dependencies**
```bash
git clone <https://github.com/jerebear02/sql-analytics-engine.git>
cd sql-analytics-engine
pip install -r requirements.txt
```

**2. Run the app**
```bash
python app.py
```

On first run, the app automatically:
- Creates `nba_analytics.db` from `schema.sql`
- Seeds 30 players, 10 teams, and 3 seasons of stats via `seed.py`

**3. Open the browser**
```
http://localhost:5000
```

---

## Project Structure

```
sql-analytics-engine/
├── app.py            # Flask backend — all SQL queries live here
├── schema.sql        # Table definitions + indexes
├── seed.py           # Data generation (30 players, 3 seasons)
├── requirements.txt
├── README.md
└── templates/
    └── index.html    # Frontend — dark data-terminal UI
```

---

## API Endpoints

| Endpoint | SQL Feature | Description |
|---|---|---|
| `GET /api/top-scorers` | `RANK()`, CTE | Top 10 scorers in latest season |
| `GET /api/yoy-improvement` | `LAG()`, CTE | Biggest year-over-year jumps |
| `GET /api/efficiency` | `NTILE()`, CTE | Player efficiency + percentile rank |
| `GET /api/team-breakdown` | Nested CTEs, `PARTITION BY` | Team stats + conference rank |
| `GET /api/consistent-performers` | Multi-season CTE, `HAVING` | Most consistent 15+ PPG players |

---

## Tech Stack

- **Backend**: Python, Flask, SQLite (`sqlite3` stdlib — no ORM)
- **Frontend**: Vanilla HTML/CSS/JS — no frameworks
- **Database**: SQLite (file-based, zero config)

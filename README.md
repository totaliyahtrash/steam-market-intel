# Steam Market Intel — ETL Pipeline

An end-to-end data engineering pipeline that processes 27,000+ Steam game records into a production-grade PostgreSQL star schema.

## What it does

- Ingests raw Steam game data (27,061 records)
- Cleans and transforms using Pandas — null handling, dtype fixing, feature engineering
- Designs and creates a star schema in PostgreSQL using psycopg2
- Loads dimension and fact tables using SQLAlchemy
- Supports idempotent runs — safe to execute multiple times without duplicate data

## Schema Design

```
dim_developer ──┐
dim_genre     ──┼──► fact_games
dim_release   ──┘
```

| Table | Rows | Description |
|-------|------|-------------|
| dim_developer | 17,102 | Unique game developers |
| dim_genre | 1,551 | Unique genres |
| dim_release | 2,619 | Release dates with year and month |
| fact_games | 27,061 | Core metrics — price, ratings, playtime, rating ratio |

## Tech Stack

- Python 3.14
- Pandas — transformation and feature engineering
- psycopg2 — schema creation, parameterized queries, transactions
- SQLAlchemy — DataFrame to Postgres loading
- PostgreSQL 18

## Project Structure

```
steam-market-intel/
├── extractor.py      # reads raw CSV into DataFrame
├── processor.py      # cleans, transforms, engineers features
├── schema.py         # creates star schema tables with FK constraints
├── loader.py         # loads dimension and fact tables into Postgres
├── main.py           # orchestrates the full pipeline
├── steam.csv         # raw data (not tracked)
└── requirements.txt
```

## Key Engineering Decisions

- **Parameterized queries** throughout — no string concatenation, no SQL injection risk
- **Idempotency check** before dimension loading — pipeline safe to re-run
- **rating_ratio** engineered feature — `positive / (positive + negative)` for clean sentiment scoring
- **Foreign key constraints** enforced at DB level — data integrity guaranteed
- **Separation of concerns** — extract, process, schema, load, orchestrate in separate files

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Author

Dhruv — github.com/totaliyahtrash

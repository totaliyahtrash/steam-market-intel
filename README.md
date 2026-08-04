# Steam Market Intel — Production ETL Pipeline

An end-to-end data engineering pipeline that processes 27,000+ Steam game records into a production-grade PostgreSQL star schema — built with production patterns including logging, config management, idempotency, incremental loading, checkpointing, and retry logic.

## What it does

- Ingests raw Steam game data (27,061 records)
- Cleans and transforms using Pandas — null handling, dtype fixing, feature engineering
- Designs and creates a star schema in PostgreSQL using psycopg2 
- Loads dimension and fact tables using SQLAlchemy
- Supports idempotent runs — safe to execute multiple times without duplicate data
- Incremental loading — watermark-based, only processes new records on each run
- Checkpointing — resumes from last successful step on failure
- Retry logic — exponential backoff on all database operations

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
- PyYAML — config management
- python-dotenv — secrets management

## Project Structure

```
steam-market-intel/
├── extractor.py      # reads raw CSV into DataFrame
├── processor.py      # cleans, transforms, engineers features
├── schema.py         # creates star schema tables with FK constraints
├── loader.py         # loads dimension and fact tables into Postgres
├── checkpoint.py     # saves and loads pipeline run state
├── retry.py          # retry logic with exponential backoff
├── main.py           # orchestrates the full pipeline
├── config.yaml       # non-sensitive config (not tracked)
├── .env              # DB credentials (not tracked)
└── requirements.txt
```

## Production Patterns

**Logging** — every pipeline run produces timestamped, levelled logs to both console and `pipeline.logs`. Named loggers per module (`steam.extractor`, `loader`, `main`) so failures are traceable to the exact file and function.

**Config management** — all hardcoded values moved to `config.yaml` (DB host, port, table names, log level). Secrets live in `.env`. Neither file is tracked by Git.

**Idempotency** — before inserting into `fact_games`, existing `appid`s are fetched and filtered out. Running the pipeline 100 times produces the same result as running it once.

**Incremental loading** — a watermark query fetches the latest `release_date` already in `dim_release`. Only games newer than the watermark are processed. Combined with `appid` deduplication at the boundary.

**Checkpointing** — after each DB operation completes, its status is saved to `checkpoint.json`. On restart after a failure, completed steps are skipped and the pipeline resumes from where it left off. The checkpoint file is deleted on successful completion.

**Retry logic** — all database operations are wrapped in `with_retry()`, which retries up to 3 times with exponential backoff (2s → 4s → 8s) before raising the exception.

## How to run

```bash
pip install -r requirements.txt

# Create a .env file with your DB password
echo "DB_PASSWORD=your_password" > .env

# Create config.yaml with your DB connection details
# (see config.yaml.example if provided)

python main.py
```

## Key Engineering Decisions

- **Parameterized queries** throughout — no string concatenation, no SQL injection risk
- **Separation of concerns** — extract, process, schema, load, checkpoint, retry in separate files
- **rating_ratio** engineered feature — `positive / (positive + negative)` for clean sentiment scoring
- **Foreign key constraints** enforced at DB level — data integrity guaranteed
- **format='mixed'** on date parsing — handles inconsistent date formats in source data gracefully

## Author

Dhruv — [github.com/syntaxdsamurai](https://github.com/totaliyahtrash)

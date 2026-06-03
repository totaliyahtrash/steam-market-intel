from sqlalchemy import create_engine
import pandas as pd
from extractor import extractor
from processor import filter_data
import psycopg2
from schema import schema_design

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers = [
        logging.FileHandler('pipeline.logs'),
        logging.StreamHandler()
    ]
)

loader = logging.getLogger('loader')

engine = create_engine('postgresql+psycopg2://postgres:dhruv@localhost:5432/postgres')
df = filter_data(extractor())

conn = psycopg2.connect(
    host='localhost', port=5432,
    database='postgres', user='postgres', password='dhruv'
)
schema_design(conn)
conn.close()

def load_dimensions(df, engine):
    existing = pd.read_sql("SELECT COUNT(*) as cnt FROM dim_developer", engine)
    if existing['cnt'][0] > 0:
        loader.info("Tables already loaded, skipping...")
        return

    dim_developer = df[['developer']].drop_duplicates()
    dim_developer.columns = ['developer_name']

    dim_release = df[['release_date']].drop_duplicates()
    dim_release['release_year'] = dim_release['release_date'].dt.year
    dim_release['release_month'] = dim_release['release_date'].dt.month

    dim_genre = df[['genres']].drop_duplicates()
    dim_genre.columns = ['genre_name']

    dim_developer.to_sql('dim_developer', engine, if_exists='append', index=False)
    dim_genre.to_sql('dim_genre', engine, if_exists='append', index=False)
    dim_release.to_sql('dim_release', engine, if_exists='append', index=False)

    loader.debug(f"Loaded {len(dim_developer)} developers")
    loader.debug(f"Loaded {len(dim_release)} releases")
    loader.debug(f"Loaded {len(dim_genre)} genres\n")

def load_fact(df, engine):
    dim_dev_db = pd.read_sql("SELECT developer_id, developer_name FROM dim_developer", engine)
    merged_df = pd.merge(df, dim_dev_db, left_on='developer', right_on='developer_name', how='left')

    dim_genre_db = pd.read_sql("SELECT genre_id, genre_name FROM dim_genre", engine)
    merged_df = pd.merge(merged_df, dim_genre_db, left_on='genres', right_on='genre_name', how='left')

    dim_release_db = pd.read_sql("SELECT release_id, release_date FROM dim_release", engine)
    dim_release_db['release_date'] = pd.to_datetime(dim_release_db['release_date'])
    merged_df = pd.merge(merged_df, dim_release_db, left_on='release_date', right_on='release_date', how='left')

    columns_to_drop = ['developer', 'developer_name', 'genres', 'genre_name', 'release_date', 'publisher']
    fact_games = merged_df.drop(columns=columns_to_drop, errors='ignore')

    fact_games.to_sql('fact_games', engine, if_exists='append', index=False)
    loader.info(f"Successfully loaded {len(fact_games)} records into fact_games!")
    loader.info(f"Fact Table Columns: {fact_games.columns.tolist()}")


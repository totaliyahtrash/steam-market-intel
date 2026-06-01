import psycopg2
from sqlalchemy import create_engine
from extractor import extractor
from processor import filter_data
from schema import schema_design
from loader import load_dimensions, load_fact

DATABASE_URL = 'postgresql+psycopg2://postgres:dhruv@localhost:5432/postgres'

DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'dhruv'
}

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    engine = create_engine(DATABASE_URL)

    try:
        schema_design(conn)
        conn.close()

        raw_df = extractor()
        processed_df = filter_data(raw_df)

        load_dimensions(processed_df, engine)
        load_fact(processed_df, engine)

        print("Pipeline completed successfully.")

    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == '__main__':
    main()
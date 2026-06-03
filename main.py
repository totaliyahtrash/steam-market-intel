import psycopg2
from sqlalchemy import create_engine

from extractor import extractor
from processor import filter_data
from schema import schema_design
from loader import load_dimensions, load_fact

import yaml
from dotenv import load_dotenv
import os

import logging
from checkpoint import save_checkpoint, load_checkpoint
from retry import with_retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers = [
        logging.FileHandler('pipeline.logs'),
        logging.StreamHandler()
    ]
)

main1 = logging.getLogger('main')

with open('config.yaml','r') as f:
    configuration = yaml.safe_load(f)
    db = configuration['database']
    port = db['port']
    host = db['host']
    user = db['user']
    name = db['name']

load_dotenv()
password = os.getenv('DB_PASSWORD')

DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'

DB_PARAMS = {
    'host': host,
    'port': port,
    'database': name,
    'user': user,
    'password': password
}

def main():
    engine = create_engine(DATABASE_URL)
    checkpoints = load_checkpoint()

    try:
        if checkpoints.get("schema_design") == "complete":
            main1.info("Skipping schema_design: already complete.")
        else:
            def run_schema_setup():
                conn = psycopg2.connect(**DB_PARAMS)
                schema_design(conn)
                conn.close()
            with_retry(run_schema_setup, retries=3, delay=2)
            save_checkpoint("schema_design", "complete")

        raw_df = extractor()
        processed_df = filter_data(raw_df)

        if checkpoints.get("load_dimensions") == "complete":
            main1.info("Skipping load_dimensions: already complete.")
        else:
            with_retry(lambda: load_dimensions(processed_df, engine), retries=3, delay=2)
            save_checkpoint("load_dimensions", "complete")

        if checkpoints.get("load_fact") == "complete":
            main1.info("Skipping load_fact: already complete.")
        else:
            with_retry(lambda: load_fact(processed_df, engine), retries=3, delay=2)
            save_checkpoint("load_fact", "complete")

        if os.path.exists('checkpoint.json'):
            os.remove('checkpoint.json')

        main1.info('pipeline successful')

    except Exception as e:
        main1.exception(f'Pipeline Failed: {e}')

if __name__ == '__main__':
    main()

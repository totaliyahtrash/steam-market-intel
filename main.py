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
        # Step 1: Schema Design (DB Operation)
        if checkpoints.get("schema_design") == "complete":
            main1.info("Skipping schema_design: already complete.")
        else:
            conn = psycopg2.connect(**DB_PARAMS)
            schema_design(conn)
            conn.close()
            save_checkpoint("schema_design", "complete")

        # In-memory operations: Always run to feed downstream loads
        raw_df = extractor()
        processed_df = filter_data(raw_df)

        # Step 2: Load Dimensions (DB Operation)
        if checkpoints.get("load_dimensions") == "complete":
            main1.info("Skipping load_dimensions: already complete.")
        else:
            load_dimensions(processed_df, engine)
            save_checkpoint("load_dimensions", "complete")

        # Step 3: Load Fact (DB Operation)
        if checkpoints.get("load_fact") == "complete":
            main1.info("Skipping load_fact: already complete.")
        else:
            load_fact(processed_df, engine)
            save_checkpoint("load_fact", "complete")

        # Clean up checkpoint file on full success
        if os.path.exists('checkpoint.json'):
            os.remove('checkpoint.json')

        main1.info('pipeline successful')

    except Exception as e:
        main1.exception(f'Pipeline Failed: {e}')

if __name__ == '__main__':
    main()

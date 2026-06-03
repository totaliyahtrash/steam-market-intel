import pandas as pd


import logging


extract = logging.getLogger('extractor')

def extractor():
    try:
        df = pd.read_csv('steam.csv')
        df.to_json('raw.json',orient='records',indent=4)
        return df
    except FileNotFoundError:
        extract.error("file not found")
    except Exception as e:
        extract.error('Unexpected error occurred')


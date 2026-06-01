import pandas as pd

def extractor():
    try:
        df = pd.read_csv('steam.csv')
        df.to_json('raw.json',orient='records',indent=4)
        return df
    except FileNotFoundError:
        print("file not found")
    except Exception as e:
        print('unexpected error occurred')


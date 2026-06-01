import pandas as pd

def filter_data(df):
    try:
        useless = ['english', 'required_age', 'steamspy_tags', 'median_playtime', 'platforms', 'categories']

        df_clean = df.drop(columns=useless)
        df_clean = df_clean.dropna()

        if 'release_date' in df_clean.columns:
            df_clean['release_date'] = pd.to_datetime(df_clean['release_date'])

        df_clean['rating_ratio'] = df_clean['positive_ratings']/(df_clean['positive_ratings']+df_clean['negative_ratings'])
        return df_clean


    except Exception as e:
        print('Error occurred while cleaning')

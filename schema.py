def schema_design(conn):
    with conn.cursor() as cur:
        cur.execute ('''
        create table if not exists dim_developer(
            developer_id serial primary key,
            developer_name varchar
        )
        ''')

        cur.execute ('''
                   create table if not exists dim_genre(
                        genre_id SERIAL primary key,
                        genre_name VARCHAR
                   )
                   ''')

        cur.execute ('''
                   create table if not exists dim_release(
                        release_id SERIAL primary key,
                        release_date DATE,
                        release_year INT,
                        release_month INT
                   )
                   ''')

        cur.execute ('''
                   create table if not exists fact_games(
                        game_id SERIAL primary key,
                        appid INT,
                        name VARCHAR,
                        price FLOAT, 
                        positive_ratings INT,
                        negative_ratings INT,
                        average_playtime INT,
                        achievements INT,
                        rating_ratio FLOAT,
                        owners VARCHAR,
                        developer_id INT REFERENCES dim_developer(developer_id) ,
                        genre_id INT REFERENCES dim_genre(genre_id),
                        release_id INT REFERENCES dim_release(release_id)
                   )
                   ''')
    conn.commit()
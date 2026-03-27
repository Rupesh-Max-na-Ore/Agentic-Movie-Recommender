import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Load dataset
movies_df = pd.read_csv("tmdb_5000_movies.csv")

# Connect to DB
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)

cur = conn.cursor()

inserted = 0

for _, row in movies_df.iterrows():
    title = row["title"]
    release_date = row.get("release_date", None)

    try:
        cur.execute(
            """
            INSERT INTO movies (title)
            VALUES (%s)
            ON CONFLICT DO NOTHING
            """,
            (title,),
        )
        inserted += 1

    except Exception:
        conn.rollback()

conn.commit()

cur.close()
conn.close()

print(f"Inserted {inserted} movies")

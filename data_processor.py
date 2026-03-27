import ast
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


# ---------------------------
# DB CONNECTION
# ---------------------------
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


# ---------------------------
# HELPERS
# ---------------------------
def convert(obj):
    try:
        return [i["name"] for i in ast.literal_eval(obj)]
    except:
        return []


def fetch_cast(obj):
    try:
        return [i["name"] for i in ast.literal_eval(obj)[:3]]
    except:
        return []


def fetch_director(obj):
    try:
        for i in ast.literal_eval(obj):
            if i["job"] == "Director":
                return i["name"]
    except:
        return None
    return None


# ---------------------------
# MAIN PROCESSOR
# ---------------------------
def process_and_insert():
    print("📥 Loading datasets...")

    movies = pd.read_csv("data/tmdb_5000_movies.csv")
    credits = pd.read_csv("data/tmdb_5000_credits.csv")

    print("🔗 Merging datasets...")
    movies = movies.merge(credits, on="title")

    print("🧠 Processing features...")

    movies["genres"] = movies["genres"].apply(convert)
    movies["keywords"] = movies["keywords"].apply(convert)
    movies["cast"] = movies["cast"].apply(fetch_cast)
    movies["director"] = movies["crew"].apply(fetch_director)

    movies["overview"] = movies["overview"].fillna("")

    movies["tags"] = (
        movies["overview"]
        + " "
        + movies["genres"].apply(lambda x: " ".join(x))
        + " "
        + movies["keywords"].apply(lambda x: " ".join(x))
        + " "
        + movies["cast"].apply(lambda x: " ".join(x))
        + " "
        + movies["director"].fillna("")
    )

    print("🗄️ Connecting to database...")
    conn = get_connection()
    cur = conn.cursor()

    print("🚀 Inserting into database...")

    inserted = 0

    for _, row in movies.iterrows():
        try:
            cur.execute(
                """
                INSERT INTO movies 
                (title, genres, keywords, cast_members, director, tags, vote_average, vote_count, overview)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    row["title"],
                    " ".join(row["genres"]),
                    " ".join(row["keywords"]),
                    " ".join(row["cast"]),
                    row["director"],
                    row["tags"],
                    row["vote_average"],
                    row["vote_count"],
                    row["overview"],
                ),
            )
            inserted += 1

        except Exception as e:
            print("Error inserting:", e)

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Done! Inserted approx {inserted} movies.")


# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    process_and_insert()

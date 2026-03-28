import ast
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("🚀 DATA PROCESSOR STARTED")


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
    import pickle

    print("📥 Loading processed data...")

    movies = pickle.load(open("movies.pkl", "rb"))

    print("🗄️ Connecting to database...")
    conn = get_connection()
    cur = conn.cursor()

    create_tables(cur)
    print("🚀 Inserting into database...")

    inserted = 0

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title TEXT UNIQUE,
        genres TEXT,
        keywords TEXT,
        cast_members TEXT,
        director TEXT,
        tags TEXT,
        vote_average FLOAT,
        vote_count INTEGER,
        overview TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS planned (
        user_username TEXT,
        movie_id INTEGER,
        expectation TEXT,
        watch_time TIMESTAMP,
        UNIQUE(user_username, movie_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS watched (
        user_username TEXT,
        movie_id INTEGER,
        review TEXT,
        rating INTEGER,
        UNIQUE(user_username, movie_id)
    );
    """)

    conn.commit()

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
                    row.get("genres", ""),
                    row.get("keywords", ""),
                    row.get("cast", ""),
                    row.get("director", ""),
                    row.get("tags", ""),
                    row.get("vote_average", 0),
                    row.get("vote_count", 0),
                    row.get("overview", ""),
                ),
            )
            inserted += 1

        except Exception as e:
            conn.rollback()  # CRITICAL FIX
            print("Error inserting:", e)
            break  # to see when fail

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Done! Inserted approx {inserted} movies.")


def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title TEXT UNIQUE,
        genres TEXT,
        keywords TEXT,
        cast_members TEXT,
        director TEXT,
        tags TEXT,
        vote_average FLOAT,
        vote_count INTEGER,
        overview TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS planned (
        user_username TEXT,
        movie_id INTEGER,
        expectation TEXT,
        watch_time TIMESTAMP,
        UNIQUE(user_username, movie_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS watched (
        user_username TEXT,
        movie_id INTEGER,
        review TEXT,
        rating INTEGER,
        UNIQUE(user_username, movie_id)
    );
    """)


# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    process_and_insert()

import os
import pickle

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# =========================
# LOAD RECOMMENDER DATA
# =========================

movies = pickle.load(open("recommender/movies.pkl", "rb"))
similarity = pickle.load(open("recommender/similarity.pkl", "rb"))

# =========================
# RECOMMENDER FUNCTIONS
# =========================


def recommend_movies(title, top_n=5):
    try:
        idx = movies[movies["title"] == title].index[0]
        distances = similarity[idx]

        movie_list = sorted(
            list(enumerate(distances)), reverse=True, key=lambda x: x[1]
        )[1 : top_n + 1]

        return [movies.iloc[i[0]].title for i in movie_list]

    except Exception as e:
        return [f"Error: {str(e)}"]


def search_movies(query, top_n=5):
    results = movies[movies["title"].str.contains(query, case=False, na=False)]
    return results["title"].head(top_n).tolist()


# =========================
# DATABASE CONNECTION
# =========================


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


# =========================
# WATCHLIST FUNCTIONS
# =========================


def add_to_watchlist(user, movie):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Step 1: Ensure user exists
        cur.execute("SELECT username FROM users WHERE username = %s", (user,))
        user_exists = cur.fetchone()

        if not user_exists:
            cur.execute("INSERT INTO users (username) VALUES (%s)", (user,))

        # Step 2: Get movie_id from title
        cur.execute("SELECT id FROM movies WHERE title ILIKE %s LIMIT 1", (movie,))
        result = cur.fetchone()

        if not result:
            return f"Movie '{movie}' not found"

        movie_id = result[0]

        # Step 3: Insert into planned table
        cur.execute(
            """
            INSERT INTO planned (user_username, movie_id, expectation)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_username, movie_id) DO NOTHING
            """,
            (user, movie_id, "Interested"),
        )

        conn.commit()
        return f"{movie} added to {user}'s watchlist"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cur.close()
        conn.close()


def get_watchlist(user):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT m.title
            FROM planned p
            JOIN movies m ON p.movie_id = m.id
            WHERE p.user_username = %s
            """,
            (user,),
        )

        rows = cur.fetchall()

        if not rows:
            return ["No movies in watchlist"]

        return [r[0] for r in rows]

    except Exception as e:
        return [f"Error: {str(e)}"]

    finally:
        cur.close()
        conn.close()


def mark_as_watched(user, movie, review="Good", rating=5):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Ensure user exists
        cur.execute("SELECT username FROM users WHERE username = %s", (user,))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (username) VALUES (%s)", (user,))

        # Get movie_id
        cur.execute(
            "SELECT id FROM movies WHERE title ILIKE %s LIMIT 1", (f"%{movie}%",)
        )
        result = cur.fetchone()

        if not result:
            return f"Movie '{movie}' not found"

        movie_id = result[0]

        # Insert into watched
        cur.execute(
            """
            INSERT INTO watched (user_username, movie_id, review, rating)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_username, movie_id) DO NOTHING
            """,
            (user, movie_id, review, rating),
        )

        # Remove from planned (optional but realistic)
        cur.execute(
            """
            DELETE FROM planned
            WHERE user_username = %s AND movie_id = %s
            """,
            (user, movie_id),
        )

        conn.commit()
        return f"{movie} marked as watched for {user}"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cur.close()
        conn.close()

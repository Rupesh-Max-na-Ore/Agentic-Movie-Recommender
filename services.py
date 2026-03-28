import os
from datetime import datetime, timedelta

import psycopg2
from dateutil import parser
from dotenv import load_dotenv

load_dotenv()

# =========================
# LOAD RECOMMENDER DATA
# =========================

movies = None
similarity = None


def load_models():
    global movies, similarity
    import os
    import pickle
    import time

    # 🔥 WAIT until files exist
    while not (
        os.path.exists("recommender/movies.pkl")
        and os.path.exists("recommender/similarity.pkl")
    ):
        print("⏳ Waiting for model files to be available...")
        time.sleep(2)

    if movies is None or similarity is None:
        print("📥 Loading model files...")
        movies = pickle.load(open("recommender/movies.pkl", "rb"))
        similarity = pickle.load(open("recommender/similarity.pkl", "rb"))


# =========================
# RECOMMENDER FUNCTIONS
# =========================


def recommend_movies(title, top_n=5):
    load_models()
    try:
        # Step 1: Check if movie exists in recommender dataset
        if title.lower() not in movies["title"].str.lower().values:
            return [
                "This movie is not in the recommendation system yet, but you can still track it in your watchlist."
            ]

        # Step 2: Get index
        idx = movies[movies["title"] == title].index[0]
        distances = similarity[idx]

        # Step 3: Get top recommendations
        movie_list = sorted(
            list(enumerate(distances)), reverse=True, key=lambda x: x[1]
        )[1 : top_n + 1]

        return [movies.iloc[i[0]].title for i in movie_list]

    except Exception as e:
        return [f"Error: {str(e)}"]


def search_movies(query, top_n=5):
    load_models()
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT title
            FROM movies
            WHERE tags ILIKE %s
            LIMIT %s
            """,
            (f"%{query}%", top_n),
        )

        rows = cur.fetchall()

        if not rows:
            return ["No movies found"]

        return [r[0] for r in rows]

    finally:
        cur.close()
        conn.close()


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


def add_to_watchlist(user, movie, expectation=None, watch_time=None):
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
        parsed_time = parse_watch_time(watch_time)

        cur.execute(
            """
            INSERT INTO planned (user_username, movie_id, expectation, watch_time)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_username, movie_id) DO NOTHING
            """,
            (user, movie_id, expectation or "Interested", parsed_time),
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
            SELECT m.title, p.expectation, p.watch_time
            FROM planned p
            JOIN movies m ON p.movie_id = m.id
            WHERE p.user_username = %s
            """,
            (user,),
        )

        rows = cur.fetchall()

        if not rows:
            return ["No movies in watchlist"]

        return [
            {
                "title": r[0],
                "expectation": r[1],
                "watch_time": r[2].strftime("%Y-%m-%d %H:%M")
                if r[2]
                else "Not scheduled",
            }
            for r in rows
        ]

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


def add_movie(
    movie_title, genres=None, keywords=None, cast_members=None, director=None
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Step 1: Check if movie already exists
        cur.execute(
            "SELECT id FROM movies WHERE title ILIKE %s LIMIT 1", (f"%{movie_title}%",)
        )
        existing = cur.fetchone()

        if existing:
            return f"Movie '{movie_title}' already exists in database"

        # Step 2: Insert movie
        cur.execute(
            """
            INSERT INTO movies (title, genres, keywords, cast_members, director)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (movie_title, genres, keywords, cast_members, director),
        )

        # 🔥 IMPORTANT: commit AFTER insert
        conn.commit()

        # Step 3: Verify insertion (debug check)
        cur.execute(
            "SELECT title FROM movies WHERE title ILIKE %s", (f"%{movie_title}%",)
        )
        verify = cur.fetchone()

        if verify:
            return f"Movie '{movie_title}' added successfully with metadata."
        else:
            return "Insert failed unexpectedly"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cur.close()
        conn.close()


def filter_movies(keyword, top_n=5):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT title
            FROM movies
            WHERE tags ILIKE %s
            LIMIT %s
            """,
            (f"%{keyword}%", top_n),
        )

        rows = cur.fetchall()

        if not rows:
            return ["No matching movies found"]

        return [r[0] for r in rows]

    finally:
        cur.close()
        conn.close()


def top_movies(keyword=None, top_n=10, verbose=False):
    load_models()
    conn = get_connection()
    cur = conn.cursor()

    try:
        if keyword:
            cur.execute(
                """
                SELECT title, vote_average, overview
                FROM movies
                WHERE tags ILIKE %s
                ORDER BY vote_average DESC, vote_count DESC
                LIMIT %s
                """,
                (f"%{keyword}%", top_n),
            )
        else:
            cur.execute(
                """
                SELECT title, vote_average, overview
                FROM movies
                ORDER BY vote_average DESC, vote_count DESC
                LIMIT %s
                """,
                (top_n,),
            )

        rows = cur.fetchall()

        if not rows:
            return ["No movies found"]

        if verbose:
            result = [
                {
                    "title": r[0],
                    "rating": round(r[1], 1) if r[1] is not None else "N/A",
                    "overview": r[2] if r[2] else "No description available",
                }
                for r in rows
            ]

            return result

        return [r[0] for r in rows]

    finally:
        cur.close()
        conn.close()


def get_movie_details(title):
    load_models()
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT 
                title,
                genres,
                keywords,
                cast_members,
                director,
                vote_average,
                vote_count,
                overview
            FROM movies
            WHERE title ILIKE %s
            LIMIT 1
            """,
            (f"%{title}%",),
        )

        row = cur.fetchone()

        if not row:
            return "Movie not found"

        return {
            "title": row[0],
            "rating": round(row[5], 1) if row[5] else "N/A",
            "votes": row[6],
            "genres": row[1],
            "keywords": row[2],
            "cast": row[3],
            "director": row[4],
            "overview": row[7] if row[7] else row[1] or "No description available",
        }

    finally:
        cur.close()
        conn.close()


def add_user(username):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username) VALUES (%s) ON CONFLICT DO NOTHING",
            (username,),
        )

        conn.commit()
        return f"User '{username}' added successfully"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cur.close()
        conn.close()


def parse_watch_time(time_str):
    if not time_str:
        return None

    try:
        # Handle "tomorrow"
        if "tomorrow" in time_str.lower():
            base = datetime.now() + timedelta(days=1)
            time_part = time_str.lower().replace("tomorrow", "").strip()
            parsed_time = (
                parser.parse(time_part).time() if time_part else datetime.now().time()
            )
            return datetime.combine(base.date(), parsed_time)

        # General parsing
        return parser.parse(time_str)

    except Exception:
        return None

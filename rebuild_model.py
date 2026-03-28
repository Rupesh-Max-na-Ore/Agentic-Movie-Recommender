import ast
import pickle

import pandas as pd

print("📥 Loading datasets...")

movies = pd.read_csv("data/tmdb_5000_movies.csv")
credits = pd.read_csv("data/tmdb_5000_credits.csv")

print("🔗 Merging datasets...")

movies = movies.merge(credits, on="title")


def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i["name"])
    return L


def fetch_cast(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i["name"])
            counter += 1
        else:
            break
    return L


def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i["job"] == "Director":
            L.append(i["name"])
    return L


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
    + movies["director"].apply(lambda x: " ".join(x))
)

movies_final = movies[
    [
        "title",
        "overview",
        "genres",
        "keywords",
        "cast",
        "director",
        "vote_average",
        "vote_count",
        "tags",
    ]
]

movies_final["genres"] = movies_final["genres"].apply(lambda x: " ".join(x))
movies_final["keywords"] = movies_final["keywords"].apply(lambda x: " ".join(x))
movies_final["cast"] = movies_final["cast"].apply(lambda x: " ".join(x))
movies_final["director"] = movies_final["director"].apply(lambda x: " ".join(x))

print("💾 Saving movies.pkl...")

pickle.dump(movies_final, open("movies.pkl", "wb"))

print("✅ movies.pkl created successfully!")

# Move to recommender directory at last
